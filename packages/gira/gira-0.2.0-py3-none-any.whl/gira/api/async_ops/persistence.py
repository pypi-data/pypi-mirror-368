"""Operation persistence for saving and restoring async operations."""

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from gira.api.bulk.schemas import (
    BulkOperationRequest,
    BulkOperationResponse,
    OperationStatus,
    OperationType,
)
from gira.api.bulk.tracker import OperationState


class OperationSnapshot:
    """Snapshot of an operation's state."""
    
    def __init__(
        self,
        operation_id: str,
        operation_type: OperationType,
        request: BulkOperationRequest,
        state: OperationState,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize operation snapshot.
        
        Args:
            operation_id: Operation ID
            operation_type: Type of operation
            request: Original request
            state: Current operation state
            metadata: Additional metadata
        """
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.request = request
        self.state = state
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "request": self.request.model_dump(),
            "state": self._serialize_state(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    def _serialize_state(self) -> Dict[str, Any]:
        """Serialize operation state."""
        return {
            "status": self.state.status.value,
            "total_items": self.state.total_items,
            "completed_items": self.state.completed_items,
            "current_item": self.state.current_item,
            "results": {
                "successful": [r.model_dump() for r in self.state.results["successful"]],
                "failed": [r.model_dump() for r in self.state.results["failed"]],
                "skipped": [r.model_dump() for r in self.state.results["skipped"]]
            },
            "created_at": self.state.created_at.isoformat(),
            "updated_at": self.state.updated_at.isoformat(),
            "started_at": self.state.started_at.isoformat() if self.state.started_at else None,
            "completed_at": self.state.completed_at.isoformat() if self.state.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OperationSnapshot':
        """Create from dictionary."""
        # This is a simplified restoration - full implementation would
        # properly deserialize all nested objects
        operation_type = OperationType(data["operation_type"])
        request = BulkOperationRequest(**data["request"])
        
        # Create basic state
        state = OperationState(
            operation_id=data["operation_id"],
            operation_type=operation_type,
            total_items=data["state"]["total_items"]
        )
        state.status = OperationStatus(data["state"]["status"])
        state.completed_items = data["state"]["completed_items"]
        
        return cls(
            operation_id=data["operation_id"],
            operation_type=operation_type,
            request=request,
            state=state,
            metadata=data.get("metadata", {})
        )


class OperationPersistence:
    """Manages persistence of operation state."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize operation persistence.
        
        Args:
            storage_dir: Directory for storing operation state
        """
        self.storage_dir = storage_dir or Path.home() / ".gira" / "operations"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._snapshots_dir = self.storage_dir / "snapshots"
        self._snapshots_dir.mkdir(exist_ok=True)
        self._index_file = self.storage_dir / "index.json"
    
    def save_snapshot(self, snapshot: OperationSnapshot) -> Path:
        """Save an operation snapshot.
        
        Args:
            snapshot: Operation snapshot to save
            
        Returns:
            Path to saved snapshot file
        """
        # Save snapshot file
        snapshot_file = self._snapshots_dir / f"{snapshot.operation_id}.json"
        
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        
        # Update index
        self._update_index(snapshot.operation_id, snapshot.operation_type, snapshot.state.status)
        
        return snapshot_file
    
    def load_snapshot(self, operation_id: str) -> Optional[OperationSnapshot]:
        """Load an operation snapshot.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Operation snapshot if found
        """
        snapshot_file = self._snapshots_dir / f"{operation_id}.json"
        
        if not snapshot_file.exists():
            return None
        
        try:
            with open(snapshot_file, 'r') as f:
                data = json.load(f)
            
            return OperationSnapshot.from_dict(data)
        except Exception:
            return None
    
    def delete_snapshot(self, operation_id: str) -> bool:
        """Delete an operation snapshot.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            True if deleted, False if not found
        """
        snapshot_file = self._snapshots_dir / f"{operation_id}.json"
        
        if snapshot_file.exists():
            snapshot_file.unlink()
            self._remove_from_index(operation_id)
            return True
        
        return False
    
    def list_snapshots(
        self,
        status: Optional[OperationStatus] = None,
        operation_type: Optional[OperationType] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List available snapshots.
        
        Args:
            status: Filter by status
            operation_type: Filter by operation type
            limit: Maximum number to return
            
        Returns:
            List of snapshot summaries
        """
        index = self._load_index()
        
        # Filter snapshots
        snapshots = []
        for op_id, info in index.items():
            if status and info.get("status") != status.value:
                continue
            if operation_type and info.get("type") != operation_type.value:
                continue
            
            snapshots.append({
                "operation_id": op_id,
                "operation_type": info.get("type"),
                "status": info.get("status"),
                "created_at": info.get("created_at"),
                "updated_at": info.get("updated_at")
            })
        
        # Sort by updated time (newest first)
        snapshots.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        if limit:
            snapshots = snapshots[:limit]
        
        return snapshots
    
    def cleanup_old_snapshots(self, days: int = 7) -> int:
        """Clean up old snapshots.
        
        Args:
            days: Delete snapshots older than this many days
            
        Returns:
            Number of snapshots deleted
        """
        import time
        
        index = self._load_index()
        current_time = time.time()
        cutoff_time = days * 24 * 60 * 60
        deleted = 0
        
        for op_id, info in list(index.items()):
            # Check if snapshot is old and completed
            if info.get("status") in ["completed", "failed", "cancelled"]:
                updated_str = info.get("updated_at", "")
                if updated_str:
                    try:
                        updated_time = datetime.fromisoformat(updated_str).timestamp()
                        if current_time - updated_time > cutoff_time:
                            if self.delete_snapshot(op_id):
                                deleted += 1
                    except Exception:
                        pass
        
        return deleted
    
    def save_checkpoint(
        self,
        operation_id: str,
        checkpoint_data: Dict[str, Any]
    ) -> Path:
        """Save a checkpoint for resumable operations.
        
        Args:
            operation_id: Operation ID
            checkpoint_data: Data to checkpoint
            
        Returns:
            Path to checkpoint file
        """
        checkpoint_file = self._snapshots_dir / f"{operation_id}.checkpoint"
        
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        return checkpoint_file
    
    def load_checkpoint(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Load a checkpoint for resuming operations.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Checkpoint data if found
        """
        checkpoint_file = self._snapshots_dir / f"{operation_id}.checkpoint"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def delete_checkpoint(self, operation_id: str) -> bool:
        """Delete a checkpoint file.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            True if deleted
        """
        checkpoint_file = self._snapshots_dir / f"{operation_id}.checkpoint"
        
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            return True
        
        return False
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load the snapshot index."""
        if not self._index_file.exists():
            return {}
        
        try:
            with open(self._index_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_index(self, index: Dict[str, Dict[str, Any]]) -> None:
        """Save the snapshot index."""
        with open(self._index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _update_index(
        self,
        operation_id: str,
        operation_type: OperationType,
        status: OperationStatus
    ) -> None:
        """Update the snapshot index."""
        index = self._load_index()
        
        index[operation_id] = {
            "type": operation_type.value,
            "status": status.value,
            "created_at": index.get(operation_id, {}).get(
                "created_at",
                datetime.now(timezone.utc).isoformat()
            ),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        self._save_index(index)
    
    def _remove_from_index(self, operation_id: str) -> None:
        """Remove an operation from the index."""
        index = self._load_index()
        index.pop(operation_id, None)
        self._save_index(index)