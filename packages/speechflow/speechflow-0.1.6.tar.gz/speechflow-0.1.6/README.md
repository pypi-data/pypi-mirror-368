# SpeechFlow

A unified Python TTS (Text-to-Speech) library that provides a simple interface for multiple TTS engines.

## Features

- **Multiple TTS Engine Support**:
  - OpenAI TTS
  - Google Gemini TTS
  - FishAudio TTS (Cloud-based, multi-voice)
  - Kokoro TTS (Multi-language, lightweight, local)
  - Style-Bert-VITS2 (Local, high-quality Japanese TTS)

- **Unified Interface**: Switch between different TTS engines without changing your code
- **Streaming Support**: Real-time audio streaming for supported engines
- **Decoupled Architecture**: Use TTS engines, audio players, and file writers independently
- **Audio Playback**: Synchronous audio player with streaming support
- **File Export**: Save synthesized speech to various audio formats

## Installation

```bash
pip install speechflow
# or
uv add speechflow
```

### GPU Support for PyTorch

SpeechFlow includes PyTorch as a dependency for some TTS engines (Kokoro, Style-Bert-VITS2). By default, pip/uv will install CPU-only PyTorch. 

**For GPU acceleration, install PyTorch BEFORE installing speechflow:**

**Option 1: Using pip**
```bash
# First install PyTorch with CUDA (example for CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Then install speechflow
pip install speechflow
```

**Option 2: Using uv**
```bash
# First add PyTorch with CUDA support
uv add torch torchvision torchaudio --index https://download.pytorch.org/whl/cu121

# Then add speechflow
uv add speechflow
```

**Note:** 
- Replace `cu121` with your CUDA version (e.g., `cu118` for CUDA 11.8, `cu124` for CUDA 12.4)
- If you've already installed speechflow with CPU PyTorch, you'll need to reinstall PyTorch:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --upgrade --force-reinstall
  ```

## Quick Start

### Basic Usage (Decoupled Components)
```python
from speechflow import OpenAITTSEngine, AudioPlayer, AudioWriter

# Initialize components
engine = OpenAITTSEngine(api_key="your-api-key")
player = AudioPlayer()
writer = AudioWriter()

# Generate audio
audio = engine.get("Hello, world!")

# Play audio
player.play(audio)

# Save to file
writer.save(audio, "output.wav")
```

### Streaming Audio

**Important Notes on Streaming Behavior:**
- **OpenAI**: True streaming with multiple chunks. First call may have 10-20s cold start delay. Uses PCM format for simplicity.
- **Gemini**: Returns complete audio in a single chunk (as of January 2025). This is a known limitation, not true streaming.

```python
from speechflow import OpenAITTSEngine, AudioPlayer, AudioWriter

# Initialize components
engine = OpenAITTSEngine(api_key="your-api-key")
player = AudioPlayer()
writer = AudioWriter()

# Warmup for OpenAI (recommended for production)
_ = list(engine.stream("Warmup"))

# Stream and play audio (returns combined AudioData)
combined_audio = player.play_stream(engine.stream("This is a long text that will be streamed..."))

# Save the combined audio to file
writer.save(combined_audio, "output.wav")
```

## Engine-Specific Features

### OpenAI TTS
```python
from speechflow import OpenAITTSEngine

engine = OpenAITTSEngine(api_key="your-api-key")
audio = engine.get(
    "Hello",
    voice="alloy",  # or: ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer
    model="gpt-4o-mini-tts",   # or: tts-1, tts-1-hd
    speed=1.0
)

# Streaming
for chunk in engine.stream("Long text..."):
    # Process audio chunks in real-time
    pass
```

### Google Gemini TTS
```python
from speechflow import GeminiTTSEngine

engine = GeminiTTSEngine(api_key="your-api-key")
audio = engine.get(
    "Hello",
    model="gemini-2.5-flash-preview-tts",  # or: gemini-2.5-pro-preview-tts
    voice="Leda",  # or: Puck, Charon, Kore, Fenrir, Aoede, and many more
    speed=1.0
)
```

### FishAudio TTS
```python
from speechflow import FishAudioTTSEngine

engine = FishAudioTTSEngine(api_key="your-api-key")
audio = engine.get(
    "Hello world",
    model="s1",  # or: s1-mini, speech-1.6, speech-1.5, agent-x0
    voice="your-voice-id"  # Use your FishAudio voice ID
)

# Streaming
for chunk in engine.stream("Streaming text..."):
    # Process audio chunks
    pass
```

### Kokoro TTS
```python
from speechflow import KokoroTTSEngine

# Default: American English
engine = KokoroTTSEngine()
audio = engine.get(
    "Hello world",
    voice="af_heart"  # Multiple voices available
)

# Japanese (requires additional setup)
engine = KokoroTTSEngine(lang_code="j")
audio = engine.get(
    "こんにちは、世界",
    voice="af_heart"
)
```

**Note for Japanese support:**
The Japanese dictionary will be automatically downloaded on first use.
If you encounter errors, you can manually download it:
```bash
python -m unidic download
```

### Style-Bert-VITS2
```python
from speechflow import StyleBertTTSEngine

# Use pre-trained model (automatically downloads on first use)
engine = StyleBertTTSEngine(model_name="jvnv-F1-jp")  # Female Japanese voice
audio = engine.get(
    "こんにちは、世界",
    style="Happy",       # Emotion: Neutral, Happy, Sad, Angry, Fear, Surprise, Disgust
    style_weight=5.0,    # Emotion strength (0.0-10.0)
    speed=1.0,          # Speech speed
    pitch=0.0           # Pitch shift in semitones
)

# Available pre-trained models:
# - jvnv-F1-jp, jvnv-F2-jp: Female voices (JP-Extra version)
# - jvnv-M1-jp, jvnv-M2-jp: Male voices (JP-Extra version)  
# - jvnv-F1, jvnv-F2, jvnv-M1, jvnv-M2: Legacy versions

# Use custom model
engine = StyleBertTTSEngine(model_path="/path/to/your/model")

# Sentence-by-sentence streaming (not true streaming)
for audio_chunk in engine.stream("長い文章を文ごとに生成します。"):
    # Process each sentence's audio
    pass
```

**Note:** Style-Bert-VITS2 is optimized for Japanese text and requires GPU for best performance.

## Language Support

### Kokoro Languages
- 🇺🇸 American English (`a`)
- 🇬🇧 British English (`b`)
- 🇪🇸 Spanish (`e`)
- 🇫🇷 French (`f`)
- 🇮🇳 Hindi (`h`)
- 🇮🇹 Italian (`i`)
- 🇯🇵 Japanese (`j`) - requires unidic
- 🇧🇷 Brazilian Portuguese (`p`)
- 🇨🇳 Mandarin Chinese (`z`)

## License

MIT