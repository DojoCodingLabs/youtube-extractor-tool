"""
YouTube Value Extractor
======================
A tool for extracting actionable insights from YouTube videos.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core.extractor import YouTubeExtractor
from .core.models import VideoMeta, TranscriptLine

__all__ = ["YouTubeExtractor", "VideoMeta", "TranscriptLine"]