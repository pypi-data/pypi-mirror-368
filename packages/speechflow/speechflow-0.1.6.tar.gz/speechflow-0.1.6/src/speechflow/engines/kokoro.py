import os
from typing import Iterator

import numpy as np
import torch
from kokoro import KPipeline

from ..core.base import AudioData, TTSEngineBase
from ..core.exceptions import ConfigurationError, TTSError


class KokoroTTSEngine(TTSEngineBase):
    """Kokoro TTS engine implementation."""

    SUPPORTED_LANGUAGES = {
        "a": "American English",
        "b": "British English",
        "e": "Spanish",
        "f": "French",
        "h": "Hindi",
        "i": "Italian",
        "j": "Japanese",
        "p": "Brazilian Portuguese",
        "z": "Mandarin Chinese",
    }

    # Common voices across languages
    SUPPORTED_VOICES = [
        "af_heart",
        "af_bella",
        "af_sarah",
        "af_sky",
        "af_nicole",
        "af_star",
        "am_michael",
        "am_adam",
        "bf_emma",
        "bm_george",
    ]

    def __init__(self, lang_code: str = "a", device: str = "cuda"):
        """Initialize Kokoro TTS engine.

        Args:
            lang_code: Language code (default: 'a' for American English)

        Raises:
            ConfigurationError: If lang_code is not supported
        """
        super().__init__()

        if lang_code not in self.SUPPORTED_LANGUAGES:
            raise ConfigurationError(
                f"Unsupported language code: {lang_code}. Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}"
            )

        self.lang_code = lang_code

        # For Japanese, ensure unidic dictionary is available
        if self.lang_code == "j":
            self._setup_japanese_dictionary()

        try:
            # Initialize Kokoro pipeline
            self.pipeline = KPipeline(lang_code=self.lang_code, repo_id="hexgrad/Kokoro-82M", device=device)
        except Exception as e:
            error_msg = str(e)

            # Provide helpful error messages for common issues
            if "MeCab" in error_msg and self.lang_code == "j":
                raise ConfigurationError(
                    "Failed to initialize Japanese language support. "
                    "Please install MeCab and unidic dictionary:\n"
                    "1. pip install unidic-lite\n"
                    "2. Or download unidic manually: python -m unidic download\n\n"
                    f"Original error: {error_msg}"
                )
            elif "espeak" in error_msg.lower():
                raise ConfigurationError(
                    f"Failed to initialize Kokoro for language '{self.lang_code}'. "
                    "Some languages require espeak-ng to be installed.\n\n"
                    f"Original error: {error_msg}"
                )
            else:
                raise ConfigurationError(f"Failed to initialize Kokoro pipeline: {error_msg}")

    def get(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> AudioData:
        """Synthesize speech from text using Kokoro TTS.

        Args:
            text: Text to synthesize
            model: Not used (for API compatibility)
            voice: Voice to use (default: 'af_heart')
            speed: Speech speed (default: 1.0)

        Returns:
            AudioData containing the synthesized speech
        """
        if voice is None:
            voice = self.SUPPORTED_VOICES[0]  # Default to 'af_heart'

        if voice not in self.SUPPORTED_VOICES:
            raise ConfigurationError(f"Unsupported voice: {voice}. Supported: {', '.join(self.SUPPORTED_VOICES)}")

        try:
            # Generate speech
            generator = self.pipeline(
                text,
                voice=voice,
                speed=speed,
                split_pattern=r"\n+",  # Split on newlines for better handling of long text
            )

            # Kokoro returns a generator, we need to collect all audio chunks
            audio_chunks = []

            for chunk_data in generator:
                audio_data = self._extract_audio(chunk_data)
                if audio_data:
                    audio_chunks.append(audio_data.data)

            # Concatenate all audio chunks
            if audio_chunks:
                combined_audio = np.concatenate(audio_chunks)
                return AudioData(
                    data=combined_audio,
                    sample_rate=24000,  # Kokoro uses 24kHz sample rate
                    channels=1,  # Mono audio
                    format="pcm",
                )
            else:
                raise TTSError("No audio data generated")

        except Exception as e:
            raise TTSError(f"Kokoro TTS synthesis failed: {str(e)}")

    def stream(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> Iterator[AudioData]:
        """Stream synthesized speech in chunks.

        Note: Kokoro generates audio in sentence/phrase chunks based on the
        split_pattern. Each chunk is yielded as it's generated.

        Args:
            text: Text to synthesize
            model: Not used (for API compatibility)
            voice: Voice to use (default: 'af_heart')
            speed: Speech speed (default: 1.0)

        Yields:
            AudioData chunks
        """
        if voice is None:
            voice = self.SUPPORTED_VOICES[0]  # Default to 'af_heart'

        if voice not in self.SUPPORTED_VOICES:
            raise ConfigurationError(f"Unsupported voice: {voice}. Supported: {', '.join(self.SUPPORTED_VOICES)}")

        try:
            # Generate speech with streaming
            generator = self.pipeline(
                text,
                voice=voice,
                speed=speed,
                split_pattern=r"\n+",  # Split on newlines for better handling
            )

            # Stream each chunk as it's generated
            for chunk_data in generator:
                audio_data = self._extract_audio(chunk_data)
                if audio_data:
                    yield audio_data

        except Exception as e:
            raise TTSError(f"Kokoro TTS streaming failed: {str(e)}")

    def _extract_audio(self, chunk_data: KPipeline.Result) -> AudioData | None:
        """Extract AudioData from Kokoro generator output.

        Args:
            chunk_data: Result object or tuple of (graphemes, phonemes, audio) from Kokoro

        Returns:
            AudioData if audio content is found, None otherwise
        """
        # Handle Result object (newer Kokoro API)
        if hasattr(chunk_data, "audio"):
            audio = chunk_data.audio
        # Handle tuple format (legacy or different API)
        elif isinstance(chunk_data, (tuple, list)) and len(chunk_data) == 3:
            graphemes, phonemes, audio = chunk_data
        else:
            # Invalid input format
            if not chunk_data:
                return None
            return None

        # Skip if no audio
        if audio is None:
            return None

        # Convert torch tensor to numpy if needed
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()

        # Ensure it's a numpy array
        if not isinstance(audio, np.ndarray):
            return None

        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Ensure audio is in the correct range [-1, 1]
        max_val = np.abs(audio).max()
        if max_val > 1.0:
            audio = audio / max_val

        return AudioData(
            data=audio,
            sample_rate=24000,  # Kokoro uses 24kHz sample rate
            channels=1,  # Mono audio
            format="pcm",
        )

    def _setup_japanese_dictionary(self):
        """Set up Japanese dictionary for MeCab.

        Automatically downloads unidic dictionary if not present.
        """
        try:
            # Check if unidic is already available
            import pathlib

            import unidic

            dicdir = pathlib.Path(unidic.DICDIR)
            mecabrc = dicdir / "mecabrc"

            if mecabrc.exists():
                # Dictionary already exists
                return

            # Dictionary doesn't exist, download it
            print("Japanese dictionary not found. Downloading unidic...")
            import subprocess
            import sys

            try:
                # Run unidic download command
                subprocess.check_call(
                    [sys.executable, "-m", "unidic", "download"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                print("Successfully downloaded Japanese dictionary.")
            except subprocess.CalledProcessError as e:
                raise ConfigurationError(
                    "Failed to download Japanese dictionary. Please run manually: python -m unidic download"
                )

        except ImportError:
            raise ConfigurationError("Japanese support requires unidic package. Please ensure misaki[ja] is installed.")
