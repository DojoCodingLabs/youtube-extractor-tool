# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup

#### Virtual Environment (Recommended)
A Python virtual environment isolates project dependencies and prevents conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install in development mode with all dependencies
pip install -e ".[dev,whisper]"

# Deactivate when done (optional)
deactivate
```

**Why use virtual environments:**
- Prevents dependency conflicts between projects
- Keeps your system Python clean
- Allows different Python versions per project
- Makes dependency management reproducible

**Key benefits:**
- `pip install` only affects the active environment
- Each project can have different package versions
- Easy to recreate environments using `requirements.txt`
- System Python remains unmodified

When activated, your shell prompt typically shows `(venv)` indicating you're in the virtual environment.

#### Direct Installation (Alternative)
```bash
# Install in development mode with all dependencies
pip install -e ".[dev,whisper]"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yt_extractor

# Run specific test file
pytest tests/test_models.py -v

# Run single test
pytest tests/test_models.py::test_video_meta_duration_formatting -v
```

### Code Quality
```bash
# Format code
black .
isort .

# Type checking
mypy yt_extractor
```

### Running the Tool
```bash
# Process single video
python -m yt_extractor.cli process "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir ./outputs

# Check configuration
python -m yt_extractor.cli config check

# View cache stats
python -m yt_extractor.cli cache stats
```

## Architecture Overview

### Core Processing Pipeline
The tool follows a three-stage pipeline orchestrated by `YouTubeExtractor`:

1. **Metadata Extraction** (`core/extractor.py`): Uses yt-dlp to fetch video metadata and YouTube Transcript API for transcripts
2. **LLM Analysis** (`llm/processor.py`): Processes the complete transcript through a single LLM call for full-context understanding
3. **Markdown Generation** (`llm/processor.py`): Converts analysis into structured markdown reports

### Key Architectural Decisions

**Full-Context Processing**: Unlike traditional chunking approaches, this tool processes entire transcripts at once to maintain context and generate comprehensive insights. The `LLMProcessor.process_video()` method uses `join_transcript_lines()` to create a single text input for the LLM.

**State Persistence**: The `RecoveryManager` (`core/recovery.py`) saves progress between pipeline stages, allowing recovery from failures without reprocessing completed stages.

**Model-Agnostic LLM Integration**: Uses LiteLLM for unified access to OpenAI, Anthropic, and Ollama models. Temperature is automatically adjusted for GPT-5 models which only support temperature=1.0.

**Dual Caching Strategy**: 
- Transcript cache (7-day TTL) via `utils/cache.py`
- LLM response cache (30-day TTL) using prompt hash for cache keys

### Configuration System
Environment-based configuration through `core/config.py` with `.env` file support. Critical settings:
- `LLM_MODEL`: Determines which LLM provider and specific model
- API keys auto-detected based on model selection
- `ENABLE_CACHE`: Controls both transcript and LLM response caching

### CLI Architecture
Built with Click, the CLI (`cli.py`) provides subcommands:
- `process`: Main video processing
- `batch`: Multiple video processing with concurrency control
- `config`: Configuration management and validation
- `cache`: Cache statistics and management
- `info`: Video metadata preview without processing

### Output Structure
Generated markdown follows a standardized format:
- YAML frontmatter with metadata
- Executive Summary (2-3 comprehensive paragraphs)
- Key Insights (detailed paragraph-form analysis, not bullet points)
- Frameworks & Methods (step-by-step actionable guidance)
- Key Timestamps (navigation references)

### Error Handling
Implements exponential backoff retry logic (`utils/retry.py`) with specific handlers for:
- Network errors
- API rate limits  
- Temporary API failures
- GPT model-specific temperature constraints

### Data Models
Three primary models in `core/models.py`:
- `VideoMeta`: YouTube video metadata with duration formatting
- `TranscriptLine`: Individual transcript segments with timing
- `ExtractedContent`: Legacy model (no longer used in current full-context approach)

### Important Implementation Notes
- The tool no longer uses chunking (removed for better context understanding)
- `ExtractedContent` model exists but is unused in current architecture
- All LLM interactions go through the retry decorator for reliability
- Cache keys include model name to prevent cross-model cache pollution
- Processing is designed to be resumable via state persistence