# meetcap Project Guide

## Overview
meetcap is an offline meeting recorder & summarizer for macOS that captures system audio and microphone simultaneously, transcribes locally with Whisper, and summarizes with a local LLM.

## Project Structure
```
meetcap/
├── meetcap/
│   ├── core/           # Core functionality
│   │   ├── devices.py  # Audio device discovery
│   │   ├── recorder.py # Audio recording via ffmpeg
│   │   └── hotkeys.py  # Global hotkey management
│   ├── services/       # Processing services
│   │   ├── transcription.py  # STT with Whisper
│   │   └── summarization.py  # LLM summarization
│   ├── utils/          # Utilities
│   │   ├── config.py   # Configuration management
│   │   └── logger.py   # Logging and error handling
│   └── cli.py          # CLI interface
├── tests/              # Test files
├── pyproject.toml      # Project configuration
└── README.md          # User documentation
```

## Key Design Decisions

### Audio Capture
- Uses ffmpeg with AVFoundation for macOS audio capture
- Prefers Aggregate Device (BlackHole + Mic) for perfect sync
- Fallback to dual-input with amix filter if needed
- 48kHz stereo WAV output

### Offline Operation
- All models run locally (no network calls)
- Uses local_files_only=True for model loading
- No telemetry or external dependencies

### Transcription
- Primary (Apple Silicon): mlx-whisper with MLX acceleration
- Fallback: faster-whisper with Metal acceleration
- Alternative: whisper.cpp CLI
- Outputs both plain text and JSON with timestamps
- Automatic fallback from mlx-whisper to faster-whisper on errors

### Summarization
- Qwen3-4B-Thinking model via llama-cpp-python
- Metal GPU acceleration on Apple Silicon
- Structured markdown output with sections
- Automatic removal of <think> tags from thinking models

## Commands

### Development
```bash
# Create/update environment
hatch env create

# Run CLI commands
hatch run meetcap record                    # Record from audio device
hatch run meetcap record --stt mlx          # Record with mlx-whisper (Apple Silicon)
hatch run meetcap summarize                 # Process existing audio file
hatch run meetcap summarize --stt mlx       # Process with mlx-whisper
hatch run meetcap devices                   # List audio devices
hatch run meetcap verify                    # Quick verification
hatch run meetcap setup                     # Interactive setup wizard

# Run tests
hatch run test

# Format code
hatch run fmt

# Lint code
hatch run lint
```

### Testing Audio Recording
```bash
# Test device listing
hatch run meetcap devices

# Test 10-second recording
hatch run python -c "
from meetcap.core.recorder import AudioRecorder
from meetcap.core.devices import list_audio_devices, select_best_device
import time

devices = list_audio_devices()
device = select_best_device(devices)
if device:
    recorder = AudioRecorder()
    recorder.start_recording(device.index, device.name)
    time.sleep(10)
    recorder.stop_recording()
"
```

## Configuration

Default config location: `~/.meetcap/config.toml`

Key settings:
- `audio.preferred_device`: Default audio device name
- `models.stt_engine`: STT engine (faster-whisper or mlx-whisper)
- `models.stt_model_path`: Path to Whisper model (faster-whisper)
- `models.mlx_stt_model_name`: MLX Whisper model name
- `models.llm_gguf_path`: Path to Qwen GGUF model
- `paths.out_dir`: Output directory for recordings
- `hotkey.stop`: Hotkey combination to stop recording

Environment variable overrides:
- `MEETCAP_DEVICE`
- `MEETCAP_STT_ENGINE`: STT engine to use
- `MEETCAP_STT_MODEL`: Faster-whisper model path
- `MEETCAP_MLX_STT_MODEL`: MLX-whisper model name
- `MEETCAP_LLM_MODEL`
- `MEETCAP_OUT_DIR`

## macOS Permissions Required

1. **Microphone Access**: System Preferences → Privacy & Security → Microphone
2. **Input Monitoring**: System Preferences → Privacy & Security → Input Monitoring (for hotkeys)

## Audio Setup Guide

1. Install BlackHole 2ch
2. Create Multi-Output Device (for monitoring):
   - Built-in Output + BlackHole
3. Create Aggregate Input (for recording):
   - BlackHole + Microphone
   - Set mic as clock source
   - Enable drift correction

## Model Setup (Automatic)

Models are selected and downloaded during `meetcap setup`:

### Whisper Models (Speech-to-Text)

**MLX-Whisper Models (Apple Silicon recommended):**
1. **mlx-community/whisper-large-v3-turbo** (default on Apple Silicon, ~1.5GB) - Fast and accurate
2. **mlx-community/whisper-large-v3-mlx** (~1.5GB) - Most accurate MLX version
3. **mlx-community/whisper-small-mlx** (~466MB) - Smallest, fastest

**Faster-Whisper Models (universal compatibility):**
1. **large-v3** (default on non-Apple Silicon, ~1.5GB) - Most accurate, slower
2. **large-v3-turbo** (~1.5GB) - Faster than v3, slightly less accurate
3. **small** (~466MB) - Fast, good for quick transcripts

### LLM Models (Summarization)
1. **Qwen3-4B-Thinking** (default, ~4-5GB) - Best for meeting summaries, removes thinking tags
2. **Qwen3-4B-Instruct** (~4-5GB) - General purpose, follows instructions
3. **GPT-OSS-20B** (~11GB) - Larger model, more capable

All models stored in: `~/.meetcap/models/`
Can override with environment variables:
- `MEETCAP_STT_ENGINE` - Choose stt engine (faster-whisper or mlx-whisper)
- `MEETCAP_STT_MODEL` - Faster-whisper model name
- `MEETCAP_MLX_STT_MODEL` - MLX-whisper model name
- `MEETCAP_LLM_MODEL` - Path to GGUF file

## Troubleshooting

### No audio devices found
- Check ffmpeg installation: `brew install ffmpeg`
- Verify microphone permissions
- Run `meetcap verify` for diagnostics

### Permission errors
- Grant Input Monitoring permission for hotkeys
- Grant Microphone permission for recording

### Model loading issues
- Verify model paths in config
- Ensure sufficient RAM/VRAM
- Check model format (GGUF for LLM)

## Code Style
- Black formatting (100 char line length)
- Type hints throughout
- Lowercase comments
- Rich console output for UX

## Commit Message Style
Follow conventional commit format with semantic prefixes:

```
feat: add new feature (new functionality)
fix: bug fixes
chore: maintenance tasks, deps, tooling
docs: documentation changes
refactor: code restructuring without behavior change
test: add or update tests
```

Structure: `type: brief description`

Multi-line format:
```
feat: add mlx-whisper support for Apple Silicon optimization

- Add MlxWhisperService for faster transcription
- Update model download system to support mlx-whisper
- Fix CLI to respect configured STT engine
- Add comprehensive tests and documentation
- Maintain backward compatibility with fallback
```

**Important**: Do not mention Claude or AI assistance in commit messages.

## Important Implementation Notes
- Subprocess management for ffmpeg is critical
- Graceful shutdown with 'q' to ffmpeg stdin
- Hotkey debouncing to prevent double triggers
- Model lazy loading to reduce startup time
- Chunking for long transcripts in LLM
