"""Tests for data models."""

import pytest
from yt_extractor.core.models import VideoMeta, TranscriptLine, ExtractedContent


def test_video_meta_duration_formatting():
    """Test duration formatting in VideoMeta."""
    # Test short duration (under 1 hour)
    meta = VideoMeta(
        id="test123", url="https://test.com", title="Test", 
        channel="TestChannel", duration_sec=125, published_at="20240101",
        language="en", tags=["test"]
    )
    assert meta.duration_formatted == "02:05"
    
    # Test long duration (over 1 hour)
    meta_long = VideoMeta(
        id="test456", url="https://test.com", title="Test", 
        channel="TestChannel", duration_sec=3725, published_at="20240101",
        language="en", tags=["test"]
    )
    assert meta_long.duration_formatted == "01:02:05"


def test_transcript_line():
    """Test TranscriptLine model."""
    line = TranscriptLine(start=10.5, duration=3.2, text="Hello world")
    assert line.end == 13.7
    assert line.text == "Hello world"


def test_extracted_content_merge():
    """Test merging ExtractedContent objects."""
    content1 = ExtractedContent(
        bullets=["Point 1", "Point 2"],
        frameworks=[{"name": "Framework A", "steps": ["Step 1"]}]
    )
    
    content2 = ExtractedContent(
        bullets=["Point 3"],
        frameworks=[{"name": "Framework B", "steps": ["Step 2"]}]
    )
    
    merged = content1.merge_with(content2)
    assert len(merged.bullets) == 3
    assert len(merged.frameworks) == 2
    assert "Point 1" in merged.bullets
    assert "Point 3" in merged.bullets