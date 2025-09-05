"""Transcript chunking utilities."""
from typing import List

from ..core.models import TranscriptLine


def chunk_transcript(lines: List[TranscriptLine], max_chars: int = 4000) -> List[List[TranscriptLine]]:
    """
    Split transcript lines into chunks based on character count.
    
    Preserves order and timestamps while keeping chunks under max_chars.
    """
    chunks: List[List[TranscriptLine]] = []
    current_chunk: List[TranscriptLine] = []
    current_length = 0
    
    for line in lines:
        line_length = len(line.text) + 1  # +1 for space separator
        
        # Start new chunk if adding this line would exceed max_chars
        if current_chunk and current_length + line_length > max_chars:
            chunks.append(current_chunk)
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def join_transcript_lines(lines: List[TranscriptLine]) -> str:
    """Join transcript lines into a single text string."""
    return " ".join(line.text.strip() for line in lines if line.text.strip())


def add_timestamps_to_chunk(lines: List[TranscriptLine]) -> str:
    """Join transcript lines and add timestamp prefix for context."""
    if not lines:
        return ""
    
    text = join_transcript_lines(lines)
    start_time = format_timestamp(lines[0].start)
    return f"[chunk_start={start_time}] {text}"


def format_timestamp(seconds: float) -> str:
    """Format seconds as mm:ss timestamp."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"