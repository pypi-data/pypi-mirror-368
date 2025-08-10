import io
import wave
from typing import Any, Iterator

import numpy as np
from google import genai
from google.genai import types

from ..core.base import AudioData, TTSEngineBase
from ..core.exceptions import ConfigurationError, StreamingError, TTSError


class GeminiTTSEngine(TTSEngineBase):
    """Google Gemini TTS engine implementation."""

    SUPPORTED_MODELS = [
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts",
    ]
    SUPPORTED_VOICES = [
        "Zephyr",  # Bright
        "Puck",  # Upbeat
        "Charon",  # Informative
        "Kore",  # Firm
        "Fenrir",  # Excitable
        "Leda",  # Youthful
        "Orus",  # Firm
        "Aoede",  # Breezy
        "Callirrhoe",  # Easy-going
        "Autonoe",  # Bright
        "Enceladus",  # Breathy
        "Iapetus",  # Clear
        "Umbriel",  # Easy-going
        "Algieba",  # Smooth
        "Despina",  # Smooth
        "Erinome",  # Clear
        "Algenib",  # Gravelly
        "Rasalgethi",  # Informative
        "Laomedeia",  # Upbeat
        "Achernar",  # Soft
        "Alnilam",  # Firm
        "Schedar",  # Even
        "Gacrux",  # Mature
        "Pulcherrima",  # Forward
        "Achird",  # Friendly
        "Zubenelgenubi",  # Casual
        "Vindemiatrix",  # Gentle
        "Sadachbia",  # Lively
        "Sadaltager",  # Knowledgeable
        "Sulafat",  # Warm
    ]

    def __init__(self, api_key: str):
        """Initialize Gemini TTS engine.

        Args:
            api_key: Gemini API key

        Raises:
            ConfigurationError: If api_key is not provided
        """
        super().__init__()

        if not api_key:
            raise ConfigurationError("Gemini API key is required")

        # Create client with API key
        self.client = genai.Client(api_key=api_key)

    def get(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Synthesize speech from text using Gemini TTS.

        Args:
            text: Text to synthesize
            **kwargs: Additional parameters (voice)

        Returns:
            AudioData containing the synthesized speech
        """

        if model is None:
            model = self.SUPPORTED_MODELS[0]

        if voice is None:
            voice = self.SUPPORTED_VOICES[0]

        try:
            # Generate audio content
            response = self.client.models.generate_content(
                model=model,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                ),
            )

            audio_data = self._extract_audio(response)
            if audio_data is None:
                raise TTSError("Failed to extract audio from response")
            return audio_data

        except Exception as e:
            raise TTSError(f"Gemini TTS synthesis failed: {str(e)}")

    async def aget(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Asynchronously synthesize speech from text using Gemini TTS.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name
            speed: Speed factor (default: 1.0)

        Returns:
            AudioData containing the synthesized speech
        """
        if model is None:
            model = self.SUPPORTED_MODELS[0]

        if voice is None:
            voice = self.SUPPORTED_VOICES[0]

        try:
            # Generate audio content
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                ),
            )

            audio_data = self._extract_audio(response)
            if audio_data is None:
                raise TTSError("Failed to extract audio from response")
            return audio_data

        except Exception as e:
            raise TTSError(f"Gemini TTS synthesis failed: {str(e)}")

    def stream(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> Iterator[AudioData]:
        """Stream synthesized speech in chunks.

        Note: As of 2025, Gemini TTS returns the complete audio in a single chunk
        rather than streaming multiple smaller chunks. This is a known limitation
        documented in the Google AI Developers Forum. The method still uses the
        streaming API for consistency, but expect only one chunk to be yielded.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Yields:
            AudioData chunks (currently only yields one chunk with complete audio)
        """

        if model is None:
            model = self.SUPPORTED_MODELS[0]

        if voice is None:
            voice = self.SUPPORTED_VOICES[0]

        response_iterator = self.client.models.generate_content_stream(
            model=model,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            ),
        )

        for response in response_iterator:
            audio_data = self._extract_audio(response)
            if audio_data:
                yield audio_data

    def _extract_audio(self, response) -> AudioData | None:
        """Extract AudioData from a GenerateContentResponse.

        Args:
            response: GenerateContentResponse from Gemini API

        Returns:
            AudioData if audio content is found, None otherwise
        """
        # Check if response has candidates
        if not response.candidates:
            return None

        # Check if candidate has content
        if not response.candidates[0].content:
            return None

        # Check if content has parts
        if not hasattr(response.candidates[0].content, "parts") or not response.candidates[0].content.parts:
            return None

        # Find audio part
        audio_part = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data is not None:
                if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                    if part.inline_data.mime_type.startswith("audio/"):
                        audio_part = part
                        break

        if not audio_part:
            return None

        # Extract audio data
        if audio_part.inline_data is not None:
            audio_bytes = audio_part.inline_data.data
            mime_type = audio_part.inline_data.mime_type

            # Parse audio format from MIME type (e.g., "audio/L16;codec=pcm;rate=24000")
            sample_rate = 24000  # Default
            channels = 1  # Default to mono

            if isinstance(mime_type, str) and audio_bytes:
                if "rate=" in mime_type:
                    rate_str = mime_type.split("rate=")[1].split(";")[0]
                    sample_rate = int(rate_str)

                # For L16 (16-bit linear PCM), convert directly to numpy array
                if "L16" in mime_type or "pcm" in mime_type:
                    # Convert raw PCM bytes to numpy array
                    audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                    # Normalize to float32 [-1, 1]
                    audio_data = audio_data.astype(np.float32) / 32767.0
                else:
                    # For other formats, try to decode as WAV
                    import base64

                    if isinstance(audio_bytes, str):
                        audio_bytes = base64.b64decode(audio_bytes)

                    with io.BytesIO(audio_bytes) as wav_buffer:
                        with wave.open(wav_buffer, "rb") as wav_file:
                            sample_rate = wav_file.getframerate()
                            channels = wav_file.getnchannels()
                            frames = wav_file.readframes(wav_file.getnframes())

                            audio_data = np.frombuffer(frames, dtype=np.int16)
                            audio_data = audio_data.astype(np.float32) / 32767.0

                return AudioData(data=audio_data, sample_rate=sample_rate, channels=channels, format="pcm")

        return None
