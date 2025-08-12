"""Update epic command for Gira."""

import json
import sys
from datetime import datetime
from typing import List, Optional

import typer
from gira.utils.console import console
from rich.panel import Panel

from gira.constants import normalize_epic_id
from gira.models import Epic, EpicStatus
from gira.utils.editor import launch_editor
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, validate_bulk_items, process_bulk_operation

def validate_ticket_id(ticket_id: str) -> str:
    """Validate and normalize ticket ID format."""
    import re

    ticket_id = ticket_id.upper()
    pattern = r"^[A-Z]{2,4}-\d+$"

    if not re.match(pattern, ticket_id):
        raise ValueError(f"Invalid ticket ID format: {ticket_id}")

    return ticket_id


def show_epic_details(epic: Epic) -> None:
    """Display detailed epic information."""
    # Create title with status
    status_style = {
        "draft": "yellow",
        "active": "green",
        "completed": "blue"
    }.get(epic.status, "white")

    title = f"[bold cyan]{epic.id}[/bold cyan] - {epic.title}"

    # Build content
    content_lines = []
    content_lines.append(f"[yellow]Status:[/yellow] [{status_style}]{epic.status.title()}[/{status_style}]")
    content_lines.append(f"[yellow]Owner:[/yellow] [green]{epic.owner}[/green]")

    if epic.description:
        content_lines.append(f"\n[yellow]Description:[/yellow]\n{epic.description}")

    if epic.target_date:
        content_lines.append(f"\n[yellow]Target Date:[/yellow] [blue]{epic.target_date}[/blue]")

    # Timestamps
    content_lines.append(f"\n[yellow]Created:[/yellow] {epic.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    content_lines.append(f"[yellow]Updated:[/yellow] {epic.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # Tickets
    if epic.tickets:
        content_lines.append(f"\n[yellow]Tickets ({len(epic.tickets)}):[/yellow]")
        for ticket_id in sorted(epic.tickets):
            content_lines.append(f"  • {ticket_id}")
    else:
        content_lines.append("\n[yellow]Tickets:[/yellow] None")

    # Display in a panel
    panel = Panel(
        "\n".join(content_lines),
        title=title,
        title_align="left",
        border_style="blue"
    )
    console.print(panel)


def update(
    epic_id: Optional[str] = typer.Argument(None, help="Epic ID to update (required unless using --stdin)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description (use '-' for stdin, 'editor' to open editor)"),
    description_file: Optional[str] = typer.Option(None, "--description-file", help="Read description from a file"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status (draft, active, completed)"),
    owner: Optional[str] = typer.Option(None, "--owner", "-o", help="New owner email"),
    target_date: Optional[str] = typer.Option(None, "--target-date", help="New target date (YYYY-MM-DD)"),
    add_ticket: Optional[List[str]] = typer.Option(None, "--add-ticket", "--add-tickets", help="Add ticket to epic (can be used multiple times)"),
    remove_ticket: Optional[List[str]] = typer.Option(None, "--remove-ticket", help="Remove ticket from epic (can be used multiple times)"),
    output: str = typer.Option("text", "--output", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output epic ID"),
    stdin: bool = typer.Option(False, "--stdin", help="Read JSON array of epic updates from stdin"),
    jsonl: bool = typer.Option(False, "--jsonl", help="Read JSONL (JSON Lines) format for streaming large datasets"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without saving them"),
) -> None:
    """Update an existing epic."""
    root = ensure_gira_project()
    
    # Handle bulk operations
    if stdin:
        if epic_id is not None:
            console.print("[red]Error:[/red] Cannot specify epic ID when using --stdin")
            raise typer.Exit(1)
        
        _update_bulk_from_stdin(
            root, title, description, status, owner, target_date,
            add_ticket, remove_ticket, output, quiet, jsonl
        )
        return
    
    # Single epic update - epic_id is required
    if epic_id is None:
        console.print("[red]Error:[/red] Epic ID is required (or use --stdin for bulk updates)")
        raise typer.Exit(1)

    # Normalize epic ID
    epic_id = normalize_epic_id(epic_id)

    # Load epic
    epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
    if not epic_path.exists():
        console.print(f"[red]Error:[/red] Epic {epic_id} not found")
        raise typer.Exit(1)

    try:
        epic = Epic.from_json_file(str(epic_path))
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load epic: {e}")
        raise typer.Exit(1) from e

    # Track if any changes were made
    changes_made = False

    # Check for mutually exclusive description options
    if description and description not in ["", "-", "editor"] and description_file:
        console.print("[red]Error:[/red] Cannot use both --description and --description-file")
        raise typer.Exit(1)

    # Handle description file input
    if description_file:
        # Read description from file
        from pathlib import Path
        try:
            file_path = Path(description_file)
            if not file_path.exists():
                console.print(f"[red]Error:[/red] File not found: {description_file}")
                raise typer.Exit(1)
            
            # Read the file with UTF-8 encoding, handling different encodings gracefully
            try:
                description = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with latin-1 as fallback
                try:
                    description = file_path.read_text(encoding='latin-1')
                    console.print("[yellow]Warning:[/yellow] File was read with latin-1 encoding")
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to read file: {e}")
                    raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to read description file: {e}")
            raise typer.Exit(1)

    # Update fields
    if title is not None:
        epic.title = title
        changes_made = True

    if description is not None or description_file:
        # Handle description input methods
        if description == "editor":
            # Open editor for description
            instructions = (
                "Update the epic description below.\n"
                "Lines starting with # will be ignored.\n"
                "Save and exit to update, or exit without saving to cancel."
            )
            editor_content = launch_editor(
                initial_content=epic.description or "",
                instructions=instructions
            )
            if editor_content is None:
                console.print("[yellow]Cancelled:[/yellow] Description not updated")
                description = epic.description  # Keep existing
            else:
                description = editor_content
                epic.description = description if description else None
                changes_made = True
        elif description == "-":
            # Read from stdin
            description = sys.stdin.read().strip()
            epic.description = description if description else None
            changes_made = True
        else:
            epic.description = description if description else None
            changes_made = True

    if status is not None:
        try:
            epic.status = EpicStatus(status.lower())
            changes_made = True
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid status '{status}'. Must be one of: draft, active, completed")
            raise typer.Exit(1)

    if owner is not None:
        epic.owner = owner
        changes_made = True

    if target_date is not None:
        if target_date == "none" or target_date == "":
            epic.target_date = None
            changes_made = True
        else:
            try:
                epic.target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                changes_made = True
            except ValueError:
                console.print(f"[red]Error:[/red] Invalid date format '{target_date}'. Use YYYY-MM-DD.")
                raise typer.Exit(1)

    # Handle ticket additions
    if add_ticket:
        for ticket_id in add_ticket:
            try:
                validated_id = validate_ticket_id(ticket_id)
                epic.add_ticket(validated_id)
                changes_made = True
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1) from e

    # Handle ticket removals
    if remove_ticket:
        for ticket_id in remove_ticket:
            try:
                validated_id = validate_ticket_id(ticket_id)
                epic.remove_ticket(validated_id)
                changes_made = True
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1) from e

    # Save if changes were made
    if changes_made:
        # Update timestamp
        epic.updated_at = datetime.now()

        # If dry-run, show what would be changed but don't save
        if dry_run:
            console.print("[yellow]DRY RUN:[/yellow] The following changes would be made:")
            console.print(f"\nEpic: [cyan]{epic_id}[/cyan]")
            
            # Show changes
            changes = []
            if title is not None:
                changes.append(f"  • Title: {title}")
            if description is not None or description_file:
                desc_preview = description[:50] + "..." if len(description) > 50 else description
                changes.append(f"  • Description: {desc_preview}")
            if status is not None:
                changes.append(f"  • Status: {status}")
            if owner is not None:
                changes.append(f"  • Owner: {owner}")
            if target_date is not None:
                if target_date == "none" or target_date == "":
                    changes.append(f"  • Target date: [cleared]")
                else:
                    changes.append(f"  • Target date: {target_date}")
            if add_ticket:
                changes.append(f"  • Add tickets: {', '.join(add_ticket)}")
            if remove_ticket:
                changes.append(f"  • Remove tickets: {', '.join(remove_ticket)}")
            
            for change in changes:
                console.print(change)
            
            console.print("\n[dim]No changes were made (dry run)[/dim]")
            return

        try:
            epic.save_to_json_file(str(epic_path))

            if output == "json":
                console.print_json(epic.model_dump_json())
            elif quiet:
                console.print(epic_id)
            else:
                console.print(f"✅ Updated epic [cyan]{epic_id}[/cyan]")
                console.print()
                show_epic_details(epic)

        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to save epic: {e}")
            raise typer.Exit(1) from e
    else:
        console.print("[yellow]No changes made[/yellow]")
        if output == "text" and not quiet:
            console.print()
            show_epic_details(epic)


def _update_bulk_from_stdin(
    root, title, description, status, owner, target_date,
    add_ticket, remove_ticket, output, quiet, jsonl
):
    """Handle bulk update operations from stdin."""
    reader = StdinReader()
    
    # Check if stdin has data
    if not reader.is_available():
        console.print("[red]Error:[/red] No data provided on stdin")
        raise typer.Exit(1)
    
    # Read items based on format
    try:
        if jsonl:
            # Process JSONL streaming
            items = list(reader.read_json_lines())
        else:
            # Process JSON array
            items = reader.read_json_array()
    except ValueError as e:
        console.print(f"[red]Error parsing input:[/red] {e}")
        raise typer.Exit(1)
    
    if not items:
        console.print("[yellow]Warning:[/yellow] No items to process")
        return
    
    # Validate bulk items
    required_fields = ["id"]  # Only ID is required for updates
    optional_fields = [
        "title", "description", "status", "owner", 
        "target_date", "add_tickets", "remove_tickets"
    ]
    
    validation_errors = validate_bulk_items(items, required_fields, optional_fields)
    if validation_errors:
        console.print("[red]Validation errors:[/red]")
        for error in validation_errors:
            console.print(f"  - {error}")
        raise typer.Exit(1)
    
    # Create update function that applies CLI overrides
    def update_single_epic(item):
        epic_id = normalize_epic_id(item["id"])
        
        # Load epic
        epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
        if not epic_path.exists():
            raise ValueError(f"Epic {epic_id} not found")
        
        epic = Epic.from_json_file(str(epic_path))
        
        # Apply updates from item, with CLI options taking precedence
        update_data = {
            "title": title or item.get("title"),
            "description": description or item.get("description"),
            "status": status or item.get("status"),
            "owner": owner or item.get("owner"),
            "target_date": target_date or item.get("target_date"),
            "add_tickets": add_ticket or item.get("add_tickets", []),
            "remove_tickets": remove_ticket or item.get("remove_tickets", [])
        }
        
        # Apply the updates
        _apply_epic_updates(epic, epic_path, **update_data)
        
        return {
            "id": epic.id,
            "title": epic.title,
            "status": epic.status
        }
    
    # Process bulk operation
    result = process_bulk_operation(
        items,
        update_single_epic,
        "epic update",
        show_progress=not quiet and len(items) > 1
    )
    
    # Output results
    if output == "json":
        console.print_json(json.dumps(result.to_dict(), indent=2))
    elif quiet:
        # Output only successful epic IDs
        for success in result.successful:
            console.print(success["result"]["id"])
    else:
        result.print_summary("epic update")
        
        # Show successful updates
        if result.successful and len(result.successful) <= 10:
            console.print("\n✅ **Updated Epics:**")
            for success in result.successful:
                epic_data = success["result"]
                console.print(f"  - [cyan]{epic_data['id']}[/cyan]: {epic_data['status']}")
        elif result.successful:
            console.print(f"\n✅ Updated {len(result.successful)} epics")
    
    # Exit with error code if any failures
    if result.failure_count > 0:
        raise typer.Exit(1)


def _apply_epic_updates(
    epic, epic_path,
    title=None, description=None, status=None, owner=None,
    target_date=None, add_tickets=None, remove_tickets=None
):
    """Apply updates to an epic and save it."""
    changes_made = False
    
    # Update fields
    if title is not None:
        epic.title = title
        changes_made = True
    
    if description is not None:
        epic.description = description if description else None
        changes_made = True
    
    if status is not None:
        try:
            epic.status = EpicStatus(status.lower())
            changes_made = True
        except ValueError:
            raise ValueError(f"Invalid status '{status}'. Must be one of: draft, active, completed")
    
    if owner is not None:
        epic.owner = owner
        changes_made = True
    
    if target_date is not None:
        if target_date == "none" or target_date == "":
            epic.target_date = None
            changes_made = True
        else:
            try:
                epic.target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                changes_made = True
            except ValueError:
                raise ValueError(f"Invalid date format '{target_date}'. Use YYYY-MM-DD.")
    
    # Handle ticket additions
    if add_tickets:
        for ticket_id in add_tickets:
            try:
                validated_id = validate_ticket_id(ticket_id)
                epic.add_ticket(validated_id)
                changes_made = True
            except ValueError as e:
                raise ValueError(f"Failed to add ticket: {e}")
    
    # Handle ticket removals
    if remove_tickets:
        for ticket_id in remove_tickets:
            try:
                validated_id = validate_ticket_id(ticket_id)
                epic.remove_ticket(validated_id)
                changes_made = True
            except ValueError as e:
                raise ValueError(f"Failed to remove ticket: {e}")
    
    # Save if changes were made
    if changes_made:
        # Update timestamp
        epic.updated_at = datetime.now()
        
        try:
            epic.save_to_json_file(str(epic_path))
        except Exception as e:
            raise ValueError(f"Failed to save epic: {e}")
    else:
        raise ValueError("No changes made")
