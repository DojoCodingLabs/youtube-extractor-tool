# Batch Process

Process multiple videos from a file

## Usage
```bash
source venv/bin/activate && python -m yt_extractor.cli batch "$1" --category "$2"
```

## Parameters
- `$1`: Path to file containing URLs (one per line)
- `$2`: Optional category for all videos

## Example
```
/batch-process "video_urls.txt" "Business/Marketing"
```