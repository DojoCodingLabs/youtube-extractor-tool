"""Test configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = Mock()
    config.llm_model = "gpt-4o-mini"
    config.enable_cache = False
    config.default_chunk_chars = 1000
    config.report_timezone = "UTC"
    config.default_output_dir = "./test_notes"
    return config


@pytest.fixture
def sample_video_meta():
    """Sample video metadata for testing."""
    from yt_extractor.core.models import VideoMeta
    return VideoMeta(
        id="test123",
        url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        channel="Test Channel",
        duration_sec=300,
        published_at="20240315",
        language="en",
        tags=["test", "example"]
    )


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing."""
    from yt_extractor.core.models import TranscriptLine
    return [
        TranscriptLine(0.0, 5.0, "Welcome to this test video."),
        TranscriptLine(5.0, 5.0, "Today we'll learn about testing."),
        TranscriptLine(10.0, 5.0, "This is important for quality code."),
        TranscriptLine(15.0, 5.0, "Let's start with the basics."),
    ]


@pytest.fixture(autouse=True)
def mock_env():
    """Set up test environment variables."""
    os.environ.setdefault("LLM_MODEL", "gpt-4o-mini")
    os.environ.setdefault("ENABLE_CACHE", "false")
    os.environ.setdefault("DEFAULT_OUTPUT_DIR", "./test_notes")