"""Bulk remove dependencies command for Gira tickets."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.csv_utils import CSVReader
from gira.utils.transaction import atomic_operation, TransactionError


def bulk_remove_deps(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket IDs to remove dependencies from (optional if using file input)"),
    deps: Optional[str] = typer.Option(None, "--deps", "-d", help="Comma-separated list of dependency IDs to remove"),
    from_csv: Optional[Path] = typer.Option(None, "--from-csv", help="CSV file with dependency mappings to remove"),
    from_json: Optional[Path] = typer.Option(None, "--from-json", help="JSON file with dependency mappings to remove"),
    all_deps: bool = typer.Option(False, "--all", help="Remove all dependencies from specified tickets"),
    no_reciprocal: bool = typer.Option(False, "--no-reciprocal", help="Don't remove reciprocal relationships"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying them"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
    transaction: bool = typer.Option(False, "--transaction", help="Execute all operations atomically with rollback on failure"),
) -> None:
    """Remove dependencies from multiple tickets at once.
    
    Examples:
        # Remove specific dependencies from multiple tickets
        gira ticket bulk-remove-deps PROJ-1 PROJ-2 --deps PROJ-3,PROJ-4
        
        # Remove all dependencies from tickets
        gira ticket bulk-remove-deps PROJ-1 PROJ-2 --all
        
        # Remove from CSV file (columns: ticket_id, dependency_id)
        gira ticket bulk-remove-deps --from-csv dependencies.csv
        
        # Remove from JSON file
        gira ticket bulk-remove-deps --from-json dependencies.json
        
        # Dry run to preview changes
        gira ticket bulk-remove-deps PROJ-1 --deps PROJ-2,PROJ-3 --dry-run
    """
    root = ensure_gira_project()
    
    # Parse input and validate arguments
    operations = _parse_input(ticket_ids, deps, all_deps, from_csv, from_json)
    if not operations:
        console.print("[red]Error:[/red] No operations specified. Provide ticket IDs with --deps/--all, or use --from-csv/--from-json")
        raise typer.Exit(1)
    
    # Validate all operations
    if not quiet:
        console.print("\n[bold]Validating dependencies to remove...[/bold]")
    
    validation_results = _validate_operations(operations, root)
    
    # Display validation results
    if validation_results["errors"]:
        _display_validation_errors(validation_results["errors"], output)
        if not dry_run:
            raise typer.Exit(1)
    
    # Show preview in dry-run mode
    if dry_run:
        _display_dry_run_preview(validation_results["valid"], no_reciprocal, output)
        return
    
    # Apply the changes
    if not quiet:
        if transaction:
            console.print("\n[bold]Removing dependencies atomically...[/bold]")
        else:
            console.print("\n[bold]Removing dependencies...[/bold]")
    
    results = _apply_removals(validation_results["valid"], no_reciprocal, root, quiet, transaction)
    
    # Display results
    _display_results(results, output)
    
    # Exit with error if any operations failed
    if results["failed"]:
        raise typer.Exit(1)


def _parse_input(
    ticket_ids: Optional[List[str]], 
    deps: Optional[str],
    all_deps: bool,
    from_csv: Optional[Path], 
    from_json: Optional[Path]
) -> List[Dict[str, Any]]:
    """Parse input arguments and return list of operations."""
    operations = []
    
    # Command line arguments
    if ticket_ids:
        if all_deps:
            # Remove all dependencies from specified tickets
            for ticket_id in ticket_ids:
                operations.append({
                    "ticket_id": ticket_id.upper(),
                    "dependency_id": "*",  # Special marker for all dependencies
                    "remove_all": True
                })
        elif deps:
            # Remove specific dependencies
            dependency_ids = [d.strip().upper() for d in deps.split(",") if d.strip()]
            for ticket_id in ticket_ids:
                for dep_id in dependency_ids:
                    operations.append({
                        "ticket_id": ticket_id.upper(),
                        "dependency_id": dep_id,
                        "remove_all": False
                    })
    
    # CSV file input
    if from_csv:
        if not from_csv.exists():
            console.print(f"[red]Error:[/red] CSV file not found: {from_csv}")
            raise typer.Exit(1)
        
        with open(from_csv, 'r') as f:
            csv_reader = CSVReader(f)
            rows = csv_reader.read_csv_dicts()
            
        for row in rows:
            if "ticket_id" in row:
                # Check if it's a remove-all operation
                if "dependency_id" in row and row["dependency_id"].strip() in ["*", "all", "ALL"]:
                    operations.append({
                        "ticket_id": row["ticket_id"].upper(),
                        "dependency_id": "*",
                        "remove_all": True
                    })
                elif "dependency_id" in row:
                    operations.append({
                        "ticket_id": row["ticket_id"].upper(),
                        "dependency_id": row["dependency_id"].upper(),
                        "remove_all": False
                    })
    
    # JSON file input
    if from_json:
        if not from_json.exists():
            console.print(f"[red]Error:[/red] JSON file not found: {from_json}")
            raise typer.Exit(1)
        
        with open(from_json, 'r') as f:
            data = json.load(f)
        
        # Support both flat array and nested format
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "ticket_id" in item:
                    ticket_id = item["ticket_id"].upper()
                    
                    # Check for remove_all flag
                    if item.get("remove_all", False):
                        operations.append({
                            "ticket_id": ticket_id,
                            "dependency_id": "*",
                            "remove_all": True
                        })
                    elif "dependency_id" in item:
                        operations.append({
                            "ticket_id": ticket_id,
                            "dependency_id": item["dependency_id"].upper(),
                            "remove_all": False
                        })
                    elif "dependencies" in item:
                        # Support format: {"ticket_id": "PROJ-1", "dependencies": ["PROJ-2", "PROJ-3"]}
                        for dep in item["dependencies"]:
                            operations.append({
                                "ticket_id": ticket_id,
                                "dependency_id": dep.upper(),
                                "remove_all": False
                            })
        elif isinstance(data, dict):
            # Support format: {"PROJ-1": ["PROJ-2", "PROJ-3"], ...}
            for ticket_id, deps in data.items():
                if isinstance(deps, list):
                    for dep in deps:
                        if dep in ["*", "all", "ALL"]:
                            operations.append({
                                "ticket_id": ticket_id.upper(),
                                "dependency_id": "*",
                                "remove_all": True
                            })
                        else:
                            operations.append({
                                "ticket_id": ticket_id.upper(),
                                "dependency_id": dep.upper(),
                                "remove_all": False
                            })
    
    return operations


def _validate_operations(operations: List[Dict[str, Any]], root: Path) -> Dict[str, Any]:
    """Validate all removal operations and return valid and error lists."""
    valid = []
    errors = []
    ticket_cache = {}
    
    # Group operations by ticket for efficient processing
    ticket_operations = {}
    for op in operations:
        ticket_id = op["ticket_id"]
        if ticket_id not in ticket_operations:
            ticket_operations[ticket_id] = []
        ticket_operations[ticket_id].append(op)
    
    for ticket_id, ops in ticket_operations.items():
        # Find ticket
        ticket, ticket_path = find_ticket(ticket_id, root)
        if not ticket:
            for op in ops:
                errors.append({
                    "operation": op,
                    "error": f"Ticket {ticket_id} not found"
                })
            continue
        
        ticket_cache[ticket_id] = (ticket, ticket_path)
        
        # Process operations for this ticket
        for op in ops:
            if op["remove_all"]:
                # For remove-all, just check if ticket has dependencies
                if not ticket.blocked_by:
                    errors.append({
                        "operation": op,
                        "error": f"Ticket {ticket_id} has no dependencies to remove"
                    })
                else:
                    valid.append(op)
            else:
                # For specific dependency removal
                dep_id = op["dependency_id"]
                
                # Check if dependency exists
                if dep_id not in ticket.blocked_by:
                    errors.append({
                        "operation": op,
                        "error": f"Ticket {ticket_id} is not blocked by {dep_id}"
                    })
                    continue
                
                # Find dependency ticket for reciprocal check
                if dep_id not in ticket_cache:
                    dep_ticket, dep_path = find_ticket(dep_id, root)
                    if dep_ticket:
                        ticket_cache[dep_id] = (dep_ticket, dep_path)
                
                valid.append(op)
    
    return {
        "valid": valid,
        "errors": errors,
        "ticket_cache": ticket_cache
    }


def _apply_removals(
    operations: List[Dict[str, Any]], 
    no_reciprocal: bool,
    root: Path,
    quiet: bool,
    use_transaction: bool = False
) -> Dict[str, List]:
    """Apply the dependency removal changes."""
    if use_transaction:
        return _apply_removals_transactional(operations, no_reciprocal, root, quiet)
    successful = []
    failed = []
    ticket_cache = {}
    modified_tickets = set()
    
    # Progress tracking
    if not quiet:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
        task = progress.add_task("Removing dependencies", total=len(operations))
        progress.start()
    
    try:
        for op in operations:
            ticket_id = op["ticket_id"]
            
            try:
                # Get ticket (with caching)
                if ticket_id not in ticket_cache:
                    ticket, ticket_path = find_ticket(ticket_id, root)
                    ticket_cache[ticket_id] = (ticket, ticket_path)
                else:
                    ticket, ticket_path = ticket_cache[ticket_id]
                
                if op["remove_all"]:
                    # Remove all dependencies
                    removed_deps = ticket.blocked_by.copy()
                    ticket.blocked_by = []
                    modified_tickets.add(ticket_id)
                    
                    # Remove reciprocals if requested
                    if not no_reciprocal:
                        for dep_id in removed_deps:
                            if dep_id not in ticket_cache:
                                dep_ticket, dep_path = find_ticket(dep_id, root)
                                if dep_ticket:
                                    ticket_cache[dep_id] = (dep_ticket, dep_path)
                            
                            if dep_id in ticket_cache:
                                dep_ticket, _ = ticket_cache[dep_id]
                                if ticket_id in dep_ticket.blocks:
                                    dep_ticket.blocks.remove(ticket_id)
                                    modified_tickets.add(dep_id)
                    
                    successful.append({
                        "ticket_id": ticket_id,
                        "removed_dependencies": removed_deps,
                        "remove_all": True,
                        "reciprocal": not no_reciprocal
                    })
                else:
                    # Remove specific dependency
                    dep_id = op["dependency_id"]
                    
                    if dep_id in ticket.blocked_by:
                        ticket.blocked_by.remove(dep_id)
                        modified_tickets.add(ticket_id)
                        
                        # Remove reciprocal if requested
                        if not no_reciprocal:
                            if dep_id not in ticket_cache:
                                dep_ticket, dep_path = find_ticket(dep_id, root)
                                if dep_ticket:
                                    ticket_cache[dep_id] = (dep_ticket, dep_path)
                            
                            if dep_id in ticket_cache:
                                dep_ticket, _ = ticket_cache[dep_id]
                                if ticket_id in dep_ticket.blocks:
                                    dep_ticket.blocks.remove(ticket_id)
                                    modified_tickets.add(dep_id)
                        
                        successful.append({
                            "ticket_id": ticket_id,
                            "dependency_id": dep_id,
                            "reciprocal": not no_reciprocal
                        })
                
            except Exception as e:
                failed.append({
                    "operation": op,
                    "error": str(e)
                })
            
            if not quiet:
                progress.update(task, advance=1)
        
        # Save all modified tickets
        if not quiet:
            progress.update(task, description="Saving changes...")
        
        timestamp = datetime.now(timezone.utc)
        for ticket_id in modified_tickets:
            if ticket_id in ticket_cache:
                ticket, ticket_path = ticket_cache[ticket_id]
                ticket.updated_at = timestamp
                ticket.save_to_json_file(str(ticket_path))
    
    finally:
        if not quiet:
            progress.stop()
    
    return {
        "successful": successful,
        "failed": failed,
        "total_tickets_modified": len(modified_tickets)
    }


def _display_validation_errors(errors: List[Dict], output_format: str) -> None:
    """Display validation errors."""
    if output_format == "json":
        console.print_json(json.dumps({"validation_errors": errors}, indent=2))
    else:
        console.print("\n[red]Validation errors found:[/red]")
        for error in errors:
            op = error["operation"]
            if op.get("remove_all"):
                console.print(f"  • {op['ticket_id']}: {error['error']}")
            else:
                console.print(f"  • {op['ticket_id']} → {op['dependency_id']}: {error['error']}")


def _display_dry_run_preview(operations: List[Dict], no_reciprocal: bool, output_format: str) -> None:
    """Display preview of changes in dry-run mode."""
    if output_format == "json":
        console.print_json(json.dumps({
            "dry_run": True,
            "operations": operations,
            "reciprocal": not no_reciprocal
        }, indent=2))
    else:
        console.print("\n[yellow]DRY RUN - No changes will be made[/yellow]")
        console.print(f"\nWould remove {len(operations)} dependencies:")
        
        table = Table(title="Planned Removals")
        table.add_column("Ticket", style="cyan")
        table.add_column("Dependencies to Remove", style="yellow")
        if not no_reciprocal:
            table.add_column("Reciprocal Removal", style="green")
        
        for op in operations[:10]:  # Show first 10
            if op.get("remove_all"):
                if no_reciprocal:
                    table.add_row(op["ticket_id"], "ALL dependencies")
                else:
                    table.add_row(
                        op["ticket_id"], 
                        "ALL dependencies",
                        "Remove from blocking tickets"
                    )
            else:
                if no_reciprocal:
                    table.add_row(op["ticket_id"], op["dependency_id"])
                else:
                    table.add_row(
                        op["ticket_id"], 
                        op["dependency_id"],
                        f"Remove {op['ticket_id']} from {op['dependency_id']}'s blocks"
                    )
        
        if len(operations) > 10:
            if no_reciprocal:
                table.add_row("...", f"... and {len(operations) - 10} more")
            else:
                table.add_row("...", f"... and {len(operations) - 10} more", "...")
        
        console.print(table)


def _display_results(results: Dict, output_format: str) -> None:
    """Display operation results."""
    if output_format == "json":
        console.print_json(json.dumps({
            "successful": len(results["successful"]),
            "failed": len(results["failed"]),
            "total_tickets_modified": results["total_tickets_modified"],
            "operations": results["successful"],
            "errors": results["failed"]
        }, indent=2))
    else:
        # Summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  ✅ Successfully removed: {len(results['successful'])} dependencies")
        console.print(f"  📝 Total tickets modified: {results['total_tickets_modified']}")
        
        if results["failed"]:
            console.print(f"  ❌ Failed: {len(results['failed'])}")
            console.print("\n[red]Failed operations:[/red]")
            for failure in results["failed"]:
                op = failure["operation"]
                if op.get("remove_all"):
                    console.print(f"  • {op['ticket_id']}: {failure['error']}")
                else:
                    console.print(f"  • {op['ticket_id']} → {op['dependency_id']}: {failure['error']}")


def _apply_removals_transactional(
    operations: List[Dict[str, Any]], 
    no_reciprocal: bool,
    root: Path,
    quiet: bool
) -> Dict[str, List]:
    """Apply dependency removals atomically with transaction support."""
    from uuid import uuid4
    
    transaction_id = str(uuid4())
    successful = []
    ticket_cache = {}
    modified_tickets = {}  # Maps ticket_id to modified ticket data
    
    try:
        with atomic_operation(transaction_id) as tx:
            # First, load all tickets that will be modified
            if not quiet:
                console.print("[dim]Loading tickets...[/dim]")
            
            # Identify all tickets that need to be loaded
            tickets_to_load = set()
            for op in operations:
                tickets_to_load.add(op["ticket_id"])
                if not no_reciprocal and not op.get("remove_all"):
                    tickets_to_load.add(op["dependency_id"])
            
            # Load all tickets
            for ticket_id in tickets_to_load:
                if ticket_id not in ticket_cache:
                    ticket, ticket_path = find_ticket(ticket_id, root)
                    if ticket:
                        ticket_cache[ticket_id] = (ticket, ticket_path)
            
            # For remove-all operations, also load dependency tickets
            if not no_reciprocal:
                for op in operations:
                    if op.get("remove_all") and op["ticket_id"] in ticket_cache:
                        ticket, _ = ticket_cache[op["ticket_id"]]
                        for dep_id in ticket.blocked_by:
                            if dep_id not in ticket_cache:
                                dep_ticket, dep_path = find_ticket(dep_id, root)
                                if dep_ticket:
                                    ticket_cache[dep_id] = (dep_ticket, dep_path)
            
            # Apply all changes in memory first
            if not quiet:
                console.print(f"[dim]Preparing {len(operations)} dependency removals...[/dim]")
            
            for op in operations:
                ticket_id = op["ticket_id"]
                
                if ticket_id in ticket_cache:
                    ticket, ticket_path = ticket_cache[ticket_id]
                    
                    # Get or create modified ticket data
                    if ticket_id not in modified_tickets:
                        modified_tickets[ticket_id] = ticket.model_dump()
                    
                    if op.get("remove_all"):
                        # Remove all dependencies
                        removed_deps = modified_tickets[ticket_id]["blocked_by"].copy()
                        modified_tickets[ticket_id]["blocked_by"] = []
                        
                        # Remove reciprocals if requested
                        if not no_reciprocal:
                            for dep_id in removed_deps:
                                if dep_id in ticket_cache:
                                    if dep_id not in modified_tickets:
                                        dep_ticket, _ = ticket_cache[dep_id]
                                        modified_tickets[dep_id] = dep_ticket.model_dump()
                                    
                                    if ticket_id in modified_tickets[dep_id]["blocks"]:
                                        modified_tickets[dep_id]["blocks"].remove(ticket_id)
                        
                        successful.append({
                            "ticket_id": ticket_id,
                            "removed_dependencies": removed_deps,
                            "remove_all": True,
                            "reciprocal": not no_reciprocal
                        })
                    else:
                        # Remove specific dependency
                        dep_id = op["dependency_id"]
                        
                        if dep_id in modified_tickets[ticket_id]["blocked_by"]:
                            modified_tickets[ticket_id]["blocked_by"].remove(dep_id)
                            
                            # Remove reciprocal if requested
                            if not no_reciprocal and dep_id in ticket_cache:
                                if dep_id not in modified_tickets:
                                    dep_ticket, _ = ticket_cache[dep_id]
                                    modified_tickets[dep_id] = dep_ticket.model_dump()
                                
                                if ticket_id in modified_tickets[dep_id]["blocks"]:
                                    modified_tickets[dep_id]["blocks"].remove(ticket_id)
                            
                            successful.append({
                                "ticket_id": ticket_id,
                                "dependency_id": dep_id,
                                "reciprocal": not no_reciprocal
                            })
            
            # Update timestamps
            timestamp = datetime.now(timezone.utc).isoformat()
            for ticket_id in modified_tickets:
                modified_tickets[ticket_id]["updated_at"] = timestamp
            
            # Add all updates to transaction
            for ticket_id, ticket_data in modified_tickets.items():
                if ticket_id in ticket_cache:
                    _, ticket_path = ticket_cache[ticket_id]
                    tx.add_update(ticket_path, ticket_data)
            
            # Transaction commits automatically on context exit
            
        # If we get here, all updates succeeded
        return {
            "successful": successful,
            "failed": [],
            "total_tickets_modified": len(modified_tickets),
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
            "transaction_id": transaction_id,
            "rolled_back": True
        }
    except Exception as e:
        return {
            "successful": [],
            "failed": [{"error": str(e)}],
            "total_tickets_modified": 0
        }