"""Cancellation token system for async operations."""

import threading
from typing import Callable, List, Optional, Set
from uuid import uuid4


class CancellationToken:
    """Token for cancelling async operations."""
    
    def __init__(self, token_id: Optional[str] = None):
        """Initialize cancellation token.
        
        Args:
            token_id: Optional token ID, generated if not provided
        """
        self.token_id = token_id or str(uuid4())
        self._cancelled = threading.Event()
        self._callbacks: List[Callable[[], None]] = []
        self._lock = threading.Lock()
        self._children: Set['CancellationToken'] = set()
        self._parent: Optional['CancellationToken'] = None
    
    @property
    def is_cancellation_requested(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancelled.is_set()
    
    def cancel(self) -> None:
        """Request cancellation of the operation."""
        if self._cancelled.is_set():
            return
        
        self._cancelled.set()
        
        # Cancel children
        with self._lock:
            for child in self._children:
                child.cancel()
            
            # Execute callbacks
            for callback in self._callbacks:
                try:
                    callback()
                except Exception:
                    # Ignore callback errors
                    pass
    
    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called on cancellation.
        
        Args:
            callback: Function to call when cancelled
        """
        with self._lock:
            if self.is_cancellation_requested:
                # Already cancelled, execute immediately
                callback()
            else:
                self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[], None]) -> None:
        """Unregister a cancellation callback.
        
        Args:
            callback: Callback to remove
        """
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def create_child(self) -> 'CancellationToken':
        """Create a child token that will be cancelled when parent is cancelled.
        
        Returns:
            Child cancellation token
        """
        child = CancellationToken()
        child._parent = self
        
        with self._lock:
            self._children.add(child)
        
        # If already cancelled, cancel child immediately
        if self.is_cancellation_requested:
            child.cancel()
        
        return child
    
    def wait(self, timeout: Optional[float] = None) -> bool:
        """Wait for cancellation.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if cancelled, False if timeout
        """
        return self._cancelled.wait(timeout)
    
    def check_cancellation(self) -> None:
        """Check if cancelled and raise if so.
        
        Raises:
            OperationCancelledException: If operation is cancelled
        """
        if self.is_cancellation_requested:
            raise OperationCancelledException(f"Operation {self.token_id} was cancelled")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cancel if exception occurred."""
        if exc_type is not None:
            self.cancel()


class CancellationTokenSource:
    """Source for creating linked cancellation tokens."""
    
    def __init__(self):
        """Initialize cancellation token source."""
        self._tokens: Set[CancellationToken] = set()
        self._lock = threading.Lock()
        self._cancelled = False
    
    def create_token(self) -> CancellationToken:
        """Create a new cancellation token.
        
        Returns:
            New cancellation token
        """
        token = CancellationToken()
        
        with self._lock:
            if self._cancelled:
                token.cancel()
            else:
                self._tokens.add(token)
        
        return token
    
    def cancel_all(self) -> None:
        """Cancel all tokens from this source."""
        with self._lock:
            self._cancelled = True
            for token in self._tokens:
                token.cancel()
            self._tokens.clear()
    
    @property
    def is_cancellation_requested(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancelled


class OperationCancelledException(Exception):
    """Exception raised when an operation is cancelled."""
    pass


class CancellationManager:
    """Manages cancellation tokens for operations."""
    
    def __init__(self):
        """Initialize cancellation manager."""
        self._tokens: dict[str, CancellationToken] = {}
        self._lock = threading.Lock()
    
    def create_token(self, operation_id: str) -> CancellationToken:
        """Create a cancellation token for an operation.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Cancellation token
        """
        token = CancellationToken(operation_id)
        
        with self._lock:
            self._tokens[operation_id] = token
        
        return token
    
    def get_token(self, operation_id: str) -> Optional[CancellationToken]:
        """Get cancellation token for an operation.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Cancellation token if exists
        """
        with self._lock:
            return self._tokens.get(operation_id)
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an operation.
        
        Args:
            operation_id: Operation ID to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        token = self.get_token(operation_id)
        if token:
            token.cancel()
            return True
        return False
    
    def remove_token(self, operation_id: str) -> None:
        """Remove a cancellation token.
        
        Args:
            operation_id: Operation ID
        """
        with self._lock:
            self._tokens.pop(operation_id, None)
    
    def clear(self) -> None:
        """Clear all tokens."""
        with self._lock:
            self._tokens.clear()