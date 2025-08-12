import argparse
from audiomaker.core import text_to_audio
from .banner import print_banner


def main():
  print_banner()
  
  parser = argparse.ArgumentParser(
    description="audiomaker - Generate long-form audio from large text"
  )
  parser.add_argument(
    "--input", type=str, required=True, help="Path to text file"
  )
  parser.add_argument(
    "--output", type=str, default="output.mp3",
    help="Path to save final audio"
  )
  parser.add_argument(
    "--chunk_size", type=int, default=3000,
    help="Number of words per chunk"
  )
  parser.add_argument(
    "--voice", type=str, default="en-US-AriaNeural",
    help="Voice for synthesis"
  )
  parser.add_argument(
    "--temp_dir", type=str, default="audio_parts",
    help="Temporary storage directory"
  )

  args = parser.parse_args()

  with open(args.input, "r", encoding="utf-8") as f:
    text = f.read()

  text_to_audio(
    text=text,
    output_path=args.output,
    chunk_size=args.chunk_size,
    voice=args.voice,
    temp_dir=args.temp_dir
  )
