import os
import asyncio
from tqdm import tqdm
from edge_tts import Communicate
from pydub import AudioSegment


async def _synthesize_chunk(text, out_path, voice):
  """Asynchronously generate audio for a text chunk."""
  communicate = Communicate(text=text, voice=voice)
  await communicate.save(out_path)


def text_to_audio(
  text: str,
  output_path: str = "output.mp3",
  chunk_size: int = 3000,
  voice: str = "en-US-AriaNeural",
  temp_dir: str = "audio_parts"
):
  """
  Convert large text into a single audio file by chunking and merging.

  Args:
    text (str): Full text to convert.
    output_path (str): Path to save final audio.
    chunk_size (int): Words per chunk for synthesis.
    voice (str): Edge-TTS voice name.
    temp_dir (str): Directory to store intermediate chunks.
  """
  os.makedirs(temp_dir, exist_ok=True)

  words = text.split()
  chunks = [' '.join(words[i:i + chunk_size])
            for i in range(0, len(words), chunk_size)]

  print(f"🔊 Generating {len(chunks)} chunks using voice '{voice}'...")

  # Generate audio chunks
  for i, chunk in tqdm(enumerate(chunks), total=len(chunks), desc="Synthesizing"):
    chunk_file = os.path.join(temp_dir, f"part_{i:04d}.mp3")
    asyncio.run(_synthesize_chunk(chunk, chunk_file, voice))

  # Merge all chunks
  print("🔗 Merging chunks into final audio file...")
  final_audio = AudioSegment.empty()

  for i in tqdm(range(len(chunks)), desc="Merging"):
    chunk_file = os.path.join(temp_dir, f"part_{i:04d}.mp3")
    if os.path.exists(chunk_file):
      final_audio += AudioSegment.from_file(chunk_file, format="mp3")
    else:
      print(f"⚠️ Missing chunk: {chunk_file}")

  final_audio.export(output_path, format="mp3")
  print(f"✅ Done! File saved: {output_path}")
