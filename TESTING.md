# Testing Guide for YouTube Extractor Tool

This guide covers how to set up and run comprehensive tests for the YouTube extractor tool.

## 🚀 Quick Start Testing

### 1. Run Test Setup Validation
```bash
python test_setup.py
```

This will check your environment and dependencies.

### 2. Set Up Configuration
```bash
# Copy test environment template
cp .env.test .env

# Edit .env with your API keys
nano .env  # or your preferred editor
```

### 3. Configure Test Videos
```bash
# Edit tests/test_videos.json with real YouTube URLs
nano tests/test_videos.json
```

Replace the example URLs with real YouTube video URLs for testing.

## 🧪 Test Levels

### Level 1: Unit Tests (No API Keys Required)
```bash
# Run basic unit tests
pytest tests/test_models.py tests/test_utils.py -v

# Run error recovery tests  
pytest tests/test_error_recovery.py -v

# Run all unit tests
pytest -v -m "not slow and not integration"
```

**What this tests:**
- Data model functionality
- Utility functions
- Error recovery mechanisms
- Retry logic
- Cache operations (mocked)

### Level 2: Integration Tests (API Keys Required)
```bash
# Run integration tests (requires API keys)
pytest tests/test_integration.py -v

# Skip slow tests
pytest tests/test_integration.py -v -m "not slow"
```

**What this tests:**
- Real API connectivity
- End-to-end video processing
- Configuration validation
- CLI integration
- Error recovery with real failures

### Level 3: Performance Tests (API Keys + Time)
```bash
# Run performance tests (slow)
pytest tests/test_integration.py::TestPerformanceAndScaling -v
```

**What this tests:**
- Concurrent video processing
- Memory usage with large transcripts
- Performance under load

## 🔧 Test Configuration

### Environment Variables
```bash
# Required for integration tests
export OPENAI_API_KEY="sk-..."     # OpenAI API key
# OR
export ANTHROPIC_API_KEY="..."     # Anthropic API key  
# OR
export LLM_MODEL="ollama/llama3.2:3b"  # Local Ollama model

# Test-specific settings
export ENABLE_CACHE=true
export DEFAULT_OUTPUT_DIR=./test_output
export DEFAULT_CHUNK_CHARS=2000    # Smaller for faster tests
```

### Test Videos Configuration
Edit `tests/test_videos.json`:

```json
{
  "test_videos": {
    "short_tech": {
      "url": "https://www.youtube.com/watch?v=REAL_VIDEO_ID",
      "description": "Short technical video with clear transcript",
      "expected_duration": "< 5 minutes"
    }
  }
}
```

**Recommended test videos:**
- **Short (2-5 min)**: Technical tutorial, clear audio
- **Medium (10-20 min)**: Educational content, structured
- **Long (30+ min)**: Conference talk, presentation
- **No transcript**: Video without captions (for Whisper testing)

## 🎯 Test Scenarios

### Scenario 1: Basic Functionality
```bash
# Test configuration
python main.py config check

# Test video info (no processing)
python main.py info "https://www.youtube.com/watch?v=VIDEO_ID"

# Test processing
python main.py process "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir ./test_output
```

### Scenario 2: Error Recovery
```bash
# Test with invalid URL (should fail gracefully)
python main.py process "https://www.youtube.com/watch?v=INVALID"

# Test with network issues (disconnect internet mid-process)
python main.py process "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Scenario 3: Batch Processing
```bash
# Create test batch file
echo "https://www.youtube.com/watch?v=VIDEO_ID_1" > test_videos.txt
echo "https://www.youtube.com/watch?v=VIDEO_ID_2" >> test_videos.txt

# Test batch processing
python main.py batch test_videos.txt --output-dir ./test_output
```

### Scenario 4: Cache Testing
```bash
# Process same video twice (should use cache second time)
python main.py process "https://www.youtube.com/watch?v=VIDEO_ID" --verbose

# Check cache stats
python main.py cache stats

# Clear cache
python main.py cache clear
```

## 🔍 Test Validation

### Output Validation
After processing, check that outputs contain:

```bash
# Check file was created
ls test_output/

# Validate content structure
grep -E "^## (TL;DR|Key Takeaways)" test_output/*.md

# Check front matter
head -20 test_output/*.md | grep -E "(type: |video_id: |title: )"

# Validate timestamps
grep -E "\[t=[0-9]{2}:[0-9]{2}\]" test_output/*.md
```

### Expected Output Structure
```markdown
---
type: "video-notes"
video_id: "VIDEO_ID"
title: "Video Title"
---

# Video Title
- Channel: Channel Name
- Duration: 15:30

## TL;DR
Summary paragraph

## Key Takeaways  
- Point with timestamp [t=05:30]
- Another point [t=12:15]

## Frameworks & Models
**Framework Name** — steps listed

## Chapters
05:30 Chapter Title
```

## 🚨 Common Issues

### Issue: "Configuration error: OPENAI_API_KEY required"
**Solution:** Set up API keys in `.env` file
```bash
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
echo "LLM_MODEL=gpt-4o-mini" >> .env
```

### Issue: "No module named 'faster_whisper'"
**Solution:** Install Whisper dependencies (optional)
```bash
pip install faster-whisper soundfile
# Also need: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)
```

### Issue: "Rate limit exceeded" 
**Solution:** 
- Use smaller chunk sizes: `DEFAULT_CHUNK_CHARS=1000`
- Add delays between requests
- Check API quota/billing

### Issue: Tests timing out
**Solution:**
- Use shorter test videos
- Reduce chunk sizes for testing
- Run with `-x` flag to stop on first failure

## 📊 Test Coverage

### Current Test Coverage
```bash
# Run tests with coverage
pytest --cov=yt_extractor --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Matrix
| Component | Unit Tests | Integration Tests | Performance Tests |
|-----------|------------|-------------------|-------------------|
| Core Models | ✅ | ✅ | ✅ |
| Utilities | ✅ | ✅ | ✅ |
| Error Recovery | ✅ | ✅ | ⚠️ |
| LLM Processing | ⚠️ | ✅ | ⚠️ |
| CLI Interface | ⚠️ | ✅ | ❌ |
| Caching | ✅ | ✅ | ❌ |

Legend: ✅ Complete, ⚠️ Partial, ❌ Missing

## 🎯 Testing Checklist

Before release:
- [ ] All unit tests pass
- [ ] Integration tests pass with real API keys
- [ ] CLI commands work correctly
- [ ] Error recovery works with real failures  
- [ ] Caching works correctly
- [ ] Multiple video formats tested
- [ ] Performance acceptable for typical use
- [ ] Documentation is accurate

## 🔄 Continuous Testing

### GitHub Actions (Future)
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/test_models.py tests/test_utils.py
      # Note: Integration tests would need API keys in secrets
```

### Local Pre-commit Hook
```bash
# Install pre-commit hook
echo "pytest tests/test_models.py tests/test_utils.py" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This ensures basic tests pass before each commit.