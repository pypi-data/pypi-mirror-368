"""Update sprint command for Gira."""

from pathlib import Path
from typing import List, Optional

import typer
from gira.utils.console import console
from gira.models import Sprint
from gira.models.sprint import SprintStatus
from gira.utils.project import ensure_gira_project

def load_sprint(sprint_id: str, root: Path) -> tuple[Optional[Sprint], Optional[Path]]:
    """Load a sprint by its ID and return the sprint and its file path."""
    sprints_dir = root / ".gira" / "sprints"

    # Check in active directory first
    active_file = sprints_dir / "active" / f"{sprint_id.upper()}.json"
    if active_file.exists():
        try:
            return Sprint.from_json_file(str(active_file)), active_file
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to load sprint {sprint_id}: {e}")
            return None, None

    # Check in root sprints directory
    sprint_file = sprints_dir / f"{sprint_id.upper()}.json"
    if sprint_file.exists():
        try:
            return Sprint.from_json_file(str(sprint_file)), sprint_file
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to load sprint {sprint_id}: {e}")
            return None, None

    return None, None


def validate_ticket_ids(ticket_ids: List[str]) -> List[str]:
    """Validate and normalize ticket IDs."""
    import re
    pattern = r"^[A-Z]{2,4}-\d+$"
    validated = []

    for ticket_id in ticket_ids:
        ticket_id = ticket_id.upper()
        if re.match(pattern, ticket_id):
            validated.append(ticket_id)
        else:
            raise ValueError(f"Invalid ticket ID format: {ticket_id}")

    return validated


def update(
    sprint_id: str = typer.Argument(..., help="Sprint ID to update (e.g., SPRINT-2025-01-15)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Update sprint name"),
    goal: Optional[str] = typer.Option(None, "--goal", "-g", help="Update sprint goal"),
    goal_file: Optional[str] = typer.Option(None, "--goal-file", help="Read goal from a file"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="Update start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="Update end date (YYYY-MM-DD)"),
    add_tickets: Optional[List[str]] = typer.Option(None, "--add-ticket", "-a", help="Add ticket(s) to sprint"),
    remove_tickets: Optional[List[str]] = typer.Option(None, "--remove-ticket", "-r", help="Remove ticket(s) from sprint"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Update sprint status (planned/active/completed)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without saving them"),
) -> None:
    """Update sprint fields."""
    root = ensure_gira_project()

    # Check for mutually exclusive goal options
    if goal and goal_file:
        console.print("[red]Error:[/red] Cannot use both --goal and --goal-file")
        raise typer.Exit(1)
    
    # Handle goal file input
    if goal_file:
        # Read goal from file
        from pathlib import Path
        try:
            file_path = Path(goal_file)
            if not file_path.exists():
                console.print(f"[red]Error:[/red] File not found: {goal_file}")
                raise typer.Exit(1)
            
            # Read the file with UTF-8 encoding, handling different encodings gracefully
            try:
                goal = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with latin-1 as fallback
                try:
                    goal = file_path.read_text(encoding='latin-1')
                    console.print("[yellow]Warning:[/yellow] File was read with latin-1 encoding")
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to read file: {e}")
                    raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to read goal file: {e}")
            raise typer.Exit(1)

    # Load the sprint
    sprint, sprint_file = load_sprint(sprint_id, root)

    if not sprint or not sprint_file:
        console.print(f"[red]Error:[/red] Sprint {sprint_id.upper()} not found")
        raise typer.Exit(1)

    # Track if any updates were made
    updated = False
    changes = []  # Track changes for dry-run output

    # Update name
    if name is not None:
        sprint.name = name
        updated = True
        changes.append(f"Name: {name}")
        if not dry_run:
            console.print(f"✓ Updated name to: {name}")

    # Update goal
    if goal is not None or goal_file:
        sprint.goal = goal
        updated = True
        goal_preview = goal[:50] + "..." if len(goal) > 50 else goal
        changes.append(f"Goal: {goal_preview}")
        if not dry_run:
            console.print(f"✓ Updated goal to: {goal}")

    # Update dates
    if start_date is not None:
        try:
            from datetime import datetime
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()

            if end_date:
                parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
                if parsed_end <= parsed_start:
                    console.print("[red]Error:[/red] End date must be after start date")
                    raise typer.Exit(1)
            elif sprint.end_date <= parsed_start:
                console.print("[red]Error:[/red] Start date must be before current end date")
                raise typer.Exit(1)

            sprint.start_date = parsed_start
            updated = True
            changes.append(f"Start date: {start_date}")
            if not dry_run:
                console.print(f"✓ Updated start date to: {start_date}")
        except ValueError:
            console.print("[red]Error:[/red] Invalid date format. Use YYYY-MM-DD")
            raise typer.Exit(1)

    if end_date is not None:
        try:
            from datetime import datetime
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()

            if parsed_end <= sprint.start_date:
                console.print("[red]Error:[/red] End date must be after start date")
                raise typer.Exit(1)

            sprint.end_date = parsed_end
            updated = True
            changes.append(f"End date: {end_date}")
            if not dry_run:
                console.print(f"✓ Updated end date to: {end_date}")
        except ValueError:
            console.print("[red]Error:[/red] Invalid date format. Use YYYY-MM-DD")
            raise typer.Exit(1)

    # Add tickets
    if add_tickets:
        try:
            validated_add = validate_ticket_ids(add_tickets)
            tickets_to_add = []
            for ticket_id in validated_add:
                if ticket_id not in sprint.tickets:
                    sprint.tickets.append(ticket_id)
                    tickets_to_add.append(ticket_id)
                    updated = True
                    if not dry_run:
                        console.print(f"✓ Added ticket: {ticket_id}")
                else:
                    if not dry_run:
                        console.print(f"[yellow]Note:[/yellow] Ticket {ticket_id} already in sprint")
            if tickets_to_add:
                changes.append(f"Add tickets: {', '.join(tickets_to_add)}")
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Remove tickets
    if remove_tickets:
        try:
            validated_remove = validate_ticket_ids(remove_tickets)
            tickets_to_remove = []
            for ticket_id in validated_remove:
                if ticket_id in sprint.tickets:
                    sprint.tickets.remove(ticket_id)
                    tickets_to_remove.append(ticket_id)
                    updated = True
                    if not dry_run:
                        console.print(f"✓ Removed ticket: {ticket_id}")
                else:
                    if not dry_run:
                        console.print(f"[yellow]Note:[/yellow] Ticket {ticket_id} not in sprint")
            if tickets_to_remove:
                changes.append(f"Remove tickets: {', '.join(tickets_to_remove)}")
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Update status
    if status is not None:
        valid_statuses = ["planned", "active", "completed"]
        if status.lower() not in valid_statuses:
            console.print(f"[red]Error:[/red] Invalid status. Must be one of: {', '.join(valid_statuses)}")
            raise typer.Exit(1)

        # Handle status transitions
        if status.lower() == "active" and sprint.status != SprintStatus.ACTIVE:
            # When activating a sprint, check if there's already an active sprint
            sprints_dir = root / ".gira" / "sprints" / "active"
            if sprints_dir.exists():
                active_sprints = list(sprints_dir.glob("*.json"))
                if active_sprints and active_sprints[0].stem != sprint.id:
                    console.print("[red]Error:[/red] There is already an active sprint. Close it first.")
                    raise typer.Exit(1)

        sprint.status = SprintStatus(status.lower())
        updated = True
        changes.append(f"Status: {status}")
        if not dry_run:
            console.print(f"✓ Updated status to: {status}")

    # Save if any updates were made
    if updated:
        if dry_run:
            # Show dry-run preview
            console.print("[yellow]DRY RUN:[/yellow] The following changes would be made:")
            console.print(f"\nSprint: [cyan]{sprint.id}[/cyan]")
            for change in changes:
                console.print(f"  • {change}")
            console.print("\n[dim]No changes were made (dry run)[/dim]")
        else:
            # Update the timestamp
            from datetime import datetime, timezone
            sprint.updated_at = datetime.now(timezone.utc)

            # Save the sprint
            sprint.save_to_json_file(str(sprint_file))
            console.print(f"\n[green]✅ Updated sprint {sprint.id}[/green]")
    else:
        console.print("[yellow]No updates specified[/yellow]")
