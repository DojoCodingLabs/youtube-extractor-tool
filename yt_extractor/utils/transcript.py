"""Transcript processing utilities."""
from typing import List

from ..core.models import TranscriptLine


def join_transcript_lines(lines: List[TranscriptLine]) -> str:
    """Join transcript lines into a single text string."""
    return " ".join(line.text.strip() for line in lines if line.text.strip())