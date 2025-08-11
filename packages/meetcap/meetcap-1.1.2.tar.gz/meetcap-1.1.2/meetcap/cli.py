"""command-line interface for meetcap"""

import signal
import sys
import threading
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from meetcap import __version__
from meetcap.core.devices import (
    find_device_by_index,
    find_device_by_name,
    list_audio_devices,
    print_devices,
    select_best_device,
)
from meetcap.core.hotkeys import HotkeyManager, PermissionChecker
from meetcap.core.recorder import AudioRecorder
from meetcap.services.model_download import (
    ensure_mlx_whisper_model,
    ensure_qwen_model,
    ensure_whisper_model,
    verify_mlx_whisper_model,
    verify_qwen_model,
    verify_whisper_model,
)
from meetcap.services.summarization import SummarizationService, save_summary
from meetcap.services.transcription import (
    FasterWhisperService,
    MlxWhisperService,
    WhisperCppService,
    save_transcript,
)
from meetcap.utils.config import Config
from meetcap.utils.logger import ErrorHandler, logger

console = Console()
app = typer.Typer(
    name="meetcap",
    help="offline meeting recorder & summarizer for macos",
    add_completion=False,
)


class RecordingOrchestrator:
    """orchestrates the recording, transcription, and summarization workflow"""

    def __init__(self, config: Config):
        """initialize orchestrator with config."""
        self.config = config
        self.recorder = None
        self.hotkey_manager = None
        self.stop_event = threading.Event()
        self.interrupt_count = 0
        self.last_interrupt_time = 0
        self.processing_complete = False
        self.graceful_stop_requested = False

    def run(
        self,
        device: str | None = None,
        output_dir: str | None = None,
        sample_rate: int | None = None,
        channels: int | None = None,
        stt_engine: str | None = None,
        llm_path: str | None = None,
        seed: int | None = None,
    ) -> None:
        """
        run the complete recording workflow.

        args:
            device: device name or index
            output_dir: output directory path
            sample_rate: audio sample rate
            channels: number of channels
            stt_engine: stt engine to use
            llm_path: path to llm model
            seed: random seed for llm
        """
        # setup configuration
        if output_dir:
            out_path = Path(output_dir)
        else:
            out_path = self.config.expand_path(self.config.get("paths", "out_dir"))

        sample_rate = sample_rate or self.config.get("audio", "sample_rate")
        channels = channels or self.config.get("audio", "channels")

        # initialize recorder
        self.recorder = AudioRecorder(
            output_dir=out_path,
            sample_rate=sample_rate,
            channels=channels,
        )

        # find audio device
        devices = list_audio_devices()
        if not devices:
            ErrorHandler.handle_runtime_error(RuntimeError("no audio input devices found"))
            return  # this line shouldn't be reached due to sys.exit, but helps with testing

        selected_device = None
        if device:
            # try as index first
            try:
                device_index = int(device)
                selected_device = find_device_by_index(devices, device_index)
            except ValueError:
                # try as name
                selected_device = find_device_by_name(devices, device)
        else:
            # auto-select best device
            preferred = self.config.get("audio", "preferred_device")
            selected_device = find_device_by_name(devices, preferred)
            if not selected_device:
                selected_device = select_best_device(devices)

        if not selected_device:
            ErrorHandler.handle_config_error(ValueError(f"device not found: {device}"))
            return  # this line shouldn't be reached due to sys.exit, but helps with testing

        # show recording banner
        console.print(
            Panel(
                f"[bold cyan]meetcap v{__version__}[/bold cyan]\n"
                f"[green]starting recording...[/green]",
                title="🎙️ meeting recorder",
                expand=False,
            )
        )

        # setup hotkey handler
        self.hotkey_manager = HotkeyManager(self._stop_recording)
        hotkey_combo = self.config.get("hotkey", "stop")

        # setup signal handler for Ctrl-C
        signal.signal(signal.SIGINT, self._handle_interrupt)

        try:
            # start recording
            self.recorder.start_recording(
                device_index=selected_device.index,
                device_name=selected_device.name,
            )

            # start hotkey listener
            self.hotkey_manager.start(hotkey_combo)
            console.print("[cyan]⌃C[/cyan] press once to stop recording, twice to exit")

            # show progress while recording
            self._show_recording_progress()

            # stop recording (triggered by hotkey or Ctrl-C)
            final_path = self.recorder.stop_recording()
            if not final_path:
                ErrorHandler.handle_runtime_error(RuntimeError("recording failed or was empty"))

            # run transcription and summarization
            self.processing_complete = False
            self._process_recording(
                audio_path=final_path,
                stt_engine=stt_engine,
                llm_path=llm_path,
                seed=seed,
            )
            self.processing_complete = True

        except KeyboardInterrupt:
            # handle KeyboardInterrupt based on current state
            if self.graceful_stop_requested:
                # this is a second Ctrl-C after we already handled a graceful stop
                console.print("\n[red]force exit requested[/red]")
                if self.recorder and self.recorder.is_recording():
                    self.recorder.stop_recording()
                return
            elif self.recorder and self.recorder.is_recording():
                # if still recording, this means it's the first Ctrl-C during recording
                console.print("\n[yellow]⏹[/yellow] stopping recording...")
                final_path = self.recorder.stop_recording()
                if final_path:
                    # continue with processing
                    self.processing_complete = False
                    self._process_recording(
                        audio_path=final_path,
                        stt_engine=stt_engine,
                        llm_path=llm_path,
                        seed=seed,
                    )
                    self.processing_complete = True
                else:
                    console.print(
                        "\n[yellow]operation cancelled - no recording to process[/yellow]"
                    )
            else:
                # if not recording, this is during processing or already stopped
                console.print("\n[yellow]operation cancelled[/yellow]")
        except Exception as e:
            ErrorHandler.handle_runtime_error(e)
        finally:
            if self.hotkey_manager:
                self.hotkey_manager.stop()
            # restore default signal handler
            signal.signal(signal.SIGINT, signal.default_int_handler)

    def _handle_interrupt(self, signum, frame) -> None:
        """handle Ctrl-C interrupt signal."""
        current_time = time.time()

        # check for double Ctrl-C (within 2 seconds)
        if current_time - self.last_interrupt_time < 2.0:
            self.interrupt_count += 1
        else:
            self.interrupt_count = 1

        self.last_interrupt_time = current_time

        if self.interrupt_count >= 2:
            # double Ctrl-C: exit immediately
            console.print("\n[red]double interrupt - exiting immediately[/red]")
            if self.recorder and self.recorder.is_recording():
                self.recorder.stop_recording()
            sys.exit(1)
        else:
            # single Ctrl-C: stop recording gracefully
            if self.recorder and self.recorder.is_recording():
                console.print(
                    "\n[yellow]⏹[/yellow] stopping recording (press Ctrl-C again to force exit)"
                )
                self._stop_recording()
                self.graceful_stop_requested = True
                # don't let KeyboardInterrupt propagate - we want to continue to processing
                return
            elif not self.processing_complete:
                console.print(
                    "\n[yellow]processing in progress (press Ctrl-C again to force exit)[/yellow]"
                )
                # don't exit during processing, let it continue
                return
            else:
                # if not recording and processing is done, exit
                sys.exit(0)

    def _stop_recording(self) -> None:
        """callback for hotkey to stop recording."""
        self.stop_event.set()

    def _show_recording_progress(self) -> None:
        """display recording progress until stopped."""
        start_time = time.time()
        hotkey_str = (
            self.config.get("hotkey", "stop")
            .replace("<cmd>", "⌘")
            .replace("<shift>", "⇧")
            .replace("+", "")
            .upper()
        )

        try:
            while not self.stop_event.is_set():
                elapsed = time.time() - start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)

                console.print(
                    f"[cyan]recording[/cyan] {minutes:02d}:{seconds:02d} "
                    f"[dim]({hotkey_str} or ⌃C to stop)[/dim]",
                    end="\r",
                )

                # use stop_event.wait() instead of time.sleep() to be more responsive
                if self.stop_event.wait(timeout=0.5):
                    break

        except KeyboardInterrupt:
            # KeyboardInterrupt during progress display - this is expected
            # the signal handler should have set the stop event
            pass

        console.print()  # new line after progress

    def _process_recording(
        self,
        audio_path: Path,
        stt_engine: str,
        llm_path: str | None,
        seed: int | None,
    ) -> None:
        """
        process recorded audio: transcribe and summarize.

        args:
            audio_path: path to recorded audio
            stt_engine: stt engine to use
            llm_path: optional llm model path
            seed: optional random seed
        """
        base_path = audio_path.with_suffix("")

        # transcription
        console.print("\n[bold]📝 transcription[/bold]")

        # use configured engine if not specified
        if not stt_engine:
            stt_engine = self.config.get("models", "stt_engine", "faster-whisper")
            # map config names to CLI names
            if stt_engine == "faster-whisper":
                stt_engine = "fwhisper"
            elif stt_engine == "mlx-whisper":
                stt_engine = "mlx"

        if stt_engine == "fwhisper":
            stt_model_name = self.config.get("models", "stt_model_name", "large-v3")
            stt_model_path = self.config.expand_path(self.config.get("models", "stt_model_path"))
            stt_service = FasterWhisperService(
                model_path=str(stt_model_path),
                model_name=stt_model_name,
                auto_download=True,
            )
        elif stt_engine == "mlx":
            mlx_model_name = self.config.get(
                "models", "mlx_stt_model_name", "mlx-community/whisper-large-v3-turbo"
            )
            mlx_model_path = self.config.expand_path(
                self.config.get("models", "mlx_stt_model_path")
            )
            stt_service = MlxWhisperService(
                model_name=mlx_model_name,
                model_path=str(mlx_model_path) if mlx_model_path.exists() else None,
                auto_download=True,
            )
        else:
            # whisper.cpp
            stt_model_path = self.config.get("models", "stt_model_path")
            whisper_cpp_path = self.config.get("models", "whisper_cpp_path", "whisper")
            stt_service = WhisperCppService(
                whisper_cpp_path=whisper_cpp_path,
                model_path=stt_model_path,
            )

        try:
            transcript_result = stt_service.transcribe(audio_path)
            text_path, json_path = save_transcript(transcript_result, base_path)
        except Exception as e:
            console.print(f"[red]transcription failed: {e}[/red]")
            return

        # summarization
        console.print("\n[bold]🤖 summarization[/bold]")

        # use provided path or default from config
        if llm_path:
            llm_path = Path(llm_path)
        else:
            llm_path = self.config.expand_path(self.config.get("models", "llm_gguf_path"))

        # ensure model exists (download if needed)
        if not llm_path.exists():
            console.print("[yellow]llm model not found, attempting download...[/yellow]")
            models_dir = self.config.expand_path(self.config.get("paths", "models_dir"))
            llm_path = ensure_qwen_model(models_dir)
            if not llm_path:
                console.print("[red]failed to download llm model[/red]")
                return

        llm_config = self.config.get_section("llm")

        llm_service = SummarizationService(
            model_path=llm_path,
            n_ctx=llm_config.get("n_ctx", 8192),
            n_threads=llm_config.get("n_threads", 6),
            n_gpu_layers=llm_config.get("n_gpu_layers", 35),
            n_batch=llm_config.get("n_batch", 1024),
            temperature=llm_config.get("temperature", 0.4),
            max_tokens=llm_config.get("max_tokens", 2048),
            seed=seed,
        )

        try:
            # read transcript text
            with open(text_path, encoding="utf-8") as f:
                transcript_text = f.read()

            summary = llm_service.summarize(transcript_text)
            summary_path = save_summary(summary, base_path)
        except Exception as e:
            console.print(f"[red]summarization failed: {e}[/red]")
            return

        # show final results
        console.print(
            Panel(
                f"[green]✅ recording complete![/green]\n\n"
                f"[bold]artifacts:[/bold]\n"
                f"  audio: {audio_path}\n"
                f"  transcript: {text_path}\n"
                f"  json: {json_path}\n"
                f"  summary: {summary_path}",
                title="📦 output files",
                expand=False,
            )
        )


@app.command()
def record(
    device: str | None = typer.Option(
        None,
        "--device",
        "-d",
        help="audio device name or index",
    ),
    out: str | None = typer.Option(
        None,
        "--out",
        "-o",
        help="output directory",
    ),
    rate: int | None = typer.Option(
        None,
        "--rate",
        "-r",
        help="sample rate (hz)",
    ),
    channels: int | None = typer.Option(
        None,
        "--channels",
        "-c",
        help="number of channels",
    ),
    stt: str | None = typer.Option(
        None,
        "--stt",
        help="stt engine: fwhisper, mlx, or whispercpp (defaults to config)",
    ),
    llm: str | None = typer.Option(
        None,
        "--llm",
        help="path to llm gguf model",
    ),
    seed: int | None = typer.Option(
        None,
        "--seed",
        help="random seed for llm",
    ),
    log_file: str | None = typer.Option(
        None,
        "--log-file",
        help="path to log file",
    ),
) -> None:
    """start recording a meeting"""
    # setup logging
    if log_file:
        logger.add_file_handler(Path(log_file))

    # load config
    config = Config()

    # run orchestrator
    orchestrator = RecordingOrchestrator(config)
    try:
        orchestrator.run(
            device=device,
            output_dir=out,
            sample_rate=rate,
            channels=channels,
            stt_engine=stt,
            llm_path=llm,
            seed=seed,
        )
    except KeyboardInterrupt:
        # suppress Typer's "Aborted!" message for KeyboardInterrupt
        # the orchestrator's signal handler already managed the graceful stop
        sys.exit(0)


@app.command()
def summarize(
    audio_file: str = typer.Argument(
        ...,
        help="path to audio file (m4a, wav, mp3, etc.)",
    ),
    stt: str | None = typer.Option(
        None,
        "--stt",
        help="stt engine: fwhisper, mlx, or whispercpp (defaults to config)",
    ),
    llm: str | None = typer.Option(
        None,
        "--llm",
        help="path to llm gguf model",
    ),
    seed: int | None = typer.Option(
        None,
        "--seed",
        help="random seed for llm",
    ),
    out: str | None = typer.Option(
        None,
        "--out",
        "-o",
        help="output directory for results",
    ),
    log_file: str | None = typer.Option(
        None,
        "--log-file",
        help="path to log file",
    ),
) -> None:
    """process an existing audio file (transcribe and summarize)"""
    # setup logging
    if log_file:
        logger.add_file_handler(Path(log_file))

    # validate input file
    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]error: file not found: {audio_file}[/red]")
        sys.exit(1)

    # check if file format is supported
    supported_formats = [".m4a", ".wav", ".mp3", ".mp4", ".aac", ".flac", ".ogg", ".opus", ".webm"]
    if audio_path.suffix.lower() not in supported_formats:
        console.print(f"[red]error: unsupported file format: {audio_path.suffix}[/red]")
        console.print(f"[yellow]supported formats: {', '.join(supported_formats)}[/yellow]")
        sys.exit(1)

    # load config
    config = Config()

    # determine output directory
    if out:
        output_dir = Path(out)
    else:
        # default to same directory as input file
        output_dir = audio_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # show processing banner
    console.print(
        Panel(
            f"[bold cyan]processing audio file[/bold cyan]\n"
            f"[white]file: {audio_path.name}[/white]\n"
            f"[white]size: {audio_path.stat().st_size / (1024 * 1024):.1f} MB[/white]",
            title="📁 file processing",
            expand=False,
        )
    )

    # create base path for outputs in the output directory
    base_name = audio_path.stem
    base_path = output_dir / base_name

    # process the file (transcribe and summarize)
    orchestrator = RecordingOrchestrator(config)
    orchestrator.processing_complete = False

    try:
        orchestrator._process_recording(
            audio_path=audio_path,
            stt_engine=stt,
            llm_path=llm,
            seed=seed,
        )
        orchestrator.processing_complete = True

        # show completion message
        console.print(
            Panel(
                f"[green]✅ processing complete![/green]\n\n"
                f"[bold]output files:[/bold]\n"
                f"  transcript: {base_path}.transcript.txt\n"
                f"  json: {base_path}.transcript.json\n"
                f"  summary: {base_path}.summary.md",
                title="📦 results",
                expand=False,
            )
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]processing cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]error processing file: {e}[/red]")
        ErrorHandler.handle_runtime_error(e)


@app.command()
def devices() -> None:
    """list available audio input devices"""
    console.print("[bold]🎤 audio input devices[/bold]\n")

    devices = list_audio_devices()
    if devices:
        print_devices(devices)
    else:
        console.print("[red]no audio devices found[/red]")
        console.print("\n[yellow]troubleshooting:[/yellow]")
        console.print("  • ensure ffmpeg is installed: brew install ffmpeg")
        console.print("  • grant microphone permission to your terminal")
        console.print("  • check audio midi setup for device configuration")


@app.command()
def setup() -> None:
    """interactive setup wizard for first-time configuration"""
    console.print(
        Panel(
            "[bold cyan]meetcap setup wizard[/bold cyan]\n"
            "[white]this will guide you through permissions and model downloads[/white]",
            title="🛠️ initial setup",
            expand=False,
        )
    )

    config = Config()
    models_dir = config.expand_path(config.get("paths", "models_dir", "~/.meetcap/models"))

    # step 1: check ffmpeg
    console.print("\n[bold]step 1: checking dependencies[/bold]")
    import subprocess

    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=2)
        if result.returncode == 0:
            console.print("[green]✓[/green] ffmpeg is installed")
        else:
            console.print("[red]✗[/red] ffmpeg error")
            console.print("[yellow]please install: brew install ffmpeg[/yellow]")
            return
    except FileNotFoundError:
        console.print("[red]✗[/red] ffmpeg not found")
        console.print("[yellow]please install: brew install ffmpeg[/yellow]")
        return

    # step 2: test microphone permission
    console.print("\n[bold]step 2: microphone permission[/bold]")
    console.print("[cyan]testing microphone access...[/cyan]")
    console.print("[yellow]⚠ macos may prompt for microphone permission[/yellow]")

    devices = list_audio_devices()
    if not devices:
        console.print("[red]✗[/red] no audio devices found")
        console.print("[yellow]grant microphone permission in system preferences[/yellow]")
        console.print("system preferences → privacy & security → microphone")
        return

    # try a brief recording to trigger permission dialog
    console.print("[cyan]attempting test recording to verify permissions...[/cyan]")
    recorder = AudioRecorder()
    try:
        test_path = recorder.start_recording(
            device_index=devices[0].index,
            device_name=devices[0].name,
        )
        time.sleep(2)  # record for 2 seconds
        recorder.stop_recording()

        # if we got here, permissions are granted
        console.print("[green]✓[/green] microphone permission granted")
        console.print(f"  detected {len(devices)} audio device(s)")

        # clean up test file
        if test_path.exists():
            test_path.unlink()
    except Exception as e:
        console.print("[red]✗[/red] microphone permission denied or error")
        console.print(f"  error: {e}")
        console.print("[yellow]grant permission in system preferences and run setup again[/yellow]")
        return

    # step 3: test hotkey permission
    console.print("\n[bold]step 3: input monitoring permission (for hotkeys)[/bold]")
    console.print("[cyan]testing hotkey functionality...[/cyan]")
    console.print("[yellow]⚠ grant input monitoring permission if prompted[/yellow]")

    # create a simple test for hotkey
    test_triggered = threading.Event()

    def test_callback():
        test_triggered.set()

    hotkey_mgr = HotkeyManager(test_callback)
    hotkey_mgr.start("<cmd>+<shift>+t")  # test hotkey

    console.print("[cyan]press ⌘⇧T to test hotkey (or wait 5 seconds to skip)...[/cyan]")

    if test_triggered.wait(timeout=5.0):
        console.print("[green]✓[/green] hotkey permission granted")
    else:
        console.print("[yellow]⚠[/yellow] hotkey not detected (permission may be needed)")
        console.print("  grant input monitoring in system preferences if you want hotkey support")
        console.print("  you can still use Ctrl-C to stop recordings")

    hotkey_mgr.stop()

    # step 4: select and download whisper model
    console.print("\n[bold]step 4: select whisper (speech-to-text) model[/bold]")

    # check if running on apple silicon
    import platform

    is_apple_silicon = platform.processor() == "arm"

    if is_apple_silicon:
        console.print(
            "[cyan]detected Apple Silicon - mlx-whisper available for better performance[/cyan]"
        )
        stt_engines = [
            {
                "key": "mlx",
                "name": "MLX Whisper (recommended for Apple Silicon)",
                "default_model": "mlx-community/whisper-large-v3-turbo",
            },
            {"key": "faster", "name": "Faster Whisper (compatible)", "default_model": "large-v3"},
        ]

        console.print("\n[cyan]available stt engines:[/cyan]")
        for i, engine in enumerate(stt_engines, 1):
            console.print(f"  {i}. [bold]{engine['name']}[/bold]")

        engine_choice = typer.prompt("\nselect engine (1-2)", default="1")
        try:
            engine_idx = int(engine_choice) - 1
            if 0 <= engine_idx < len(stt_engines):
                selected_engine = stt_engines[engine_idx]
            else:
                selected_engine = stt_engines[0]
        except ValueError:
            selected_engine = stt_engines[0]
    else:
        selected_engine = {"key": "faster", "name": "Faster Whisper", "default_model": "large-v3"}

    console.print(f"\n[cyan]selected engine: {selected_engine['name']}[/cyan]")

    if selected_engine["key"] == "mlx":
        # mlx-whisper models
        mlx_models = [
            {
                "name": "mlx-community/whisper-large-v3-turbo",
                "desc": "Fast and accurate (recommended)",
                "size": "~1.5GB",
            },
            {
                "name": "mlx-community/whisper-large-v3-mlx",
                "desc": "Most accurate",
                "size": "~1.5GB",
            },
            {
                "name": "mlx-community/whisper-small-mlx",
                "desc": "Smallest, fastest",
                "size": "~466MB",
            },
        ]

        console.print("\n[cyan]available mlx-whisper models:[/cyan]")
        for i, model in enumerate(mlx_models, 1):
            console.print(
                f"  {i}. [bold]{model['name'].split('/')[-1]}[/bold] - {model['desc']} ({model['size']})"
            )

        choice = typer.prompt("\nselect model (1-3)", default="1")
        try:
            model_idx = int(choice) - 1
            if 0 <= model_idx < len(mlx_models):
                mlx_model_name = mlx_models[model_idx]["name"]
            else:
                mlx_model_name = mlx_models[0]["name"]
        except ValueError:
            mlx_model_name = mlx_models[0]["name"]

        console.print(f"\n[cyan]selected: {mlx_model_name.split('/')[-1]}[/cyan]")

        # verify/download if needed
        if verify_mlx_whisper_model(mlx_model_name, models_dir):
            console.print(
                f"[green]✓[/green] mlx-whisper {mlx_model_name.split('/')[-1]} already installed"
            )
        else:
            console.print(
                f"[cyan]downloading mlx-whisper {mlx_model_name.split('/')[-1]}...[/cyan]"
            )
            console.print("[dim]this may take several minutes[/dim]")

            model_path = ensure_mlx_whisper_model(mlx_model_name, models_dir)

            if model_path:
                console.print("[green]✓[/green] mlx-whisper model ready")
            else:
                console.print("[red]✗[/red] mlx-whisper download failed")
                console.print("[yellow]check your internet connection and try again[/yellow]")
                return

        # update config
        config.config["models"]["stt_engine"] = "mlx-whisper"
        config.config["models"]["mlx_stt_model_name"] = mlx_model_name
        config.save()

    else:
        # faster-whisper models
        whisper_models = [
            {"name": "large-v3", "desc": "Most accurate, slower (default)", "size": "~1.5GB"},
            {
                "name": "large-v3-turbo",
                "desc": "Faster than v3, slightly less accurate",
                "size": "~1.5GB",
            },
            {"name": "small", "desc": "Fast, good for quick transcripts", "size": "~466MB"},
        ]

        console.print("\n[cyan]available whisper models:[/cyan]")
        for i, model in enumerate(whisper_models, 1):
            console.print(
                f"  {i}. [bold]{model['name']}[/bold] - {model['desc']} ({model['size']})"
            )

        choice = typer.prompt("\nselect model (1-3)", default="1")
        try:
            model_idx = int(choice) - 1
            if 0 <= model_idx < len(whisper_models):
                stt_model_name = whisper_models[model_idx]["name"]
            else:
                stt_model_name = "large-v3"
        except ValueError:
            stt_model_name = "large-v3"

        console.print(f"\n[cyan]selected: {stt_model_name}[/cyan]")

        # download if needed
        if verify_whisper_model(stt_model_name, models_dir):
            console.print(f"[green]✓[/green] whisper {stt_model_name} already installed")
        else:
            console.print(f"[cyan]downloading whisper {stt_model_name}...[/cyan]")
            console.print("[dim]this may take several minutes[/dim]")

            model_path = ensure_whisper_model(stt_model_name, models_dir)

            if model_path:
                console.print("[green]✓[/green] whisper model downloaded")
            else:
                console.print("[red]✗[/red] whisper download failed")
                console.print("[yellow]check your internet connection and try again[/yellow]")
                return

        # update config
        config.config["models"]["stt_engine"] = "faster-whisper"
        config.config["models"]["stt_model_name"] = stt_model_name
        config.config["models"]["stt_model_path"] = f"~/.meetcap/models/whisper-{stt_model_name}"
        config.save()

    # step 5: select and download llm model
    console.print("\n[bold]step 5: select llm (summarization) model[/bold]")

    llm_models = [
        {
            "key": "thinking",
            "name": "Qwen3-4B-Thinking",
            "desc": "Best for meeting summaries (default)",
            "size": "~4-5GB",
        },
        {
            "key": "instruct",
            "name": "Qwen3-4B-Instruct",
            "desc": "General purpose, follows instructions",
            "size": "~4-5GB",
        },
        {
            "key": "gpt-oss",
            "name": "GPT-OSS-20B",
            "desc": "Larger model, more capable",
            "size": "~11GB",
        },
    ]

    console.print("\n[cyan]available llm models:[/cyan]")
    for i, model in enumerate(llm_models, 1):
        console.print(f"  {i}. [bold]{model['name']}[/bold] - {model['desc']} ({model['size']})")

    choice = typer.prompt("\nselect model (1-3)", default="1")
    try:
        model_idx = int(choice) - 1
        if 0 <= model_idx < len(llm_models):
            llm_choice = llm_models[model_idx]
        else:
            llm_choice = llm_models[0]
    except ValueError:
        llm_choice = llm_models[0]

    console.print(f"\n[cyan]selected: {llm_choice['name']}[/cyan]")

    # map choice to filename
    model_filenames = {
        "thinking": "Qwen3-4B-Thinking-2507-Q8_K_XL.gguf",
        "instruct": "Qwen3-4B-Instruct-2507-Q8_K_XL.gguf",
        "gpt-oss": "gpt-oss-20b-Q4_K_M.gguf",
    }

    model_filename = model_filenames[llm_choice["key"]]
    model_path = models_dir / model_filename

    # check if already exists
    if model_path.exists():
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 100:
            console.print(f"[green]✓[/green] {llm_choice['name']} already installed")
        else:
            console.print("[yellow]⚠[/yellow] model file seems incomplete, re-downloading")
            model_path = None
    else:
        model_path = None

    if not model_path:
        console.print(f"[cyan]downloading {llm_choice['name']} ({llm_choice['size']})...[/cyan]")
        console.print("[yellow]⚠ this is a large download and may take 10-30 minutes[/yellow]")

        # ask for confirmation
        if typer.confirm("proceed with download?"):
            model_path = ensure_qwen_model(models_dir, model_choice=llm_choice["key"])

            if model_path:
                console.print(f"[green]✓[/green] {llm_choice['name']} downloaded")
                # update config with selected model
                config.config["models"]["llm_model_name"] = model_filename
                config.config["models"]["llm_gguf_path"] = f"~/.meetcap/models/{model_filename}"
                config.save()
            else:
                console.print(f"[red]✗[/red] {llm_choice['name']} download failed")
                console.print("[yellow]check your internet connection and try again[/yellow]")
                return
        else:
            console.print("[yellow]skipped llm download (summarization will not work)[/yellow]")

    # final summary
    console.print(
        Panel(
            "[green]✅ setup complete![/green]\n\n"
            "you're ready to start recording meetings:\n"
            "[cyan]meetcap record[/cyan]",
            title="🎉 success",
            expand=False,
        )
    )


@app.command()
def verify() -> None:
    """quick verification of system setup"""
    console.print("[bold]🔍 system verification[/bold]\n")

    config = Config()
    checks = []

    # check ffmpeg
    import subprocess

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=2,
        )
        if result.returncode == 0:
            checks.append(("ffmpeg", "✅ installed", "green"))
        else:
            checks.append(("ffmpeg", "❌ error", "red"))
    except FileNotFoundError:
        checks.append(("ffmpeg", "❌ not found", "red"))
    except Exception:
        checks.append(("ffmpeg", "⚠️ unknown", "yellow"))

    # check audio devices
    devices = list_audio_devices()
    if devices:
        aggregate_found = any(d.is_aggregate for d in devices)
        if aggregate_found:
            checks.append(
                ("audio devices", f"✅ {len(devices)} found (aggregate detected)", "green")
            )
        else:
            checks.append(("audio devices", f"⚠️ {len(devices)} found (no aggregate)", "yellow"))
    else:
        checks.append(("audio devices", "❌ none found", "red"))

    # check microphone permission
    if PermissionChecker.check_microphone_permission():
        checks.append(("microphone", "✅ permission likely granted", "green"))
    else:
        checks.append(("microphone", "⚠️ permission unknown", "yellow"))

    # check stt models (no download)
    stt_model_name = config.get("models", "stt_model_name", "large-v3")
    mlx_model_name = config.get(
        "models", "mlx_stt_model_name", "mlx-community/whisper-large-v3-turbo"
    )
    models_dir = config.expand_path(config.get("paths", "models_dir", "~/.meetcap/models"))

    # check faster-whisper
    if verify_whisper_model(stt_model_name, models_dir):
        checks.append(("faster-whisper", f"✅ {stt_model_name} ready", "green"))
    else:
        checks.append(("faster-whisper", f"❌ {stt_model_name} not found", "red"))

    # check mlx-whisper (only on Apple Silicon)
    import platform

    if platform.processor() == "arm":
        if verify_mlx_whisper_model(mlx_model_name, models_dir):
            checks.append(("mlx-whisper", f"✅ {mlx_model_name.split('/')[-1]} ready", "green"))
        else:
            checks.append(("mlx-whisper", f"❌ {mlx_model_name.split('/')[-1]} not found", "red"))
    else:
        checks.append(("mlx-whisper", "⚠️ requires Apple Silicon", "yellow"))

    # check qwen llm model (no download)
    if verify_qwen_model(models_dir):
        checks.append(("llm model", "✅ Qwen3-4B ready", "green"))
    else:
        checks.append(("llm model", "❌ Qwen3-4B not found", "red"))

    # check output directory
    out_dir = config.expand_path(config.get("paths", "out_dir"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        checks.append(("output dir", "✅ writable", "green"))
    except Exception as e:
        checks.append(("output dir", f"❌ error: {e}", "red"))

    # display results
    table = Table(show_header=True, header_style="bold")
    table.add_column("component", style="cyan")
    table.add_column("status")

    all_good = True
    for component, status, color in checks:
        table.add_row(component, f"[{color}]{status}[/{color}]")
        if color == "red":
            all_good = False

    console.print(table)

    if not all_good:
        console.print("\n[yellow]⚠ some components are missing or need attention[/yellow]")
        console.print("run 'meetcap setup' to install models and configure permissions")
    else:
        console.print("\n[green]✅ all checks passed![/green]")
        console.print("ready to record with: meetcap record")


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="show version",
    ),
) -> None:
    """meetcap - offline meeting recorder & summarizer for macos"""
    if version:
        console.print(f"meetcap v{__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        ErrorHandler.handle_general_error(e)
