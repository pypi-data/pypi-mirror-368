"""Operation tracking for bulk operations."""

import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from gira.api.bulk.schemas import (
    OperationResult,
    OperationStatus,
    OperationType,
    ProgressInfo,
)


class OperationState:
    """State of a single bulk operation."""
    
    def __init__(
        self,
        operation_id: str,
        operation_type: OperationType,
        total_items: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.status = OperationStatus.PENDING
        self.total_items = total_items
        self.completed_items = 0
        self.current_item: Optional[str] = None
        self.results: Dict[str, List[OperationResult]] = {
            "successful": [],
            "failed": [],
            "skipped": []
        }
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self._lock = Lock()
    
    @property
    def progress(self) -> ProgressInfo:
        """Get current progress information."""
        percentage = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        
        # Calculate ETA if operation has started
        eta = None
        if self.started_at and self.completed_items > 0 and self.completed_items < self.total_items:
            elapsed = (datetime.now(timezone.utc) - self.started_at).total_seconds()
            avg_time_per_item = elapsed / self.completed_items
            remaining_items = self.total_items - self.completed_items
            eta = int(avg_time_per_item * remaining_items)
        
        return ProgressInfo(
            completed=self.completed_items,
            total=self.total_items,
            percentage=round(percentage, 2),
            current_item=self.current_item,
            estimated_time_remaining=eta
        )
    
    def update_status(self, status: OperationStatus):
        """Update operation status."""
        with self._lock:
            self.status = status
            self.updated_at = datetime.now(timezone.utc)
            
            if status == OperationStatus.IN_PROGRESS and not self.started_at:
                self.started_at = self.updated_at
            elif status in [OperationStatus.COMPLETED, OperationStatus.FAILED, 
                          OperationStatus.PARTIALLY_COMPLETED, OperationStatus.CANCELLED]:
                self.completed_at = self.updated_at
    
    def start_item(self, item_id: str):
        """Mark an item as being processed."""
        with self._lock:
            self.current_item = item_id
            self.updated_at = datetime.now(timezone.utc)
    
    def complete_item(self, result: OperationResult):
        """Mark an item as completed."""
        with self._lock:
            if result.error:
                self.results["failed"].append(result)
            elif result.status == "skipped":
                self.results["skipped"].append(result)
            else:
                self.results["successful"].append(result)
            
            self.completed_items += 1
            self.current_item = None
            self.updated_at = datetime.now(timezone.utc)
            
            # Update overall status if all items are processed
            if self.completed_items >= self.total_items:
                if len(self.results["failed"]) == 0:
                    self.status = OperationStatus.COMPLETED
                elif len(self.results["successful"]) > 0:
                    self.status = OperationStatus.PARTIALLY_COMPLETED
                else:
                    self.status = OperationStatus.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "status": self.status.value,
            "progress": self.progress.model_dump(),
            "results": {
                "successful": [r.model_dump() for r in self.results["successful"]],
                "failed": [r.model_dump() for r in self.results["failed"]],
                "skipped": [r.model_dump() for r in self.results["skipped"]]
            },
            "metadata": {
                **self.metadata,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "completed_at": self.completed_at.isoformat() if self.completed_at else None,
                "duration_ms": int((self.completed_at - self.started_at).total_seconds() * 1000) 
                              if self.started_at and self.completed_at else None
            }
        }


class OperationTracker:
    """Tracks the status and progress of bulk operations."""
    
    def __init__(self, max_operations: int = 1000, ttl_seconds: int = 3600):
        """Initialize operation tracker.
        
        Args:
            max_operations: Maximum number of operations to track
            ttl_seconds: Time to live for completed operations
        """
        self.operations: Dict[str, OperationState] = {}
        self.max_operations = max_operations
        self.ttl_seconds = ttl_seconds
        self._lock = Lock()
        self._operation_order: List[str] = []
    
    def create_operation(
        self,
        operation_type: OperationType,
        total_items: int,
        operation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new operation to track.
        
        Returns:
            Operation ID
        """
        operation_id = operation_id or str(uuid4())
        
        with self._lock:
            # Clean up old operations if at capacity
            if len(self.operations) >= self.max_operations:
                self._cleanup_operations()
            
            # Create new operation state
            state = OperationState(
                operation_id=operation_id,
                operation_type=operation_type,
                total_items=total_items,
                metadata=metadata
            )
            
            self.operations[operation_id] = state
            self._operation_order.append(operation_id)
        
        return operation_id
    
    def get_operation(self, operation_id: str) -> Optional[OperationState]:
        """Get operation state by ID."""
        return self.operations.get(operation_id)
    
    def update_status(self, operation_id: str, status: OperationStatus) -> bool:
        """Update operation status.
        
        Returns:
            True if updated, False if operation not found
        """
        operation = self.operations.get(operation_id)
        if operation:
            operation.update_status(status)
            return True
        return False
    
    def start_item(self, operation_id: str, item_id: str) -> bool:
        """Mark an item as being processed.
        
        Returns:
            True if updated, False if operation not found
        """
        operation = self.operations.get(operation_id)
        if operation:
            operation.start_item(item_id)
            return True
        return False
    
    def complete_item(self, operation_id: str, result: OperationResult) -> bool:
        """Mark an item as completed.
        
        Returns:
            True if updated, False if operation not found
        """
        operation = self.operations.get(operation_id)
        if operation:
            operation.complete_item(result)
            return True
        return False
    
    def get_active_operations(self) -> List[OperationState]:
        """Get all active (non-completed) operations."""
        with self._lock:
            return [
                op for op in self.operations.values()
                if op.status not in [
                    OperationStatus.COMPLETED,
                    OperationStatus.FAILED,
                    OperationStatus.PARTIALLY_COMPLETED,
                    OperationStatus.CANCELLED
                ]
            ]
    
    def get_recent_operations(self, limit: int = 10) -> List[OperationState]:
        """Get most recent operations."""
        with self._lock:
            # Return in reverse order (most recent first)
            operation_ids = self._operation_order[-limit:]
            return [
                self.operations[op_id] 
                for op_id in reversed(operation_ids) 
                if op_id in self.operations
            ]
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an operation.
        
        Returns:
            True if cancelled, False if operation not found or already completed
        """
        operation = self.operations.get(operation_id)
        if operation and operation.status in [OperationStatus.PENDING, OperationStatus.IN_PROGRESS]:
            operation.update_status(OperationStatus.CANCELLED)
            return True
        return False
    
    def _cleanup_operations(self):
        """Clean up old completed operations."""
        now = datetime.now(timezone.utc)
        cutoff_time = self.ttl_seconds
        
        # Find operations to remove
        to_remove = []
        for op_id, operation in self.operations.items():
            if operation.completed_at:
                age = (now - operation.completed_at).total_seconds()
                if age > cutoff_time:
                    to_remove.append(op_id)
        
        # If no old operations, remove oldest completed ones
        if not to_remove and len(self.operations) >= self.max_operations:
            completed_ops = [
                (op_id, op) for op_id, op in self.operations.items()
                if op.completed_at
            ]
            # Sort by completion time and remove oldest
            completed_ops.sort(key=lambda x: x[1].completed_at)
            to_remove = [op_id for op_id, _ in completed_ops[:len(completed_ops)//2]]
        
        # Remove operations
        for op_id in to_remove:
            del self.operations[op_id]
            self._operation_order.remove(op_id)
    
    def save_to_file(self, filepath: Path):
        """Save operation states to a file."""
        import json
        
        with self._lock:
            data = {
                op_id: op.to_dict() 
                for op_id, op in self.operations.items()
            }
            
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: Path):
        """Load operation states from a file."""
        import json
        
        if not filepath.exists():
            return
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Note: This is a simplified load that doesn't fully restore state
        # In production, you'd want to properly deserialize OperationState objects
        with self._lock:
            self.operations.clear()
            self._operation_order.clear()
            
            for op_id, op_data in data.items():
                # Create basic state (would need full deserialization in production)
                state = OperationState(
                    operation_id=op_id,
                    operation_type=OperationType(op_data["operation_type"]),
                    total_items=op_data["progress"]["total"]
                )
                state.status = OperationStatus(op_data["status"])
                state.completed_items = op_data["progress"]["completed"]
                
                self.operations[op_id] = state
                self._operation_order.append(op_id)