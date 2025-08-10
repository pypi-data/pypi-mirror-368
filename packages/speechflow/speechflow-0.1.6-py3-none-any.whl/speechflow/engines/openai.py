from typing import Any, Iterator

import numpy as np
from openai import OpenAI

from ..core.base import AudioData, TTSEngineBase
from ..core.exceptions import ConfigurationError, TTSError


class OpenAITTSEngine(TTSEngineBase):
    """OpenAI TTS engine implementation."""

    SUPPORTED_MODELS = [
        "gpt-4o-mini-tts",
        "tts-1",
        "tts-1-hd",
    ]
    SUPPORTED_VOICES = ["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]

    def __init__(self, api_key: str):
        """Initialize OpenAI TTS engine.

        Args:
            api_key: OpenAI API key

        Raises:
            ConfigurationError: If api_key is not provided
        """
        super().__init__()

        if not api_key:
            raise ConfigurationError("OpenAI API key is required")

        self.client = OpenAI(api_key=api_key)

    def get(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> AudioData:
        """Synthesize speech from text using OpenAI TTS.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name
            speed: Speech speed (0.25 to 4.0)

        Returns:
            AudioData containing the synthesized speech
        """
        if model is None:
            model = self.SUPPORTED_MODELS[0]

        if voice is None:
            voice = self.SUPPORTED_VOICES[0]

        try:
            response = self.client.audio.speech.create(
                model=model, voice=voice, input=text, speed=speed, response_format="pcm"
            )

            # Read PCM data from response
            audio_bytes = response.read()
            return self._extract_audio(audio_bytes)

        except Exception as e:
            raise TTSError(f"OpenAI TTS synthesis failed: {str(e)}")

    def stream(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> Iterator[AudioData]:
        """Stream synthesized speech in chunks.

        Note: The first API call may experience a cold start delay (10-20 seconds).
        For production use, consider implementing a warm-up call during initialization
        to ensure low latency for subsequent requests. PCM format may have higher
        latency compared to WAV format.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name
            speed: Speech speed (0.25 to 4.0)

        Yields:
            AudioData chunks
        """
        if model is None:
            model = self.SUPPORTED_MODELS[0]

        if voice is None:
            voice = self.SUPPORTED_VOICES[0]

        try:
            # Use PCM format for streaming - no header parsing needed
            with self.client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="pcm",  # Raw PCM format
            ) as response:
                # Stream raw PCM chunks
                pcm_buffer = bytearray()

                for chunk in response.iter_bytes(chunk_size=4096):  # 4KB chunks
                    if chunk:
                        pcm_buffer.extend(chunk)

                        # Yield chunks when buffer is large enough
                        if len(pcm_buffer) >= 16384:  # 16KB buffer for smooth playback
                            # Ensure even number of bytes for int16
                            bytes_to_process = (len(pcm_buffer) // 2) * 2
                            pcm_data = pcm_buffer[:bytes_to_process]
                            pcm_buffer = pcm_buffer[bytes_to_process:]

                            yield self._extract_audio(pcm_data)

                # Process any remaining data in buffer
                if len(pcm_buffer) > 0:
                    # Ensure even number of bytes for int16
                    bytes_to_process = (len(pcm_buffer) // 2) * 2
                    if bytes_to_process > 0:
                        pcm_data = pcm_buffer[:bytes_to_process]
                        yield self._extract_audio(pcm_data)

        except Exception as e:
            raise TTSError(f"OpenAI TTS streaming failed: {str(e)}")

    def _extract_audio(self, audio_bytes: bytes) -> AudioData:
        """Extract AudioData from raw PCM bytes.

        Args:
            audio_bytes: Raw PCM audio data

        Returns:
            AudioData containing the extracted audio
        """
        # Convert raw PCM bytes to numpy array
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
        # Normalize to float32 [-1, 1]
        audio_data = audio_data.astype(np.float32) / 32767.0

        # PCM format from OpenAI is 24kHz mono
        return AudioData(data=audio_data, sample_rate=24000, channels=1, format="pcm")
