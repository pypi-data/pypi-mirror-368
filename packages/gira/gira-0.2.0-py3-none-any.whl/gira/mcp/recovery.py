"""Error recovery framework for Gira MCP server operations."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Generator, List, Optional, TypeVar, Union
from uuid import uuid4

from gira.mcp.errors import (
    EnhancedMCPError, 
    ErrorCategory, 
    ErrorCodes, 
    ErrorSeverity,
    RecoveryStrategy
)
from gira.utils.transaction import Transaction

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class RecoveryContext:
    """Context for tracking recovery operations."""
    
    def __init__(self, operation_id: str = None):
        self.operation_id = operation_id or str(uuid4())
        self.start_time = time.time()
        self.attempts = 0
        self.errors: List[EnhancedMCPError] = []
        self.recovery_actions: List[str] = []
        self.transaction: Optional[Transaction] = None
    
    def add_error(self, error: EnhancedMCPError) -> None:
        """Add an error to the recovery context."""
        self.errors.append(error)
        logger.debug(f"Recovery context {self.operation_id}: Added error {error.code}")
    
    def add_recovery_action(self, action: str) -> None:
        """Add a recovery action to the context."""
        self.recovery_actions.append(action)
        logger.info(f"Recovery context {self.operation_id}: {action}")
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since recovery started."""
        return time.time() - self.start_time


class RecoveryHandler(ABC):
    """Abstract base class for error recovery handlers."""
    
    @abstractmethod
    def can_handle(self, error: EnhancedMCPError) -> bool:
        """Check if this handler can recover from the given error."""
        pass
    
    @abstractmethod
    def recover(self, error: EnhancedMCPError, context: RecoveryContext) -> bool:
        """Attempt to recover from the error.
        
        Returns:
            True if recovery was successful, False otherwise
        """
        pass


class RetryRecoveryHandler(RecoveryHandler):
    """Recovery handler that implements retry logic with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def can_handle(self, error: EnhancedMCPError) -> bool:
        """Check if error is retryable."""
        return bool(
            error.recovery_strategy and
            error.recovery_strategy.auto_recoverable and
            error.category in [
                ErrorCategory.NETWORK,
                ErrorCategory.STORAGE,
                ErrorCategory.TIMEOUT,
                ErrorCategory.PROCESSING
            ]
        )
    
    def recover(self, error: EnhancedMCPError, context: RecoveryContext) -> bool:
        """Attempt recovery through retries."""
        if not error.recovery_strategy:
            return False
        
        strategy = error.recovery_strategy
        if strategy.retry_count >= strategy.max_retries:
            context.add_recovery_action(f"Max retries ({strategy.max_retries}) exceeded")
            return False
        
        # Calculate delay with exponential backoff
        delay = min(
            strategy.backoff_seconds * (2 ** strategy.retry_count),
            self.max_delay
        )
        
        context.add_recovery_action(f"Retrying in {delay:.1f}s (attempt {strategy.retry_count + 1}/{strategy.max_retries})")
        
        # Update retry count
        strategy.retry_count += 1
        
        # Sleep for the calculated delay
        time.sleep(delay)
        
        return True


class TransactionRollbackHandler(RecoveryHandler):
    """Recovery handler that rolls back failed transactions."""
    
    def can_handle(self, error: EnhancedMCPError) -> bool:
        """Check if error requires transaction rollback."""
        return (
            error.category in [
                ErrorCategory.PROCESSING,
                ErrorCategory.VALIDATION,
                ErrorCategory.STORAGE
            ] and
            error.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]
        )
    
    def recover(self, error: EnhancedMCPError, context: RecoveryContext) -> bool:
        """Attempt recovery through transaction rollback."""
        if not context.transaction:
            return False
        
        try:
            context.add_recovery_action("Rolling back transaction")
            context.transaction.rollback()
            context.add_recovery_action("Transaction rollback completed")
            return True
        except Exception as rollback_error:
            context.add_recovery_action(f"Transaction rollback failed: {rollback_error}")
            logger.exception(f"Failed to rollback transaction in recovery context {context.operation_id}")
            return False


class ConfigurationRecoveryHandler(RecoveryHandler):
    """Recovery handler for configuration-related errors."""
    
    def can_handle(self, error: EnhancedMCPError) -> bool:
        """Check if error is configuration-related."""
        return error.category == ErrorCategory.CONFIGURATION
    
    def recover(self, error: EnhancedMCPError, context: RecoveryContext) -> bool:
        """Attempt recovery for configuration errors."""
        if error.code == ErrorCodes.PROJECT_NOT_INITIALIZED:
            context.add_recovery_action("Configuration error detected - check project initialization")
            # Could potentially auto-initialize in some cases, but safer to suggest manual action
            return False
        
        context.add_recovery_action("Configuration issue requires manual intervention")
        return False


class RecoveryManager:
    """Manages error recovery operations."""
    
    def __init__(self):
        self.handlers: List[RecoveryHandler] = [
            RetryRecoveryHandler(),
            TransactionRollbackHandler(),
            ConfigurationRecoveryHandler()
        ]
        self.active_contexts: Dict[str, RecoveryContext] = {}
    
    def add_handler(self, handler: RecoveryHandler) -> None:
        """Add a custom recovery handler."""
        self.handlers.append(handler)
    
    def create_recovery_context(self, operation_id: str = None) -> RecoveryContext:
        """Create a new recovery context."""
        context = RecoveryContext(operation_id)
        self.active_contexts[context.operation_id] = context
        return context
    
    def attempt_recovery(self, error: EnhancedMCPError, context: RecoveryContext) -> bool:
        """Attempt to recover from an error using available handlers.
        
        Returns:
            True if recovery was successful, False otherwise
        """
        context.add_error(error)
        
        for handler in self.handlers:
            if handler.can_handle(error):
                try:
                    if handler.recover(error, context):
                        context.add_recovery_action(f"Recovery successful using {handler.__class__.__name__}")
                        return True
                except Exception as recovery_error:
                    logger.exception(f"Recovery handler {handler.__class__.__name__} failed")
                    context.add_recovery_action(f"Recovery failed: {recovery_error}")
        
        context.add_recovery_action("No suitable recovery handler found")
        return False
    
    def cleanup_context(self, operation_id: str) -> None:
        """Clean up a recovery context."""
        if operation_id in self.active_contexts:
            del self.active_contexts[operation_id]


# Global recovery manager instance
recovery_manager = RecoveryManager()


@contextmanager
def recovery_context(operation_id: str = None, use_transaction: bool = False) -> Generator[RecoveryContext, None, None]:
    """Context manager for recovery operations.
    
    Args:
        operation_id: Optional operation ID
        use_transaction: Whether to create a transaction for rollback
        
    Yields:
        RecoveryContext for the operation
    """
    context = recovery_manager.create_recovery_context(operation_id)
    
    if use_transaction:
        context.transaction = Transaction()
    
    try:
        yield context
    finally:
        # Clean up transaction if it exists and wasn't committed
        if context.transaction and not context.transaction.committed:
            try:
                context.transaction.rollback()
            except Exception:
                logger.exception(f"Failed to cleanup transaction in recovery context {context.operation_id}")
        
        recovery_manager.cleanup_context(context.operation_id)


def with_recovery(
    max_retries: int = 3,
    use_transaction: bool = False,
    recoverable_errors: Optional[List[ErrorCategory]] = None
) -> Callable[[F], F]:
    """Decorator to add automatic error recovery to functions.
    
    Args:
        max_retries: Maximum number of recovery attempts
        use_transaction: Whether to use transactions for rollback
        recoverable_errors: List of error categories that can be recovered
        
    Returns:
        Decorated function with recovery capabilities
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_id = f"{func.__name__}_{str(uuid4())[:8]}"
            
            with recovery_context(operation_id, use_transaction) as context:
                last_error = None
                
                for attempt in range(max_retries + 1):
                    context.attempts = attempt + 1
                    
                    try:
                        # Execute the original function
                        return func(*args, **kwargs)
                    
                    except EnhancedMCPError as error:
                        last_error = error
                        
                        # Check if error category is recoverable
                        if recoverable_errors and error.category not in recoverable_errors:
                            logger.debug(f"Error category {error.category} not in recoverable list")
                            break
                        
                        # Attempt recovery
                        if attempt < max_retries:
                            if recovery_manager.attempt_recovery(error, context):
                                logger.info(f"Recovery successful for {func.__name__}, retrying...")
                                continue
                            else:
                                logger.warning(f"Recovery failed for {func.__name__}")
                                break
                        else:
                            logger.error(f"Max recovery attempts reached for {func.__name__}")
                    
                    except Exception as error:
                        # Convert to EnhancedMCPError for recovery handling
                        enhanced_error = EnhancedMCPError(
                            message=f"Unexpected error in {func.__name__}",
                            code=ErrorCodes.INTERNAL_ERROR,
                            category=ErrorCategory.INTERNAL,
                            severity=ErrorSeverity.ERROR,
                            original_exception=error
                        )
                        last_error = enhanced_error
                        break
                
                # If we get here, recovery failed or error wasn't recoverable
                if last_error:
                    raise last_error
                
                # This shouldn't happen, but just in case
                raise EnhancedMCPError(
                    message=f"Unknown error in {func.__name__}",
                    code=ErrorCodes.UNKNOWN_ERROR
                )
        
        return wrapper
    return decorator


def graceful_degradation(
    fallback_value: Any = None,
    fallback_function: Optional[Callable] = None,
    log_level: int = logging.WARNING
) -> Callable[[F], F]:
    """Decorator to provide graceful degradation for non-critical operations.
    
    Args:
        fallback_value: Value to return if operation fails
        fallback_function: Function to call if operation fails
        log_level: Log level for degradation events
        
    Returns:
        Decorated function with graceful degradation
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                logger.log(
                    log_level,
                    f"Graceful degradation activated for {func.__name__}: {error}"
                )
                
                if fallback_function:
                    try:
                        return fallback_function(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback function also failed: {fallback_error}")
                
                return fallback_value
        
        return wrapper
    return decorator


# Utility functions for common recovery patterns

def create_retry_strategy(
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
    auto_recoverable: bool = True
) -> RecoveryStrategy:
    """Create a retry recovery strategy.
    
    Args:
        max_retries: Maximum number of retries
        backoff_seconds: Initial backoff time
        auto_recoverable: Whether error can be auto-recovered
        
    Returns:
        RecoveryStrategy instance
    """
    return RecoveryStrategy(
        strategy_type="retry",
        auto_recoverable=auto_recoverable,
        max_retries=max_retries,
        backoff_seconds=backoff_seconds
    )


def is_transient_error(error: EnhancedMCPError) -> bool:
    """Check if an error is likely transient and recoverable.
    
    Args:
        error: Error to check
        
    Returns:
        True if error is likely transient
    """
    transient_categories = [
        ErrorCategory.NETWORK,
        ErrorCategory.TIMEOUT,
        ErrorCategory.STORAGE
    ]
    
    transient_codes = [
        ErrorCodes.CONNECTION_FAILED,
        ErrorCodes.TIMEOUT_ERROR,
        ErrorCodes.STORAGE_ERROR
    ]
    
    return (
        error.category in transient_categories or
        error.code in transient_codes
    )