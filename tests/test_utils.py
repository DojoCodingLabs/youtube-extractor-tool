"""Tests for utility functions."""

import pytest
from yt_extractor.core.models import VideoMeta, TranscriptLine
from yt_extractor.utils.formatting import format_time, safe_filename
from yt_extractor.utils.transcript import join_transcript_lines


def test_format_time():
    """Test time formatting utility."""
    assert format_time(65.5) == "01:05"
    assert format_time(125.8) == "02:05"
    assert format_time(30) == "00:30"


def test_safe_filename():
    """Test safe filename generation."""
    meta = VideoMeta(
        id="abc123",
        url="https://youtube.com/watch?v=abc123",
        title="How to Build Amazing Apps!",
        channel="Tech Channel",
        duration_sec=600,
        published_at="20240315",
        language="en",
        tags=["tech", "programming"]
    )
    
    filename = safe_filename(meta)
    assert filename.startswith("20240315--abc123--")
    assert filename.endswith(".md")
    assert "how-to-build-amazing-apps" in filename



def test_join_transcript_lines():
    """Test joining transcript lines."""
    lines = [
        TranscriptLine(0.0, 2.0, "Hello"),
        TranscriptLine(2.0, 2.0, "world"),
        TranscriptLine(4.0, 2.0, "test"),
    ]
    
    joined = join_transcript_lines(lines)
    assert joined == "Hello world test"