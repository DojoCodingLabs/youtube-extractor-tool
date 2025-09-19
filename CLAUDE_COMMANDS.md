# Claude Commands for YouTube Extractor Tool

This file contains predefined commands that Claude Code can execute to automate common tasks in the YouTube extractor project.

## Quick Reference

### Core Video Processing
- `/process-video url=<URL> category=<CATEGORY>` - Process single video
- `/batch-process file=<FILE> category=<CATEGORY>` - Process multiple videos
- `/start-ui` - Launch web interface

### Development & Testing
- `/test-cli` - Test CLI functionality
- `/run-tests` - Run all tests with coverage
- `/type-check` - Run type checking
- `/lint-code` - Format and lint code

### File Management
- `/list-categories` - Show all categories
- `/count-videos` - Count videos by category
- `/find-video query=<SEARCH>` - Search video content
- `/backup-outputs` - Create backup

### Analytics
- `/video-stats` - Show processing statistics
- `/category-breakdown` - Videos per category
- `/recent-videos count=<N>` - Show recent videos

### Setup & Maintenance
- `/install-deps` - Install dependencies
- `/check-config` - Validate configuration
- `/clear-cache` - Clear all caches

## Usage Examples

### Process a YouTube video
```
/process-video "https://www.youtube.com/watch?v=abc123" "AI/Agents"
```

### Process multiple videos from a file
```
/batch-process "video_urls.txt" "Business/Marketing"
```

### Search for videos about a topic
```
/find-video "machine learning"
```

### Show recent activity
```
/recent-videos 5
```

### Backup your work
```
/backup-outputs
```

## Command Structure

Commands use space-separated parameters:
- `/command-name` - Simple commands with no parameters
- `/command-name "param1"` - Commands with single parameter
- `/command-name "param1" "param2"` - Commands with multiple parameters

Parameters are parsed as `$1`, `$2`, etc. in bash scripts. Use quotes for parameters with spaces.

## Available Parameters

### Common Parameters
- `$1` - Primary parameter (URL, file path, search term, etc.)
- `$2` - Secondary parameter (category, count, etc.)
- `$3` - Additional parameters as needed

### Parameter Examples
- **URL**: "https://www.youtube.com/watch?v=abc123"
- **Category**: "AI/Agents", "Business/Marketing", "Crypto/DeFi"
- **File path**: "video_urls.txt", "test_models.py"
- **Search term**: "machine learning", "crypto"
- **Count**: 5, 10, 20
- **Commit message**: "Add categorization feature"
- **Feature name**: "video-categories", "web-ui"

## Tips

1. **Categories**: Use forward slashes for nested categories like "AI/Agents" or "Business/Marketing"

2. **Batch Processing**: Create a text file with one YouTube URL per line for batch processing

3. **Search**: Use `/find-video` to locate videos by content or title across all categories

4. **Backup**: Run `/backup-outputs` before major changes to preserve your video collection

5. **Development**: Use `/lint-code` and `/type-check` before committing changes

## Environment Setup

These commands assume you have:
- Virtual environment at `./venv/`
- Dependencies installed via pip
- Git repository initialized
- Streamlit installed for web UI

If you need to set up the environment, run:
```
/create-venv
```

## Customization

You can modify the `.claude_commands` file to:
- Add new commands for your specific workflow
- Modify existing commands with different parameters
- Create shortcuts for frequently used operations

The commands are designed to be simple, focused, and reusable across different development scenarios.