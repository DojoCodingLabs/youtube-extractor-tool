# Configuration Guide

This guide covers all configuration options for the YouTube Value Extractor.

## Environment Variables

The tool uses environment variables for configuration. You can set these in a `.env` file or export them directly.

### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_MODEL` | The LLM model to use for analysis | `gpt-4o-mini` | No |
| `OPENAI_API_KEY` | OpenAI API key (required for GPT models) | - | For OpenAI models |
| `ANTHROPIC_API_KEY` | Anthropic API key (required for Claude models) | - | For Anthropic models |

### Output Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEFAULT_OUTPUT_DIR` | Default directory for output files | `./notes` | No |
| `REPORT_TZ` | Timezone for report timestamps | `America/Costa_Rica` | No |

### Caching Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_CACHE` | Enable/disable caching | `true` | No |
| `CACHE_DIR` | Directory for cache files | `./.cache` | No |

### Processing Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MAX_CONCURRENT_VIDEOS` | Maximum concurrent video processing | `3` | No |

### Whisper Configuration (Optional)

Only needed if you want to use Whisper for fallback transcription when YouTube transcripts aren't available.

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WHISPER_MODEL` | Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) | `base` | No |
| `WHISPER_DEVICE` | Processing device (`auto`, `cuda`, `cpu`) | `auto` | No |
| `WHISPER_COMPUTE_TYPE` | Compute precision (`float16`, `float32`, `int8`) | `float16` | No |

## LLM Model Options

### OpenAI Models (Recommended)
- `gpt-4o-mini` - Fast and cost-effective (default)
- `gpt-4o` - Higher quality, more expensive
- `gpt-4-turbo` - Good balance of speed and quality
- `gpt-3.5-turbo` - Fastest, least expensive

### Anthropic Models
- `claude-3-5-sonnet-latest` - Latest Sonnet model
- `claude-3-5-haiku-latest` - Fastest Claude model
- `claude-3-opus-latest` - Highest quality Claude model

### Local Models (via Ollama)
- `ollama/llama3.1:8b` - Meta's Llama 3.1 8B
- `ollama/llama3.1:70b` - Meta's Llama 3.1 70B (requires significant RAM)
- `ollama/qwen2.5:7b` - Alibaba's Qwen 2.5 7B

## Configuration Examples

### Example 1: OpenAI with Custom Output

```env
# .env file
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-key-here
DEFAULT_OUTPUT_DIR=./video-insights
REPORT_TZ=America/New_York
ENABLE_CACHE=true
```

### Example 2: Anthropic with Whisper Fallback

```env
# .env file
LLM_MODEL=claude-3-5-sonnet-latest
ANTHROPIC_API_KEY=your-anthropic-key-here
DEFAULT_OUTPUT_DIR=./reports
WHISPER_MODEL=small
WHISPER_DEVICE=cuda
```

### Example 3: Local Ollama Setup

```env
# .env file
LLM_MODEL=ollama/llama3.1:8b
DEFAULT_OUTPUT_DIR=./local-analysis
ENABLE_CACHE=false
MAX_CONCURRENT_VIDEOS=1
```

## CLI Configuration

You can override environment variables using CLI flags:

```bash
# Override output directory
python -m yt_extractor.cli process VIDEO_URL --output-dir ./custom-output

# Use verbose mode
python -m yt_extractor.cli process VIDEO_URL --verbose

# Override concurrent processing
python -m yt_extractor.cli batch videos.txt --concurrent 5
```

## Configuration Management Commands

### Check Current Configuration

```bash
python -m yt_extractor.cli config check
```

This command will:
- Show all current configuration values
- Validate API keys
- Check model accessibility
- Verify directory permissions

### Initialize New Configuration

```bash
python -m yt_extractor.cli config init
```

This creates a new `.env` file with default values and prompts for required settings.

## Best Practices

### Performance Optimization

1. **Model Selection**: 
   - Use `gpt-4o-mini` for most use cases (fast, cost-effective)
   - Upgrade to `gpt-4o` for complex technical content
   - Consider `claude-3-5-sonnet-latest` for detailed analysis

2. **Caching**:
   - Keep caching enabled (`ENABLE_CACHE=true`)
   - Transcripts are cached for 7 days
   - LLM responses are cached for 30 days

3. **Concurrent Processing**:
   - Default `MAX_CONCURRENT_VIDEOS=3` works well
   - Increase for faster batch processing (if API limits allow)
   - Decrease for rate-limited APIs or limited resources

### Security

1. **API Keys**:
   - Never commit `.env` files to version control
   - Use environment variables in production
   - Rotate keys regularly

2. **File Permissions**:
   - Ensure output directories have appropriate permissions
   - Cache directory should be writable

### Troubleshooting

#### Common Issues

1. **Missing API Key**:
   ```
   ConfigurationError: OPENAI_API_KEY required for OpenAI models
   ```
   Solution: Set the appropriate API key for your chosen model.

2. **Model Not Available**:
   ```
   LLMProcessingError: Model gpt-5 not found
   ```
   Solution: Check model name spelling and availability.

3. **Cache Permission Error**:
   ```
   CacheError: Failed to initialize cache
   ```
   Solution: Ensure cache directory is writable or change `CACHE_DIR`.

#### Validation

Run the config check command to validate your setup:

```bash
python -m yt_extractor.cli config check
```

This will identify configuration issues and suggest fixes.