"""Core functionality for YouTube extraction."""

from .models import VideoMeta, TranscriptLine
from .extractor import YouTubeExtractor
from .recovery import RecoveryManager, SafeProcessor
from .exceptions import YouTubeExtractorError, TranscriptUnavailableError, VideoNotFoundError

__all__ = [
    "VideoMeta", "TranscriptLine", "YouTubeExtractor",
    "RecoveryManager", "SafeProcessor",
    "YouTubeExtractorError", "TranscriptUnavailableError", "VideoNotFoundError"
]