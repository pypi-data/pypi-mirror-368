"""Bulk update command for Gira tickets."""

import json
from typing import List, Optional
from pathlib import Path

import typer
from gira.utils.console import console
from gira.cli.commands.ticket.update import _apply_ticket_updates
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, process_bulk_operation
from gira.utils.ticket_utils import find_ticket
from gira.utils.transaction import atomic_operation, TransactionError

def bulk_update(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="List of ticket IDs to update (optional if using stdin)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title (applied to all tickets)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description (applied to all tickets)"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="New priority"),
    ticket_type: Optional[str] = typer.Option(None, "--type", help="New ticket type"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="New assignee (use 'none' to clear)"),
    add_labels: Optional[str] = typer.Option(None, "--add-labels", help="Labels to add (comma-separated)"),
    remove_labels: Optional[str] = typer.Option(None, "--remove-labels", help="Labels to remove (comma-separated)"),
    epic: Optional[str] = typer.Option(None, "--epic", "-e", help="New epic ID (use 'none' to clear)"),
    parent: Optional[str] = typer.Option(None, "--parent", help="New parent ID (use 'none' to clear)"),
    story_points: Optional[int] = typer.Option(None, "--story-points", "-sp", help="New story points estimate (use 0 to clear)"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket IDs"),
    strict: bool = typer.Option(False, "--strict", help="Enforce strict assignee validation (no external assignees)"),
    all_or_nothing: bool = typer.Option(False, "--all-or-nothing", help="Fail entire operation if any ticket update fails"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without saving them"),
    stdin: bool = typer.Option(False, "--stdin", help="Read CSV format from stdin (first column must be ticket ID)"),
    csv_delimiter: str = typer.Option(",", "--csv-delimiter", help="CSV delimiter character (default: comma)"),
    skip_invalid: bool = typer.Option(False, "--skip-invalid", help="Skip invalid rows and continue processing"),
    fail_on_error: bool = typer.Option(True, "--fail-on-error/--no-fail-on-error", help="Exit with error if any update fails (default: true)"),
    transaction: bool = typer.Option(False, "--transaction", help="Execute all updates atomically with rollback on failure"),
) -> None:
    """Update multiple tickets with the same changes."""
    root = ensure_gira_project()
    
    # Handle stdin CSV input
    if stdin:
        return _bulk_update_from_stdin(root, output, quiet, strict, all_or_nothing, dry_run, 
                                      csv_delimiter, skip_invalid, fail_on_error)
    
    # Require ticket IDs if not using stdin
    if not ticket_ids:
        console.print("[red]Error:[/red] Ticket IDs are required when not using --stdin")
        raise typer.Exit(1)
    
    # Check if any changes requested
    has_changes = any([
        title is not None,
        description is not None,
        status is not None,
        priority is not None,
        ticket_type is not None,
        assignee is not None,
        add_labels is not None,
        remove_labels is not None,
        epic is not None,
        parent is not None,
        story_points is not None
    ])
    
    if not has_changes:
        console.print("[yellow]Warning:[/yellow] No changes specified")
        raise typer.Exit(0)
    
    # Validate special values for description in bulk mode
    if description in ["editor", "-"]:
        console.print(f"[red]Error:[/red] Cannot use '{description}' for description in bulk update mode")
        raise typer.Exit(1)
    
    # Process tickets
    updated_tickets = []
    failed_tickets = []
    
    if not quiet:
        if transaction:
            console.print(f"[bold]Updating {len(ticket_ids)} tickets atomically...[/bold]\n")
        else:
            console.print(f"[bold]Updating {len(ticket_ids)} tickets...[/bold]\n")
    
    # If using transactions, we need to collect all updates first
    if transaction and not dry_run:
        _execute_transactional_updates(
            ticket_ids, root, quiet, output, strict,
            title, description, status, priority, ticket_type,
            assignee, add_labels, remove_labels, epic, parent, story_points
        )
        return
    
    # Non-transactional mode (current behavior)
    for ticket_id in ticket_ids:
        try:
            # Find the ticket
            ticket, ticket_path = find_ticket(ticket_id, root)
            if not ticket:
                raise ValueError(f"Ticket {ticket_id.upper()} not found")
            
            if dry_run:
                # In dry-run mode, just show what would happen
                console.print(f"[yellow]DRY RUN:[/yellow] Would update ticket [cyan]{ticket.id}[/cyan]")
                
                # Show changes that would be made
                changes = []
                if title is not None:
                    changes.append(f"  • Title: {title}")
                if description is not None:
                    desc_preview = description[:50] + "..." if len(description) > 50 else description
                    changes.append(f"  • Description: {desc_preview}")
                if status is not None:
                    changes.append(f"  • Status: {ticket.status} → {status}")
                if priority is not None:
                    changes.append(f"  • Priority: {ticket.priority} → {priority}")
                if ticket_type is not None:
                    changes.append(f"  • Type: {ticket.type} → {ticket_type}")
                if assignee is not None:
                    if assignee.lower() == "none":
                        changes.append(f"  • Assignee: [cleared]")
                    else:
                        changes.append(f"  • Assignee: {assignee}")
                if add_labels is not None:
                    changes.append(f"  • Add labels: {add_labels}")
                if remove_labels is not None:
                    changes.append(f"  • Remove labels: {remove_labels}")
                if epic is not None:
                    if epic.lower() == "none":
                        changes.append(f"  • Epic: [cleared]")
                    else:
                        changes.append(f"  • Epic: {epic}")
                if parent is not None:
                    if parent.lower() == "none":
                        changes.append(f"  • Parent: [cleared]")
                    else:
                        changes.append(f"  • Parent: {parent}")
                if story_points is not None:
                    if story_points == 0:
                        changes.append(f"  • Story points: [cleared]")
                    else:
                        changes.append(f"  • Story points: {story_points}")
                
                for change in changes:
                    console.print(change)
                console.print()
                
                updated_tickets.append(ticket)
            else:
                # Apply the updates
                _apply_ticket_updates(
                    ticket, ticket_path, root, strict,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    ticket_type=ticket_type,
                    assignee=assignee,
                    add_labels=add_labels,
                    remove_labels=remove_labels,
                    epic=epic,
                    parent=parent,
                    story_points=story_points
                )
                
                updated_tickets.append(ticket)
                
                if not quiet and output != "json":
                    console.print(f"✅ Updated ticket [cyan]{ticket.id}[/cyan]")
                    
        except Exception as e:
            failed_tickets.append((ticket_id, str(e)))
            if not quiet and output != "json":
                console.print(f"❌ Failed to update [cyan]{ticket_id}[/cyan]: {e}")
            
            # If all-or-nothing mode, stop processing
            if all_or_nothing:
                console.print("\n[red]Error:[/red] Stopping due to --all-or-nothing flag")
                raise typer.Exit(1)
    
    # Output results
    if dry_run:
        console.print(f"\n[dim]No changes were made (dry run)[/dim]")
        return
    
    if output == "json":
        import json
        result = {
            "updated": [t.id for t in updated_tickets],
            "failed": [{"id": tid, "error": err} for tid, err in failed_tickets],
            "summary": {
                "total": len(ticket_ids),
                "updated": len(updated_tickets),
                "failed": len(failed_tickets)
            }
        }
        console.print_json(json.dumps(result, indent=2))
    elif quiet:
        # Only output successfully updated ticket IDs
        for ticket in updated_tickets:
            console.print(ticket.id)
    else:
        # Print summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total tickets: {len(ticket_ids)}")
        console.print(f"  ✅ Successfully updated: {len(updated_tickets)}")
        if failed_tickets:
            console.print(f"  ❌ Failed: {len(failed_tickets)}")
            console.print("\n[bold]Failed tickets:[/bold]")
            for tid, err in failed_tickets:
                console.print(f"  - [cyan]{tid}[/cyan]: {err}")
    
    # Exit with error code if any failures
    if failed_tickets and not all_or_nothing:
        raise typer.Exit(1)


def _bulk_update_from_stdin(root, output: str, quiet: bool, strict: bool, 
                           all_or_nothing: bool, dry_run: bool,
                           csv_delimiter: str, skip_invalid: bool, 
                           fail_on_error: bool) -> None:
    """Update multiple tickets from CSV stdin input."""
    # Read and validate stdin
    stdin_reader = StdinReader()
    
    if not stdin_reader.is_available():
        console.print("[red]Error:[/red] No data available on stdin")
        raise typer.Exit(1)
    
    try:
        # Read CSV format
        from gira.utils.csv_utils import CSVReader
        csv_reader = CSVReader(stdin_reader.stream, delimiter=csv_delimiter)
        items = csv_reader.read_csv_dicts()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    if not items:
        console.print("[yellow]Warning:[/yellow] No items to process")
        return
    
    # Validate that all items have an ID
    validation_errors = []
    for i, item in enumerate(items):
        if 'id' not in item or not item['id']:
            validation_errors.append(f"Row {i+1}: Missing required field 'id'")
    
    if validation_errors and not skip_invalid:
        console.print("[red]Validation errors:[/red]")
        for error in validation_errors:
            console.print(f"  - {error}")
        raise typer.Exit(1)
    elif validation_errors and skip_invalid:
        console.print(f"[yellow]Warning:[/yellow] Found {len(validation_errors)} validation errors. Continuing with --skip-invalid...")
    
    # Process bulk updates
    def update_single_ticket(item):
        ticket_id = item.get('id')
        if not ticket_id:
            raise ValueError("Missing ticket ID")
        
        # Find the ticket
        ticket, ticket_path = find_ticket(ticket_id, root)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id.upper()} not found")
        
        if dry_run:
            # In dry-run mode, just show what would happen
            console.print(f"[yellow]DRY RUN:[/yellow] Would update ticket [cyan]{ticket.id}[/cyan]")
            
            # Show changes that would be made
            changes = []
            for field, value in item.items():
                if field == 'id':
                    continue
                if value:
                    if field == 'description':
                        desc_preview = value[:50] + "..." if len(value) > 50 else value
                        changes.append(f"  • {field}: {desc_preview}")
                    else:
                        changes.append(f"  • {field}: {value}")
            
            for change in changes:
                console.print(change)
            console.print()
            
            return {"id": ticket.id, "status": "would_update"}
        else:
            # Apply the updates
            _apply_ticket_updates(
                ticket, ticket_path, root, strict,
                title=item.get('title'),
                description=item.get('description'),
                status=item.get('status'),
                priority=item.get('priority'),
                ticket_type=item.get('type'),
                assignee=item.get('assignee'),
                add_labels=item.get('add_labels'),
                remove_labels=item.get('remove_labels'),
                epic=item.get('epic'),
                parent=item.get('parent'),
                story_points=item.get('story_points')
            )
            
            return {"id": ticket.id, "status": "updated"}
    
    result = process_bulk_operation(
        items, 
        update_single_ticket,
        "ticket update",
        show_progress=not quiet and len(items) > 1
    )
    
    # Output results
    if dry_run:
        console.print(f"\n[dim]No changes were made (dry run)[/dim]")
        return
    
    if output == "json":
        console.print_json(json.dumps(result.to_dict(), indent=2))
    elif quiet:
        # Output only successful ticket IDs
        for success in result.successful:
            console.print(success["result"]["id"])
    else:
        result.print_summary("ticket update")
        
        # Show successful tickets if not too many
        if result.successful and len(result.successful) <= 10:
            console.print("\n✅ **Updated Tickets:**")
            for success in result.successful:
                ticket_data = success["result"]
                console.print(f"  - [cyan]{ticket_data['id']}[/cyan]")
        elif result.successful:
            console.print(f"\n✅ Updated {len(result.successful)} tickets")
    
    # Exit with error code if any failures and fail_on_error is True
    if result.failure_count > 0 and fail_on_error:
        if all_or_nothing:
            console.print("\n[red]Error:[/red] Operation failed due to --all-or-nothing flag")
        raise typer.Exit(1)


def _execute_transactional_updates(
    ticket_ids: List[str], root: Path, quiet: bool, output: str, strict: bool,
    title: Optional[str], description: Optional[str], status: Optional[str],
    priority: Optional[str], ticket_type: Optional[str], assignee: Optional[str],
    add_labels: Optional[str], remove_labels: Optional[str], epic: Optional[str],
    parent: Optional[str], story_points: Optional[int]
) -> None:
    """Execute bulk updates in a transaction with rollback support."""
    from datetime import datetime, timezone
    from uuid import uuid4
    
    transaction_id = str(uuid4())
    updated_tickets = []
    
    try:
        with atomic_operation(transaction_id) as tx:
            # First pass: validate all tickets and collect updates
            tickets_to_update = []
            
            if not quiet:
                console.print("[dim]Validating tickets...[/dim]")
            
            for ticket_id in ticket_ids:
                ticket, ticket_path = find_ticket(ticket_id, root)
                if not ticket:
                    raise ValueError(f"Ticket {ticket_id.upper()} not found")
                tickets_to_update.append((ticket, ticket_path))
            
            # Second pass: apply updates in transaction
            if not quiet:
                console.print(f"[dim]Applying updates to {len(tickets_to_update)} tickets...[/dim]")
            
            for ticket, ticket_path in tickets_to_update:
                # Create a copy of the ticket for updates
                ticket_dict = ticket.model_dump()
                
                # Apply updates to the dictionary
                if title is not None:
                    ticket_dict["title"] = title
                if description is not None:
                    ticket_dict["description"] = description
                if status is not None:
                    ticket_dict["status"] = status
                if priority is not None:
                    ticket_dict["priority"] = priority
                if ticket_type is not None:
                    ticket_dict["type"] = ticket_type
                if assignee is not None:
                    ticket_dict["assignee"] = None if assignee.lower() == "none" else assignee
                if epic is not None:
                    ticket_dict["epic_id"] = None if epic.lower() == "none" else epic
                if parent is not None:
                    ticket_dict["parent_id"] = None if parent.lower() == "none" else parent
                if story_points is not None:
                    ticket_dict["story_points"] = None if story_points == 0 else story_points
                
                # Handle labels
                if add_labels is not None:
                    labels_to_add = [l.strip() for l in add_labels.split(",") if l.strip()]
                    ticket_dict["labels"] = list(set(ticket_dict.get("labels", []) + labels_to_add))
                if remove_labels is not None:
                    labels_to_remove = [l.strip() for l in remove_labels.split(",") if l.strip()]
                    ticket_dict["labels"] = [l for l in ticket_dict.get("labels", []) if l not in labels_to_remove]
                
                # Update timestamp
                ticket_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
                
                # Add update operation to transaction
                tx.add_update(ticket_path, ticket_dict)
                updated_tickets.append(ticket.id)
                
                if not quiet and output != "json":
                    console.print(f"  • Preparing update for [cyan]{ticket.id}[/cyan]")
            
            # Transaction commits automatically on context exit
            
        # If we get here, all updates succeeded
        if output == "json":
            result = {
                "updated": updated_tickets,
                "failed": [],
                "summary": {
                    "total": len(ticket_ids),
                    "updated": len(updated_tickets),
                    "failed": 0
                },
                "transaction_id": transaction_id
            }
            console.print_json(json.dumps(result, indent=2))
        elif quiet:
            for ticket_id in updated_tickets:
                console.print(ticket_id)
        else:
            console.print(f"\n[green]✅ Successfully updated {len(updated_tickets)} tickets atomically[/green]")
            console.print(f"[dim]Transaction ID: {transaction_id}[/dim]")
            
    except TransactionError as e:
        if not quiet:
            console.print(f"\n[red]❌ Transaction failed: {e}[/red]")
            console.print("[yellow]All changes have been rolled back[/yellow]")
        
        if output == "json":
            result = {
                "updated": [],
                "failed": [{"error": str(e), "transaction_id": transaction_id}],
                "summary": {
                    "total": len(ticket_ids),
                    "updated": 0,
                    "failed": len(ticket_ids)
                },
                "transaction_id": transaction_id,
                "rolled_back": True
            }
            console.print_json(json.dumps(result, indent=2))
        
        raise typer.Exit(1)
    except Exception as e:
        if not quiet:
            console.print(f"\n[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)