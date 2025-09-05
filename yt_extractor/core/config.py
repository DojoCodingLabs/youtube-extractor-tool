"""Configuration management for the YouTube extractor."""
import os
from pathlib import Path
from typing import Optional

from ..core.exceptions import ConfigurationError


class Config:
    """Configuration manager with environment variable support."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize config, optionally loading from .env file."""
        if env_file and Path(env_file).exists():
            self._load_env_file(env_file)
    
    @property
    def llm_model(self) -> str:
        """LLM model to use."""
        return os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API key."""
        return os.getenv("OPENAI_API_KEY")
    
    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Anthropic API key."""
        return os.getenv("ANTHROPIC_API_KEY")
    
    @property
    def whisper_model(self) -> str:
        """Whisper model for fallback transcription."""
        return os.getenv("WHISPER_MODEL", "base")
    
    @property
    def whisper_device(self) -> str:
        """Whisper device (auto, cuda, cpu)."""
        return os.getenv("WHISPER_DEVICE", "auto")
    
    @property
    def whisper_compute_type(self) -> str:
        """Whisper compute type."""
        return os.getenv("WHISPER_COMPUTE_TYPE", "float16")
    
    @property
    def report_timezone(self) -> str:
        """Timezone for report timestamps."""
        return os.getenv("REPORT_TZ", "America/Costa_Rica")
    
    @property
    def default_output_dir(self) -> str:
        """Default output directory for notes."""
        return os.getenv("DEFAULT_OUTPUT_DIR", "./notes")
    
    @property
    def enable_cache(self) -> bool:
        """Whether caching is enabled."""
        return os.getenv("ENABLE_CACHE", "true").lower() in ("true", "1", "yes")
    
    @property
    def cache_dir(self) -> str:
        """Cache directory."""
        return os.getenv("CACHE_DIR", "./.cache")
    
    @property
    def default_chunk_chars(self) -> int:
        """Default characters per chunk."""
        try:
            return int(os.getenv("DEFAULT_CHUNK_CHARS", "4000"))
        except ValueError:
            return 4000
    
    @property
    def max_concurrent_videos(self) -> int:
        """Maximum number of videos to process concurrently."""
        try:
            return int(os.getenv("MAX_CONCURRENT_VIDEOS", "3"))
        except ValueError:
            return 3
    
    def validate(self) -> None:
        """Validate configuration."""
        model = self.llm_model.lower()
        
        # Check for required API keys based on model
        if "gpt" in model or "openai" in model:
            if not self.openai_api_key:
                raise ConfigurationError("OPENAI_API_KEY required for OpenAI models")
        elif "claude" in model or "anthropic" in model:
            if not self.anthropic_api_key:
                raise ConfigurationError("ANTHROPIC_API_KEY required for Anthropic models")
        elif not model.startswith("ollama/"):
            raise ConfigurationError(f"Unsupported model: {self.llm_model}")
    
    def _load_env_file(self, env_file: str) -> None:
        """Load environment variables from .env file."""
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
        except Exception as e:
            raise ConfigurationError(f"Failed to load {env_file}: {e}")


# Global config instance
config = Config()