class TTSError(Exception):
    """Base exception for TalkFlow TTS library."""
    pass


class EngineNotFoundError(TTSError):
    """Raised when requested TTS engine is not found or not supported."""
    pass


class AudioProcessingError(TTSError):
    """Raised when audio processing fails."""
    pass


class ConfigurationError(TTSError):
    """Raised when configuration is invalid."""
    pass


class StreamingError(TTSError):
    """Raised when streaming audio fails."""
    pass