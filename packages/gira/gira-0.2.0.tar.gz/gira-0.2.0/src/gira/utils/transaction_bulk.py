"""Transactional support for bulk operations."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

from gira.models import Ticket
from gira.utils.console import console
from gira.utils.transaction import TransactionError, atomic_operation


class TransactionalBulkOperation:
    """Wrapper for executing bulk operations with transaction support."""

    def __init__(self,
                 operation_name: str,
                 use_transaction: bool = False,
                 transaction_id: Optional[str] = None,
                 log_dir: Optional[Path] = None):
        """Initialize transactional bulk operation.
        
        Args:
            operation_name: Name of the operation for logging
            use_transaction: Whether to use transaction support
            transaction_id: Optional transaction ID
            log_dir: Optional directory for transaction logs
        """
        self.operation_name = operation_name
        self.use_transaction = use_transaction
        self.transaction_id = transaction_id
        self.log_dir = log_dir or Path.home() / ".gira" / "transactions"
        self.operations: List[Tuple[Callable, tuple, dict]] = []
        self.results = {"successful": [], "failed": []}

    def add_operation(self, func: Callable, *args, **kwargs) -> None:
        """Add an operation to be executed."""
        self.operations.append((func, args, kwargs))

    def execute(self, show_progress: bool = True) -> Dict[str, List]:
        """Execute all operations, with optional transaction support.
        
        Returns:
            Dictionary with 'successful' and 'failed' lists
        """
        if self.use_transaction:
            return self._execute_transactional(show_progress)
        else:
            return self._execute_non_transactional(show_progress)

    def _execute_non_transactional(self, show_progress: bool) -> Dict[str, List]:
        """Execute operations without transaction support (current behavior)."""
        if show_progress and self.operations:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"Executing {self.operation_name}", total=len(self.operations))

                for func, args, kwargs in self.operations:
                    try:
                        result = func(*args, **kwargs)
                        self.results["successful"].append(result)
                    except Exception as e:
                        self.results["failed"].append({
                            "operation": f"{func.__name__}({args}, {kwargs})",
                            "error": str(e)
                        })
                    progress.update(task, advance=1)
        else:
            # No progress bar
            for func, args, kwargs in self.operations:
                try:
                    result = func(*args, **kwargs)
                    self.results["successful"].append(result)
                except Exception as e:
                    self.results["failed"].append({
                        "operation": f"{func.__name__}({args}, {kwargs})",
                        "error": str(e)
                    })

        return self.results

    def _execute_transactional(self, show_progress: bool) -> Dict[str, List]:
        """Execute operations with transaction support."""
        # First, validate all operations and collect file changes
        file_operations = []
        validation_errors = []

        if show_progress:
            console.print(f"\n[bold]Validating {self.operation_name} operations...[/bold]")

        for func, args, kwargs in self.operations:
            try:
                # Get file operations without executing
                ops = self._extract_file_operations(func, args, kwargs)
                file_operations.extend(ops)
            except Exception as e:
                validation_errors.append({
                    "operation": f"{func.__name__}({args}, {kwargs})",
                    "error": str(e)
                })

        if validation_errors:
            console.print(f"\n[red]Validation failed for {len(validation_errors)} operations[/red]")
            for error in validation_errors:
                console.print(f"  • {error['operation']}: {error['error']}")
            self.results["failed"] = validation_errors
            return self.results

        # Execute all operations atomically
        try:
            with atomic_operation(self.transaction_id, self.log_dir) as tx:
                if show_progress:
                    console.print(f"\n[bold]Executing {self.operation_name} atomically...[/bold]")

                # Add all file operations to transaction
                for op_type, path, data in file_operations:
                    if op_type == "create":
                        tx.add_create(path, data)
                    elif op_type == "update":
                        tx.add_update(path, data)
                    elif op_type == "delete":
                        tx.add_delete(path)
                    elif op_type == "move":
                        tx.add_move(path, data)

                # Transaction commits automatically on context exit
                self.results["successful"] = [{"transaction_id": self.transaction_id, "operations": len(file_operations)}]

                if show_progress:
                    console.print(f"[green]✓ Successfully completed {len(file_operations)} operations atomically[/green]")

        except TransactionError as e:
            console.print(f"\n[red]Transaction failed: {e}[/red]")
            console.print("[yellow]All changes have been rolled back[/yellow]")
            self.results["failed"] = [{"error": str(e), "rolled_back": True}]
            raise

        return self.results

    def _extract_file_operations(self, func: Callable, args: tuple, kwargs: dict) -> List[Tuple[str, Path, Any]]:
        """Extract file operations from a function without executing it.
        
        This is a placeholder that needs to be implemented for each operation type.
        For now, we'll execute the function in a dry-run mode if available.
        """
        # This would need to be customized for each operation type
        # For demonstration, returning empty list
        return []


def create_transactional_ticket_updater(use_transaction: bool = False) -> Callable:
    """Create a ticket update function that supports transactions.
    
    Args:
        use_transaction: Whether to use transaction support
        
    Returns:
        Function that updates a ticket with optional transaction support
    """
    def update_ticket(ticket: Ticket, ticket_path: Path, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a ticket with the given changes."""
        # Apply updates to ticket
        for field, value in updates.items():
            if hasattr(ticket, field):
                setattr(ticket, field, value)

        # Update timestamp
        from datetime import datetime, timezone
        ticket.updated_at = datetime.now(timezone.utc)

        # Save to file
        ticket.save_to_json_file(str(ticket_path))

        return {
            "ticket_id": ticket.id,
            "updated_fields": list(updates.keys()),
            "path": str(ticket_path)
        }

    return update_ticket


def transactional_bulk_update(
    tickets: List[Tuple[Ticket, Path]],
    updates: Dict[str, Any],
    use_transaction: bool = False,
    show_progress: bool = True
) -> Dict[str, List]:
    """Update multiple tickets with transaction support.
    
    Args:
        tickets: List of (ticket, path) tuples
        updates: Dictionary of field updates
        use_transaction: Whether to use transaction support
        show_progress: Whether to show progress bar
        
    Returns:
        Dictionary with 'successful' and 'failed' lists
    """
    bulk_op = TransactionalBulkOperation(
        operation_name="bulk ticket update",
        use_transaction=use_transaction
    )

    updater = create_transactional_ticket_updater(use_transaction)

    # Add all update operations
    for ticket, path in tickets:
        bulk_op.add_operation(updater, ticket, path, updates)

    # Execute all operations
    return bulk_op.execute(show_progress)
