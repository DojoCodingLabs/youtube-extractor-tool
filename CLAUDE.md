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
# Process single video (outputs to ./outputs/category/)
python -m yt_extractor.cli process "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir ./outputs --category "AI/Agents"

# Start web UI (includes batch queue and PDF export features)
source venv/bin/activate && streamlit run web_ui.py

# Test PDF generation
python test_pdf_generation.py

# Test queue manager
python test_queue_manager.py

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

**Model-Agnostic LLM Integration**: Uses LiteLLM for unified access to OpenAI, Anthropic, and Ollama models. Temperature is automatically adjusted for GPT-5 models which only support temperature=1.0. Token limits are removed for GPT-5 to accommodate reasoning tokens plus output.

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
Generated markdown follows a standardized format and is saved to `./outputs/$Category/`:
- YAML frontmatter with metadata
- Executive Summary (2-3 comprehensive paragraphs)
- Key Insights (detailed paragraph-form analysis, not bullet points)
- Frameworks & Methods (step-by-step actionable guidance)
- Key Timestamps (navigation references)

Files are organized by category: `./outputs/AI/Agents/video-title.md`

### Batch Queue System
The web UI includes a visual batch processing queue (`utils/queue_manager.py`) for processing multiple videos:
- **Queue Management**: Add multiple YouTube URLs at once (via text input or file upload)
- **Visual Tracking**: Real-time status updates with color-coded badges (Pending, Processing, Completed, Failed)
- **Queue Operations**: Reorder items (move up/down), remove items, retry failed items
- **Persistent Storage**: Queue state saved to JSON (`./outputs/.queue/queue.json`)
- **Batch Processing**: Process entire queue with progress bar and live status updates
- **Category Assignment**: Apply same category to all videos in a batch
- **Statistics Dashboard**: View counts of total, pending, processing, completed, and failed items

Queue item states:
- ⏳ **Pending**: Waiting to be processed
- 🔄 **Processing**: Currently being analyzed
- ✅ **Completed**: Successfully processed with output path
- ❌ **Failed**: Processing failed with error message (can be retried)

### PDF Export Feature
The web UI includes a dedicated PDF export feature (`utils/pdf_generator.py`) that converts markdown summaries to professionally styled PDFs:
- **Drag-and-drop interface**: Upload markdown files directly in the "PDF Export" tab
- **Professional styling**: Clean typography with system fonts, proper heading hierarchy, and optimized spacing
- **Customization options**: Choose page size (Letter/A4), font size, and metadata inclusion
- **WeasyPrint-based**: Uses WeasyPrint for excellent CSS support and quality output
- **Automatic formatting**: Preserves markdown features like code blocks, tables, and lists
- **Export management**: View and re-download recent exports from the UI

Generated PDFs include:
- Styled metadata header with video information
- Page numbers and headers
- Professional document formatting optimized for printing
- Saved to `./outputs/pdf_exports/` directory

### Error Handling
Implements exponential backoff retry logic (`utils/retry.py`) with specific handlers for:
- Network errors
- API rate limits
- Temporary API failures
- GPT-5 specific issues (empty responses, JSON formatting)
- Automatic JSON trailing comma fixes for GPT-5 output
- Enhanced retry logic for GPT-5 (5 attempts with longer delays)

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