"""Tests for utility functions."""

import pytest
from yt_extractor.core.models import VideoMeta, TranscriptLine
from yt_extractor.utils.formatting import format_time, safe_filename
from yt_extractor.utils.chunking import chunk_transcript, join_transcript_lines


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


def test_chunk_transcript():
    """Test transcript chunking."""
    lines = [
        TranscriptLine(0.0, 2.0, "First sentence."),
        TranscriptLine(2.0, 2.0, "Second sentence."),
        TranscriptLine(4.0, 2.0, "Third sentence."),
        TranscriptLine(6.0, 2.0, "Fourth sentence."),
    ]
    
    chunks = chunk_transcript(lines, max_chars=30)
    
    # Should create multiple chunks due to character limit
    assert len(chunks) >= 2
    
    # All lines should be preserved
    total_lines = sum(len(chunk) for chunk in chunks)
    assert total_lines == len(lines)


def test_join_transcript_lines():
    """Test joining transcript lines."""
    lines = [
        TranscriptLine(0.0, 2.0, "Hello"),
        TranscriptLine(2.0, 2.0, "world"),
        TranscriptLine(4.0, 2.0, "test"),
    ]
    
    joined = join_transcript_lines(lines)
    assert joined == "Hello world test"