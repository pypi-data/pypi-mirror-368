"""Enhanced progress tracking with callbacks for async operations."""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

from gira.api.bulk.schemas import ProgressInfo


@dataclass
class ProgressMetrics:
    """Detailed metrics for operation progress."""
    items_per_second: float = 0.0
    elapsed_ms: int = 0
    errors_count: int = 0
    average_item_time_ms: float = 0.0
    success_rate: float = 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "items_per_second": round(self.items_per_second, 2),
            "elapsed_ms": self.elapsed_ms,
            "errors_count": self.errors_count,
            "average_item_time_ms": round(self.average_item_time_ms, 2),
            "success_rate": round(self.success_rate, 2)
        }


@dataclass
class ProgressUpdate:
    """Progress update event."""
    operation_id: str
    progress: ProgressInfo
    metrics: ProgressMetrics
    current_step: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_id": self.operation_id,
            "progress": self.progress.model_dump(),
            "metrics": self.metrics.to_dict(),
            "current_step": self.current_step,
            "timestamp": self.timestamp.isoformat()
        }


class ProgressCallback:
    """Base class for progress callbacks."""
    
    def on_progress(self, update: ProgressUpdate) -> None:
        """Called on progress update."""
        pass
    
    def on_step_change(self, operation_id: str, step: str) -> None:
        """Called when operation step changes."""
        pass
    
    def on_item_complete(self, operation_id: str, item_id: str, success: bool) -> None:
        """Called when an item is completed."""
        pass
    
    def on_operation_complete(self, operation_id: str, status: str) -> None:
        """Called when operation completes."""
        pass


class EnhancedProgressTracker:
    """Enhanced progress tracker with callback support."""
    
    def __init__(self, operation_id: str, total_items: int):
        """Initialize progress tracker.
        
        Args:
            operation_id: Operation ID
            total_items: Total number of items to process
        """
        self.operation_id = operation_id
        self.total_items = total_items
        self.completed_items = 0
        self.failed_items = 0
        self.current_item: Optional[str] = None
        self.current_step: Optional[str] = None
        self.start_time = time.time()
        self.item_times: List[float] = []
        self._callbacks: List[ProgressCallback] = []
        self._lock = Lock()
        self._step_start_time: Optional[float] = None
        self._item_start_time: Optional[float] = None
    
    def add_callback(self, callback: ProgressCallback) -> None:
        """Add a progress callback.
        
        Args:
            callback: Callback to add
        """
        with self._lock:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: ProgressCallback) -> None:
        """Remove a progress callback.
        
        Args:
            callback: Callback to remove
        """
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def set_step(self, step: str) -> None:
        """Set the current operation step.
        
        Args:
            step: Step description
        """
        with self._lock:
            self.current_step = step
            self._step_start_time = time.time()
            
            # Copy callbacks list to avoid issues if modified during iteration
            callbacks = self._callbacks.copy()
        
        # Call callbacks outside of lock to prevent deadlocks
        for callback in callbacks:
            try:
                callback.on_step_change(self.operation_id, step)
            except Exception:
                pass
    
    def start_item(self, item_id: str) -> None:
        """Mark an item as being processed.
        
        Args:
            item_id: Item ID
        """
        with self._lock:
            self.current_item = item_id
            self._item_start_time = time.time()
    
    def complete_item(self, item_id: str, success: bool = True) -> None:
        """Mark an item as completed.
        
        Args:
            item_id: Item ID
            success: Whether item succeeded
        """
        # Update state and get data for callbacks while holding lock
        with self._lock:
            self.completed_items += 1
            if not success:
                self.failed_items += 1
            
            # Track item time
            if self._item_start_time:
                item_time = time.time() - self._item_start_time
                self.item_times.append(item_time)
                # Keep only last 100 times for averaging
                if len(self.item_times) > 100:
                    self.item_times.pop(0)
            
            self.current_item = None
            self._item_start_time = None
            
            # Get current progress for callbacks (already holding lock, so calculate directly)
            percentage = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
            
            # Calculate ETA
            eta = None
            if self.completed_items > 0 and self.completed_items < self.total_items:
                elapsed = time.time() - self.start_time
                avg_time = elapsed / self.completed_items
                remaining = self.total_items - self.completed_items
                eta = int(avg_time * remaining)
            
            progress = ProgressInfo(
                completed=self.completed_items,
                total=self.total_items,
                percentage=round(percentage, 2),
                current_item=self.current_item,
                estimated_time_remaining=eta
            )
            
            # Get metrics (already holding lock, so calculate directly)
            elapsed = time.time() - self.start_time
            elapsed_ms = int(elapsed * 1000)
            
            # Calculate items per second
            items_per_second = self.completed_items / elapsed if elapsed > 0 else 0
            
            # Calculate average item time
            avg_item_time = 0.0
            if self.item_times:
                avg_item_time = sum(self.item_times) / len(self.item_times) * 1000
            
            # Calculate success rate
            success_rate = 100.0
            if self.completed_items > 0:
                success_rate = ((self.completed_items - self.failed_items) / self.completed_items) * 100
            
            metrics = ProgressMetrics(
                items_per_second=items_per_second,
                elapsed_ms=elapsed_ms,
                errors_count=self.failed_items,
                average_item_time_ms=avg_item_time,
                success_rate=success_rate
            )
            
            # Create update object
            update = ProgressUpdate(
                operation_id=self.operation_id,
                progress=progress,
                metrics=metrics,
                current_step=self.current_step
            )
            
            # Copy callbacks list to avoid issues if modified during iteration
            callbacks = self._callbacks.copy()
        
        # Call callbacks outside of lock to prevent deadlocks
        for callback in callbacks:
            try:
                callback.on_item_complete(self.operation_id, item_id, success)
                callback.on_progress(update)
            except Exception:
                pass
    
    def get_progress(self) -> ProgressInfo:
        """Get current progress information."""
        with self._lock:
            percentage = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
            
            # Calculate ETA
            eta = None
            if self.completed_items > 0 and self.completed_items < self.total_items:
                elapsed = time.time() - self.start_time
                avg_time = elapsed / self.completed_items
                remaining = self.total_items - self.completed_items
                eta = int(avg_time * remaining)
            
            return ProgressInfo(
                completed=self.completed_items,
                total=self.total_items,
                percentage=round(percentage, 2),
                current_item=self.current_item,
                estimated_time_remaining=eta
            )
    
    def get_metrics(self) -> ProgressMetrics:
        """Get detailed progress metrics."""
        with self._lock:
            elapsed = time.time() - self.start_time
            elapsed_ms = int(elapsed * 1000)
            
            # Calculate items per second
            items_per_second = self.completed_items / elapsed if elapsed > 0 else 0
            
            # Calculate average item time
            avg_item_time = 0.0
            if self.item_times:
                avg_item_time = sum(self.item_times) / len(self.item_times) * 1000
            
            # Calculate success rate
            success_rate = 100.0
            if self.completed_items > 0:
                success_rate = ((self.completed_items - self.failed_items) / self.completed_items) * 100
            
            return ProgressMetrics(
                items_per_second=items_per_second,
                elapsed_ms=elapsed_ms,
                errors_count=self.failed_items,
                average_item_time_ms=avg_item_time,
                success_rate=success_rate
            )
    
    def complete_operation(self, status: str) -> None:
        """Mark operation as complete.
        
        Args:
            status: Final status
        """
        with self._lock:
            # Copy callbacks list to avoid issues if modified during iteration
            callbacks = self._callbacks.copy()
        
        # Call callbacks outside of lock to prevent deadlocks
        for callback in callbacks:
            try:
                callback.on_operation_complete(self.operation_id, status)
            except Exception:
                pass


class LoggingProgressCallback(ProgressCallback):
    """Progress callback that logs updates."""
    
    def __init__(self, logger):
        """Initialize with logger."""
        self.logger = logger
    
    def on_progress(self, update: ProgressUpdate) -> None:
        """Log progress update."""
        self.logger.info(
            f"Operation {update.operation_id}: "
            f"{update.progress.completed}/{update.progress.total} "
            f"({update.progress.percentage}%)"
        )
    
    def on_step_change(self, operation_id: str, step: str) -> None:
        """Log step change."""
        self.logger.info(f"Operation {operation_id} step: {step}")
    
    def on_operation_complete(self, operation_id: str, status: str) -> None:
        """Log operation completion."""
        self.logger.info(f"Operation {operation_id} completed with status: {status}")


class WebhookProgressCallback(ProgressCallback):
    """Progress callback that sends updates to a webhook."""
    
    def __init__(self, webhook_url: str, batch_size: int = 10):
        """Initialize webhook callback.
        
        Args:
            webhook_url: URL to send updates to
            batch_size: Number of updates to batch before sending
        """
        self.webhook_url = webhook_url
        self.batch_size = batch_size
        self._updates: List[ProgressUpdate] = []
        self._lock = Lock()
    
    def on_progress(self, update: ProgressUpdate) -> None:
        """Queue progress update for webhook."""
        with self._lock:
            self._updates.append(update)
            
            if len(self._updates) >= self.batch_size:
                self._send_updates()
    
    def on_operation_complete(self, operation_id: str, status: str) -> None:
        """Send final update on completion."""
        with self._lock:
            self._send_updates()  # Flush any pending updates
        
        # Send completion notification
        self._send_completion(operation_id, status)
    
    def _send_updates(self) -> None:
        """Send batched updates to webhook."""
        if not self._updates:
            return
        
        try:
            import requests
            
            data = {
                "updates": [u.to_dict() for u in self._updates],
                "batch_size": len(self._updates)
            }
            
            requests.post(self.webhook_url, json=data, timeout=5)
            self._updates.clear()
            
        except Exception:
            # Log error but don't fail operation
            pass
    
    def _send_completion(self, operation_id: str, status: str) -> None:
        """Send completion notification."""
        try:
            import requests
            
            data = {
                "operation_id": operation_id,
                "status": status,
                "event": "operation_complete",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            requests.post(self.webhook_url, json=data, timeout=5)
            
        except Exception:
            pass