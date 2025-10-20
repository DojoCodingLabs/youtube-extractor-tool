# Changelog

All notable changes to the YouTube Extractor Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Batch Queue System** - Visual queue for processing multiple videos in sequence
  - New "Batch Queue" tab in web UI for queue management
  - Add multiple URLs via text input or file upload
  - Real-time status tracking with color-coded badges (Pending, Processing, Completed, Failed)
  - Queue operations: reorder items (move up/down), remove items, retry failed items
  - Persistent queue storage in JSON (`./outputs/.queue/queue.json`)
  - Statistics dashboard showing total, pending, processing, completed, and failed counts
  - Progress bar and live status updates during processing
  - Comprehensive documentation in `docs/BATCH_QUEUE.md`
  - Test script for verification (`test_queue_manager.py`)
  - Programmatic API via `yt_extractor.utils.queue_manager.ProcessingQueue`

- **PDF Export Feature** - Convert markdown summaries to professionally formatted PDFs
  - New "PDF Export" tab in web UI with drag-and-drop interface
  - Customizable export options (page size, font size, metadata inclusion)
  - Professional styling with clean typography and proper formatting
  - Recent exports list with re-download capability
  - Comprehensive documentation in `docs/PDF_EXPORT.md`
  - Test script for verification (`test_pdf_generation.py`)
  - Programmatic API via `yt_extractor.utils.pdf_generator.PDFGenerator`

### Changed
- Web UI refactored into 3-tab interface (Process Videos | Batch Queue | PDF Export)
- Updated dependencies to include WeasyPrint, markdown2, and Streamlit

### Dependencies
- Added `weasyprint>=60.0` for PDF generation
- Added `markdown2>=2.4.0` for markdown to HTML conversion
- Added `streamlit>=1.28.0` for web UI

### Documentation
- Added `docs/BATCH_QUEUE.md` - Batch queue user guide and API reference
- Added `docs/PDF_EXPORT.md` - Complete PDF export user guide
- Added `docs/PDF_EXPORT_QUICKSTART.md` - PDF export quick start guide
- Added `PDF_EXPORT_SUMMARY.md` - PDF export implementation summary
- Updated `CLAUDE.md` with batch queue and PDF export architecture notes

## [1.0.0] - 2025-XX-XX

### Added
- Initial release of YouTube Extractor Tool
- Video processing with GPT-5 analysis
- Markdown summary generation
- CLI interface with multiple commands
- Web UI for easy video processing
- Caching system for transcripts and LLM responses
- Support for multiple LLM providers (OpenAI, Anthropic, Ollama)
- Recovery system for resumable processing
- Category-based organization

### Features
- Extract metadata from YouTube videos
- Download transcripts via YouTube Transcript API
- Full-context LLM analysis (no chunking)
- Structured markdown output with YAML frontmatter
- Executive summaries, key insights, and frameworks
- Batch processing support
- Configuration management
- Cache statistics and management

### Documentation
- README with setup instructions
- CLAUDE.md for development guidance
- Comprehensive inline documentation
