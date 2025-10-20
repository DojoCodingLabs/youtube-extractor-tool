# Batch Queue Feature

The YouTube Extractor Tool includes a powerful batch processing queue system that allows you to process multiple videos in sequence with visual progress tracking and queue management.

## Features

### 📋 Queue Management
- Add multiple YouTube URLs at once (text input or file upload)
- Visual queue display with status tracking
- Reorder queue items (move up/down)
- Remove individual items or clear by status
- Retry failed items
- Duplicate URL detection

### 🎨 Visual Interface
- Color-coded status badges:
  - ⏳ **Pending** (Orange): Waiting to be processed
  - 🔄 **Processing** (Blue): Currently being analyzed
  - ✅ **Completed** (Green): Successfully processed
  - ❌ **Failed** (Red): Processing error occurred

### 📊 Real-Time Progress
- Live status updates as videos process
- Progress bar showing overall completion
- Statistics dashboard (Total, Pending, Processing, Completed, Failed)
- Individual item progress tracking

### 💾 Persistent State
- Queue automatically saved to disk
- Resume processing after page refresh or restart
- Queue history preserved
- Saved to `./outputs/.queue/queue.json`

## Usage

### Via Web UI (Recommended)

1. **Start the Web UI**
   ```bash
   source venv/bin/activate
   streamlit run web_ui.py
   ```

2. **Navigate to Batch Queue Tab**
   - Click on the "📋 Batch Queue" tab

3. **Add URLs to Queue**

   **Option A: Paste URLs Directly**
   - Paste YouTube URLs in the text area (one per line)
   - Select a category (optional)
   - Click "➕ Add to Queue"

   **Option B: Upload Text File**
   - Create a .txt file with one URL per line:
     ```
     https://www.youtube.com/watch?v=VIDEO_ID_1
     https://www.youtube.com/watch?v=VIDEO_ID_2
     https://www.youtube.com/watch?v=VIDEO_ID_3
     # This is a comment (lines starting with # are ignored)
     https://www.youtube.com/watch?v=VIDEO_ID_4
     ```
   - Upload the file
   - Select a category
   - Click "➕ Add to Queue"

4. **Manage Queue**
   - **Reorder**: Use 🔼/🔽 buttons to change processing order
   - **Remove**: Click 🗑️ to remove pending items
   - **Retry**: Click 🔄 Retry on failed items to try again

5. **Process Queue**
   - Click "▶️ Process Queue" to start
   - Watch progress in real-time
   - Processing runs sequentially (one video at a time)

6. **Clean Up**
   - Click "🗑️ Clear Completed" to remove successful items
   - Click "🗑️ Clear Failed" to remove failed items

## Example Workflows

### Workflow 1: Process Research Papers Playlist
```
1. Copy all URLs from a YouTube playlist
2. Paste into Batch Queue text area
3. Set category to "Research/AI"
4. Add to queue
5. Review queue (videos appear with metadata)
6. Click "Process Queue"
7. Go grab coffee ☕ while it processes
8. Return to find all summaries in outputs/Research/AI/
```

### Workflow 2: Process URLs from File
```bash
# Create urls.txt
cat > urls.txt << EOF
https://www.youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=def456
https://www.youtube.com/watch?v=ghi789
EOF

# In web UI:
# 1. Go to Batch Queue tab
# 2. Upload urls.txt
# 3. Select category
# 4. Add to queue
# 5. Process queue
```

### Workflow 3: Resume Interrupted Processing
```
# If processing was interrupted (page refresh, crash, etc.)
1. Reopen web UI
2. Go to Batch Queue tab
3. Queue automatically loads from disk
4. Failed items show error messages
5. Click "Process Queue" to continue
6. Or retry individual failed items
```

## Technical Details

### Queue Storage
- Location: `./outputs/.queue/queue.json`
- Format: JSON with queue items array
- Auto-saves after every operation
- Thread-safe for concurrent access

### Queue Item Structure
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "category": "AI/Agents",
  "status": "pending",
  "title": "Video Title",
  "channel": "Channel Name",
  "error": null,
  "output_path": null,
  "added_at": "2025-10-20T12:00:00",
  "processed_at": null,
  "id": "abc12345"
}
```

### Processing Logic
1. Get all pending items from queue
2. For each item:
   - Update status to "processing"
   - Fetch metadata if not available
   - Call `YouTubeExtractor.process_video()`
   - Update status to "completed" or "failed"
   - Save queue state
3. Show final statistics

### Error Handling
- Failed items remain in queue with error message
- Processing continues to next item after failure
- Failed items can be retried individually
- Queue state always preserved

## Programmatic Usage

You can use the queue manager programmatically:

```python
from pathlib import Path
from yt_extractor.utils.queue_manager import ProcessingQueue, QueueStatus
from yt_extractor.core.extractor import YouTubeExtractor

# Initialize queue
queue = ProcessingQueue()

# Add URLs
urls = [
    "https://www.youtube.com/watch?v=abc123",
    "https://www.youtube.com/watch?v=def456",
]
queue.add_multiple(urls, category="AI/Agents")

# Process queue
extractor = YouTubeExtractor()

def process_func(url, category):
    return extractor.process_video(url, category=category)

results = queue.process_queue(
    process_func=process_func,
    stop_on_error=False,  # Continue processing on errors
)

print(f"Completed: {len(results['completed'])}")
print(f"Failed: {len(results['failed'])}")
```

### Custom Progress Callback
```python
def on_progress(item, current, total):
    print(f"Processing {current}/{total}: {item.url}")

results = queue.process_queue(
    process_func=process_func,
    on_progress=on_progress,
)
```

## Queue Management API

### Adding Items
```python
# Add single URL
item = queue.add("https://www.youtube.com/...", category="AI")

# Add multiple URLs
items = queue.add_multiple(urls, category="AI")
```

### Retrieving Items
```python
# Get all items
all_items = queue.get_all()

# Get by status
pending = queue.get_by_status(QueueStatus.PENDING)
completed = queue.get_by_status(QueueStatus.COMPLETED)
failed = queue.get_by_status(QueueStatus.FAILED)

# Get by ID
item = queue.get_by_id("abc12345")
```

### Updating Items
```python
# Update status
queue.update_status(
    item_id="abc12345",
    status=QueueStatus.COMPLETED,
    output_path="/path/to/output.md"
)

# Update metadata
queue.update_metadata(
    item_id="abc12345",
    title="Video Title",
    channel="Channel Name"
)
```

### Organizing Items
```python
# Move items
queue.move_up("abc12345")    # Move up in queue
queue.move_down("abc12345")  # Move down in queue

# Remove items
queue.remove("abc12345")

# Clear by status
queue.clear(status_filter=QueueStatus.COMPLETED)
queue.clear(status_filter=QueueStatus.FAILED)

# Clear all
queue.clear()
```

### Statistics
```python
stats = queue.get_stats()
# Returns:
# {
#     "total": 10,
#     "pending": 3,
#     "processing": 1,
#     "completed": 5,
#     "failed": 1
# }
```

## Tips & Best Practices

### Performance
- **Sequential Processing**: Queue processes one video at a time to respect API limits
- **GPT-5 Compatible**: Works with GPT-5's longer processing times
- **Cache-Aware**: Leverages existing transcript and LLM caches

### Organization
- Use consistent category naming (e.g., "AI/Agents", "Business/Marketing")
- Add descriptive comments in URL files (lines starting with #)
- Clear completed items periodically to keep queue manageable

### Error Recovery
- Failed items can be retried after fixing issues (API keys, network, etc.)
- Queue persists across sessions - safe to close and reopen
- Error messages help diagnose issues

### Batch Size
- No hard limit on queue size
- Recommended: 10-50 videos per batch for manageability
- Process overnight for large batches

## Troubleshooting

### Queue Not Loading
- Check `./outputs/.queue/queue.json` exists
- Verify JSON is valid (use `cat outputs/.queue/queue.json | python -m json.tool`)
- Delete queue file to start fresh if corrupted

### Processing Stuck
- Check for API key issues (`python -m yt_extractor.cli config check`)
- Verify network connectivity
- Look at error messages in failed items
- Try processing a single video first

### Duplicate URLs Not Detected
- Duplicates only detected for non-failed items
- Failed items can be re-added
- URLs are compared exactly (must match character-for-character)

### Queue Cleared Unexpectedly
- Check for file system issues
- Verify `outputs/.queue/` directory permissions
- Review app logs for errors

## Future Enhancements

Potential improvements (not yet implemented):
- [ ] Concurrent processing (2-3 videos simultaneously)
- [ ] Priority levels for queue items
- [ ] Scheduled processing (cron-like)
- [ ] Email notifications on completion
- [ ] Export queue as CSV/JSON
- [ ] Import queue from CSV/JSON
- [ ] Queue templates (save/load common batches)
- [ ] Automatic playlist URL expansion
- [ ] Filter/search queue items

## Support

For issues or questions:
1. Check this documentation
2. Review `CLAUDE.md` for architecture details
3. Run test script: `python test_queue_manager.py`
4. Open an issue on GitHub with:
   - Queue JSON contents (if applicable)
   - Error messages
   - Steps to reproduce
