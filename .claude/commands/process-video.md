# Process Video

Process a YouTube video with optional category

## Usage
```bash
source venv/bin/activate && python -m yt_extractor.cli process "$1" --category "$2"
```

## Parameters
- `$1`: YouTube URL to process
- `$2`: Optional category (e.g., "AI/Agents", "Business/Marketing")

## Example
```
/process-video "https://www.youtube.com/watch?v=abc123" "AI/Agents"
```