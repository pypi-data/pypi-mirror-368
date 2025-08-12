"""Clear all dependencies command for Gira tickets."""

import json
from typing import List, Optional
from datetime import datetime, timezone

import typer
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.transaction import atomic_operation, TransactionError


def clear_deps(
    ticket_ids: List[str] = typer.Argument(..., help="Ticket IDs to clear all dependencies from"),
    no_reciprocal: bool = typer.Option(False, "--no-reciprocal", help="Don't remove reciprocal relationships"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying them"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
    transaction: bool = typer.Option(False, "--transaction", help="Execute all operations atomically with rollback on failure"),
) -> None:
    """Clear all dependencies from one or more tickets.
    
    This is a convenience command equivalent to:
    gira ticket bulk-remove-deps TICKET_IDS --all
    
    Examples:
        # Clear all dependencies from a single ticket
        gira ticket clear-deps PROJ-123
        
        # Clear dependencies from multiple tickets
        gira ticket clear-deps PROJ-123 PROJ-124 PROJ-125
        
        # Clear without removing reciprocal relationships
        gira ticket clear-deps PROJ-123 --no-reciprocal
        
        # Preview changes first
        gira ticket clear-deps PROJ-123 --dry-run
    """
    root = ensure_gira_project()
    
    # Normalize ticket IDs
    ticket_ids = [tid.upper() for tid in ticket_ids]
    
    # Find and validate all tickets
    if not quiet:
        console.print("\n[bold]Validating tickets...[/bold]")
    
    tickets_to_clear = []
    errors = []
    total_deps_to_remove = 0
    
    for ticket_id in ticket_ids:
        ticket, ticket_path = find_ticket(ticket_id, root)
        if not ticket:
            errors.append(f"Ticket {ticket_id} not found")
            continue
        
        if not ticket.blocked_by:
            errors.append(f"Ticket {ticket_id} has no dependencies to clear")
            continue
        
        tickets_to_clear.append({
            "ticket": ticket,
            "ticket_path": ticket_path,
            "ticket_id": ticket_id,
            "dependencies": ticket.blocked_by.copy()
        })
        total_deps_to_remove += len(ticket.blocked_by)
    
    # Display errors if any
    if errors:
        if output == "json":
            console.print_json(json.dumps({"validation_errors": errors}, indent=2))
        else:
            console.print("\n[red]Validation errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
        
        if not tickets_to_clear:
            raise typer.Exit(1)
    
    # Show preview in dry-run mode
    if dry_run:
        _display_dry_run_preview(tickets_to_clear, no_reciprocal, total_deps_to_remove, output)
        return
    
    # Confirmation prompt
    if not force and not quiet and output != "json":
        _display_confirmation_table(tickets_to_clear, no_reciprocal, total_deps_to_remove)
        
        confirm = typer.confirm(
            f"\nThis will remove {total_deps_to_remove} dependencies from {len(tickets_to_clear)} tickets. Continue?",
            default=False
        )
        if not confirm:
            console.print("[yellow]Operation cancelled[/yellow]")
            raise typer.Exit(0)
    
    # Apply the changes
    if not quiet:
        if transaction:
            console.print("\n[bold]Clearing dependencies atomically...[/bold]")
        else:
            console.print("\n[bold]Clearing dependencies...[/bold]")
    
    results = _clear_dependencies(tickets_to_clear, no_reciprocal, root, quiet, transaction)
    
    # Display results
    _display_results(results, output)


def _display_dry_run_preview(tickets_to_clear: List[dict], no_reciprocal: bool, total_deps: int, output_format: str) -> None:
    """Display preview of changes in dry-run mode."""
    if output_format == "json":
        preview_data = {
            "dry_run": True,
            "tickets": [
                {
                    "ticket_id": item["ticket_id"],
                    "dependencies_to_remove": item["dependencies"]
                }
                for item in tickets_to_clear
            ],
            "total_dependencies": total_deps,
            "remove_reciprocal": not no_reciprocal
        }
        console.print_json(json.dumps(preview_data, indent=2))
    else:
        console.print("\n[yellow]DRY RUN - No changes will be made[/yellow]")
        _display_confirmation_table(tickets_to_clear, no_reciprocal, total_deps)


def _display_confirmation_table(tickets_to_clear: List[dict], no_reciprocal: bool, total_deps: int) -> None:
    """Display a table showing what will be cleared."""
    table = Table(title=f"Dependencies to Clear ({total_deps} total)")
    table.add_column("Ticket", style="cyan")
    table.add_column("Current Dependencies", style="yellow")
    table.add_column("Count", justify="right", style="magenta")
    
    for item in tickets_to_clear:
        deps_str = ", ".join(item["dependencies"])
        if len(deps_str) > 50:
            deps_str = deps_str[:47] + "..."
        table.add_row(
            item["ticket_id"],
            deps_str,
            str(len(item["dependencies"]))
        )
    
    console.print(table)
    
    if not no_reciprocal:
        console.print("\n[dim]Note: Reciprocal relationships will also be removed[/dim]")


def _clear_dependencies(
    tickets_to_clear: List[dict], 
    no_reciprocal: bool,
    root,
    quiet: bool,
    use_transaction: bool = False
) -> dict:
    """Clear all dependencies from the specified tickets."""
    if use_transaction:
        return _clear_dependencies_transactional(tickets_to_clear, no_reciprocal, root, quiet)
    successful = []
    failed = []
    modified_tickets = {}  # Changed from set to dict to avoid hashable issues
    reciprocal_tickets = {}
    
    # Progress tracking
    if not quiet:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
        task = progress.add_task("Clearing dependencies", total=len(tickets_to_clear))
        progress.start()
    
    try:
        # First pass: clear dependencies from target tickets
        for item in tickets_to_clear:
            ticket = item["ticket"]
            ticket_path = item["ticket_path"]
            ticket_id = item["ticket_id"]
            dependencies = item["dependencies"]
            
            try:
                # Clear all blocked_by dependencies
                ticket.blocked_by = []
                modified_tickets[ticket_id] = (ticket, ticket_path)
                
                # Track for reciprocal removal
                if not no_reciprocal:
                    for dep_id in dependencies:
                        if dep_id not in reciprocal_tickets:
                            reciprocal_tickets[dep_id] = []
                        reciprocal_tickets[dep_id].append(ticket_id)
                
                successful.append({
                    "ticket_id": ticket_id,
                    "cleared_dependencies": dependencies,
                    "count": len(dependencies)
                })
                
            except Exception as e:
                failed.append({
                    "ticket_id": ticket_id,
                    "error": str(e)
                })
            
            if not quiet:
                progress.update(task, advance=1)
        
        # Second pass: remove reciprocal relationships
        if not no_reciprocal and reciprocal_tickets:
            if not quiet:
                progress.update(task, description="Removing reciprocal relationships...")
            
            for dep_id, blocking_tickets in reciprocal_tickets.items():
                # Check if this ticket is already modified (don't reload from disk)
                if dep_id in modified_tickets:
                    dep_ticket, dep_path = modified_tickets[dep_id]
                else:
                    dep_ticket, dep_path = find_ticket(dep_id, root)
                
                if dep_ticket:
                    # Remove all blocking tickets from this dependency's blocks list
                    original_blocks = len(dep_ticket.blocks)
                    dep_ticket.blocks = [bid for bid in dep_ticket.blocks if bid not in blocking_tickets]
                    
                    if len(dep_ticket.blocks) < original_blocks:
                        modified_tickets[dep_id] = (dep_ticket, dep_path)
        
        # Save all modified tickets
        if not quiet:
            progress.update(task, description="Saving changes...")
        
        timestamp = datetime.now(timezone.utc)
        for ticket_id, (ticket, ticket_path) in modified_tickets.items():
            ticket.updated_at = timestamp
            ticket.save_to_json_file(str(ticket_path))
    
    finally:
        if not quiet:
            progress.stop()
    
    return {
        "successful": successful,
        "failed": failed,
        "total_tickets_modified": len(modified_tickets),
        "reciprocal_tickets_updated": len(reciprocal_tickets) if not no_reciprocal else 0
    }


def _display_results(results: dict, output_format: str) -> None:
    """Display operation results."""
    if output_format == "json":
        console.print_json(json.dumps({
            "successful": len(results["successful"]),
            "failed": len(results["failed"]),
            "total_tickets_modified": results["total_tickets_modified"],
            "reciprocal_tickets_updated": results["reciprocal_tickets_updated"],
            "cleared": results["successful"],
            "errors": results["failed"]
        }, indent=2))
    else:
        # Summary
        console.print(f"\n[bold]Summary:[/bold]")
        
        total_deps_cleared = sum(item["count"] for item in results["successful"])
        console.print(f"  ✅ Successfully cleared: {len(results['successful'])} tickets")
        console.print(f"  🔗 Total dependencies removed: {total_deps_cleared}")
        console.print(f"  📝 Total tickets modified: {results['total_tickets_modified']}")
        
        if results["reciprocal_tickets_updated"] > 0:
            console.print(f"  ↔️  Reciprocal tickets updated: {results['reciprocal_tickets_updated']}")
        
        if results["failed"]:
            console.print(f"  ❌ Failed: {len(results['failed'])}")
            console.print("\n[red]Failed operations:[/red]")
            for failure in results["failed"]:
                console.print(f"  • {failure['ticket_id']}: {failure['error']}")
        
        # Show details for successful operations
        if results["successful"] and len(results["successful"]) <= 10:
            console.print("\n[green]Cleared dependencies:[/green]")
            for item in results["successful"]:
                console.print(f"  • {item['ticket_id']}: Removed {item['count']} dependencies")


def _clear_dependencies_transactional(
    tickets_to_clear: List[dict], 
    no_reciprocal: bool,
    root,
    quiet: bool
) -> dict:
    """Clear dependencies atomically with transaction support."""
    from uuid import uuid4
    
    transaction_id = str(uuid4())
    successful = []
    modified_tickets = {}  # Maps ticket_id to modified ticket data
    reciprocal_tickets = {}
    
    try:
        with atomic_operation(transaction_id) as tx:
            # First, load all ticket data into memory
            if not quiet:
                console.print("[dim]Loading tickets...[/dim]")
            
            # Collect all reciprocal tickets that need to be loaded
            reciprocal_ids = set()
            if not no_reciprocal:
                for item in tickets_to_clear:
                    reciprocal_ids.update(item["dependencies"])
            
            # Load reciprocal tickets
            reciprocal_ticket_cache = {}
            for dep_id in reciprocal_ids:
                dep_ticket, dep_path = find_ticket(dep_id, root)
                if dep_ticket:
                    reciprocal_ticket_cache[dep_id] = (dep_ticket, dep_path)
            
            # Apply all changes in memory first
            if not quiet:
                console.print(f"[dim]Preparing to clear dependencies from {len(tickets_to_clear)} tickets...[/dim]")
            
            # First pass: clear dependencies from target tickets
            for item in tickets_to_clear:
                ticket = item["ticket"]
                ticket_path = item["ticket_path"]
                ticket_id = item["ticket_id"]
                dependencies = item["dependencies"]
                
                # Create modified ticket data
                ticket_dict = ticket.model_dump()
                ticket_dict["blocked_by"] = []
                modified_tickets[ticket_id] = (ticket_dict, ticket_path)
                
                # Track for reciprocal removal
                if not no_reciprocal:
                    for dep_id in dependencies:
                        if dep_id not in reciprocal_tickets:
                            reciprocal_tickets[dep_id] = []
                        reciprocal_tickets[dep_id].append(ticket_id)
                
                successful.append({
                    "ticket_id": ticket_id,
                    "cleared_dependencies": dependencies,
                    "count": len(dependencies)
                })
            
            # Second pass: remove reciprocal relationships
            if not no_reciprocal and reciprocal_tickets:
                for dep_id, blocking_tickets in reciprocal_tickets.items():
                    if dep_id in reciprocal_ticket_cache:
                        dep_ticket, dep_path = reciprocal_ticket_cache[dep_id]
                        
                        # Create or get modified ticket data
                        if dep_id in modified_tickets:
                            dep_dict, _ = modified_tickets[dep_id]
                        else:
                            dep_dict = dep_ticket.model_dump()
                        
                        # Remove blocking tickets from blocks list
                        original_blocks = len(dep_dict["blocks"])
                        dep_dict["blocks"] = [bid for bid in dep_dict["blocks"] if bid not in blocking_tickets]
                        
                        if len(dep_dict["blocks"]) < original_blocks:
                            modified_tickets[dep_id] = (dep_dict, dep_path)
            
            # Update timestamps
            timestamp = datetime.now(timezone.utc).isoformat()
            for ticket_id, (ticket_dict, _) in modified_tickets.items():
                ticket_dict["updated_at"] = timestamp
            
            # Add all updates to transaction
            for ticket_id, (ticket_dict, ticket_path) in modified_tickets.items():
                tx.add_update(ticket_path, ticket_dict)
            
            # Transaction commits automatically on context exit
            
        # If we get here, all updates succeeded
        return {
            "successful": successful,
            "failed": [],
            "total_tickets_modified": len(modified_tickets),
            "reciprocal_tickets_updated": len(reciprocal_tickets) if not no_reciprocal else 0,
            "transaction_id": transaction_id
        }
        
    except TransactionError as e:
        if not quiet:
            console.print(f"\n[red]Transaction failed: {e}[/red]")
            console.print("[yellow]All changes have been rolled back[/yellow]")
        
        return {
            "successful": [],
            "failed": [{"error": str(e), "transaction_id": transaction_id}],
            "total_tickets_modified": 0,
            "reciprocal_tickets_updated": 0,
            "transaction_id": transaction_id,
            "rolled_back": True
        }
    except Exception as e:
        return {
            "successful": [],
            "failed": [{"error": str(e)}],
            "total_tickets_modified": 0,
            "reciprocal_tickets_updated": 0
        }