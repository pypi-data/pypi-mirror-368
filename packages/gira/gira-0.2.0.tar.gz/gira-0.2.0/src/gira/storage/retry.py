"""Retry logic for network operations."""

import time
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, Union

from gira.storage.exceptions import (
    StorageConnectionError,
    StorageError,
    StorageNotFoundError,
    StoragePermissionError,
)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    ):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            retryable_exceptions: Tuple of exceptions that should trigger retry
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (
            StorageConnectionError,
            ConnectionError,
            TimeoutError,
        )


def calculate_delay(
    attempt: int,
    config: RetryConfig,
) -> float:
    """Calculate delay for a retry attempt.
    
    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration
        
    Returns:
        Delay in seconds
    """
    delay = min(
        config.initial_delay * (config.exponential_base ** attempt),
        config.max_delay,
    )
    
    if config.jitter:
        import random
        # Add jitter of ±25%
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)


def retry_with_config(config: RetryConfig) -> Callable:
    """Decorator to retry functions with specific configuration.
    
    Args:
        config: Retry configuration
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    # Check if it's actually a non-retryable wrapped exception
                    if isinstance(e, (StorageNotFoundError, StoragePermissionError)):
                        raise
                    
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        time.sleep(delay)
                    else:
                        # Last attempt failed
                        break
                except Exception:
                    # Non-retryable exception, re-raise immediately
                    raise
            
            # All attempts failed
            if last_exception:
                raise StorageError(
                    f"Operation failed after {config.max_attempts} attempts: {last_exception}"
                ) from last_exception
        
        return wrapper
    return decorator


# Default retry decorator for common operations
default_retry = retry_with_config(RetryConfig())


# Decorator specifically for storage operations
def retryable_storage_operation(func: Callable) -> Callable:
    """Decorator to make storage operations retryable.
    
    This decorator adds retry logic to storage backend methods,
    automatically retrying on transient failures like network errors.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with retry logic
    """
    return retry_with_config(
        RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            jitter=True,
            retryable_exceptions=(
                StorageConnectionError,
                ConnectionError,
                TimeoutError,
                # Network-related OS errors (but not FileNotFoundError)
                BlockingIOError,
                BrokenPipeError,
                ConnectionAbortedError,
                ConnectionRefusedError,
                ConnectionResetError,
            ),
        )
    )(func)


def retry_operation(
    operation: Callable[[], Any],
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None,
) -> Any:
    """Execute an operation with retry logic.
    
    Args:
        operation: Function to execute
        config: Optional retry configuration (uses default if None)
        operation_name: Optional name for logging purposes
        
    Returns:
        Result of the operation
        
    Raises:
        StorageError: If all retry attempts fail
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return operation()
        except config.retryable_exceptions as e:
            last_exception = e
            
            if attempt < config.max_attempts - 1:
                delay = calculate_delay(attempt, config)
                time.sleep(delay)
            else:
                # Last attempt failed
                break
        except Exception:
            # Non-retryable exception, re-raise immediately
            raise
    
    # All attempts failed
    operation_desc = operation_name or "Operation"
    raise StorageError(
        f"{operation_desc} failed after {config.max_attempts} attempts: {last_exception}"
    ) from last_exception


class RetryableStorageOperation:
    """Context manager for retryable storage operations."""
    
    def __init__(
        self,
        operation_name: str,
        config: Optional[RetryConfig] = None,
    ):
        self.operation_name = operation_name
        self.config = config or RetryConfig()
        self.attempt = 0
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success
            return False
        
        if not isinstance(exc_val, self.config.retryable_exceptions):
            # Non-retryable exception
            return False
        
        self.attempt += 1
        
        if self.attempt >= self.config.max_attempts:
            # Max attempts reached
            elapsed = time.time() - self.start_time
            raise StorageError(
                f"{self.operation_name} failed after {self.attempt} attempts "
                f"over {elapsed:.1f} seconds: {exc_val}"
            ) from exc_val
        
        # Calculate and apply delay
        delay = calculate_delay(self.attempt - 1, self.config)
        time.sleep(delay)
        
        # Suppress the exception to allow retry
        return True