"""FishAudio TTS demo script."""

import os
import time
from pathlib import Path

from dotenv import load_dotenv

from speechflow import AudioPlayer, AudioWriter, FishAudioTTSEngine

load_dotenv()


def demo_basic_streaming(engine, player, writer):
    """Demo: Basic streaming with FishAudio."""
    print("\n=== 1. Basic Streaming ===")

    text = "Hello, this is a demonstration of FishAudio text-to-speech engine."
    output_path = "output/fishaudio_stream.wav"

    print(f"Text: {text}")
    print("Streaming and playing...")

    start_time = time.time()

    # Stream and play
    stream = engine.stream(text)
    combined_audio = player.play_stream(stream)

    streaming_time = time.time() - start_time
    print(f"Streaming completed in {streaming_time:.2f}s")
    print(f"Audio duration: {combined_audio.duration:.2f}s")

    # Save audio
    print(f"Saving to {output_path}...")
    writer.save(combined_audio, output_path)
    print("Saved successfully")


def demo_model_selection(engine, player):
    """Demo: Different model selection."""
    print("\n=== 2. Model Selection Demo ===")

    text = "Testing different FishAudio models."
    models = ["s1", "s1-mini", "speech-1.6"]

    for model in models:
        print(f"\nModel: {model}")
        try:
            stream = engine.stream(text, model=model)
            audio = player.play_stream(stream)
            print(f"Duration: {audio.duration:.2f}s")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error with model '{model}': {str(e)}")


def demo_long_text(engine, player, writer):
    """Demo: Long text streaming."""
    print("\n=== 3. Long Text Streaming ===")

    text = """FishAudio is a cutting-edge text-to-speech platform that offers high-quality voice synthesis.
    It supports multiple languages and voices, making it suitable for various applications.
    The streaming capability allows for real-time audio generation, which is perfect for interactive applications.
    This demonstration shows how to integrate FishAudio with the SpeechFlow library."""

    output_path = "output/fishaudio_long.wav"
    print(f"Text: {text[:100]}...")
    print("Streaming long text...")

    start_time = time.time()

    # Stream and save
    stream = engine.stream(text)
    combined_audio = writer.save_stream(stream, output_path)

    total_time = time.time() - start_time
    print(f"\nTotal streaming time: {total_time:.2f}s")
    print(f"Audio duration: {combined_audio.duration:.2f}s")
    print(f"Saved to {output_path}")


def demo_voice_selection(engine, player):
    """Demo: Voice selection (if API key has access to custom voices)."""
    print("\n=== 4. Voice Selection Demo ===")

    text = "Testing different voices with FishAudio."

    # Note: Replace with actual voice IDs from your FishAudio account
    voices = [None, "voice_id_1", "voice_id_2"]  # None uses default voice

    for voice in voices:
        voice_name = voice if voice else "default"
        print(f"\nVoice: {voice_name}")
        try:
            stream = engine.stream(text, voice=voice)
            audio = player.play_stream(stream)
            print(f"Duration: {audio.duration:.2f}s")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error with voice '{voice_name}': {str(e)}")


def demo_japanese_text(engine, player, writer):
    """Demo: Japanese text synthesis."""
    print("\n=== 5. Japanese Text Demo ===")

    text = "こんにちは。FishAudioを使用した日本語の音声合成のデモンストレーションです。"
    output_path = "output/fishaudio_japanese.wav"

    print(f"Text: {text}")
    print("Streaming Japanese text...")

    try:
        stream = engine.stream(text)
        combined_audio = player.play_stream(stream)

        print(f"Audio duration: {combined_audio.duration:.2f}s")

        # Save audio
        writer.save(combined_audio, output_path)
        print(f"Saved to {output_path}")
    except Exception as e:
        print(f"Error with Japanese text: {str(e)}")


def main():
    """Run all FishAudio demos."""
    print("=== FishAudio TTS Demo ===")
    print("Showcasing features of the FishAudio engine")

    # Check for API key
    api_key = os.getenv("FISHAUDIO_API_KEY")
    if not api_key:
        print("\nError: FISHAUDIO_API_KEY environment variable not set")
        print("Please set your FishAudio API key:")
        print("  export FISHAUDIO_API_KEY=your_api_key_here")
        return

    try:
        # Initialize components
        print("\nInitializing...")
        engine = FishAudioTTSEngine(api_key=api_key)
        writer = AudioWriter()

        print("Initialized successfully")
        print(f"Sample rate: {engine.sample_rate} Hz")

        # Create output directory
        Path("output").mkdir(exist_ok=True)

        # Use AudioPlayer with context manager
        with AudioPlayer() as player:
            # Run demos
            demo_basic_streaming(engine, player, writer)
            time.sleep(1)

            demo_model_selection(engine, player)
            time.sleep(1)

            demo_long_text(engine, player, writer)
            time.sleep(1)

            demo_voice_selection(engine, player)
            time.sleep(1)

            demo_japanese_text(engine, player, writer)

        print("\n=== All demos completed successfully! ===")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure FISHAUDIO_API_KEY is set correctly")
        print("2. Check your internet connection")
        print("3. Verify your API key has the necessary permissions")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
