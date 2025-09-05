"""Setup script for YouTube Value Extractor."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="youtube-extractor-tool",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Extract actionable insights from YouTube videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube-extractor-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "litellm>=1.48.0",
        "youtube_transcript_api>=0.6.2",
        "yt-dlp>=2024.4.9",
        "pydantic>=2.7.0",
        "python-slugify>=8.0.4",
        "rich>=13.0.0",
        "click>=8.1.0",
        "diskcache>=5.6.0",
    ],
    extras_require={
        "whisper": [
            "faster-whisper>=1.0.0",
            "soundfile>=0.12.1",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "yt-extract=yt_extractor.cli:main",
        ],
    },
)