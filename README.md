# YouTube Value Extractor

A powerful tool for extracting actionable insights from YouTube videos. Transform video content into structured, skimmable markdown reports with key takeaways, frameworks, and chapter outlines.

## ✨ Features

- **🎯 Smart Content Extraction**: Automatically extracts key takeaways, frameworks, and actionable insights
- **📝 Clean Markdown Output**: Generates well-structured reports with timestamps and metadata
- **🚀 Multiple LLM Support**: Works with OpenAI, Anthropic, or local models via Ollama
- **⚡ Intelligent Caching**: Caches transcripts and LLM responses for faster processing
- **🔄 Whisper Fallback**: Local transcription when YouTube transcripts aren't available
- **🛠 Rich CLI**: Full-featured command-line interface with progress indicators
- **📊 Batch Processing**: Process multiple videos efficiently

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-extractor-tool.git
cd youtube-extractor-tool

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set your API key:
```bash
# For OpenAI
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here

# For Anthropic
# LLM_MODEL=claude-3-5-sonnet-latest
# ANTHROPIC_API_KEY=your-key-here

# For local models
# LLM_MODEL=ollama/llama3.1:8b
```

### Basic Usage

```bash
# Process a single video
python main.py process "https://www.youtube.com/watch?v=VIDEO_ID"

# Process multiple videos
python main.py process "https://www.youtube.com/watch?v=ID1" "https://www.youtube.com/watch?v=ID2"

# Process from file (one URL per line)
echo "https://www.youtube.com/watch?v=ID1" > videos.txt
python main.py batch videos.txt

# Check configuration
python main.py config check

# View video info without processing
python main.py info "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 📋 CLI Commands

### Main Commands

- `process [URLs...]` - Process one or more YouTube videos
- `batch FILE` - Process multiple videos from a file
- `info URL` - Show video information without processing

### Configuration Commands

- `config check` - Validate configuration and show current settings
- `config init` - Create a new .env configuration file

### Cache Commands

- `cache stats` - Show cache statistics
- `cache clear` - Clear all cached data

### Command Options

- `--output-dir, -o` - Specify output directory
- `--format` - Choose output format (markdown, json)
- `--dry-run` - Preview without saving files
- `--verbose, -v` - Enable verbose output
- `--concurrent, -c` - Set concurrent processing limit

## 📖 Output Format

The tool generates markdown files with this structure:

```markdown
---
type: video-notes
source: youtube
url: https://www.youtube.com/watch?v=VIDEO_ID
video_id: VIDEO_ID
title: Video Title
channel: Channel Name
published: 20240315
created: 2024-03-15 10:30
tags: ["tag1", "tag2"]
---

# Video Title
- Channel: Channel Name  
- Published: 2024-03-15
- Duration: 25:30
- URL: https://www.youtube.com/watch?v=VIDEO_ID

## TL;DR
One paragraph summary of the core idea and value.

## Key Takeaways
- Main point with timestamp [t=05:30]
- Another insight with timestamp [t=12:45]
- Important concept with timestamp [t=18:20]

## Frameworks & Models
**Framework Name** — Step-by-step breakdown:
1. First step
2. Second step  
3. Third step
Source: [t=15:30]

## Chapters
02:30 Introduction and Overview
08:15 Core Concepts
15:45 Implementation Details
22:10 Conclusion and Next Steps
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_MODEL` | LLM model to use | `gpt-4o-mini` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `DEFAULT_OUTPUT_DIR` | Output directory | `./notes` |
| `ENABLE_CACHE` | Enable caching | `true` |
| `CACHE_DIR` | Cache directory | `./.cache` |
| `DEFAULT_CHUNK_CHARS` | Chunk size for processing | `4000` |
| `REPORT_TZ` | Timezone for timestamps | `America/Costa_Rica` |

### Whisper Configuration (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `WHISPER_MODEL` | Whisper model size | `base` |
| `WHISPER_DEVICE` | Device (auto/cuda/cpu) | `auto` |
| `WHISPER_COMPUTE_TYPE` | Compute precision | `float16` |

## 🔧 Advanced Features

### Caching

The tool automatically caches:
- **Transcripts**: Avoid re-downloading YouTube transcripts
- **LLM Responses**: Skip re-processing identical content chunks

Cache management:
```bash
# View cache statistics
python main.py cache stats

# Clear cache
python main.py cache clear
```

### Whisper Fallback

For videos without YouTube transcripts, install Whisper support:

```bash
# Install optional Whisper dependencies
pip install faster-whisper soundfile

# Requires ffmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### Batch Processing

Create a file with one YouTube URL per line:

```txt
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2  
https://www.youtube.com/watch?v=VIDEO_ID_3
```

Then process them all:
```bash
python main.py batch videos.txt --concurrent 3
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yt_extractor

# Run specific tests
pytest tests/test_models.py -v
```

### Code Formatting

```bash
# Format code
black .
isort .

# Type checking
mypy yt_extractor
```

### Project Structure

```
yt_extractor/
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── exceptions.py      # Custom exceptions
│   ├── extractor.py       # Main extractor class
│   └── models.py          # Data models
├── llm/
│   ├── __init__.py
│   ├── processor.py       # LLM interaction
│   └── prompts.py         # Prompt templates
├── utils/
│   ├── __init__.py
│   ├── cache.py           # Caching utilities
│   ├── chunking.py        # Transcript chunking
│   └── formatting.py     # Output formatting
└── cli.py                 # Command-line interface
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

- Create an [issue](https://github.com/yourusername/youtube-extractor-tool/issues) for bugs or feature requests
- Check existing issues before creating new ones

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust YouTube metadata extraction
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for transcript fetching
- [LiteLLM](https://github.com/BerriAI/litellm) for unified LLM API access
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output