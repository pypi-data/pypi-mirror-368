import time

from speechflow import AudioPlayer, AudioWriter, KokoroTTSEngine


def demo_synthesize_play_and_save(engine, player, writer):
    """Demo: Synthesize, play and save audio."""
    print("\n=== 1. Synthesize + Play + Save ===")

    text = "Hello, this is a demonstration of Kokoro text to speech synthesis."
    output_path = "output/kokoro_synthesize.wav"
    print(f"Text: {text}")

    # Synthesize
    print("Synthesizing...")
    start_time = time.time()
    audio = engine.get(text)
    synthesis_time = time.time() - start_time
    print(f"Synthesized in {synthesis_time:.2f}s")
    print(f"Audio duration: {audio.duration:.2f}s")

    # Play
    print("Playing audio...")
    player.play(audio)

    # Save
    print(f"Saving to {output_path}...")
    writer.save(audio, output_path)
    print("Saved successfully")


def demo_streaming_play(engine, player):
    """Demo: Stream synthesis with real-time playback."""
    print("\n=== 2. Streaming + Real-time Playback ===")

    text = """Kokoro is a lightweight text-to-speech model.
It supports multiple languages and voices.
This demonstrates streaming synthesis with real-time playback."""

    print(f"Text: {text[:50]}...")
    print("Streaming and playing...")

    start_time = time.time()
    # Stream and play audio, getting the combined result
    combined_audio = player.play_stream(engine.stream(text))
    total_time = time.time() - start_time

    print(f"Total streaming time: {total_time:.2f}s")
    print(f"Audio duration: {combined_audio.duration:.2f}s")
    print(f"Efficiency ratio: {combined_audio.duration / total_time:.2f}x")


def demo_streaming_save(engine, writer):
    """Demo: Stream synthesis with progressive saving."""
    print("\n=== 3. Streaming + Progressive Save ===")

    text = """This is a longer text to demonstrate progressive saving.
Each chunk is saved as it's generated.
The final file contains all chunks combined."""

    output_path = "output/kokoro_stream.wav"
    print(f"Text: {text[:50]}...")

    print("Streaming and saving...")
    start_time = time.time()

    # Stream and save progressively
    chunk_count = 0
    for i, chunk in enumerate(engine.stream(text)):
        chunk_count += 1
        print(f"  Chunk {i+1}: {chunk.duration:.2f}s")

    # Save using streaming method
    combined_audio = writer.save_stream(engine.stream(text), output_path)

    save_time = time.time() - start_time
    print(f"Saved {chunk_count} chunks in {save_time:.2f}s")
    print(f"Total audio duration: {combined_audio.duration:.2f}s")


def demo_multiple_voices(engine, player):
    """Demo: Test different voices."""
    print("\n=== 4. Multiple Voices Demo ===")

    text = "Testing different Kokoro voices."
    voices = ["af_heart", "af_bella", "am_michael", "bf_emma"]

    for voice in voices:
        print(f"\nVoice: {voice}")
        try:
            audio = engine.get(text, voice=voice)
            print(f"  Duration: {audio.duration:.2f}s")
            player.play(audio)
            time.sleep(0.5)
        except Exception as e:
            print(f"  Error: {str(e)}")


def demo_multiple_languages(player):
    """Demo: Test different languages."""
    print("\n=== 5. Multiple Languages Demo ===")

    languages = {
        "a": ("Hello, this is American English.", "af_heart"),
        "b": ("Hello, this is British English.", "bf_emma"),
        "j": ("こんにちは、これは日本語です。", "af_heart"),
        "e": ("Hola, esto es español.", "af_heart"),
        "f": ("Bonjour, ceci est en français.", "af_heart"),
    }

    for lang_code, (text, voice) in languages.items():
        print(f"\nLanguage: {lang_code}")
        print(f"Text: {text}")
        try:
            # Create engine with specific language
            engine = KokoroTTSEngine(lang_code=lang_code)
            audio = engine.get(text, voice=voice)
            print(f"  Duration: {audio.duration:.2f}s")
            player.play(audio)
            time.sleep(0.5)
        except Exception as e:
            error_msg = str(e)
            if "Japanese language support" in error_msg:
                print("  ⚠️  Japanese requires additional setup:")
                print("     pip install unidic-lite")
                print("     or: python -m unidic download")
            elif "espeak" in error_msg.lower():
                print(f"  ⚠️  Language '{lang_code}' requires espeak-ng to be installed")
            else:
                print(f"  Error: {error_msg}")


def main():
    """Run all Kokoro demos."""
    print("=== Kokoro TTS Comprehensive Demo ===")
    print("Showcasing all features of the Kokoro TTS engine")

    try:
        # Initialize components
        print("\nInitializing...")
        engine = KokoroTTSEngine()  # Default to American English
        writer = AudioWriter()
        print("Initialized successfully")

        # Use AudioPlayer with context manager
        with AudioPlayer() as player:
            # Run all demos
            demo_synthesize_play_and_save(engine, player, writer)
            time.sleep(1)

            demo_streaming_play(engine, player)
            time.sleep(1)

            demo_streaming_save(engine, writer)
            time.sleep(1)

            demo_multiple_voices(engine, player)
            time.sleep(1)

            demo_multiple_languages(player)

        print("\n=== All demos completed successfully! ===")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure kokoro is installed: pip install kokoro")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()