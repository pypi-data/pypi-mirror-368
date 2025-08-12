"""Transaction support for bulk operations in Gira."""

import json
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from gira.utils.console import console
from gira.utils.errors import GiraError


class TransactionError(GiraError):
    """Raised when a transaction operation fails."""
    pass


class FileOperation:
    """Represents a single file operation in a transaction."""

    def __init__(self, operation_type: str, path: Path, backup_path: Optional[Path] = None, data: Optional[Any] = None):
        self.operation_type = operation_type  # 'create', 'update', 'delete', 'move'
        self.path = path
        self.backup_path = backup_path
        self.data = data
        self.timestamp = datetime.now(timezone.utc)


class Transaction:
    """Manages atomic file operations with rollback support."""

    def __init__(self, transaction_id: Optional[str] = None, log_dir: Optional[Path] = None):
        self.transaction_id = transaction_id or str(uuid4())
        self.operations: List[FileOperation] = []
        self.backup_dir = Path(tempfile.mkdtemp(prefix=f"gira_tx_{self.transaction_id}_"))
        self.log_dir = log_dir
        self.committed = False
        self.rolled_back = False
        self._original_files: Dict[Path, Optional[Path]] = {}  # Maps file paths to their backups

    def add_create(self, path: Path, data: Any) -> None:
        """Add a file creation operation to the transaction."""
        if path.exists():
            raise TransactionError(f"Cannot create {path}: file already exists")
        self.operations.append(FileOperation("create", path, data=data))

    def add_update(self, path: Path, data: Any) -> None:
        """Add a file update operation to the transaction."""
        if not path.exists():
            raise TransactionError(f"Cannot update {path}: file does not exist")

        # Create backup
        backup_path = self._backup_file(path)
        self.operations.append(FileOperation("update", path, backup_path, data))

    def add_delete(self, path: Path) -> None:
        """Add a file deletion operation to the transaction."""
        if not path.exists():
            raise TransactionError(f"Cannot delete {path}: file does not exist")

        # Create backup
        backup_path = self._backup_file(path)
        self.operations.append(FileOperation("delete", path, backup_path))

    def add_move(self, source: Path, destination: Path) -> None:
        """Add a file move operation to the transaction."""
        if not source.exists():
            raise TransactionError(f"Cannot move {source}: file does not exist")
        if destination.exists():
            raise TransactionError(f"Cannot move to {destination}: file already exists")

        self.operations.append(FileOperation("move", source, data=destination))

    def _backup_file(self, path: Path) -> Path:
        """Create a backup of a file."""
        if path in self._original_files:
            # Already backed up
            return self._original_files[path]

        backup_path = self.backup_dir / f"{path.name}.{uuid4().hex}"
        shutil.copy2(path, backup_path)
        self._original_files[path] = backup_path
        return backup_path

    def commit(self) -> None:
        """Commit all operations in the transaction."""
        if self.committed:
            raise TransactionError("Transaction already committed")
        if self.rolled_back:
            raise TransactionError("Transaction already rolled back")

        try:
            # Execute all operations
            for op in self.operations:
                self._execute_operation(op)

            self.committed = True
            self._log_transaction("commit")

        except Exception as e:
            # Rollback on any error
            self.rollback()
            raise TransactionError(f"Transaction failed: {e}") from e
        finally:
            # Clean up backup directory if commit succeeded
            if self.committed and self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)

    def rollback(self) -> None:
        """Rollback all operations in the transaction."""
        if self.committed:
            raise TransactionError("Cannot rollback committed transaction")
        if self.rolled_back:
            return  # Already rolled back

        # Process operations in reverse order
        for op in reversed(self.operations):
            try:
                self._rollback_operation(op)
            except Exception as e:
                console.print(f"[red]Warning: Failed to rollback {op.path}: {e}[/red]")

        self.rolled_back = True
        self._log_transaction("rollback")

        # Clean up backup directory
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

    def _execute_operation(self, op: FileOperation) -> None:
        """Execute a single file operation."""
        if op.operation_type == "create":
            op.path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(op.data, (dict, list)):
                op.path.write_text(json.dumps(op.data, indent=2))
            else:
                op.path.write_text(str(op.data))

        elif op.operation_type == "update":
            if isinstance(op.data, (dict, list)):
                op.path.write_text(json.dumps(op.data, indent=2))
            else:
                op.path.write_text(str(op.data))

        elif op.operation_type == "delete":
            op.path.unlink()

        elif op.operation_type == "move":
            destination = op.data
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(op.path), str(destination))

    def _rollback_operation(self, op: FileOperation) -> None:
        """Rollback a single file operation."""
        if op.operation_type == "create":
            # Delete the created file
            if op.path.exists():
                op.path.unlink()

        elif op.operation_type == "update" or op.operation_type == "delete":
            # Restore from backup
            if op.backup_path and op.backup_path.exists():
                shutil.copy2(op.backup_path, op.path)

        elif op.operation_type == "move":
            # Move back
            destination = op.data
            if destination.exists() and not op.path.exists():
                shutil.move(str(destination), str(op.path))

    def _log_transaction(self, action: str) -> None:
        """Log transaction details for debugging."""
        if not self.log_dir:
            return

        log_file = self.log_dir / f"transaction_{self.transaction_id}.log"
        log_entry = {
            "transaction_id": self.transaction_id,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operations": [
                {
                    "type": op.operation_type,
                    "path": str(op.path),
                    "backup_path": str(op.backup_path) if op.backup_path else None,
                    "timestamp": op.timestamp.isoformat()
                }
                for op in self.operations
            ]
        }

        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # An exception occurred, rollback
            self.rollback()
        elif not self.committed and not self.rolled_back:
            # No exception and not yet committed, auto-commit
            self.commit()


@contextmanager
def atomic_operation(transaction_id: Optional[str] = None, log_dir: Optional[Path] = None):
    """Context manager for atomic file operations.
    
    Usage:
        with atomic_operation() as tx:
            tx.add_update(path1, data1)
            tx.add_update(path2, data2)
            # All operations committed atomically on exit
            # Rolled back if any exception occurs
    """
    tx = Transaction(transaction_id, log_dir)
    try:
        yield tx
        if not tx.committed and not tx.rolled_back:
            tx.commit()
    except Exception:
        if not tx.rolled_back:
            tx.rollback()
        raise


def batch_operation(operations: List[Tuple[str, Path, Any]], transaction_id: Optional[str] = None) -> None:
    """Execute multiple file operations atomically.
    
    Args:
        operations: List of (operation_type, path, data) tuples
        transaction_id: Optional transaction ID
        
    Raises:
        TransactionError: If any operation fails
    """
    with atomic_operation(transaction_id) as tx:
        for op_type, path, data in operations:
            if op_type == "create":
                tx.add_create(path, data)
            elif op_type == "update":
                tx.add_update(path, data)
            elif op_type == "delete":
                tx.add_delete(path)
            elif op_type == "move":
                tx.add_move(path, data)
            else:
                raise ValueError(f"Unknown operation type: {op_type}")
