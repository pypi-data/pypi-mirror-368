import os
import time

from dotenv import load_dotenv

from speechflow import AudioPlayer, AudioWriter, GeminiTTSEngine


def demo_synthesize_play_and_save(engine, player, writer):
    """Demo: Synthesize, play and save audio."""
    print("\n=== 1. Synthesize + Play + Save ===")

    text = "Geminiで、音声合成を行い、再生と保存を行います。"
    output_path = "output/gemini_synthesize.wav"
    print(f"Text: {text}")

    try:
        # Synthesize
        print("Synthesizing...")
        start = time.time()
        audio = engine.get(text)
        synth_time = time.time() - start
        print(f"Synthesized in {synth_time:.2f}s")
        print(f"Audio shape: {audio.data.shape}, Sample rate: {audio.sample_rate}Hz")

        # Play
        print("Playing...")
        play_start = time.time()
        player.play(audio)
        play_time = time.time() - play_start

        # Save
        print("Saving...")
        save_start = time.time()
        writer.save(audio, output_path)
        save_time = time.time() - save_start

        print(f"Complete!")
        print(f"  Synthesis: {synth_time:.2f}s")
        print(f"  Playback: {play_time:.2f}s")
        print(f"  Save: {save_time:.2f}s")
        print(f"  Output: {output_path}")

    except Exception as e:
        print(f"Error: {e}")


def demo_stream_play_and_save(engine, player, writer):
    """Demo: Stream, play and save."""
    print("\n=== 2. Stream + Play + Save ===")
    print("Note: Gemini returns complete audio in single chunk")

    text = "ストリーミングで、音声を再生しながら保存します。Geminiは現在、単一チャンクで返されます。"
    output_path = "output/gemini_stream.wav"
    print(f"Text: {text}")

    try:
        print("\n--- Play first, then save ---")
        start = time.time()

        # Stream and play, getting combined audio
        print("Streaming and playing...")
        combined_audio = player.play_stream(engine.stream(text))
        play_time = time.time() - start

        # Save the combined audio
        print("Saving played audio...")
        writer.save(combined_audio, output_path)
        total_time = time.time() - start

        print(f"Complete!")
        print(f"  Stream + Play: {play_time:.2f}s")
        print(f"  Total with save: {total_time:.2f}s")
        print(f"  Audio shape: {combined_audio.data.shape}")
        print(f"  Output: {output_path}")

    except Exception as e:
        print(f"Error: {e}")


def demo_different_voices(engine, player):
    """Demo: Different voices and models."""
    print("\n=== 3. Voice Variations ===")

    configurations = [
        {"voice": "Leda", "text": "Speak friendly: こんにちは、私はレダです。明瞭で親しみやすい声が特徴です。"},
        {
            "voice": "Puck",
            "text": "Speak playful and fast: こんにちは、私はパックです。独特で、遊び心のある、声のトーンを、持っています。",
        },
        {"voice": "Kore", "text": "Speak warm and slowly: こんにちは、私はコアです。温かく、表現豊かな声をしています。"},
    ]

    for config in configurations:
        print(f"\nVoice: {config['voice']}")
        try:
            audio = engine.get(config["text"], voice=config["voice"])
            player.play(audio)
            print("Played")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Run all Gemini demos."""
    print("=== Gemini TTS Comprehensive Demo ===")
    print("Showcasing all features of the Gemini TTS engine")

    try:
        # Initialize components

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY", "your_gemini_api_key")

        print("\nInitializing...")
        engine = GeminiTTSEngine(api_key=api_key)
        writer = AudioWriter()
        print("Initialized successfully")

        # Use AudioPlayer with context manager
        with AudioPlayer() as player:
            # Warmup (though Gemini doesn't benefit as much as OpenAI)
            print("\nWarming up...")
            _ = engine.get("Warmup")
            print("Warmup complete")

            # Run all demos
            demo_synthesize_play_and_save(engine, player, writer)
            time.sleep(1)

            demo_stream_play_and_save(engine, player, writer)
            time.sleep(1)

            demo_different_voices(engine, player)

        print("\n=== All demos completed ===")
        print("\nNote: Gemini currently returns complete audio in a single chunk.")
        print("This is a known limitation as of June 2025.")

    except Exception as e:
        print(f"\nFatal error: {e}")
        print("\nMake sure SPEECHFLOW_GEMINI_API_KEY is set in your .env file")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
