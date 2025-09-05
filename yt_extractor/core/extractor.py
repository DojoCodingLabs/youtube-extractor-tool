"""Main YouTube extractor class."""
import tempfile
from pathlib import Path
from typing import List, Optional

import yt_dlp
from rich.console import Console
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

from ..core.config import config
from ..core.exceptions import TranscriptUnavailableError, VideoNotFoundError
from ..core.models import TranscriptLine, VideoMeta
from ..llm.processor import LLMProcessor
from ..utils.formatting import ensure_output_dir, safe_filename, wrap_with_front_matter
from ..utils.cache import cache
from ..utils.retry import network_retry
from .recovery import SafeProcessor

console = Console()


class YouTubeExtractor:
    """Main class for extracting value from YouTube videos."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.llm_processor = LLMProcessor()
    
    def process_video(self, url: str, output_dir: Optional[str] = None) -> Path:
        """
        Process a single YouTube video and save the result with recovery support.
        
        Returns the path to the generated markdown file.
        """
        # Extract video ID for recovery tracking
        video_id = self._extract_video_id(url)
        safe_processor = SafeProcessor(video_id)
        
        try:
            # Get metadata with recovery support
            meta = safe_processor.safe_execute(
                "metadata", 
                self.fetch_metadata, 
                url
            )
            safe_processor.recovery.save_metadata(meta)
            
            # Get transcript with recovery support
            transcript = safe_processor.safe_execute(
                "transcript",
                self.fetch_transcript,
                meta.id
            )
            safe_processor.recovery.save_transcript(transcript)
            
            # Process with LLM with recovery support
            markdown_body = safe_processor.safe_execute(
                "llm_processing",
                self.llm_processor.process_video,
                meta,
                transcript
            )
            
            # Wrap with front matter
            full_markdown = wrap_with_front_matter(
                markdown_body, 
                meta, 
                config.report_timezone
            )
            
            # Save to file
            output_path = ensure_output_dir(output_dir or config.default_output_dir)
            filename = safe_filename(meta)
            file_path = output_path / filename
            
            file_path.write_text(full_markdown, encoding="utf-8")
            console.print(f"[green]✅ Saved to: {file_path}[/green]")
            
            # Mark as successfully completed
            safe_processor.cleanup()
            
            return file_path
            
        except Exception as e:
            console.print(f"[red]❌ Processing failed for {url}: {e}[/red]")
            # Don't cleanup on failure - keep state for potential recovery
            raise
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        import re
        
        # Common YouTube URL patterns
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Fallback: use a hash of the URL if no ID found
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:11]
    
    def process_videos(self, urls: List[str], output_dir: Optional[str] = None) -> List[Path]:
        """
        Process multiple YouTube videos.
        
        Returns list of paths to generated markdown files.
        """
        results = []
        errors = []
        
        for url in urls:
            try:
                result = self.process_video(url, output_dir)
                results.append(result)
            except Exception as e:
                console.print(f"[red]❌ Failed on {url}: {e}[/red]")
                errors.append((url, str(e)))
        
        if errors:
            console.print("\n[yellow]Some URLs failed:[/yellow]")
            for url, error in errors:
                console.print(f"[red]- {url}: {error}[/red]")
        
        return results
    
    @network_retry
    def fetch_metadata(self, url: str) -> VideoMeta:
        """Fetch video metadata using yt-dlp."""
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            return VideoMeta(
                id=info.get("id"),
                url=url,
                title=info.get("title") or "Untitled",
                channel=info.get("uploader") or info.get("channel") or "Unknown",
                duration_sec=int(info.get("duration") or 0),
                published_at=info.get("upload_date") or "",
                language=info.get("language"),
                tags=info.get("tags") or [],
            )
        except Exception as e:
            raise VideoNotFoundError(f"Failed to fetch metadata for {url}: {e}")
    
    def fetch_transcript(
        self, 
        video_id: str, 
        lang_priority: Optional[List[str]] = None
    ) -> List[TranscriptLine]:
        """
        Fetch transcript using YouTube API with Whisper fallback.
        
        Args:
            video_id: YouTube video ID
            lang_priority: Preferred language codes (e.g., ["en", "es"])
        
        Returns:
            List of transcript lines with timing
        """
        if lang_priority is None:
            lang_priority = ["en", "es"]
        
        # Check cache first
        cached_transcript = cache.get_transcript(video_id)
        if cached_transcript:
            console.print("[dim]Using cached transcript[/dim]")
            return cached_transcript
        
        # Try YouTube's official transcript API first
        try:
            api = YouTubeTranscriptApi()
            
            # Try to fetch transcript in preferred languages
            for lang_code in lang_priority:
                try:
                    console.print(f"[dim]Trying language: {lang_code}[/dim]")
                    transcript_data = api.fetch(video_id, languages=[lang_code])
                    
                    transcript_lines = [
                        TranscriptLine(
                            start=segment.start,
                            duration=segment.duration,
                            text=segment.text
                        )
                        for segment in transcript_data
                    ]
                    
                    console.print(f"[green]✅ Found transcript in {lang_code} with {len(transcript_lines)} segments[/green]")
                    # Cache the transcript
                    cache.set_transcript(video_id, transcript_lines)
                    return transcript_lines
                    
                except Exception as e:
                    console.print(f"[dim]Failed for {lang_code}: {e}[/dim]")
                    continue
            
            # Try with default language (auto-detect)
            try:
                console.print("[dim]Trying with auto-detected language[/dim]")
                transcript_data = api.fetch(video_id)
                
                transcript_lines = [
                    TranscriptLine(
                        start=segment.start,
                        duration=segment.duration,
                        text=segment.text
                    )
                    for segment in transcript_data
                ]
                
                console.print(f"[green]✅ Found transcript with auto-detection: {len(transcript_lines)} segments[/green]")
                # Cache the transcript
                cache.set_transcript(video_id, transcript_lines)
                return transcript_lines
                
            except Exception as e:
                console.print(f"[yellow]Auto-detection also failed: {e}[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]YouTube transcript API failed: {e}[/yellow]")
        
        # Try Whisper fallback
        try:
            transcript_lines = self._whisper_fallback_transcribe(
                f"https://www.youtube.com/watch?v={video_id}",
                lang_priority
            )
            # Cache the transcript
            cache.set_transcript(video_id, transcript_lines)
            return transcript_lines
        except Exception as e:
            raise TranscriptUnavailableError(
                f"No transcript available via YouTube API, and Whisper fallback failed: {e}. "
                "Install 'faster-whisper' and ffmpeg to enable local transcription."
            )
    
    def _whisper_fallback_transcribe(
        self, 
        video_url: str, 
        lang_priority: Optional[List[str]] = None
    ) -> List[TranscriptLine]:
        """Download audio and transcribe via faster-whisper."""
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ImportError as e:
            raise TranscriptUnavailableError(
                "Whisper fallback requires 'faster-whisper'. "
                "Install it and ffmpeg to enable local transcription."
            ) from e
        
        # Download audio to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            outtmpl = str(Path(tmpdir) / "%(id)s.%(ext)s")
            ydl_opts = {
                "quiet": True,
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                audio_path = Path(tmpdir) / f"{info['id']}.mp3"
            
            # Initialize Whisper model
            model = WhisperModel(
                config.whisper_model,
                device=config.whisper_device,
                compute_type=config.whisper_compute_type
            )
            
            # Transcribe
            language = lang_priority[0] if lang_priority else None
            segments, _info = model.transcribe(
                str(audio_path),
                language=language,
                vad_filter=True
            )
            
            # Convert to TranscriptLine objects
            lines = []
            for segment in segments:
                start = float(getattr(segment, "start", 0.0))
                end = float(getattr(segment, "end", start))
                text = (getattr(segment, "text", "") or "").strip()
                
                if text:
                    duration = max(0.0, end - start)
                    lines.append(TranscriptLine(start=start, duration=duration, text=text))
            
            if not lines:
                raise TranscriptUnavailableError("Whisper produced no segments")
            
            return lines