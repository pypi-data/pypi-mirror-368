from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Iterator

import numpy as np


@dataclass
class AudioData:
    """Container for audio data and metadata."""

    data: np.ndarray
    sample_rate: int
    channels: int = 1
    format: str = "pcm"

    @property
    def duration(self) -> float:
        """Get audio duration in seconds."""
        return len(self.data) / self.sample_rate


class TTSEngineBase(ABC):
    """Abstract base class for TTS engines."""

    def __init__(self):
        """Initialize TTS engine."""
        pass

    @abstractmethod
    def get(self, text: str, model: str | None = None, voice: str | None = None) -> AudioData:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        pass

    async def aget(self, text: str, model: str | None = None, voice: str | None = None) -> AudioData:
        """Asynchronously synthesize speech from text.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        pass

    @abstractmethod
    def stream(self, text: str, model: str | None = None, voice: str | None = None) -> Iterator[AudioData]:
        """Stream synthesized speech in chunks.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Yields:
            AudioData chunks
        """
        pass
