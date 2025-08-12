# 🎙️ AudioMaker

[![PyPI version](https://badge.fury.io/py/audiomaker.svg)](https://pypi.org/project/audiomaker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/audiomaker)](https://pypi.org/project/audiomaker/)

**AudioMaker** is a Python package for generating **seamless, long-form audio** from massive text inputs.  
Unlike traditional TTS tools, AudioMaker can handle **book-length content** (even 4+ hours) by **splitting text into chunks**, synthesizing each chunk, and merging them into a single audio file.

---

## ✨ Features

- 📚 **Handles huge text** – turn entire books into one MP3
- 🧩 **Chunking system** – bypasses TTS length limits automatically
- 🔗 **Seamless merging** – no awkward pauses or breaks
- 🎙️ **Custom voices** – choose from Microsoft Edge-TTS voices
- 🛠 **Flexible usage** – CLI or Python API
- ⏱ **Progress bars** – real-time status with `tqdm`

---

## 📦 Installation

```bash
pip install audiomaker

# or

git clone https://github.com/ankushrathour/audiomaker.git
cd audiomaker
pip install -e .
```

## 🚀 Usage

1️⃣ Command-Line Interface (CLI)
```bash
audiomaker --input file.txt --output file.mp3 --chunk_size 3000 --voice en-US-AriaNeural
```

####  Arguments:
######  Flag Description Default
- input Path to input text file Required

- output Path to save final audio output.mp3

- chunk_size Number of words per TTS chunk 3000

- voice Edge-TTS voice name en-US-AriaNeural

- temp_dir Directory for temporary audio chunks audio_parts

2️⃣ Python API from audiomaker import text_to_audio

```bash
# Load text from file
with open("file.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Convert to audio
text_to_audio(
    text=text, output_path="output.mp3",
    chunk_size=3000, voice="en-US-AriaNeural", temp_dir="audio_parts"
)
```

# 🎨 Example Voices
Some popular Microsoft Edge-TTS voices you can use:

- en-US-AriaNeural
- en-GB-RyanNeural
- en-IN-NeerjaNeural
- en-AU-NatashaNeural

For a complete list of available voices, please refer to the full list of [Voices](https://github.com/rany2/edge-tts?tab=readme-ov-file#changing-the-voice).

# ⚠️ Notes

Edge-TTS requires an internet connection to access Microsoft’s speech
services. Chunk size may need to be adjusted depending on the voice and
text formatting. Intermediate audio files are stored in temp_dir and can
be deleted after processing.

# 💡 Tagline

**AudioMaker** – Unlimited text, one seamless voice.