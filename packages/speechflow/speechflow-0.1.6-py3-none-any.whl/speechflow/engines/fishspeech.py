from typing import Iterator

from ..core.base import AudioData, TTSEngineBase


class FishSpeechTTSEngine(TTSEngineBase):
    """FishSpeech TTS engine implementation."""

    def __init__(self, model_path: str):
        """Initialize FishSpeech TTS engine.

        Args:
            model_name: Name of the FishSpeech model to use

        Raises:
            ConfigurationError: If model_name is not supported
        """
        super().__init__()
        raise NotImplementedError("FishSpeech TTS engine is not yet implemented")

    def get(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Synthesize speech from text using FishSpeech TTS.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        raise NotImplementedError("FishSpeech TTS engine is not yet implemented")

    async def aget(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Asynchronously synthesize speech from text.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        raise NotImplementedError("FishSpeech TTS engine is not yet implemented")

    def stream(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> Iterator[AudioData]:
        """Stream synthesized speech in chunks.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name
        Yields:
            AudioData chunks
        """
        raise NotImplementedError("FishSpeech TTS engine is not yet implemented")
