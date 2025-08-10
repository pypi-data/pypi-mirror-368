from .audio import AudioPlayer, AudioWriter
from .core import AudioData, AudioProcessingError, EngineNotFoundError, TTSEngineBase, TTSError
from .engines import FishAudioTTSEngine, GeminiTTSEngine, KokoroTTSEngine, OpenAITTSEngine, StyleBertTTSEngine

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

__all__ = [
    # Core
    "TTSEngineBase",
    "AudioData",
    # Exceptions
    "TTSError",
    "EngineNotFoundError",
    "AudioProcessingError",
    # Audio components
    "AudioPlayer",
    "AudioWriter",
    # Engines
    "FishAudioTTSEngine",
    "GeminiTTSEngine",
    "KokoroTTSEngine",
    "OpenAITTSEngine",
    "StyleBertTTSEngine",
]
