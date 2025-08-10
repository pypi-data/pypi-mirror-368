from typing import Iterator, Literal, cast

import numpy as np
from fish_audio_sdk import ReferenceAudio, Session, TTSRequest

from ..core.base import AudioData, TTSEngineBase
from ..core.exceptions import ConfigurationError, StreamingError, TTSError


class FishAudioTTSEngine(TTSEngineBase):
    """FishAudio TTS engine implementation."""

    SUPPORTED_MODELS = [
        "s1",
        "s1-mini",
        "speech-1.6",
        "speech-1.5",
        "agent-x0",
    ]

    def __init__(self, api_key: str):
        """Initialize FishAudio TTS engine.

        Args:
            api_key: FishAudio API key

        Raises:
            ConfigurationError: If api_key is not provided
        """
        super().__init__()

        if not api_key:
            raise ConfigurationError("FishAudio API key is required")

        # Create client with API key
        self.session = Session(apikey=api_key)
        self.sample_rate = 24000  # Default sample rate (FishAudio works better with 24kHz)
        
        # For chunk boundary handling
        self._carry_over_byte = None

    def get(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Synthesize speech from text using FishAudio TTS.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        # Reset carry-over byte for new synthesis
        self._carry_over_byte = None
        
        response_iterator = self.stream(text, model=model, voice=voice)
        audio_chunks = []
        sample_rate = None
        channels = None
        
        for audio_data in response_iterator:
            audio_chunks.append(audio_data.data)
            # Get audio properties from first chunk
            if sample_rate is None:
                sample_rate = audio_data.sample_rate
                channels = audio_data.channels

        if not audio_chunks:
            raise TTSError("No audio data received from FishAudio")

        # Concatenate all float32 audio chunks
        combined_audio = np.concatenate(audio_chunks)

        return AudioData(
            data=combined_audio,
            sample_rate=sample_rate,
            channels=channels,
            format="pcm",
        )

    async def aget(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Asynchronously synthesize speech from text using FishAudio TTS.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        raise NotImplementedError("Asynchronous synthesis is not implemented for FishAudioTTSEngine")

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
        # Reset carry-over byte for new stream
        self._carry_over_byte = None

        # Normalize model name to lowercase and validate
        if model is not None:
            model = model.lower()
        
        if model is None or model not in self.SUPPORTED_MODELS:
            model = self.SUPPORTED_MODELS[0]

        try:
            response_iterator = self.session.tts(
                backend=cast(Literal["speech-1.5", "speech-1.6", "agent-x0", "s1", "s1-mini"], model),
                request=TTSRequest(
                    text=text,
                    reference_id=voice,
                    format="pcm",
                    sample_rate=self.sample_rate,
                ),
            )

            # Iterate through all responses
            for response in response_iterator:
                if response is None:
                    continue

                audio_data = self._extract_audio(response)
                if audio_data:
                    yield audio_data

        except RuntimeError as e:
            if "Generator did not stop" in str(e):
                # This error can occur at the end of the stream, which is normal
                pass
            else:
                raise StreamingError(f"FishAudio streaming error: {str(e)}")
        except Exception as e:
            raise TTSError(f"FishAudio TTS error: {str(e)}")
        finally:
            # Reset carry-over byte at the end of stream
            self._carry_over_byte = None

    def _extract_audio(self, response: bytes) -> AudioData | None:
        """Extract AudioData from FishAudio response with proper boundary handling.

        Args:
            response: bytes response from the TTS service

        Returns:
            AudioData if audio content is found, None otherwise
        """
        audio_bytes = response

        # Skip empty responses
        if not audio_bytes:
            return None

        # Prepend carry-over byte from previous chunk if exists
        if self._carry_over_byte is not None:
            audio_bytes = self._carry_over_byte + audio_bytes
            self._carry_over_byte = None

        # Check if we need to carry over the last byte for next chunk
        if len(audio_bytes) % 2 == 1:
            self._carry_over_byte = audio_bytes[-1:]
            audio_bytes = audio_bytes[:-1]

        # Skip if no valid data remains
        if len(audio_bytes) == 0:
            return None

        # Always decode as little-endian int16 (standard PCM format)
        audio_data = np.frombuffer(audio_bytes, dtype="<i2")
        
        if audio_data.size == 0:
            return None

        # Normalize to float32 [-1, 1]
        audio_data = audio_data.astype(np.float32) / 32767.0

        # Get audio properties
        sample_rate = self.sample_rate
        channels = 1  # Default to mono

        return AudioData(data=audio_data, sample_rate=sample_rate, channels=channels, format="pcm")
