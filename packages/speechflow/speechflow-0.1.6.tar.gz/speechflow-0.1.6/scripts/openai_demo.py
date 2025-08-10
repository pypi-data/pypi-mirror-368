import os
import time

from dotenv import load_dotenv

from speechflow import AudioPlayer, AudioWriter, OpenAITTSEngine


def demo_synthesize_play_and_save(engine, player, writer):
    """Demo: Synthesize, play and save audio."""
    print("\n=== 1. Synthesize + Play + Save ===")

    text = "こんにちは、これはOpenAIの音声合成のデモンストレーションです。"
    output_path = "output/openai_synthesize.wav"
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
    """Demo: Stream, play and save with low latency."""
    print("\n=== 2. Stream + Play + Save (Low Latency) ===")
    print("Expected latency: 0.5-0.7s after warmup")

    text = """これはOpenAI TTSのストリーミングデモンストレーションです。
シンセサイズ関数とは異なり、ストリーム関数は最初のチャンクが到着するとすぐに再生を開始し、
長いテキストに対してより良いユーザー体験を提供します。"""
    output_path = "output/openai_stream.wav"
    print(f"Text: {text[:50]}...")

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
        print(f"  Stream + Play: {play_time:.2f}s (first chunk ~0.5-0.7s)")
        print(f"  Total with save: {total_time:.2f}s")
        print(f"  Audio shape: {combined_audio.data.shape}")
        print(f"  Output: {output_path}")

    except Exception as e:
        print(f"Error: {e}")


def demo_different_voices(engine, player):
    """Demo: Different voices and speeds."""
    print("\n=== 3. Voice and Speed Variations ===")

    configurations = [
        {"voice": "alloy", "speed": 1.0, "text": "こんにちは、私はアロイです。通常の速度で話しています。"},
        {"voice": "nova", "speed": 1.1, "text": "こんにちは、私はノヴァです。少し速めに話しています。"},
        {"voice": "echo", "speed": 0.9, "text": "こんにちは、私はエコーです。ゆっくりと話しています。"},
    ]

    for config in configurations:
        print(f"\nVoice: {config['voice']}, Speed: {config['speed']}x")
        try:
            audio = engine.get(config["text"], voice=config["voice"], speed=config["speed"])
            player.play(audio)
            print("Played")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Run all OpenAI demos."""
    print("=== OpenAI TTS Comprehensive Demo ===")
    print("Showcasing all features of the OpenAI TTS engine")
    print("\nIMPORTANT: First call may have 10-20s cold start delay.")
    print("Subsequent calls will have 0.5-0.7s latency.")

    try:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY", "your_openai_api_key")

        # Initialize components
        print("\nInitializing...")
        engine = OpenAITTSEngine(api_key=api_key)
        writer = AudioWriter()
        print("Initialized successfully")

        # Use AudioPlayer with context manager
        with AudioPlayer() as player:
            # IMPORTANT: Warmup to avoid cold start on actual demos
            print("\nWarming up (this may take 10-20 seconds)...")
            warmup_start = time.time()
            _ = list(engine.stream("Warmup test"))
            warmup_time = time.time() - warmup_start
            print(f"Warmup complete in {warmup_time:.1f}s")
            print("  Subsequent calls will be much faster!")

            # Run all demos
            demo_synthesize_play_and_save(engine, player, writer)
            time.sleep(1)

            demo_stream_play_and_save(engine, player, writer)
            time.sleep(1)

            demo_different_voices(engine, player)

        print("\n=== All demos completed ===")
        print("\nKey takeaways:")
        print("- Streaming provides low latency (0.5-0.7s) after warmup")
        print("- Multiple voices and speeds available")
        print("- Supports various languages including Japanese")
        print("- WAV format provides best compatibility and latency")

    except Exception as e:
        print(f"\nFatal error: {e}")
        print("\nMake sure SPEECHFLOW_OPENAI_API_KEY is set in your .env file")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
