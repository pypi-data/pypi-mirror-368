"""Style-BERT-VITS2 TTS demo script."""

import time
from pathlib import Path

from speechflow import AudioPlayer, AudioWriter, StyleBertTTSEngine


def demo_basic_synthesis(engine, player, writer):
    """Demo: Basic synthesis with Style-BERT-VITS2."""
    print("\n=== 1. Basic Synthesis ===")

    text = "こんにちは、Style-BERT-VITS2による音声合成のデモンストレーションです。"
    output_path = "output/stylebert_basic.wav"

    print(f"Text: {text}")
    print("Synthesizing...")

    start_time = time.time()
    audio = engine.get(text)
    synthesis_time = time.time() - start_time

    print(f"Synthesis completed in {synthesis_time:.2f}s")
    print(f"Audio duration: {audio.duration:.2f}s")

    # Play audio
    print("Playing audio...")
    player.play(audio)

    # Save audio
    print(f"Saving to {output_path}...")
    writer.save(audio, output_path)
    print("Saved successfully")


def demo_style_control(engine: StyleBertTTSEngine, player: AudioPlayer):
    """Demo: Style control features."""
    print("\n=== 2. Style Control Demo ===")

    text = "感情を込めて話します。"
    styles = ["Neutral", "Happy", "Sad", "Angry"]

    for style in styles:
        print(f"\nStyle: {style}")
        try:
            audio = engine.get(
                text,
                style=style,
                style_weight=5.0,  # Strong style effect
            )
            print(f"Duration: {audio.duration:.2f}s")
            player.play(audio)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error with style '{style}': {str(e)}")


def demo_speed_control(engine, player):
    """Demo: Speed control."""
    print("\n=== 3. Speed Control Demo ===")

    text = "話す速度を変えてみます。"
    speeds = [0.7, 1.0, 1.3]

    for speed in speeds:
        print(f"\nSpeed: {speed}x")
        audio = engine.get(text, speed=speed)
        print(f"Duration: {audio.duration:.2f}s")
        player.play(audio)
        time.sleep(0.5)


def demo_streaming(engine, player, writer):
    """Demo: Streaming synthesis (sentence by sentence)."""
    print("\n=== 4. Streaming Demo ===")

    text = """今日は良い天気ですね。
桜が満開で、とても美しいです。
春の訪れを感じます。
皆さんも素敵な一日をお過ごしください。"""

    output_path = "output/stylebert_stream.wav"
    print(f"Text: {text[:50]}...")
    print("Streaming and playing...")

    start_time = time.time()

    # Stream and play
    stream = engine.stream(text)
    combined_audio = player.play_stream(stream)

    total_time = time.time() - start_time
    print(f"\nTotal streaming time: {total_time:.2f}s")
    print(f"Audio duration: {combined_audio.duration:.2f}s")

    # Save combined audio
    writer.save(combined_audio, output_path)
    print(f"Saved to {output_path}")


def demo_custom_model(player):
    """Demo: Loading a custom model."""
    print("\n=== 5. Custom Model Demo ===")

    # Example of loading a custom model
    custom_model_path = Path("path/to/custom/model")

    if custom_model_path.exists():
        try:
            engine = StyleBertTTSEngine(model_path=str(custom_model_path))
            audio = engine.get("カスタムモデルのテストです。")
            player.play(audio)
        except Exception as e:
            print(f"Error loading custom model: {str(e)}")
    else:
        print(f"Custom model path not found: {custom_model_path}")
        print("Skipping custom model demo")


def main():
    """Run all Style-BERT-VITS2 demos."""
    print("=== Style-BERT-VITS2 TTS Demo ===")
    print("Showcasing features of the Style-BERT-VITS2 engine")

    try:
        # Initialize components
        print("\nInitializing...")

        # Use default pre-trained model
        engine = StyleBertTTSEngine(model_name="jvnv-F1-jp")
        writer = AudioWriter()

        print("Initialized successfully")
        print(f"Using device: {engine.device}")
        print(f"Sample rate: {engine.sample_rate} Hz")

        # Create output directory
        Path("output").mkdir(exist_ok=True)

        # Use AudioPlayer with context manager
        with AudioPlayer() as player:
            # Run demos
            demo_basic_synthesis(engine, player, writer)
            time.sleep(1)

            demo_style_control(engine, player)
            time.sleep(1)

            demo_speed_control(engine, player)
            time.sleep(1)

            demo_streaming(engine, player, writer)
            time.sleep(1)

            demo_custom_model(player)

        print("\n=== All demos completed successfully! ===")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure style-bert-vits2 is installed")
        print("2. First run will download the model (may take time)")
        print("3. GPU is recommended for better performance")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
