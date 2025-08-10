import queue
import threading
from typing import Iterator, Optional

import numpy as np
import pyaudio

from ..core.base import AudioData
from ..core.exceptions import AudioProcessingError


class AudioPlayer:
    """Audio player using PyAudio for both single audio and streaming playback."""

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.current_sample_rate: Optional[int] = None
        self.current_channels: Optional[int] = None

        # For streaming playback
        self.audio_queue = queue.Queue(maxsize=100)
        self.stop_event = threading.Event()
        self.playback_thread = None

    def _ensure_stream(self, sample_rate: int, channels: int) -> None:
        """Ensure stream is open with correct parameters."""
        # Check if we need a new stream
        if self.stream is None or self.current_sample_rate != sample_rate or self.current_channels != channels:
            # Close existing stream if any
            if self.stream is not None:
                self.close_stream()

            # Open new stream
            self.stream = self.pyaudio.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=sample_rate,
                output=True,
                frames_per_buffer=2048,  # Balanced buffer for smooth playback
            )
            self.current_sample_rate = sample_rate
            self.current_channels = channels

    def play(self, audio: AudioData) -> AudioData:
        """Play audio data (blocking).

        Args:
            audio: AudioData to play
        """
        try:
            self._ensure_stream(audio.sample_rate, audio.channels)

            # Ensure audio data is in the correct format
            if audio.data.dtype != np.float32:
                audio_data = audio.data.astype(np.float32)
            else:
                audio_data = audio.data

            # Play audio (blocking)
            assert self.stream is not None, "Stream must be initialized before playing"
            self.stream.write(audio_data.tobytes())

            # Return the original audio data
            return audio

        except Exception as e:
            raise AudioProcessingError(f"Failed to play audio: {str(e)}")

    def play_stream(self, audio_stream: Iterator[AudioData]) -> AudioData:
        """Play audio from a stream of AudioData chunks.

        This method starts playback immediately when the first chunk arrives
        and continues playing subsequent chunks seamlessly.

        Args:
            audio_stream: Iterator yielding AudioData chunks

        Returns:
            AudioData: Combined audio data from all chunks
        """
        # Start playback thread
        self.stop_event.clear()
        self.playback_thread = threading.Thread(target=self._playback_worker)
        self.playback_thread.start()

        # Collect all chunks for return value
        all_chunks = []
        sample_rate = None
        channels = None
        format = None

        try:
            # Feed chunks to the queue
            for chunk in audio_stream:
                if self.stop_event.is_set():
                    break

                # Initialize stream with first chunk's parameters
                if self.stream is None:
                    self._ensure_stream(chunk.sample_rate, chunk.channels)

                # Set audio parameters from first valid chunk
                if sample_rate is None and chunk.sample_rate is not None:
                    sample_rate = chunk.sample_rate
                if channels is None and chunk.channels is not None:
                    channels = chunk.channels
                if format is None and chunk.format is not None:
                    format = chunk.format

                # Ensure audio data is in the correct format
                if chunk.data.dtype != np.float32:
                    audio_data = chunk.data.astype(np.float32)
                else:
                    audio_data = chunk.data

                # Store chunk for return value
                all_chunks.append(audio_data)

                # Put chunk in queue (will block if queue is full)
                try:
                    self.audio_queue.put(audio_data.tobytes(), timeout=2.0)
                except queue.Full:
                    print("Warning: Audio queue is full, skipping chunk")

        finally:
            # Signal end of stream
            self.audio_queue.put(None)

            # Wait for playback to complete
            if self.playback_thread:
                self.playback_thread.join(timeout=30.0)

            # Clean up
            self._cleanup_stream()

        # Combine all chunks into a single AudioData
        if not all_chunks:
            raise AudioProcessingError("No audio chunks received from stream")

        # Check if audio parameters were initialized
        if sample_rate is None or channels is None or format is None:
            raise AudioProcessingError("Audio parameters not initialized. Stream may have ended without sending any chunks.")

        combined_data = np.concatenate(all_chunks)
        return AudioData(data=combined_data, sample_rate=sample_rate, channels=channels, format=format)

    def _playback_worker(self):
        """Worker thread for continuous playback."""
        while not self.stop_event.is_set():
            try:
                # Get audio data from queue
                audio_data = self.audio_queue.get(timeout=0.1)

                if audio_data is None:
                    # End of stream marker
                    break

                # Play the chunk
                if self.stream and not self.stream.is_stopped():
                    self.stream.write(audio_data)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Playback error: {e}")
                break

    def _cleanup_stream(self):
        """Clean up PyAudio stream."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.current_sample_rate = None
            self.current_channels = None

    def close_stream(self) -> None:
        """Close the current stream."""
        self._cleanup_stream()

    def stop(self):
        """Stop playback and clean up resources."""
        self.stop_event.set()

        # Clear queue
        try:
            while True:
                self.audio_queue.get_nowait()
        except queue.Empty:
            pass

        # Wait for playback thread
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=2.0)

        self._cleanup_stream()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def __del__(self):
        """Clean up PyAudio instance."""
        self.stop()
        if hasattr(self, "pyaudio"):
            self.pyaudio.terminate()
