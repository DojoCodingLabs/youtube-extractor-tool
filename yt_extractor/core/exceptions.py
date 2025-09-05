"""Custom exceptions for YouTube extraction."""


class YouTubeExtractorError(Exception):
    """Base exception for YouTube extractor errors."""
    pass


class VideoNotFoundError(YouTubeExtractorError):
    """Raised when a video cannot be found or accessed."""
    pass


class TranscriptUnavailableError(YouTubeExtractorError):
    """Raised when transcript is not available for a video."""
    pass


class LLMProcessingError(YouTubeExtractorError):
    """Raised when LLM processing fails."""
    pass


class ConfigurationError(YouTubeExtractorError):
    """Raised when there's a configuration error."""
    pass


class CacheError(YouTubeExtractorError):
    """Raised when cache operations fail."""
    pass