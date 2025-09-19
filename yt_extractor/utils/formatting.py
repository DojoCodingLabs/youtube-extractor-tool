"""Formatting utilities."""
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, Optional

from slugify import slugify

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore

from ..core.models import VideoMeta


def format_time(seconds: float) -> str:
    """Format seconds as mm:ss."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def safe_filename(meta: VideoMeta) -> str:
    """Generate a safe filename from video metadata."""
    title_slug = slugify(meta.title)
    return f"{meta.published_at or 'undated'}--{meta.id}--{title_slug}.md"


def wrap_with_front_matter(md_body: str, meta: VideoMeta, tz: str, category: Optional[str] = None) -> str:
    """Wrap markdown content with YAML front matter."""
    zone = ZoneInfo(tz) if ZoneInfo else None
    now = dt.datetime.now(zone) if zone else dt.datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    
    front_matter = {
        "type": "video-notes",
        "source": "youtube",
        "url": meta.url,
        "video_id": meta.id,
        "title": meta.title,
        "channel": meta.channel,
        "published": meta.published_at,
        "created": date_str,
        "tags": meta.tags,
    }

    if category:
        front_matter["category"] = category
    
    front = "---\n"
    front += "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in front_matter.items())
    front += "\n---\n\n"
    
    return front + md_body.strip() + "\n"


def ensure_output_dir(output_dir: str) -> Path:
    """Ensure output directory exists and return Path object."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path