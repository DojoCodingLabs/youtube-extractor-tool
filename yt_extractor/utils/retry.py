"""Retry utilities for handling transient failures."""
import asyncio
import random
import time
from functools import wraps
from typing import Any, Callable, List, Type, TypeVar, Union

from rich.console import Console

from ..core.exceptions import YouTubeExtractorError

console = Console()

T = TypeVar('T')


class RetryError(YouTubeExtractorError):
    """Raised when all retry attempts are exhausted."""
    pass


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], tuple] = Exception
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
        exceptions: Exception types to retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed, raise the exception
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    console.print(
                        f"[yellow]Attempt {attempt + 1}/{max_attempts} failed: {e}[/yellow]"
                    )
                    console.print(f"[dim]Retrying in {delay:.1f} seconds...[/dim]")
                    
                    time.sleep(delay)
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    console.print(f"[red]Non-retryable error: {e}[/red]")
                    raise
            
            # All attempts exhausted
            console.print(f"[red]All {max_attempts} attempts failed[/red]")
            raise RetryError(f"Failed after {max_attempts} attempts: {last_exception}")
        
        return wrapper
    return decorator


async def async_retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], tuple] = Exception
):
    """
    Async decorator for retrying functions with exponential backoff.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        break
                    
                    delay = min(initial_delay * (exponential_base ** attempt), max_delay)
                    
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    console.print(
                        f"[yellow]Attempt {attempt + 1}/{max_attempts} failed: {e}[/yellow]"
                    )
                    console.print(f"[dim]Retrying in {delay:.1f} seconds...[/dim]")
                    
                    await asyncio.sleep(delay)
                except Exception as e:
                    console.print(f"[red]Non-retryable error: {e}[/red]")
                    raise
            
            console.print(f"[red]All {max_attempts} attempts failed[/red]")
            raise RetryError(f"Failed after {max_attempts} attempts: {last_exception}")
        
        return wrapper
    return decorator


def retry_on_conditions(
    conditions: List[Callable[[Exception], bool]],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0
):
    """
    Retry based on custom conditions.
    
    Args:
        conditions: List of functions that take an exception and return True if should retry
        max_attempts: Maximum retry attempts
        initial_delay: Initial delay between retries
        max_delay: Maximum delay between retries
    """
    def should_retry(exception: Exception) -> bool:
        return any(condition(exception) for condition in conditions)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1 or not should_retry(e):
                        break
                    
                    delay = min(initial_delay * (2 ** attempt), max_delay)
                    console.print(
                        f"[yellow]Retryable error on attempt {attempt + 1}: {e}[/yellow]"
                    )
                    console.print(f"[dim]Retrying in {delay:.1f} seconds...[/dim]")
                    time.sleep(delay)
            
            if should_retry(last_exception):
                raise RetryError(f"Failed after {max_attempts} attempts: {last_exception}")
            else:
                # Non-retryable error, raise original exception
                raise last_exception
        
        return wrapper
    return decorator


# Common retry conditions
def is_network_error(exception: Exception) -> bool:
    """Check if exception is a network-related error."""
    error_messages = [
        "connection error", "timeout", "network", "dns", 
        "connection reset", "connection refused", "unreachable"
    ]
    error_str = str(exception).lower()
    return any(msg in error_str for msg in error_messages)


def is_api_rate_limit(exception: Exception) -> bool:
    """Check if exception is an API rate limit error."""
    error_messages = [
        "rate limit", "too many requests", "quota exceeded", 
        "429", "rate exceeded"
    ]
    error_str = str(exception).lower()
    return any(msg in error_str for msg in error_messages)


def is_temporary_api_error(exception: Exception) -> bool:
    """Check if exception is a temporary API error."""
    error_messages = [
        "internal server error", "502", "503", "504", 
        "service unavailable", "temporary", "try again"
    ]
    error_str = str(exception).lower()
    return any(msg in error_str for msg in error_messages)


# Pre-configured retry decorators
network_retry = retry_on_conditions(
    conditions=[is_network_error, is_temporary_api_error],
    max_attempts=3,
    initial_delay=2.0,
    max_delay=30.0
)

api_retry = retry_on_conditions(
    conditions=[is_api_rate_limit, is_temporary_api_error],
    max_attempts=5,
    initial_delay=5.0,
    max_delay=120.0
)

def is_gpt5_empty_response(exception: Exception) -> bool:
    """Check if exception is GPT-5 returning empty content."""
    error_str = str(exception).lower()
    return "empty content" in error_str or "no json found" in error_str

def is_gpt5_error(exception: Exception) -> bool:
    """Check if exception is a GPT-5 specific issue."""
    error_str = str(exception).lower()
    return any(msg in error_str for msg in [
        "empty content", "no json found", "temperature=", "gpt-5",
        "rate limit", "model issue", "api issue"
    ])

# Enhanced LLM retry with longer delays for GPT-5
llm_retry = retry_on_conditions(
    conditions=[is_gpt5_error, is_api_rate_limit, is_temporary_api_error, is_gpt5_empty_response],
    max_attempts=5,  # More attempts for GPT-5
    initial_delay=2.0,  # Longer initial delay
    max_delay=60.0  # Much longer max delay
)