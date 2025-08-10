import wave
from pathlib import Path
from typing import Iterator

import numpy as np

from ..core.base import AudioData
from ..core.exceptions import AudioProcessingError


class AudioWriter:
    """Audio file writer supporting various formats."""

    def save(self, audio: AudioData, output_path: str | Path) -> AudioData:
        """Save audio data to file.

        Args:
            audio: AudioData to save
            output_path: Path to save the audio file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get file extension
        extension = output_path.suffix.lower()

        if extension in [".wav", ".wave"]:
            self._save_wav(audio, output_path)
        else:
            raise AudioProcessingError(f"Unsupported audio format: {extension}")

        return audio

    def save_stream(self, audio_stream: Iterator[AudioData], output_path: str | Path) -> AudioData:
        """Save streaming audio data to file.

        This method accumulates all chunks from the stream and saves them as a single file.
        For WAV format, it writes the header after collecting all data to ensure correct file size.

        Args:
            audio_stream: Iterator yielding AudioData chunks
            output_path: Path to save the audio file

        Returns:
            AudioData: Combined audio data from all chunks
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get file extension
        extension = output_path.suffix.lower()

        if extension in [".wav", ".wave"]:
            return self._save_wav_stream(audio_stream, output_path)
        else:
            raise AudioProcessingError(f"Unsupported audio format for streaming: {extension}")

    def _save_wav(self, audio: AudioData, output_path: Path) -> None:
        """Save audio as WAV file.

        Args:
            audio: AudioData to save
            output_path: Path to save the WAV file
        """
        try:
            # Convert float32 to int16 for WAV format
            if audio.data.dtype == np.float32:
                # Clip to [-1, 1] range and convert to int16
                audio_data = np.clip(audio.data, -1.0, 1.0)
                audio_data = (audio_data * 32767).astype(np.int16)
            else:
                audio_data = audio.data.astype(np.int16)

            # Write WAV file
            assert audio.sample_rate is not None, "Sample rate must be set"
            assert audio.channels is not None, "Channels must be set"

            with wave.open(str(output_path), "wb") as wav_file:
                wav_file.setnchannels(audio.channels)
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(audio.sample_rate)
                wav_file.writeframes(audio_data.tobytes())

        except Exception as e:
            raise AudioProcessingError(f"Failed to save WAV file: {str(e)}")

    def _save_wav_stream(self, audio_stream: Iterator[AudioData], output_path: Path) -> AudioData:
        """Save streaming audio as WAV file.

        Args:
            audio_stream: Iterator yielding AudioData chunks
            output_path: Path to save the WAV file

        Returns:
            AudioData: Combined audio data from all chunks
        """
        try:
            # Collect all chunks
            chunks = []
            chunks_float32 = []  # Keep original float32 data for return value
            sample_rate = None
            channels = None
            format = None

            for chunk in audio_stream:
                # Get audio parameters from first chunk
                if sample_rate is None:
                    sample_rate = chunk.sample_rate
                    channels = chunk.channels
                    format = chunk.format

                # Verify consistency
                if chunk.sample_rate != sample_rate or chunk.channels != channels:
                    raise AudioProcessingError(
                        "Inconsistent audio parameters in stream. "
                        f"Expected {sample_rate}Hz/{channels}ch, "
                        f"got {chunk.sample_rate}Hz/{chunk.channels}ch"
                    )

                # Store original float32 data for return value
                if chunk.data.dtype != np.float32:
                    chunks_float32.append(chunk.data.astype(np.float32))
                else:
                    chunks_float32.append(chunk.data)

                # Convert and store chunk for saving
                if chunk.data.dtype == np.float32:
                    audio_data = np.clip(chunk.data, -1.0, 1.0)
                    audio_data = (audio_data * 32767).astype(np.int16)
                else:
                    audio_data = chunk.data.astype(np.int16)

                chunks.append(audio_data)

            if not chunks:
                raise AudioProcessingError("No audio data received from stream")

            # Concatenate all chunks
            combined_audio = np.concatenate(chunks)

            # Write WAV file with complete data
            assert sample_rate is not None, "Sample rate must be set"
            assert channels is not None, "Channels must be set"
            assert format is not None, "Format must be set"
            with wave.open(str(output_path), "wb") as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(combined_audio.tobytes())

            # Create combined AudioData from original float32 data
            combined_float32 = np.concatenate(chunks_float32)

            assert sample_rate is not None, "Sample rate must be set"
            assert channels is not None, "Channels must be set"
            assert format is not None, "Format must be set"
            return AudioData(data=combined_float32, sample_rate=sample_rate, channels=channels, format=format)

        except AudioProcessingError:
            raise
        except Exception as e:
            raise AudioProcessingError(f"Failed to save streaming WAV file: {str(e)}")
