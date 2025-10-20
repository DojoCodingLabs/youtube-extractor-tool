"""Queue management for batch video processing."""

import json
import logging
import re
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

# Module constants
QUEUE_ITEM_ID_LENGTH = 8
MAX_FILE_SAVE_RETRIES = 3
YOUTUBE_URL_PATTERN = re.compile(
    r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+.*$'
)

# Configure logging
logger = logging.getLogger(__name__)


class QueueStatus(str, Enum):
    """Status of queue items."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueueItem:
    """Represents a single item in the processing queue."""
    url: str
    category: Optional[str] = None
    status: QueueStatus = QueueStatus.PENDING
    title: Optional[str] = None
    channel: Optional[str] = None
    error: Optional[str] = None
    output_path: Optional[str] = None
    added_at: str = None
    processed_at: Optional[str] = None
    id: Optional[str] = None

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.added_at is None:
            self.added_at = datetime.now().isoformat()
        if self.id is None:
            import hashlib
            self.id = hashlib.md5(f"{self.url}{self.added_at}".encode()).hexdigest()[:QUEUE_ITEM_ID_LENGTH]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["status"] = self.status.value if isinstance(self.status, QueueStatus) else self.status
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueueItem":
        """Create from dictionary."""
        # Convert status string to enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = QueueStatus(data["status"])
        return cls(**data)


def _validate_youtube_url(url: str) -> bool:
    """
    Validate YouTube URL format.

    Args:
        url: URL string to validate

    Returns:
        True if valid YouTube URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    return bool(YOUTUBE_URL_PATTERN.match(url.strip()))


def _sanitize_category(category: Optional[str]) -> Optional[str]:
    """
    Sanitize category string.

    Args:
        category: Category string to sanitize

    Returns:
        Sanitized category or None if empty/invalid

    Raises:
        ValueError: If category contains dangerous characters
    """
    if not category or not isinstance(category, str):
        return None

    # Strip whitespace
    category = category.strip()
    if not category:
        return None

    # Check for path traversal attempts
    if '..' in category or '\\' in category or '\0' in category:
        raise ValueError(f"Invalid category: contains dangerous characters")

    return category


class ProcessingQueue:
    """Manages a queue of videos to be processed."""

    def __init__(self, queue_dir: Path = None, max_size: int = 1000):
        """
        Initialize the processing queue.

        Args:
            queue_dir: Directory to store queue state (default: outputs/.queue)
            max_size: Maximum number of items allowed in queue (default: 1000)
        """
        self.queue_dir = queue_dir or Path("outputs/.queue")
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = self.queue_dir / "queue.json"
        self.max_size = max_size

        self._items: List[QueueItem] = []
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        """Load queue from disk."""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "r") as f:
                    data = json.load(f)
                    self._items = [QueueItem.from_dict(item) for item in data.get("items", [])]
                logger.info(f"Loaded {len(self._items)} items from queue")
            except Exception as e:
                logger.warning(f"Failed to load queue: {e}")
                self._items = []

    def _save(self):
        """Save queue to disk with retry logic and atomic writes."""
        import time

        for attempt in range(MAX_FILE_SAVE_RETRIES):
            try:
                data = {
                    "items": [item.to_dict() for item in self._items],
                    "updated_at": datetime.now().isoformat(),
                }

                # Write to temp file first (atomic operation)
                temp_file = self.queue_file.with_suffix('.tmp')
                with open(temp_file, "w") as f:
                    json.dump(data, f, indent=2)

                # Atomic rename
                temp_file.replace(self.queue_file)
                logger.debug(f"Queue saved successfully ({len(self._items)} items)")
                return

            except Exception as e:
                logger.warning(f"Failed to save queue (attempt {attempt + 1}/{MAX_FILE_SAVE_RETRIES}): {e}")
                if attempt < MAX_FILE_SAVE_RETRIES - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Failed to save queue after {MAX_FILE_SAVE_RETRIES} attempts")
                    raise IOError(f"Could not save queue: {e}")

    def add(self, url: str, category: Optional[str] = None, title: Optional[str] = None,
            channel: Optional[str] = None) -> QueueItem:
        """
        Add a URL to the queue with validation.

        Args:
            url: YouTube video URL
            category: Category for organizing the video
            title: Optional video title (will be fetched if not provided)
            channel: Optional channel name

        Returns:
            The created QueueItem

        Raises:
            ValueError: If URL is invalid, already in queue, or queue is full
        """
        # Validate URL
        url = url.strip() if isinstance(url, str) else ""
        if not _validate_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")

        # Sanitize category
        category = _sanitize_category(category)

        with self._lock:
            # Check queue size limit
            if len(self._items) >= self.max_size:
                raise ValueError(f"Queue is full (maximum {self.max_size} items)")

            # Check for duplicates
            if any(item.url == url and item.status != QueueStatus.FAILED for item in self._items):
                raise ValueError(f"URL already in queue: {url}")

            item = QueueItem(url=url, category=category, title=title, channel=channel)
            self._items.append(item)
            self._save()
            logger.info(f"Added item to queue: {url} (category: {category})")
            return item

    def add_multiple(self, urls: List[str], category: Optional[str] = None) -> List[QueueItem]:
        """
        Add multiple URLs to the queue.

        Args:
            urls: List of YouTube video URLs
            category: Category for all videos

        Returns:
            List of created QueueItems
        """
        items = []
        for url in urls:
            url = url.strip()
            if not url or url.startswith("#"):  # Skip empty lines and comments
                continue
            try:
                item = self.add(url, category=category)
                items.append(item)
            except ValueError:
                # Skip duplicates
                continue
        return items

    def remove(self, item_id: str) -> bool:
        """
        Remove an item from the queue.

        Args:
            item_id: ID of the item to remove

        Returns:
            True if item was removed, False if not found
        """
        with self._lock:
            original_len = len(self._items)
            self._items = [item for item in self._items if item.id != item_id]
            removed = len(self._items) < original_len
            if removed:
                self._save()
            return removed

    def clear(self, status_filter: Optional[QueueStatus] = None):
        """
        Clear the queue.

        Args:
            status_filter: If provided, only remove items with this status
        """
        with self._lock:
            if status_filter:
                self._items = [item for item in self._items if item.status != status_filter]
            else:
                self._items = []
            self._save()

    def get_all(self) -> List[QueueItem]:
        """Get all items in the queue."""
        with self._lock:
            return self._items.copy()

    def get_by_status(self, status: QueueStatus) -> List[QueueItem]:
        """Get items with a specific status."""
        with self._lock:
            return [item for item in self._items if item.status == status]

    def get_by_id(self, item_id: str) -> Optional[QueueItem]:
        """Get an item by ID."""
        with self._lock:
            for item in self._items:
                if item.id == item_id:
                    return item
            return None

    def update_status(self, item_id: str, status: QueueStatus,
                     error: Optional[str] = None,
                     output_path: Optional[str] = None):
        """
        Update the status of a queue item.

        Args:
            item_id: ID of the item to update
            status: New status
            error: Error message if status is FAILED
            output_path: Path to generated file if status is COMPLETED
        """
        with self._lock:
            for item in self._items:
                if item.id == item_id:
                    item.status = status
                    if error:
                        item.error = error
                    if output_path:
                        item.output_path = output_path
                    if status in (QueueStatus.COMPLETED, QueueStatus.FAILED):
                        item.processed_at = datetime.now().isoformat()
                    self._save()
                    return
            raise ValueError(f"Item not found: {item_id}")

    def update_metadata(self, item_id: str, title: Optional[str] = None,
                       channel: Optional[str] = None):
        """
        Update metadata for a queue item.

        Args:
            item_id: ID of the item to update
            title: Video title
            channel: Channel name
        """
        with self._lock:
            for item in self._items:
                if item.id == item_id:
                    if title:
                        item.title = title
                    if channel:
                        item.channel = channel
                    self._save()
                    return

    def move_up(self, item_id: str) -> bool:
        """
        Move an item up in the queue.

        Args:
            item_id: ID of the item to move

        Returns:
            True if moved, False if already at top or not found
        """
        with self._lock:
            for i, item in enumerate(self._items):
                if item.id == item_id and i > 0:
                    self._items[i], self._items[i-1] = self._items[i-1], self._items[i]
                    self._save()
                    return True
            return False

    def move_down(self, item_id: str) -> bool:
        """
        Move an item down in the queue.

        Args:
            item_id: ID of the item to move

        Returns:
            True if moved, False if already at bottom or not found
        """
        with self._lock:
            for i, item in enumerate(self._items):
                if item.id == item_id and i < len(self._items) - 1:
                    self._items[i], self._items[i+1] = self._items[i+1], self._items[i]
                    self._save()
                    return True
            return False

    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        with self._lock:
            return {
                "total": len(self._items),
                "pending": sum(1 for item in self._items if item.status == QueueStatus.PENDING),
                "processing": sum(1 for item in self._items if item.status == QueueStatus.PROCESSING),
                "completed": sum(1 for item in self._items if item.status == QueueStatus.COMPLETED),
                "failed": sum(1 for item in self._items if item.status == QueueStatus.FAILED),
            }

    def get_next_pending(self) -> Optional[QueueItem]:
        """Get the next pending item in the queue."""
        with self._lock:
            for item in self._items:
                if item.status == QueueStatus.PENDING:
                    return item
            return None

    def process_queue(self,
                     process_func: Callable[[str, Optional[str]], Path],
                     on_progress: Optional[Callable[[QueueItem, int, int], None]] = None,
                     stop_on_error: bool = False) -> Dict[str, List[QueueItem]]:
        """
        Process all pending items in the queue.

        Args:
            process_func: Function to process each URL (url, category) -> output_path
            on_progress: Optional callback for progress updates (item, current, total)
            stop_on_error: Whether to stop processing on first error

        Returns:
            Dict with 'completed' and 'failed' lists of QueueItems
        """
        pending_items = self.get_by_status(QueueStatus.PENDING)
        total = len(pending_items)
        completed = []
        failed = []

        for i, item in enumerate(pending_items, 1):
            try:
                # Update status to processing
                self.update_status(item.id, QueueStatus.PROCESSING)

                # Callback for progress
                if on_progress:
                    on_progress(item, i, total)

                # Process the video
                output_path = process_func(item.url, item.category)

                # Update status to completed
                self.update_status(item.id, QueueStatus.COMPLETED, output_path=str(output_path))
                completed.append(item)

            except Exception as e:
                error_msg = str(e)
                self.update_status(item.id, QueueStatus.FAILED, error=error_msg)
                failed.append(item)

                if stop_on_error:
                    break

        return {
            "completed": completed,
            "failed": failed,
        }
