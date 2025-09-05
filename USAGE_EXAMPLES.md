# Usage Examples & Best Practices

This guide provides comprehensive examples and best practices for using the YouTube Value Extractor effectively.

## Quick Start Examples

### Single Video Processing

```bash
# Basic usage with default settings
python -m yt_extractor.cli process "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# With custom output directory
python -m yt_extractor.cli process "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output-dir ./my-insights

# With verbose output to see progress details
python -m yt_extractor.cli process "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --verbose
```

### Multiple Videos

```bash
# Process multiple videos at once
python -m yt_extractor.cli process \
  "https://www.youtube.com/watch?v=video1" \
  "https://www.youtube.com/watch?v=video2" \
  "https://www.youtube.com/watch?v=video3"
```

### Batch Processing

Create a file `videos.txt` with one URL per line:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=jNQXAC9IVRw  
https://www.youtube.com/watch?v=9bZkp7q19f0
```

Then process all videos:
```bash
# Basic batch processing
python -m yt_extractor.cli batch videos.txt

# With custom concurrency (careful with rate limits)
python -m yt_extractor.cli batch videos.txt --concurrent 2

# Batch processing with custom output
python -m yt_extractor.cli batch videos.txt --output-dir ./batch-insights --verbose
```

## Advanced Use Cases

### Content Creators & Educators

**Scenario**: Analyzing competitor content for insights and trends.

```bash
# Create a list of competitor videos
cat > competitor_analysis.txt << EOF
https://www.youtube.com/watch?v=competitor1
https://www.youtube.com/watch?v=competitor2
https://www.youtube.com/watch?v=competitor3
EOF

# Process with organized output
python -m yt_extractor.cli batch competitor_analysis.txt \
  --output-dir ./competitor-insights \
  --concurrent 2 \
  --verbose
```

**Best Practices**:
- Use descriptive output directory names
- Process competitor videos monthly for trend analysis
- Keep concurrency low to respect API limits

### Business & Strategy Teams

**Scenario**: Extracting insights from conference talks and business content.

```bash
# Process high-value business content
python -m yt_extractor.cli process \
  "https://www.youtube.com/watch?v=business-talk" \
  --output-dir ./business-insights

# Check video info first to ensure it's worth processing
python -m yt_extractor.cli info "https://www.youtube.com/watch?v=business-talk"
```

**Best Practices**:
- Always check video duration and topic relevance first
- Use higher-quality models (`gpt-4o`) for complex business content
- Organize outputs by category (./insights/business/, ./insights/tech/, etc.)

### Researchers & Students

**Scenario**: Processing educational content and lectures.

```bash
# Process lecture series
cat > course_lectures.txt << EOF
https://www.youtube.com/watch?v=lecture1
https://www.youtube.com/watch?v=lecture2
https://www.youtube.com/watch?v=lecture3
EOF

# Process with academic-friendly settings
python -m yt_extractor.cli batch course_lectures.txt \
  --output-dir ./course-notes \
  --concurrent 1 \
  --verbose
```

**Best Practices**:
- Process one video at a time for complex academic content
- Use specific output directories for each course
- Enable verbose mode to track processing progress

### Technical Teams

**Scenario**: Processing technical tutorials and documentation.

```bash
# Process technical content with local model for privacy
export LLM_MODEL=ollama/llama3.1:8b
python -m yt_extractor.cli process \
  "https://www.youtube.com/watch?v=tech-tutorial" \
  --output-dir ./tech-docs
```

**Best Practices**:
- Consider local models for proprietary content
- Use consistent naming conventions for technical documentation
- Enable caching for frequently re-processed content

## Configuration Examples

### High-Volume Processing Setup

```env
# .env for batch processing
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-key-here
DEFAULT_OUTPUT_DIR=./batch-processing
ENABLE_CACHE=true
CACHE_DIR=./.cache
MAX_CONCURRENT_VIDEOS=3
```

### Quality-Focused Setup

```env
# .env for detailed analysis
LLM_MODEL=gpt-4o
OPENAI_API_KEY=your-key-here
DEFAULT_OUTPUT_DIR=./premium-insights
ENABLE_CACHE=true
MAX_CONCURRENT_VIDEOS=1
REPORT_TZ=America/New_York
```

### Privacy-First Setup

```env
# .env for local processing
LLM_MODEL=ollama/llama3.1:8b
DEFAULT_OUTPUT_DIR=./private-analysis
ENABLE_CACHE=false
MAX_CONCURRENT_VIDEOS=1
```

## Cache Management

### Understanding Cache Behavior

```bash
# Check cache status and size
python -m yt_extractor.cli cache stats

# Example output:
# Cache Status: Enabled
# Total Items: 45
# Disk Usage: 12.3 MB
# Cache Directory: /path/to/.cache
```

### Cache Best Practices

```bash
# Clear cache when changing models or prompts
python -m yt_extractor.cli cache clear

# Monitor cache size in production environments
python -m yt_extractor.cli cache stats | grep "Disk Usage"
```

## Error Handling & Recovery

### Common Scenarios

**Scenario**: Processing fails due to network issues
```bash
# The tool automatically retries with exponential backoff
# Check verbose output to see retry attempts
python -m yt_extractor.cli process VIDEO_URL --verbose
```

**Scenario**: Partial batch processing failure
```bash
# Individual video failures don't stop batch processing
# Check the output directory to see which videos completed
python -m yt_extractor.cli batch videos.txt --verbose
ls -la ./output-dir/
```

### Recovery Strategies

1. **State Persistence**: The tool saves progress between stages
2. **Selective Retry**: Only failed videos need reprocessing
3. **Cache Benefits**: Completed transcripts and analyses are cached

## Output Organization Patterns

### By Date
```bash
TODAY=$(date +%Y-%m-%d)
python -m yt_extractor.cli process VIDEO_URL --output-dir "./insights/${TODAY}"
```

### By Category
```bash
# Business content
python -m yt_extractor.cli process BUSINESS_URL --output-dir ./insights/business

# Technical content
python -m yt_extractor.cli process TECH_URL --output-dir ./insights/technical

# Educational content  
python -m yt_extractor.cli process EDU_URL --output-dir ./insights/education
```

### By Source
```bash
# Conference talks
python -m yt_extractor.cli batch conference_talks.txt --output-dir ./insights/conferences

# Podcast episodes
python -m yt_extractor.cli batch podcasts.txt --output-dir ./insights/podcasts
```

## Performance Optimization

### Model Selection Guide

| Content Type | Recommended Model | Reasoning |
|--------------|------------------|-----------|
| Business/Strategy | `gpt-4o` | Complex concepts need higher quality |
| Technical Tutorials | `gpt-4o-mini` | Good balance of speed and accuracy |
| Educational Content | `claude-3-5-sonnet-latest` | Excellent at structured explanations |
| General Content | `gpt-4o-mini` | Cost-effective for most use cases |

### Batch Processing Optimization

```bash
# For large batches, use lower concurrency to avoid rate limits
python -m yt_extractor.cli batch large_list.txt --concurrent 1 --verbose

# For smaller batches with reliable internet, increase concurrency
python -m yt_extractor.cli batch small_list.txt --concurrent 5
```

## Integration Examples

### Shell Script for Regular Processing

```bash
#!/bin/bash
# daily_insights.sh

# Set date for organization
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="./daily-insights/${DATE}"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Process today's important videos
python -m yt_extractor.cli batch todays_videos.txt \
  --output-dir "${OUTPUT_DIR}" \
  --verbose

# Show results
echo "Processed videos saved to: ${OUTPUT_DIR}"
ls -la "${OUTPUT_DIR}"
```

### Python Script Integration

```python
#!/usr/bin/env python3
"""Example Python integration"""

import subprocess
import sys
from pathlib import Path

def process_video(url, output_dir="./insights"):
    """Process a single video and return output path"""
    
    cmd = [
        sys.executable, "-m", "yt_extractor.cli", 
        "process", url, 
        "--output-dir", output_dir
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Successfully processed: {url}")
        return True
    else:
        print(f"❌ Failed to process: {url}")
        print(f"Error: {result.stderr}")
        return False

# Example usage
if __name__ == "__main__":
    videos = [
        "https://www.youtube.com/watch?v=example1",
        "https://www.youtube.com/watch?v=example2"
    ]
    
    for video in videos:
        process_video(video, "./batch-output")
```

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: "ConfigurationError: OPENAI_API_KEY required"
```bash
# Solution: Set your API key
export OPENAI_API_KEY=sk-your-key-here
# Or add to .env file
```

**Issue**: "Video has no transcript available"
```bash
# Solution: Enable Whisper fallback or skip video
pip install faster-whisper soundfile
```

**Issue**: Rate limit errors
```bash
# Solution: Reduce concurrency and add delays
python -m yt_extractor.cli batch videos.txt --concurrent 1
```

**Issue**: Out of memory errors
```bash
# Solution: Use smaller model or reduce concurrent videos
export LLM_MODEL=gpt-4o-mini
export MAX_CONCURRENT_VIDEOS=1
```

### Debug Mode

```bash
# Enable maximum verbosity for debugging
python -m yt_extractor.cli process VIDEO_URL --verbose

# Check configuration
python -m yt_extractor.cli config check
```

## Best Practices Summary

### Do's ✅
- Always check video info before processing long content
- Use caching for repeated processing
- Organize outputs with descriptive directory names
- Start with lower concurrency and increase gradually
- Monitor API usage and costs
- Use appropriate models for content complexity

### Don'ts ❌
- Don't process extremely long videos (>2 hours) without checking first
- Don't use high concurrency with rate-limited APIs
- Don't disable caching unless you have specific privacy requirements
- Don't ignore configuration validation errors
- Don't process copyrighted content without permission

### Performance Tips 🚀
- Enable caching for repeated analysis
- Use `gpt-4o-mini` for most content types
- Batch similar content together
- Monitor and clear cache periodically
- Use local models for sensitive content
- Set appropriate timezone for timestamps