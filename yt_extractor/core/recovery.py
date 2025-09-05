"""Recovery mechanisms for partial processing failures."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from .exceptions import YouTubeExtractorError
from .models import TranscriptLine, VideoMeta

console = Console()


class ProcessingState:
    """Tracks processing state for recovery purposes."""
    
    def __init__(self, video_id: str, state_dir: Optional[str] = None):
        """Initialize processing state."""
        self.video_id = video_id
        self.state_dir = Path(state_dir or ".processing_state")
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / f"{video_id}.json"
    
    def save_state(self, step: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """Save current processing state."""
        try:
            state = {
                "video_id": self.video_id,
                "step": step,
                "data": data,
                "metadata": metadata or {},
                "timestamp": str(Path().stat().st_mtime)
            }
            
            self.state_file.write_text(json.dumps(state, default=str, indent=2))
            console.print(f"[dim]Saved state: {step}[/dim]")
            
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to save state: {e}[/yellow]")
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load saved processing state."""
        if not self.state_file.exists():
            return None
        
        try:
            content = self.state_file.read_text()
            state = json.loads(content)
            console.print(f"[blue]Found saved state: {state.get('step', 'unknown')}[/blue]")
            return state
            
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load state: {e}[/yellow]")
            return None
    
    def clear_state(self) -> None:
        """Clear processing state after successful completion."""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
        except Exception:
            pass  # Ignore cleanup errors


class RecoveryManager:
    """Manages recovery from partial processing failures."""
    
    def __init__(self, video_id: str):
        """Initialize recovery manager."""
        self.video_id = video_id
        self.state = ProcessingState(video_id)
        self.recovered_data = {}
    
    def can_recover_from(self, step: str) -> bool:
        """Check if we can recover from a specific processing step."""
        saved_state = self.state.load_state()
        if not saved_state:
            return False
        
        recovery_steps = [
            "metadata_fetched",
            "transcript_fetched", 
            "chunks_processed",
            "content_extracted",
            "markdown_generated"
        ]
        
        saved_step = saved_state.get("step")
        return saved_step in recovery_steps and recovery_steps.index(saved_step) >= recovery_steps.index(step)
    
    def recover_metadata(self) -> Optional[VideoMeta]:
        """Recover video metadata from saved state."""
        saved_state = self.state.load_state()
        if not saved_state:
            return None
        
        # Check if we can recover from current step
        if not self.can_recover_from("metadata_fetched"):
            return None
        
        try:
            # For metadata_fetched step, data is the metadata directly
            if saved_state.get("step") == "metadata_fetched":
                data = saved_state["data"]
                return VideoMeta(**data)
            
            # For later steps, check metadata in the saved state
            metadata = saved_state.get("metadata", {})
            if "video_meta" in metadata:
                return VideoMeta(**metadata["video_meta"])
            
            return None
            
        except Exception as e:
            console.print(f"[yellow]Failed to recover metadata: {e}[/yellow]")
            return None
    
    def recover_transcript(self) -> Optional[List[TranscriptLine]]:
        """Recover transcript from saved state."""
        saved_state = self.state.load_state()
        if not saved_state or saved_state.get("step") not in ["transcript_fetched", "chunks_processed"]:
            return None
        
        try:
            data = saved_state["data"]
            if saved_state.get("step") == "transcript_fetched":
                return [TranscriptLine(**item) for item in data]
            else:
                # For chunks_processed, we need to extract transcript from metadata
                metadata = saved_state.get("metadata", {})
                transcript_data = metadata.get("original_transcript", [])
                return [TranscriptLine(**item) for item in transcript_data]
                
        except Exception as e:
            console.print(f"[yellow]Failed to recover transcript: {e}[/yellow]")
            return None
    
    def recover_extracted_content(self) -> Optional[Dict[str, Any]]:
        """Recover extracted content from saved state."""
        saved_state = self.state.load_state()
        if not saved_state or saved_state.get("step") != "content_extracted":
            return None
        
        try:
            return saved_state["data"]
        except Exception as e:
            console.print(f"[yellow]Failed to recover extracted content: {e}[/yellow]")
            return None
    
    def save_metadata(self, metadata: VideoMeta) -> None:
        """Save metadata for recovery."""
        self.state.save_state(
            step="metadata_fetched",
            data=metadata.__dict__
        )
    
    def save_transcript(self, transcript: List[TranscriptLine]) -> None:
        """Save transcript for recovery."""
        transcript_data = [
            {
                "start": line.start,
                "duration": line.duration, 
                "text": line.text
            }
            for line in transcript
        ]
        
        # Preserve existing metadata from previous steps
        existing_metadata = {}
        saved_state = self.state.load_state()
        if saved_state and saved_state.get("step") == "metadata_fetched":
            existing_metadata["video_meta"] = saved_state["data"]
        
        self.state.save_state(
            step="transcript_fetched",
            data=transcript_data,
            metadata=existing_metadata
        )
    
    def save_chunks_processed(self, chunks: List[List[TranscriptLine]], partials: List[Dict[str, Any]]) -> None:
        """Save chunk processing results for recovery."""
        # Save the partials with original transcript in metadata for full recovery
        transcript_data = []
        for chunk_list in chunks:
            transcript_data.extend([
                {
                    "start": line.start,
                    "duration": line.duration,
                    "text": line.text
                }
                for line in chunk_list
            ])
        
        self.state.save_state(
            step="chunks_processed",
            data=partials,
            metadata={"original_transcript": transcript_data}
        )
    
    def save_extracted_content(self, content: Dict[str, Any]) -> None:
        """Save extracted content for recovery."""
        # Preserve existing metadata from previous steps
        existing_metadata = {}
        saved_state = self.state.load_state()
        if saved_state:
            if saved_state.get("step") == "metadata_fetched":
                existing_metadata["video_meta"] = saved_state["data"]
            elif saved_state.get("step") in ["transcript_fetched", "chunks_processed"]:
                existing_metadata = saved_state.get("metadata", {})
        
        self.state.save_state(
            step="content_extracted", 
            data=content,
            metadata=existing_metadata
        )
    
    def complete_processing(self) -> None:
        """Mark processing as complete and cleanup."""
        console.print("[green]✅ Processing completed successfully[/green]")
        self.state.clear_state()


class SafeProcessor:
    """Wrapper for safe processing with automatic recovery."""
    
    def __init__(self, video_id: str):
        """Initialize safe processor."""
        self.video_id = video_id
        self.recovery = RecoveryManager(video_id)
    
    def safe_execute(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Execute an operation safely with recovery support.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: Function to execute
            *args, **kwargs: Arguments for the operation
        
        Returns:
            Result of the operation
        """
        try:
            console.print(f"[blue]Executing: {operation_name}[/blue]")
            result = operation_func(*args, **kwargs)
            console.print(f"[green]✅ {operation_name} completed[/green]")
            return result
            
        except Exception as e:
            console.print(f"[red]❌ {operation_name} failed: {e}[/red]")
            
            # Check if we can provide partial results
            if hasattr(self.recovery, f"recover_{operation_name.lower()}"):
                console.print(f"[yellow]Attempting recovery for {operation_name}...[/yellow]")
                recovery_func = getattr(self.recovery, f"recover_{operation_name.lower()}")
                recovered = recovery_func()
                
                if recovered is not None:
                    console.print(f"[green]✅ Recovered {operation_name} from saved state[/green]")
                    return recovered
            
            # If no recovery possible, re-raise the exception
            raise YouTubeExtractorError(f"{operation_name} failed and recovery not possible: {e}")
    
    def cleanup(self):
        """Cleanup processing state."""
        self.recovery.complete_processing()