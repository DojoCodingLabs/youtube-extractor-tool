"""Caching utilities for transcripts and LLM responses."""
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import diskcache

from ..core.config import config
from ..core.exceptions import CacheError
from ..core.models import TranscriptLine


class Cache:
    """Disk-based cache for transcripts and LLM responses."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache."""
        self.enabled = config.enable_cache
        self.cache_dir = Path(cache_dir or config.cache_dir)
        
        if self.enabled:
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self._cache = diskcache.Cache(str(self.cache_dir))
            except Exception as e:
                raise CacheError(f"Failed to initialize cache: {e}")
        else:
            self._cache = None
    
    def get_transcript(self, video_id: str) -> Optional[List[TranscriptLine]]:
        """Get cached transcript for video ID."""
        if not self.enabled or not self._cache:
            return None
        
        try:
            key = f"transcript:{video_id}"
            cached_data = self._cache.get(key)
            
            if cached_data:
                # Convert back to TranscriptLine objects
                return [
                    TranscriptLine(
                        start=item["start"],
                        duration=item["duration"],
                        text=item["text"]
                    )
                    for item in cached_data
                ]
            return None
        except Exception:
            return None
    
    def set_transcript(self, video_id: str, transcript: List[TranscriptLine], ttl: int = 86400 * 7) -> None:
        """Cache transcript for video ID (default 7 days)."""
        if not self.enabled or not self._cache:
            return
        
        try:
            key = f"transcript:{video_id}"
            # Convert to serializable format
            data = [
                {
                    "start": line.start,
                    "duration": line.duration,
                    "text": line.text
                }
                for line in transcript
            ]
            self._cache.set(key, data, expire=ttl)
        except Exception:
            pass  # Silently fail on cache errors
    
    def get_llm_response(self, prompt_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached LLM response for prompt hash."""
        if not self.enabled or not self._cache:
            return None
        
        try:
            key = f"llm:{prompt_hash}"
            return self._cache.get(key)
        except Exception:
            return None
    
    def set_llm_response(
        self, 
        prompt_hash: str, 
        response: Dict[str, Any], 
        ttl: int = 86400 * 30
    ) -> None:
        """Cache LLM response (default 30 days)."""
        if not self.enabled or not self._cache:
            return
        
        try:
            key = f"llm:{prompt_hash}"
            self._cache.set(key, response, expire=ttl)
        except Exception:
            pass  # Silently fail on cache errors
    
    def hash_prompt(self, system_prompt: str, user_prompt: str, model: str) -> str:
        """Generate hash for prompt caching."""
        content = f"{system_prompt}||{user_prompt}||{model}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def clear(self) -> None:
        """Clear all cached data."""
        if not self.enabled or not self._cache:
            return
        
        try:
            self._cache.clear()
        except Exception as e:
            raise CacheError(f"Failed to clear cache: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.enabled or not self._cache:
            return {"enabled": False}
        
        try:
            return {
                "enabled": True,
                "size": len(self._cache),
                "disk_usage": self._cache.volume(),
                "cache_dir": str(self.cache_dir)
            }
        except Exception:
            return {"enabled": True, "error": "Failed to get stats"}
    
    def close(self) -> None:
        """Close cache connection."""
        if self._cache:
            try:
                self._cache.close()
            except Exception:
                pass


# Global cache instance
cache = Cache()