"""CLI commands for managing async operations."""

import json
import time
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from gira.api.async_ops.manager import AsyncOperationManager
from gira.api.async_ops.persistence import OperationPersistence
from gira.api.bulk.schemas import OperationStatus
from gira.utils.console import console

app = typer.Typer(
    name="operation",
    help="Manage async bulk operations",
    no_args_is_help=True
)


def get_async_manager() -> AsyncOperationManager:
    """Get or create async operation manager."""
    # In production, this would be a singleton or service
    return AsyncOperationManager()


def get_persistence() -> OperationPersistence:
    """Get operation persistence."""
    return OperationPersistence()


@app.command()
def status(
    operation_id: str = typer.Argument(..., help="Operation ID to check"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """Check the status of an async operation."""
    manager = get_async_manager()
    
    # Get operation status
    status_info = manager.get_operation_status(operation_id)
    
    if not status_info:
        console.print(f"[red]Error:[/red] Operation {operation_id} not found")
        raise typer.Exit(1)
    
    if output == "json":
        console.print_json(json.dumps(status_info, indent=2))
    else:
        # Display status
        console.print(f"\n[bold]Operation: {operation_id}[/bold]")
        console.print(f"Status: [cyan]{status_info['status']}[/cyan]")
        
        # Progress
        progress = status_info.get("progress", {})
        console.print(
            f"Progress: {progress.get('completed', 0)}/{progress.get('total', 0)} "
            f"({progress.get('percentage', 0)}%)"
        )
        
        if progress.get("current_item"):
            console.print(f"Current item: {progress['current_item']}")
        
        if progress.get("estimated_time_remaining"):
            eta = progress["estimated_time_remaining"]
            console.print(f"ETA: {eta}s")
        
        # Current step
        if status_info.get("current_step"):
            console.print(f"Step: {status_info['current_step']}")
        
        # Metrics
        metrics = status_info.get("metrics", {})
        if metrics:
            console.print("\n[bold]Metrics:[/bold]")
            console.print(f"  Items/sec: {metrics.get('items_per_second', 0):.2f}")
            console.print(f"  Elapsed: {metrics.get('elapsed_ms', 0)/1000:.1f}s")
            console.print(f"  Errors: {metrics.get('errors_count', 0)}")
            console.print(f"  Success rate: {metrics.get('success_rate', 100):.1f}%")
        
        # Cancellation
        cancellation = status_info.get("cancellation", {})
        if cancellation.get("can_cancel"):
            console.print(f"\n[dim]Can be cancelled: Yes[/dim]")
            if cancellation.get("cancel_requested"):
                console.print("[yellow]Cancellation requested[/yellow]")


@app.command()
def list(
    active: bool = typer.Option(False, "--active", help="Show only active operations"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum operations to show"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """List async operations."""
    if active:
        # List active operations
        manager = get_async_manager()
        operations = manager.list_active_operations()
    else:
        # List from persistence
        persistence = get_persistence()
        operations = persistence.list_snapshots(limit=limit)
    
    if output == "json":
        console.print_json(json.dumps(operations, indent=2))
    else:
        if not operations:
            console.print("[dim]No operations found[/dim]")
            return
        
        # Create table
        table = Table(title="Async Operations")
        table.add_column("Operation ID", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Progress")
        table.add_column("Updated")
        
        for op in operations:
            # Get progress info
            progress_str = "-"
            if "progress" in op:
                p = op["progress"]
                progress_str = f"{p.get('completed', 0)}/{p.get('total', 0)}"
            
            # Get status color
            status = op.get("status", "unknown")
            status_style = "green"
            if status == "failed":
                status_style = "red"
            elif status == "cancelled":
                status_style = "yellow"
            elif status == "in_progress":
                status_style = "blue"
            
            table.add_row(
                op.get("operation_id", "-")[:8],
                op.get("operation_type", "-"),
                f"[{status_style}]{status}[/{status_style}]",
                progress_str,
                op.get("updated_at", "-")[:19] if op.get("updated_at") else "-"
            )
        
        console.print(table)


@app.command()
def cancel(
    operation_id: str = typer.Argument(..., help="Operation ID to cancel"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Cancel a running operation."""
    if not force:
        confirm = typer.confirm(f"Cancel operation {operation_id}?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)
    
    manager = get_async_manager()
    
    if manager.cancel_operation(operation_id):
        console.print(f"[green]✓[/green] Cancellation requested for operation {operation_id}")
    else:
        console.print(f"[red]Error:[/red] Could not cancel operation {operation_id}")
        raise typer.Exit(1)


@app.command()
def wait(
    operation_id: str = typer.Argument(..., help="Operation ID to wait for"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout in seconds"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
) -> None:
    """Wait for an operation to complete."""
    manager = get_async_manager()
    
    start_time = time.time()
    last_progress = -1
    
    if not quiet:
        console.print(f"Waiting for operation {operation_id}...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=quiet
    ) as progress:
        task = progress.add_task("Waiting...", total=None)
        
        while True:
            # Check status
            status_info = manager.get_operation_status(operation_id)
            
            if not status_info:
                console.print(f"[red]Error:[/red] Operation {operation_id} not found")
                raise typer.Exit(1)
            
            # Update progress
            op_progress = status_info.get("progress", {})
            percentage = op_progress.get("percentage", 0)
            
            if percentage != last_progress:
                desc = f"Progress: {percentage:.1f}%"
                if status_info.get("current_step"):
                    desc += f" - {status_info['current_step']}"
                progress.update(task, description=desc)
                last_progress = percentage
            
            # Check if complete
            status = status_info.get("status")
            if status in ["completed", "failed", "cancelled"]:
                break
            
            # Check timeout
            if time.time() - start_time > timeout:
                console.print(f"\n[yellow]Timeout waiting for operation {operation_id}[/yellow]")
                raise typer.Exit(1)
            
            time.sleep(1)
    
    # Final status
    if status == "completed":
        console.print(f"\n[green]✓[/green] Operation {operation_id} completed successfully")
    elif status == "failed":
        console.print(f"\n[red]✗[/red] Operation {operation_id} failed")
        raise typer.Exit(1)
    elif status == "cancelled":
        console.print(f"\n[yellow]![/yellow] Operation {operation_id} was cancelled")
        raise typer.Exit(1)


@app.command()
def resume(
    all: bool = typer.Option(False, "--all", help="Resume all incomplete operations"),
    operation_id: Optional[str] = typer.Argument(None, help="Specific operation to resume"),
) -> None:
    """Resume operations from persistence."""
    manager = get_async_manager()
    
    if all:
        resumed = manager.resume_operations()
        if resumed:
            console.print(f"[green]✓[/green] Resumed {len(resumed)} operations:")
            for op_id in resumed:
                console.print(f"  - {op_id}")
        else:
            console.print("[dim]No operations to resume[/dim]")
    elif operation_id:
        # Resume specific operation
        persistence = get_persistence()
        snapshot = persistence.load_snapshot(operation_id)
        
        if not snapshot:
            console.print(f"[red]Error:[/red] Operation {operation_id} not found")
            raise typer.Exit(1)
        
        # Note: Full implementation would actually resume the operation
        console.print(f"[yellow]Resume not fully implemented for individual operations[/yellow]")
    else:
        console.print("[red]Error:[/red] Specify --all or provide an operation ID")
        raise typer.Exit(1)


@app.command()
def cleanup(
    days: int = typer.Option(7, "--days", "-d", help="Delete operations older than N days"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted"),
) -> None:
    """Clean up old operation snapshots."""
    persistence = get_persistence()
    
    if dry_run:
        # Show what would be deleted
        old_snapshots = persistence.list_snapshots()
        count = 0
        
        import time
        from datetime import datetime
        
        current_time = time.time()
        cutoff_time = days * 24 * 60 * 60
        
        for snapshot in old_snapshots:
            if snapshot.get("status") in ["completed", "failed", "cancelled"]:
                updated_str = snapshot.get("updated_at", "")
                if updated_str:
                    try:
                        updated_time = datetime.fromisoformat(updated_str).timestamp()
                        if current_time - updated_time > cutoff_time:
                            count += 1
                            console.print(
                                f"Would delete: {snapshot['operation_id']} "
                                f"({snapshot['status']}, {updated_str[:10]})"
                            )
                    except:
                        pass
        
        console.print(f"\n[dim]Would delete {count} operations[/dim]")
    else:
        deleted = persistence.cleanup_old_snapshots(days)
        console.print(f"[green]✓[/green] Deleted {deleted} old operation snapshots")


if __name__ == "__main__":
    app()