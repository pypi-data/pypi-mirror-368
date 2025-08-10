import json
import os
import re
from pathlib import Path
from typing import Iterator

import numpy as np
import torch

from ..core.base import AudioData, TTSEngineBase
from ..core.exceptions import ConfigurationError, TTSError


class StyleBertTTSEngine(TTSEngineBase):
    """Style-BERT-VITS2 TTS engine implementation."""

    # Default models available on Hugging Face
    DEFAULT_MODELS = {
        "jvnv-F1-jp": "litagin/style_bert_vits2_jvnv",
        "jvnv-M1-jp": "litagin/style_bert_vits2_jvnv",
        "jvnv-F2-jp": "litagin/style_bert_vits2_jvnv",
        "jvnv-M2-jp": "litagin/style_bert_vits2_jvnv",
        "jvnv-F1": "litagin/style_bert_vits2_jvnv",
        "jvnv-M1": "litagin/style_bert_vits2_jvnv",
        "jvnv-F2": "litagin/style_bert_vits2_jvnv",
        "jvnv-M2": "litagin/style_bert_vits2_jvnv",
    }

    # Supported styles
    SUPPORTED_STYLES = [
        "Neutral",
        "Happy",
        "Sad",
        "Angry",
        "Fear",
        "Surprise",
        "Disgust",
    ]

    def __init__(
        self,
        model_name: str | None = None,
        model_path: str | None = None,
        device: str = "auto",
    ):
        """Initialize Style-BERT-VITS2 TTS engine.

        Args:
            model_name: Name of pre-trained model (e.g., "jvnv-F1-jp")
            model_path: Path to custom model directory
            device: Device to use ("cuda", "cpu", or "auto")

        Raises:
            ConfigurationError: If neither model_name nor model_path is provided
        """
        super().__init__()

        if not model_name and not model_path:
            raise ConfigurationError("Either model_name or model_path must be provided")

        # Set device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Model paths
        self.model_name = model_name
        self.model_path = model_path

        # Initialize model
        self._init_model()

    def _init_model(self):
        """Initialize the TTS model."""
        try:
            if self.model_path:
                # Load from custom path
                self._load_custom_model(self.model_path)
            else:
                # Load pre-trained model
                self._load_pretrained_model(self.model_name)

        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Style-BERT-VITS2 model: {str(e)}")

    def _load_pretrained_model(self, model_name: str):
        """Load a pre-trained model from Hugging Face.

        Args:
            model_name: Name of the pre-trained model
        """
        if model_name not in self.DEFAULT_MODELS:
            raise ConfigurationError(f"Unknown model: {model_name}. Available models: {', '.join(self.DEFAULT_MODELS.keys())}")

        # Get repository name
        repo_id = self.DEFAULT_MODELS[model_name]

        # Extract base repository name for cache directory
        repo_name = repo_id.split("/")[-1]

        # Get cache directory for the repository
        repo_cache_dir = Path.home() / ".cache" / "speechflow" / "stylebert" / repo_name
        model_cache_dir = repo_cache_dir / model_name

        # Check if model is already downloaded
        config_path = model_cache_dir / "config.json"
        if not config_path.exists():
            print(f"Downloading model '{model_name}'...")
            self._download_model(model_name, repo_cache_dir)

        # Load model from the specific model subdirectory
        self._load_custom_model(str(model_cache_dir))

    def _download_model(self, model_name: str, cache_dir: Path):
        """Download model from Hugging Face.

        Args:
            model_name: Name of the model
            cache_dir: Directory to save the model
        """
        from huggingface_hub import snapshot_download

        repo_id = self.DEFAULT_MODELS[model_name]

        try:
            snapshot_download(repo_id=repo_id, local_dir=str(cache_dir), local_dir_use_symlinks=False)
            print(f"Model '{model_name}' downloaded successfully.")
        except Exception as e:
            raise TTSError(f"Failed to download model: {str(e)}")

    def _load_custom_model(self, model_path: str):
        """Load model from a custom path.

        Args:
            model_path: Path to the model directory
        """
        model_dir = Path(model_path)

        # Check required files
        config_path = model_dir / "config.json"
        if not config_path.exists():
            raise ConfigurationError(f"config.json not found in {model_path}")

        # Load config
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        # Initialize TTS model
        try:
            from style_bert_vits2.constants import Languages
            from style_bert_vits2.nlp import bert_models
            from style_bert_vits2.tts_model import TTSModel

            # Load BERT models for Japanese
            print("Loading BERT models for Japanese...")
            bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
            bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

            # Check for style vectors file
            style_vec_path = model_dir / "style_vectors.npy"
            if not style_vec_path.exists():
                raise ConfigurationError(f"style_vectors.npy not found in {model_path}")

            # Find the model file (.safetensors)
            model_files = list(model_dir.glob("*.safetensors"))
            if not model_files:
                raise ConfigurationError(f"No .safetensors model file found in {model_path}")

            # Use the first safetensors file found
            model_file_path = model_files[0]

            self.model = TTSModel(
                model_path=str(model_file_path),
                config_path=str(config_path),
                style_vec_path=str(style_vec_path),
                device=self.device,
            )
        except ImportError:
            raise ConfigurationError("style-bert-vits2 is not installed. Please install with: pip install style-bert-vits2")

        # Get model info
        self.sample_rate = self.config.get("data", {}).get("sampling_rate", 44100)
        self.speakers = self.config.get("data", {}).get("spk2id", {})

    def get(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
        speaker_id: int = 0,
        style: str = "Neutral",
        style_weight: float = 1.0,
        speed: float = 1.0,
        pitch: float = 0.0,
    ) -> AudioData:
        """Synthesize speech from text using Style-BERT-VITS2.

        Args:
            text: Text to synthesize
            model: Not used (for API compatibility)
            voice: Not used (for API compatibility)
            speaker_id: Speaker ID (default: 0)
            style: Style name (default: "Neutral")
            style_weight: Style weight 0.0-10.0 (default: 1.0)
            speed: Speech speed (default: 1.0)
            pitch: Pitch shift in semitones (default: 0.0)

        Returns:
            AudioData containing the synthesized speech
        """
        try:
            # Validate parameters
            if speaker_id >= len(self.speakers):
                raise TTSError(f"Invalid speaker_id: {speaker_id}. Available: 0-{len(self.speakers) - 1}")

            if style not in self.SUPPORTED_STYLES:
                raise TTSError(f"Unsupported style: {style}. Available: {', '.join(self.SUPPORTED_STYLES)}")

            # Generate audio
            sr, audio = self.model.infer(
                text=text,
                speaker_id=speaker_id,
                style=style,
                style_weight=style_weight,
                length=1.0 / speed,  # Inverse for speed
                sdp_ratio=0.2,
                noise=0.6,
                noise_w=0.8,
                pitch_scale=2 ** (pitch / 12),  # Convert semitones to scale factor
            )

            # Update sample rate from model output
            self.sample_rate = sr

            # Extract audio data
            audio_data = self._extract_audio(audio)
            if audio_data is None:
                raise TTSError("Failed to generate audio")

            return audio_data

        except Exception as e:
            raise TTSError(f"Style-BERT-VITS2 synthesis failed: {str(e)}")

    def stream(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
        speaker_id: int = 0,
        style: str = "Neutral",
        style_weight: float = 1.0,
        speed: float = 1.0,
        pitch: float = 0.0,
    ) -> Iterator[AudioData]:
        """Stream synthesized speech in chunks.

        Note: Style-BERT-VITS2 doesn't support true streaming.
        This method splits text into sentences and yields each sentence's audio.

        Args:
            text: Text to synthesize
            model: Not used (for API compatibility)
            voice: Not used (for API compatibility)
            speaker_id: Speaker ID (default: 0)
            style: Style name (default: "Neutral")
            style_weight: Style weight 0.0-10.0 (default: 1.0)
            speed: Speech speed (default: 1.0)
            pitch: Pitch shift in semitones (default: 0.0)

        Yields:
            AudioData chunks (one per sentence)
        """
        # Split text into sentences
        sentences = re.split(r"[。！？\.\!\?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return

        # Generate audio for each sentence
        for sentence in sentences:
            try:
                audio_data = self.synthesize(
                    text=sentence,
                    speaker_id=speaker_id,
                    style=style,
                    style_weight=style_weight,
                    speed=speed,
                    pitch=pitch,
                )
                yield audio_data

            except Exception as e:
                raise TTSError(f"Style-BERT-VITS2 streaming failed on sentence '{sentence}': {str(e)}")

    def _extract_audio(self, audio) -> AudioData | None:
        """Extract AudioData from model output.

        Args:
            audio: Output from Style-BERT-VITS2 model

        Returns:
            AudioData if successful, None otherwise
        """
        if audio is None:
            return None

        # Convert to numpy array if it's a torch tensor
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()

        # Ensure it's a numpy array
        if not isinstance(audio, np.ndarray):
            return None

        # Ensure float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Remove batch dimension if present
        if audio.ndim > 1:
            audio = audio.squeeze()

        # Normalize if needed
        max_val = np.abs(audio).max()
        if max_val > 1.0:
            audio = audio / max_val

        return AudioData(
            data=audio,
            sample_rate=self.sample_rate,
            channels=1,  # Mono
            format="pcm",
        )
