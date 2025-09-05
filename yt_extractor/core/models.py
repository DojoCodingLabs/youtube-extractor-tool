"""Data models for YouTube extraction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VideoMeta:
    """Video metadata from YouTube."""
    id: str
    url: str
    title: str
    channel: str
    duration_sec: int
    published_at: str  # ISO date or YYYYMMDD from yt-dlp
    language: Optional[str]
    tags: List[str]

    @property
    def duration_formatted(self) -> str:
        """Format duration as HH:MM:SS or MM:SS."""
        hours, remainder = divmod(self.duration_sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"


@dataclass
class TranscriptLine:
    """A single line of transcript with timing."""
    start: float
    duration: float
    text: str

    @property
    def end(self) -> float:
        """End time of this transcript line."""
        return self.start + self.duration


@dataclass
class ExtractedContent:
    """Content extracted from video analysis."""
    bullets: List[str]
    frameworks: List[dict]
    
    def merge_with(self, other: ExtractedContent) -> ExtractedContent:
        """Merge this content with another ExtractedContent."""
        return ExtractedContent(
            bullets=self.bullets + other.bullets,
            frameworks=self.frameworks + other.frameworks
        )