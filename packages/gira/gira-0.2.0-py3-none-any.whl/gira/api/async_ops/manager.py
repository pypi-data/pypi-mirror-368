"""Async operation manager for background processing."""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from queue import Queue, Empty, Full
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

from gira.api.async_ops.cancellation import (
    CancellationManager,
    CancellationToken,
    OperationCancelledException,
)
from gira.api.async_ops.persistence import OperationPersistence, OperationSnapshot
from gira.api.async_ops.progress import EnhancedProgressTracker, ProgressCallback
from gira.api.bulk.manager import BulkOperationManager
from gira.api.bulk.schemas import (
    BulkOperationRequest,
    BulkOperationResponse,
    OperationStatus,
    OperationType,
)
from gira.api.bulk.tracker import OperationState, OperationTracker


class AsyncOperation:
    """Represents an async operation."""
    
    def __init__(
        self,
        operation_id: str,
        operation_type: OperationType,
        request: BulkOperationRequest,
        manager: BulkOperationManager,
        cancellation_token: CancellationToken,
        progress_tracker: EnhancedProgressTracker
    ):
        """Initialize async operation.
        
        Args:
            operation_id: Operation ID
            operation_type: Type of operation
            request: Operation request
            manager: Bulk operation manager
            cancellation_token: Cancellation token
            progress_tracker: Progress tracker
        """
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.request = request
        self.manager = manager
        self.cancellation_token = cancellation_token
        self.progress_tracker = progress_tracker
        self.future: Optional[Future] = None
        self.result: Optional[BulkOperationResponse] = None
        self.error: Optional[Exception] = None
    
    def is_complete(self) -> bool:
        """Check if operation is complete."""
        return self.future is not None and self.future.done()
    
    def get_status(self) -> OperationStatus:
        """Get operation status."""
        if self.cancellation_token.is_cancellation_requested:
            return OperationStatus.CANCELLED
        elif self.error:
            return OperationStatus.FAILED
        elif self.result:
            return OperationStatus.COMPLETED
        elif self.future and not self.future.done():
            return OperationStatus.IN_PROGRESS
        else:
            return OperationStatus.PENDING


class AsyncOperationManager:
    """Manages async bulk operations."""
    
    def __init__(
        self,
        max_workers: int = 4,
        max_queue_size: int = 100,
        persistence_dir: Optional[Path] = None
    ):
        """Initialize async operation manager.
        
        Args:
            max_workers: Maximum concurrent operations
            max_queue_size: Maximum queued operations
            persistence_dir: Directory for operation persistence
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.operation_queue: Queue[AsyncOperation] = Queue(maxsize=max_queue_size)
        self.active_operations: Dict[str, AsyncOperation] = {}
        self.cancellation_manager = CancellationManager()
        self.persistence = OperationPersistence(persistence_dir)
        self._lock = threading.Lock()
        self._shutdown = False
        
        # Start queue processor
        self._queue_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._queue_thread.start()
    
    def submit_operation(
        self,
        manager: BulkOperationManager,
        request: BulkOperationRequest,
        operation_id: Optional[str] = None,
        progress_callbacks: Optional[List[ProgressCallback]] = None,
        persist: bool = True
    ) -> str:
        """Submit an operation for async execution.
        
        Args:
            manager: Bulk operation manager
            request: Operation request
            operation_id: Optional operation ID
            progress_callbacks: Progress callbacks
            persist: Whether to persist operation state
            
        Returns:
            Operation ID
            
        Raises:
            RuntimeError: If queue is full
        """
        if self._shutdown:
            raise RuntimeError("Operation manager is shutting down")
        
        # Generate operation ID if not provided
        operation_id = operation_id or str(uuid4())
        request.operation_id = operation_id
        
        # Create cancellation token
        cancellation_token = self.cancellation_manager.create_token(operation_id)
        
        # Create progress tracker
        progress_tracker = EnhancedProgressTracker(
            operation_id=operation_id,
            total_items=len(request.items)
        )
        
        # Add callbacks
        if progress_callbacks:
            for callback in progress_callbacks:
                progress_tracker.add_callback(callback)
        
        # Create async operation
        operation = AsyncOperation(
            operation_id=operation_id,
            operation_type=manager.operation_type,
            request=request,
            manager=manager,
            cancellation_token=cancellation_token,
            progress_tracker=progress_tracker
        )
        
        # Save initial snapshot if persisting
        if persist:
            self._save_snapshot(operation)
        
        # Queue operation
        try:
            self.operation_queue.put_nowait(operation)
        except Full:
            raise RuntimeError("Operation queue is full")
        
        with self._lock:
            self.active_operations[operation_id] = operation
        
        return operation_id
    
    def get_operation(self, operation_id: str) -> Optional[AsyncOperation]:
        """Get an operation by ID.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Async operation if found
        """
        with self._lock:
            return self.active_operations.get(operation_id)
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an operation.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            True if cancelled
        """
        return self.cancellation_manager.cancel_operation(operation_id)
    
    def wait_for_operation(
        self,
        operation_id: str,
        timeout: Optional[float] = None
    ) -> Optional[BulkOperationResponse]:
        """Wait for an operation to complete.
        
        Args:
            operation_id: Operation ID
            timeout: Maximum time to wait
            
        Returns:
            Operation response if complete
        """
        operation = self.get_operation(operation_id)
        if not operation:
            return None
        
        if operation.future:
            try:
                operation.future.result(timeout=timeout)
                return operation.result
            except Exception:
                return None
        
        return None
    
    def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed operation status.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Status information
        """
        operation = self.get_operation(operation_id)
        if not operation:
            # Try loading from persistence
            snapshot = self.persistence.load_snapshot(operation_id)
            if snapshot:
                return {
                    "operation_id": operation_id,
                    "status": snapshot.state.status.value,
                    "progress": snapshot.state.progress.model_dump(),
                    "persisted": True
                }
            return None
        
        progress = operation.progress_tracker.get_progress()
        metrics = operation.progress_tracker.get_metrics()
        
        return {
            "operation_id": operation_id,
            "status": operation.get_status().value,
            "progress": progress.model_dump(),
            "metrics": metrics.to_dict(),
            "current_step": operation.progress_tracker.current_step,
            "cancellation": {
                "can_cancel": not operation.is_complete(),
                "cancel_requested": operation.cancellation_token.is_cancellation_requested
            }
        }
    
    def list_active_operations(self) -> List[Dict[str, Any]]:
        """List all active operations.
        
        Returns:
            List of operation summaries
        """
        with self._lock:
            operations = []
            for op_id, operation in self.active_operations.items():
                operations.append({
                    "operation_id": op_id,
                    "operation_type": operation.operation_type.value,
                    "status": operation.get_status().value,
                    "progress": operation.progress_tracker.get_progress().model_dump()
                })
            return operations
    
    def resume_operations(self) -> List[str]:
        """Resume operations from persistence.
        
        Returns:
            List of resumed operation IDs
        """
        resumed = []
        
        # Load incomplete operations
        snapshots = self.persistence.list_snapshots(
            status=OperationStatus.IN_PROGRESS
        )
        
        for snapshot_info in snapshots:
            op_id = snapshot_info["operation_id"]
            snapshot = self.persistence.load_snapshot(op_id)
            
            if snapshot and snapshot.state.status == OperationStatus.IN_PROGRESS:
                # Check if operation is already active
                if op_id not in self.active_operations:
                    # Attempt to resume
                    if self._resume_operation(snapshot):
                        resumed.append(op_id)
        
        return resumed
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the operation manager.
        
        Args:
            wait: Whether to wait for operations to complete
        """
        self._shutdown = True
        
        if wait:
            # Cancel all pending operations
            with self._lock:
                for operation in self.active_operations.values():
                    operation.cancellation_token.cancel()
        
        # Shutdown executor
        self.executor.shutdown(wait=wait)
    
    def _process_queue(self) -> None:
        """Process queued operations."""
        while not self._shutdown:
            try:
                # Get operation from queue
                operation = self.operation_queue.get(timeout=1)
                
                # Submit to executor
                future = self.executor.submit(
                    self._execute_operation,
                    operation
                )
                operation.future = future
                
            except Empty:
                continue
            except Exception:
                # Log error but continue processing
                pass
    
    def _execute_operation(self, operation: AsyncOperation) -> None:
        """Execute an operation with cancellation support."""
        try:
            # Set up operation tracker integration
            self._setup_tracker_integration(operation)
            
            # Update progress
            operation.progress_tracker.set_step("Starting operation")
            
            # Execute with cancellation checks
            result = self._execute_with_cancellation(operation)
            
            operation.result = result
            operation.progress_tracker.complete_operation("completed")
            
        except OperationCancelledException:
            operation.progress_tracker.complete_operation("cancelled")
            
        except Exception as e:
            operation.error = e
            operation.progress_tracker.complete_operation("failed")
            
        finally:
            # Save final snapshot
            self._save_snapshot(operation)
            
            # Cleanup
            self.cancellation_manager.remove_token(operation.operation_id)
    
    def _execute_with_cancellation(
        self,
        operation: AsyncOperation
    ) -> BulkOperationResponse:
        """Execute operation with cancellation checks."""
        # Monkey-patch the manager's process_item to check cancellation
        original_process = operation.manager.process_item
        
        def cancellable_process(item, options, context=None):
            # Check cancellation before each item
            operation.cancellation_token.check_cancellation()
            
            # Update progress
            item_id = operation.manager._get_item_id(item)
            operation.progress_tracker.start_item(item_id)
            
            try:
                result = original_process(item, options, context)
                operation.progress_tracker.complete_item(item_id, not result.error)
                return result
            except Exception as e:
                operation.progress_tracker.complete_item(item_id, False)
                raise
        
        operation.manager.process_item = cancellable_process
        
        try:
            # Execute operation
            return operation.manager._execute_sync(
                operation.request,
                operation.operation_id
            )
        finally:
            # Restore original method
            operation.manager.process_item = original_process
    
    def _setup_tracker_integration(self, operation: AsyncOperation) -> None:
        """Set up integration between operation tracker and progress tracker."""
        # Get the operation state from the tracker
        op_state = operation.manager.tracker.get_operation(operation.operation_id)
        if op_state:
            # Sync initial state
            operation.progress_tracker.completed_items = op_state.completed_items
    
    def _save_snapshot(self, operation: AsyncOperation) -> None:
        """Save operation snapshot."""
        try:
            # Get operation state from tracker
            op_state = operation.manager.tracker.get_operation(operation.operation_id)
            if not op_state:
                return
            
            snapshot = OperationSnapshot(
                operation_id=operation.operation_id,
                operation_type=operation.operation_type,
                request=operation.request,
                state=op_state,
                metadata={
                    "error": str(operation.error) if operation.error else None,
                    "cancelled": operation.cancellation_token.is_cancellation_requested
                }
            )
            
            self.persistence.save_snapshot(snapshot)
            
        except Exception:
            # Don't fail operation on persistence error
            pass
    
    def _resume_operation(self, snapshot: OperationSnapshot) -> bool:
        """Resume an operation from snapshot.
        
        Args:
            snapshot: Operation snapshot
            
        Returns:
            True if resumed successfully
        """
        # This is a simplified resume - full implementation would
        # reconstruct the operation state and continue processing
        # from where it left off
        return False