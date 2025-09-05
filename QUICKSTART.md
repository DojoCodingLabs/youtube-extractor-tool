# Quick Start Guide

Get up and running with the YouTube Value Extractor in under 5 minutes.

## 1. Install

```bash
git clone https://github.com/yourusername/youtube-extractor-tool.git
cd youtube-extractor-tool
pip install -e .
```

## 2. Configure

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your OpenAI API key:
# LLM_MODEL=gpt-4o-mini
# OPENAI_API_KEY=sk-your-openai-key-here
```

## 3. Run

```bash
# Process a video
python -m yt_extractor.cli process "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"

# Results will be saved to ./outputs/
```

## 4. Example Output

Your analysis will include:
- **Executive Summary**: 2-3 comprehensive paragraphs
- **Key Insights**: Detailed analysis paragraphs (not bullet points)  
- **Frameworks**: Step-by-step actionable methods
- **Timestamps**: Key moments for navigation

## Need Help?

- **Configuration**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Examples**: See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **Issues**: Check configuration with `python -m yt_extractor.cli config check`

## Common Issues

**"Missing API Key"**: Add your OpenAI API key to `.env`
**"No transcript found"**: Install Whisper support: `pip install -e ".[whisper]"`
**"Rate limit"**: Use `--concurrent 1` for batch processing