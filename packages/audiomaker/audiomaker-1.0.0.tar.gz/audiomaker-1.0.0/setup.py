from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Read README.md for PyPI long description
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
  name="audiomaker",
  version="1.0.0",
  description="Unlimited text-to-speech generation with chunking and seamless merging",
  long_description=long_description,
  long_description_content_type="text/markdown",
  author="Ankush Rathour",
  author_email="ankush.14072000.rathour@gmail.com",
  url="https://github.com/AnkushRathour/AudioMaker",
  license="MIT",
  packages=find_packages(),
  python_requires=">=3.8",
  install_requires=[
    "tqdm>=4.64.0",
    "edge-tts>=6.1.9",
    "pydub>=0.25.1",
  ],
  entry_points={
    "console_scripts": [
        "audiomaker=audiomaker.cli:main",
    ],
  },
  keywords="text-to-speech tts audio synthesis mp3 wav microsoft-edge",
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Multimedia :: Sound/Audio :: Speech",
  ],
  project_urls={
    "Bug Tracker": "https://github.com/AnkushRathour/AudioMaker/issues",
    "Source": "https://github.com/AnkushRathour/AudioMaker",
  },
)
