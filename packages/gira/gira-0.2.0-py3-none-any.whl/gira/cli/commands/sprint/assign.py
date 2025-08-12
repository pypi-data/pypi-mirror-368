"""Advanced sprint assignment commands for retroactive ticket assignment."""

import json
from datetime import datetime, timezone, date
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict

import typer
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Confirm, Prompt
from rich import box

from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets
from gira.models.sprint import Sprint
from gira.models.ticket import Ticket


def load_sprint_by_id(sprint_id: str, root: Path) -> Optional[Sprint]:
    """Load a sprint by its ID from any location."""
    sprints_dir = root / ".gira" / "sprints"
    
    # Check root sprints directory first
    sprint_file = sprints_dir / f"{sprint_id.upper()}.json"
    if sprint_file.exists():
        try:
            return Sprint.from_json_file(str(sprint_file))
        except Exception:
            pass
    
    # Check status subdirectories
    for status_dir in ["active", "completed", "planned"]:
        status_path = sprints_dir / status_dir / f"{sprint_id.upper()}.json"
        if status_path.exists():
            try:
                return Sprint.from_json_file(str(status_path))
            except Exception:
                pass
    
    return None


def load_all_sprints(root: Path) -> List[Sprint]:
    """Load all sprints from the project."""
    sprints = []
    sprints_dir = root / ".gira" / "sprints"
    
    # Load from root directory
    if sprints_dir.exists():
        for sprint_file in sprints_dir.glob("*.json"):
            try:
                sprint = Sprint.from_json_file(str(sprint_file))
                sprints.append(sprint)
            except Exception:
                continue
    
    # Load from status subdirectories
    for status_dir in ["active", "completed", "planned"]:
        status_path = sprints_dir / status_dir
        if status_path.exists():
            for sprint_file in status_path.glob("*.json"):
                try:
                    sprint = Sprint.from_json_file(str(sprint_file))
                    sprints.append(sprint)
                except Exception:
                    continue
    
    return sprints


def get_unassigned_tickets(tickets: List[Ticket]) -> List[Ticket]:
    """Get tickets that are not assigned to any sprint."""
    return [t for t in tickets if not t.sprint_id]


def find_tickets_by_completion_date(
    tickets: List[Ticket], 
    start_date: date, 
    end_date: date
) -> List[Ticket]:
    """Find tickets completed within a date range."""
    completed_tickets = []
    
    for ticket in tickets:
        if ticket.status != "done":
            continue
            
        # Use updated_at as proxy for completion date
        completion_date = ticket.updated_at
        if completion_date.tzinfo is None:
            completion_date = completion_date.replace(tzinfo=timezone.utc)
        
        completion_date = completion_date.date()
        
        if start_date <= completion_date <= end_date:
            completed_tickets.append(ticket)
    
    return completed_tickets


def find_tickets_by_epic(tickets: List[Ticket], epic_id: str) -> List[Ticket]:
    """Find tickets belonging to a specific epic."""
    return [t for t in tickets if t.epic_id == epic_id]


def save_sprint_with_tickets(sprint: Sprint, root: Path) -> bool:
    """Save a sprint with updated ticket assignments."""
    sprints_dir = root / ".gira" / "sprints"
    
    # Find the correct file location based on status
    if sprint.status == "active":
        sprint_file = sprints_dir / "active" / f"{sprint.id}.json"
    elif sprint.status == "completed":
        sprint_file = sprints_dir / "completed" / f"{sprint.id}.json"
    elif sprint.status == "planned":
        sprint_file = sprints_dir / "planned" / f"{sprint.id}.json"
    else:
        sprint_file = sprints_dir / f"{sprint.id}.json"
    
    # Ensure directory exists
    sprint_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Update timestamp
        sprint.updated_at = datetime.now(timezone.utc)
        sprint.save_to_json_file(str(sprint_file))
        return True
    except Exception as e:
        console.print(f"[red]Error saving sprint:[/red] {e}")
        return False


def assign_by_dates(
    sprint_id: str = typer.Argument(..., help="Sprint ID to assign tickets to"),
    start_date: Optional[str] = typer.Option(None, "--start", help="Start date for ticket search (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end", help="End date for ticket search (YYYY-MM-DD)"),
    include_assigned: bool = typer.Option(False, "--include-assigned", help="Include tickets already assigned to other sprints"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying them")
):
    """Assign tickets to sprint based on completion dates."""
    root = ensure_gira_project()
    
    # Load the target sprint
    sprint = load_sprint_by_id(sprint_id, root)
    if not sprint:
        console.print(f"[red]Error:[/red] Sprint {sprint_id} not found")
        raise typer.Exit(1)
    
    # Use sprint dates if not provided
    if not start_date:
        start_date = sprint.start_date.isoformat()
    if not end_date:
        end_date = sprint.end_date.isoformat()
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]Error:[/red] Invalid date format. Use YYYY-MM-DD")
        raise typer.Exit(1)
    
    # Load all tickets
    tickets = load_all_tickets(root, include_archived=True)
    
    # Find tickets completed in date range
    completed_tickets = find_tickets_by_completion_date(tickets, start_dt, end_dt)
    
    # Filter out already assigned tickets if needed
    if not include_assigned:
        completed_tickets = [t for t in completed_tickets if not t.sprint_id]
    
    if not completed_tickets:
        console.print("[yellow]No tickets found for the specified criteria[/yellow]")
        return
    
    # Display summary
    console.print(f"\n[cyan]📅 Date-based Sprint Assignment[/cyan]")
    console.print(f"Sprint: [bold]{sprint.name}[/bold] ({sprint.id})")
    console.print(f"Date range: {start_date} to {end_date}")
    console.print(f"Found [yellow]{len(completed_tickets)}[/yellow] tickets to assign\n")
    
    # Show tickets table
    table = Table(title="Tickets to Assign", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Completed", style="green")
    table.add_column("Epic", style="magenta")
    table.add_column("Points", justify="right", style="yellow")
    
    total_points = 0
    for ticket in completed_tickets:
        completion_date = ticket.updated_at.date().isoformat()
        epic_display = ticket.epic_id or "[dim]None[/dim]"
        points = ticket.story_points or 0
        total_points += points
        
        table.add_row(
            ticket.id,
            ticket.title[:40] + "..." if len(ticket.title) > 40 else ticket.title,
            completion_date,
            epic_display,
            str(points) if points > 0 else "[dim]0[/dim]"
        )
    
    console.print(table)
    console.print(f"\nTotal story points: [yellow]{total_points}[/yellow]")
    
    if dry_run:
        console.print("\n[yellow]DRY RUN:[/yellow] No changes will be made")
        return
    
    # Confirm assignment
    if not Confirm.ask(f"\nAssign these {len(completed_tickets)} tickets to sprint {sprint.id}?"):
        console.print("[dim]Assignment cancelled[/dim]")
        return
    
    # Assign tickets
    assigned_count = 0
    for ticket in completed_tickets:
        if ticket.id not in sprint.tickets:
            sprint.tickets.append(ticket.id)
            assigned_count += 1
    
    # Save sprint
    if save_sprint_with_tickets(sprint, root):
        console.print(f"\n[green]✅ Successfully assigned {assigned_count} tickets to sprint {sprint.id}[/green]")
    else:
        console.print(f"[red]❌ Failed to save sprint {sprint.id}[/red]")


def assign_by_epic(
    sprint_id: str = typer.Argument(..., help="Sprint ID to assign tickets to"),
    epic_id: str = typer.Argument(..., help="Epic ID to assign tickets from"),
    status_filter: Optional[str] = typer.Option(None, "--status", help="Only assign tickets with this status (e.g., 'done')"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying them")
):
    """Assign all tickets from an epic to a sprint."""
    root = ensure_gira_project()
    
    # Load the target sprint
    sprint = load_sprint_by_id(sprint_id, root)
    if not sprint:
        console.print(f"[red]Error:[/red] Sprint {sprint_id} not found")
        raise typer.Exit(1)
    
    # Load all tickets
    tickets = load_all_tickets(root, include_archived=True)
    
    # Find tickets from the epic
    epic_tickets = find_tickets_by_epic(tickets, epic_id.upper())
    
    # Apply status filter if specified
    if status_filter:
        epic_tickets = [t for t in epic_tickets if t.status == status_filter]
    
    if not epic_tickets:
        console.print(f"[yellow]No tickets found for epic {epic_id}" + 
                     (f" with status '{status_filter}'" if status_filter else "") + "[/yellow]")
        return
    
    # Display summary
    console.print(f"\n[cyan]🎯 Epic-based Sprint Assignment[/cyan]")
    console.print(f"Sprint: [bold]{sprint.name}[/bold] ({sprint.id})")
    console.print(f"Epic: [bold]{epic_id}[/bold]")
    if status_filter:
        console.print(f"Status filter: [yellow]{status_filter}[/yellow]")
    console.print(f"Found [yellow]{len(epic_tickets)}[/yellow] tickets to assign\n")
    
    # Show tickets table
    table = Table(title="Epic Tickets to Assign", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")
    table.add_column("Points", justify="right", style="yellow")
    table.add_column("Current Sprint", style="magenta")
    
    total_points = 0
    for ticket in epic_tickets:
        points = ticket.story_points or 0
        total_points += points
        current_sprint = ticket.sprint_id or "[dim]None[/dim]"
        
        # Color status
        status_color = {
            "done": "green",
            "in_progress": "yellow", 
            "review": "cyan",
            "todo": "blue",
            "backlog": "white"
        }.get(ticket.status, "white")
        
        table.add_row(
            ticket.id,
            ticket.title[:35] + "..." if len(ticket.title) > 35 else ticket.title,
            f"[{status_color}]{ticket.status}[/{status_color}]",
            str(points) if points > 0 else "[dim]0[/dim]",
            current_sprint
        )
    
    console.print(table)
    console.print(f"\nTotal story points: [yellow]{total_points}[/yellow]")
    
    if dry_run:
        console.print("\n[yellow]DRY RUN:[/yellow] No changes will be made")
        return
    
    # Confirm assignment
    if not Confirm.ask(f"\nAssign these {len(epic_tickets)} tickets from epic {epic_id} to sprint {sprint.id}?"):
        console.print("[dim]Assignment cancelled[/dim]")
        return
    
    # Assign tickets
    assigned_count = 0
    for ticket in epic_tickets:
        if ticket.id not in sprint.tickets:
            sprint.tickets.append(ticket.id)
            assigned_count += 1
    
    # Save sprint
    if save_sprint_with_tickets(sprint, root):
        console.print(f"\n[green]✅ Successfully assigned {assigned_count} tickets to sprint {sprint.id}[/green]")
    else:
        console.print(f"[red]❌ Failed to save sprint {sprint.id}[/red]")


def assign_wizard():
    """Interactive wizard for assigning unassigned tickets to sprints."""
    root = ensure_gira_project()
    
    # Load data
    console.print("[cyan]🧙 Sprint Assignment Wizard[/cyan]\n")
    console.print("Loading tickets and sprints...")
    
    tickets = load_all_tickets(root, include_archived=True)
    sprints = load_all_sprints(root)
    unassigned_tickets = get_unassigned_tickets(tickets)
    
    if not unassigned_tickets:
        console.print("[green]🎉 All tickets are already assigned to sprints![/green]")
        return
    
    if not sprints:
        console.print("[red]No sprints found. Create a sprint first.[/red]")
        return
    
    console.print(f"Found [yellow]{len(unassigned_tickets)}[/yellow] unassigned tickets")
    console.print(f"Found [cyan]{len(sprints)}[/cyan] sprints\n")
    
    # Group tickets by status for better organization
    tickets_by_status = defaultdict(list)
    for ticket in unassigned_tickets:
        tickets_by_status[ticket.status].append(ticket)
    
    # Show summary
    summary_table = Table(title="Unassigned Tickets by Status", box=box.ROUNDED)
    summary_table.add_column("Status", style="cyan")
    summary_table.add_column("Count", justify="right", style="yellow")
    summary_table.add_column("Story Points", justify="right", style="green")
    
    total_points = 0
    for status, status_tickets in tickets_by_status.items():
        count = len(status_tickets)
        points = sum(t.story_points or 0 for t in status_tickets)
        total_points += points
        
        status_color = {
            "done": "green",
            "in_progress": "yellow",
            "review": "cyan", 
            "todo": "blue",
            "backlog": "white"
        }.get(status, "white")
        
        summary_table.add_row(
            f"[{status_color}]{status}[/{status_color}]",
            str(count),
            str(points)
        )
    
    summary_table.add_section()
    summary_table.add_row("[bold]Total[/bold]", f"[bold]{len(unassigned_tickets)}[/bold]", f"[bold]{total_points}[/bold]")
    
    console.print(summary_table)
    console.print()
    
    # Interactive assignment process
    while True:
        console.print("[bold]Assignment Options:[/bold]")
        console.print("1. 📅 Assign tickets by completion date")
        console.print("2. 🎯 Assign tickets by epic")
        console.print("3. 📋 Assign specific tickets manually")
        console.print("4. 📊 Show detailed ticket list")
        console.print("5. 🚪 Exit wizard")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"], default="1")
        
        if choice == "1":
            _wizard_assign_by_date(unassigned_tickets, sprints, root)
        elif choice == "2":
            _wizard_assign_by_epic(unassigned_tickets, sprints, root)
        elif choice == "3":
            _wizard_assign_manual(unassigned_tickets, sprints, root)
        elif choice == "4":
            _wizard_show_tickets(unassigned_tickets)
        elif choice == "5":
            console.print("[dim]Exiting wizard[/dim]")
            break
        
        # Refresh unassigned tickets after each operation
        tickets = load_all_tickets(root, include_archived=True)
        unassigned_tickets = get_unassigned_tickets(tickets)
        
        if not unassigned_tickets:
            console.print("\n[green]🎉 All tickets have been assigned![/green]")
            break
        
        console.print(f"\n[yellow]{len(unassigned_tickets)} tickets remaining[/yellow]")
        if not Confirm.ask("Continue with more assignments?"):
            break


def _wizard_assign_by_date(unassigned_tickets: List[Ticket], sprints: List[Sprint], root: Path):
    """Wizard helper for date-based assignment."""
    done_tickets = [t for t in unassigned_tickets if t.status == "done"]
    if not done_tickets:
        console.print("[yellow]No completed tickets to assign by date[/yellow]")
        return
    
    # Show available sprints
    console.print("\n[bold]Available Sprints:[/bold]")
    for i, sprint in enumerate(sprints, 1):
        console.print(f"{i}. {sprint.name} ({sprint.id}) - {sprint.start_date} to {sprint.end_date}")
    
    try:
        choice = int(Prompt.ask("Select sprint number")) - 1
        if 0 <= choice < len(sprints):
            selected_sprint = sprints[choice]
            
            # Find tickets completed during sprint
            sprint_tickets = find_tickets_by_completion_date(
                done_tickets, selected_sprint.start_date, selected_sprint.end_date
            )
            
            if sprint_tickets:
                console.print(f"\nFound {len(sprint_tickets)} tickets completed during sprint period")
                if Confirm.ask("Assign these tickets?"):
                    for ticket in sprint_tickets:
                        if ticket.id not in selected_sprint.tickets:
                            selected_sprint.tickets.append(ticket.id)
                    
                    if save_sprint_with_tickets(selected_sprint, root):
                        console.print(f"[green]✅ Assigned {len(sprint_tickets)} tickets to {selected_sprint.id}[/green]")
            else:
                console.print("[yellow]No tickets found for sprint date range[/yellow]")
        
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")


def _wizard_assign_by_epic(unassigned_tickets: List[Ticket], sprints: List[Sprint], root: Path):
    """Wizard helper for epic-based assignment."""
    # Get unique epics from unassigned tickets
    epics = set(t.epic_id for t in unassigned_tickets if t.epic_id)
    if not epics:
        console.print("[yellow]No unassigned tickets have epic assignments[/yellow]")
        return
    
    console.print(f"\n[bold]Available Epics ({len(epics)}):[/bold]")
    epic_list = list(epics)
    for i, epic in enumerate(epic_list, 1):
        epic_tickets = [t for t in unassigned_tickets if t.epic_id == epic]
        console.print(f"{i}. {epic} ({len(epic_tickets)} tickets)")
    
    try:
        epic_choice = int(Prompt.ask("Select epic number")) - 1
        if 0 <= epic_choice < len(epic_list):
            selected_epic = epic_list[epic_choice]
            epic_tickets = [t for t in unassigned_tickets if t.epic_id == selected_epic]
            
            console.print(f"\n[bold]Available Sprints:[/bold]")
            for i, sprint in enumerate(sprints, 1):
                console.print(f"{i}. {sprint.name} ({sprint.id})")
            
            sprint_choice = int(Prompt.ask("Select sprint number")) - 1
            if 0 <= sprint_choice < len(sprints):
                selected_sprint = sprints[sprint_choice]
                
                console.print(f"\nAssigning {len(epic_tickets)} tickets from {selected_epic} to {selected_sprint.id}")
                if Confirm.ask("Proceed?"):
                    for ticket in epic_tickets:
                        if ticket.id not in selected_sprint.tickets:
                            selected_sprint.tickets.append(ticket.id)
                    
                    if save_sprint_with_tickets(selected_sprint, root):
                        console.print(f"[green]✅ Assigned {len(epic_tickets)} tickets to {selected_sprint.id}[/green]")
    
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")


def _wizard_assign_manual(unassigned_tickets: List[Ticket], sprints: List[Sprint], root: Path):
    """Wizard helper for manual ticket assignment."""
    console.print("[yellow]Manual assignment not yet implemented[/yellow]")
    console.print("Use options 1 or 2 for now, or assign tickets manually with:")
    console.print("  gira sprint update SPRINT-ID --add-ticket TICKET-ID")


def _wizard_show_tickets(unassigned_tickets: List[Ticket]):
    """Show detailed list of unassigned tickets."""
    table = Table(title="Unassigned Tickets (Detailed)", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")
    table.add_column("Epic", style="magenta") 
    table.add_column("Points", justify="right", style="yellow")
    table.add_column("Updated", style="dim")
    
    for ticket in unassigned_tickets[:20]:  # Limit to first 20
        epic_display = ticket.epic_id or "[dim]None[/dim]"
        points = ticket.story_points or 0
        updated = ticket.updated_at.date().isoformat()
        
        status_color = {
            "done": "green",
            "in_progress": "yellow",
            "review": "cyan",
            "todo": "blue", 
            "backlog": "white"
        }.get(ticket.status, "white")
        
        table.add_row(
            ticket.id,
            ticket.title[:30] + "..." if len(ticket.title) > 30 else ticket.title,
            f"[{status_color}]{ticket.status}[/{status_color}]",
            epic_display,
            str(points) if points > 0 else "[dim]0[/dim]",
            updated
        )
    
    console.print(table)
    if len(unassigned_tickets) > 20:
        console.print(f"[dim]... and {len(unassigned_tickets) - 20} more tickets[/dim]")


def _expand_ticket_pattern(root: Path, pattern: str) -> List[str]:
    """Expand ticket pattern to list of ticket IDs.
    
    Supports:
    - Wildcards: TEST-1* matches TEST-10, TEST-11, etc.
    - Ranges: TEST-1..10 matches TEST-1 through TEST-10
    - Single IDs: TEST-1 returns [TEST-1]
    """
    import re
    from gira.utils.ticket_utils import find_ticket
    
    tickets = []
    
    # Check for range pattern (e.g., TEST-1..10)
    range_match = re.match(r'^([A-Z]+-?)(\d+)\.\.(\d+)$', pattern.upper())
    if range_match:
        prefix, start_num, end_num = range_match.groups()
        try:
            start = int(start_num)
            end = int(end_num)
            for i in range(start, end + 1):
                ticket_id = f"{prefix}{i}"
                if find_ticket(ticket_id, root)[0]:  # Check if ticket exists
                    tickets.append(ticket_id)
        except ValueError:
            pass
        return tickets
    
    # Check for wildcard pattern (e.g., TEST-1*)
    if '*' in pattern:
        pattern_regex = re.escape(pattern.upper()).replace(r'\*', '.*')
        pattern_regex = f'^{pattern_regex}$'
        
        # Search through all ticket files
        for status_dir in ["todo", "in_progress", "review", "done", "backlog"]:
            board_path = root / ".gira" / "board" / status_dir
            if board_path.exists():
                for ticket_file in board_path.glob("*.json"):
                    ticket_id = ticket_file.stem
                    if re.match(pattern_regex, ticket_id):
                        tickets.append(ticket_id)
        
        return sorted(set(tickets))
    
    # Single ticket ID - check if it exists
    if find_ticket(pattern.upper(), root)[0]:
        return [pattern.upper()]
    
    return []


def _get_swimlane_ids(root: Path) -> List[str]:
    """Get list of valid swimlane/status IDs."""
    board_path = root / ".gira" / "board"
    if not board_path.exists():
        return []
    
    return [d.name for d in board_path.iterdir() if d.is_dir()]


def _ticket_exists(root: Path, ticket_id: str) -> bool:
    """Check if a ticket exists."""
    from gira.utils.ticket_utils import find_ticket
    ticket, _ = find_ticket(ticket_id, root)
    return ticket is not None


def _update_ticket_sprint_assignment(root: Path, ticket_id: str, sprint_id: str) -> bool:
    """Update a ticket's sprint assignment."""
    from gira.utils.ticket_utils import find_ticket
    
    ticket, ticket_path = find_ticket(ticket_id, root)
    if not ticket:
        return False
    
    # Update ticket's sprint_id
    ticket.sprint_id = sprint_id
    
    try:
        ticket.save_to_json_file(str(ticket_path))
        return True
    except Exception:
        return False


def _show_assignment_preview(sprint: Sprint, tickets_to_assign: List[Ticket], total_points: int):
    """Show preview of tickets to be assigned."""
    console.print(f"\n[yellow]About to assign {len(tickets_to_assign)} ticket(s) to sprint:[/yellow]")
    console.print(f"Sprint: [bold]{sprint.name}[/bold] ({sprint.id})")
    
    # Show capacity information if available
    if hasattr(sprint, 'capacity') and sprint.capacity:
        current_points = sum(ticket.story_points or 0 for ticket in load_all_tickets(Path.cwd()) if ticket.sprint_id == sprint.id)
        new_total = current_points + total_points
        console.print(f"Current capacity: {current_points}/{sprint.capacity} points")
        console.print(f"After assignment: {new_total}/{sprint.capacity} points")
        
        if new_total > sprint.capacity:
            console.print(f"[red]⚠️  Would exceed capacity by {new_total - sprint.capacity} points[/red]")
    
    # Show tickets table
    table = Table(title="Tickets to Assign", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")
    table.add_column("Points", justify="right", style="yellow")
    table.add_column("Current Sprint", style="magenta")
    
    for ticket in tickets_to_assign[:10]:  # Show first 10
        current_sprint = ticket.sprint_id or "[dim]None[/dim]"
        points = ticket.story_points or 0
        
        # Color status
        status_color = {
            "done": "green",
            "in_progress": "yellow", 
            "review": "cyan",
            "todo": "blue",
            "backlog": "white"
        }.get(ticket.status, "white")
        
        table.add_row(
            ticket.id,
            ticket.title[:35] + "..." if len(ticket.title) > 35 else ticket.title,
            f"[{status_color}]{ticket.status}[/{status_color}]",
            str(points) if points > 0 else "[dim]0[/dim]",
            current_sprint
        )
    
    if len(tickets_to_assign) > 10:
        table.add_row("...", f"and {len(tickets_to_assign) - 10} more", "...", "...", "...")
    
    console.print(table)
    console.print(f"\nTotal story points to assign: [yellow]{total_points}[/yellow]")


def assign(
    sprint_id: str = typer.Argument(..., help="Sprint ID to assign tickets to"),
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to assign (supports patterns like 'GCM-1*', ranges like 'GCM-1..10', or '-' for stdin)"),
    from_file: Optional[str] = typer.Option(None, "--from-file", help="Read ticket IDs from file"),
    from_query: Optional[str] = typer.Option(None, "--query", help="Assign tickets matching query"),
    from_context: bool = typer.Option(False, "--from-context", help="Assign tickets from current context"),
    force: bool = typer.Option(False, "--force", "-f", help="Legacy option (confirmation removed for AI-friendliness)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying them"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table, json)"),
):
    """Assign multiple tickets to a sprint.
    
    This command provides a simple way to assign multiple tickets to a sprint
    in one operation. Supports various input methods and pattern matching.
    
    Examples:
        # Assign specific tickets
        gira sprint assign SPRINT-2025-07-28 GCM-1 GCM-2 GCM-3
        
        # Pattern matching
        gira sprint assign SPRINT-2025-07-28 GCM-1*
        gira sprint assign SPRINT-2025-07-28 GCM-1..10
        
        # From stdin
        echo -e "GCM-1\\nGCM-2" | gira sprint assign SPRINT-2025-07-28 -
        
        # From file
        gira sprint assign SPRINT-2025-07-28 --from-file tickets.txt
        
        # Preview changes
        gira sprint assign SPRINT-2025-07-28 GCM-1* --dry-run
    """
    root = ensure_gira_project()
    
    # Load the target sprint
    sprint = load_sprint_by_id(sprint_id, root)
    if not sprint:
        console.print(f"[red]Error:[/red] Sprint {sprint_id} not found")
        raise typer.Exit(1)
    
    # Collect ticket IDs from various sources
    all_ticket_ids = []
    
    # From arguments
    if ticket_ids:
        if len(ticket_ids) == 1 and ticket_ids[0] == "-":
            # Read from stdin
            import sys
            stdin_content = sys.stdin.read().strip()
            if stdin_content:
                all_ticket_ids.extend(stdin_content.split('\n'))
        else:
            # Expand patterns
            for ticket_id_pattern in ticket_ids:
                expanded = _expand_ticket_pattern(root, ticket_id_pattern)
                if expanded:
                    all_ticket_ids.extend(expanded)
                else:
                    # If pattern expansion returns nothing, keep the original pattern
                    # This allows us to show proper error messages for non-existent tickets
                    all_ticket_ids.append(ticket_id_pattern)
    
    # From file
    if from_file:
        try:
            with open(from_file, 'r') as f:
                file_ticket_ids = [line.strip() for line in f if line.strip()]
                all_ticket_ids.extend(file_ticket_ids)
        except FileNotFoundError:
            console.print(f"[red]Error:[/red] File {from_file} not found")
            raise typer.Exit(1)
    
    # From query (placeholder for future implementation)
    if from_query:
        console.print("[yellow]Query-based assignment not yet implemented[/yellow]")
        console.print("Use specific ticket IDs or patterns for now")
        raise typer.Exit(1)
    
    # From context (placeholder for future implementation)
    if from_context:
        console.print("[yellow]Context-based assignment not yet implemented[/yellow]")
        console.print("Use specific ticket IDs or patterns for now")
        raise typer.Exit(1)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ticket_ids = []
    for ticket_id in all_ticket_ids:
        if ticket_id not in seen:
            seen.add(ticket_id)
            unique_ticket_ids.append(ticket_id)
    all_ticket_ids = unique_ticket_ids
    
    if not all_ticket_ids:
        console.print("[red]Error:[/red] No ticket IDs provided")
        console.print("Provide ticket IDs as arguments, use --from-file, or pipe from stdin")
        raise typer.Exit(1)
    
    # Load and validate tickets
    valid_tickets = []
    missing_tickets = []
    already_assigned = []
    done_tickets = []
    
    for ticket_id in all_ticket_ids:
        from gira.utils.ticket_utils import find_ticket
        ticket, ticket_path = find_ticket(ticket_id, root)
        if not ticket:
            missing_tickets.append(ticket_id)
            continue
        
        # Check if already assigned to this sprint
        if ticket.sprint_id == sprint_id:
            already_assigned.append(ticket_id)
            continue
        
        # Track done tickets for warning
        if ticket.status == "done":
            done_tickets.append(ticket_id)
        
        valid_tickets.append(ticket)
    
    # Handle missing tickets
    if missing_tickets:
        if not quiet:
            console.print(f"[yellow]Warning:[/yellow] {len(missing_tickets)} ticket(s) not found:")
            for ticket_id in missing_tickets[:5]:  # Show first 5
                console.print(f"  - {ticket_id}")
            if len(missing_tickets) > 5:
                console.print(f"  ... and {len(missing_tickets) - 5} more")
    
    # Handle already assigned tickets
    if already_assigned and not quiet:
        console.print(f"[yellow]Info:[/yellow] {len(already_assigned)} ticket(s) already assigned to {sprint_id}")
    
    # Handle done tickets warning
    if done_tickets and not quiet:
        console.print(f"[yellow]Warning:[/yellow] {len(done_tickets)} ticket(s) are already done")
    
    if not valid_tickets:
        if not quiet:
            console.print("[yellow]No tickets to assign[/yellow]")
        raise typer.Exit(0)
    
    # Calculate total story points
    total_points = sum(ticket.story_points or 0 for ticket in valid_tickets)
    
    # Show preview if requested or if many tickets (AI-friendly: no confirmation by default)
    if not quiet and (len(valid_tickets) >= 5 or dry_run):
        _show_assignment_preview(sprint, valid_tickets, total_points)
    
    if dry_run:
        console.print("\n[yellow]DRY RUN:[/yellow] No changes were made")
        return
    
    # Perform assignments
    successful_assignments = []
    failed_assignments = []
    
    for ticket in valid_tickets:
        # Update ticket's sprint_id
        if _update_ticket_sprint_assignment(root, ticket.id, sprint_id):
            successful_assignments.append(ticket.id)
            # Also add to sprint's ticket list if not already there
            if ticket.id not in sprint.tickets:
                sprint.tickets.append(ticket.id)
        else:
            failed_assignments.append(ticket.id)
    
    # Save updated sprint
    if successful_assignments:
        if not save_sprint_with_tickets(sprint, root):
            console.print(f"[red]Error:[/red] Failed to save sprint {sprint_id}")
            raise typer.Exit(1)
    
    # Output results
    if output == "json":
        import json
        result = {
            "sprint_id": sprint_id,
            "summary": {
                "total_requested": len(all_ticket_ids),
                "successful": len(successful_assignments),
                "already_assigned": len(already_assigned),
                "missing": len(missing_tickets),
                "failed": len(failed_assignments)
            },
            "successful_assignments": successful_assignments,
            "already_assigned": already_assigned,
            "missing_tickets": missing_tickets,
            "failed_assignments": failed_assignments
        }
        console.print(json.dumps(result, indent=2))
    else:
        if not quiet:
            if successful_assignments:
                console.print(f"\n✅ Successfully assigned {len(successful_assignments)} ticket(s) to sprint {sprint_id}")
            if failed_assignments:
                console.print(f"[red]❌ Failed to assign {len(failed_assignments)} ticket(s)[/red]")


def unassign(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to unassign (supports patterns like 'GCM-1*', ranges like 'GCM-1..10', or '-' for stdin)"),
    all_tickets: bool = typer.Option(False, "--all", help="Unassign all tickets from specified sprint"),
    from_sprint: Optional[str] = typer.Option(None, "--from", help="Unassign only from this specific sprint"),
    force: bool = typer.Option(False, "--force", "-f", help="Legacy option (confirmation removed for AI-friendliness)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying them"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table, json)"),
):
    """Remove tickets from sprint assignments.
    
    Examples:
        # Unassign specific tickets from any sprint
        gira sprint unassign GCM-1 GCM-2 GCM-3
        
        # Unassign tickets from specific sprint
        gira sprint unassign GCM-1 GCM-2 --from SPRINT-2025-07-28
        
        # Unassign all tickets from a sprint
        gira sprint unassign --all --from SPRINT-2025-07-28
        
        # Pattern matching
        gira sprint unassign GCM-1*
        
        # Preview changes
        gira sprint unassign GCM-1* --dry-run
    """
    root = ensure_gira_project()
    
    # Collect ticket IDs
    all_ticket_ids = []
    
    if all_tickets and from_sprint:
        # Unassign all tickets from specific sprint
        sprint = load_sprint_by_id(from_sprint, root)
        if not sprint:
            console.print(f"[red]Error:[/red] Sprint {from_sprint} not found")
            raise typer.Exit(1)
        all_ticket_ids.extend(sprint.tickets)
    elif ticket_ids:
        if len(ticket_ids) == 1 and ticket_ids[0] == "-":
            # Read from stdin
            import sys
            stdin_content = sys.stdin.read().strip()
            if stdin_content:
                all_ticket_ids.extend(stdin_content.split('\n'))
        else:
            # Expand patterns
            for ticket_id_pattern in ticket_ids:
                expanded = _expand_ticket_pattern(root, ticket_id_pattern)
                if expanded:
                    all_ticket_ids.extend(expanded)
                else:
                    # If pattern expansion returns nothing, keep the original pattern
                    # This allows us to show proper error messages for non-existent tickets
                    all_ticket_ids.append(ticket_id_pattern)
    else:
        console.print("[red]Error:[/red] No tickets specified")
        console.print("Provide ticket IDs, use --all with --from, or pipe from stdin")
        raise typer.Exit(1)
    
    # Remove duplicates
    all_ticket_ids = list(dict.fromkeys(all_ticket_ids))
    
    if not all_ticket_ids:
        console.print("[red]Error:[/red] No ticket IDs provided")
        raise typer.Exit(1)
    
    # Load and validate tickets
    valid_tickets = []
    missing_tickets = []
    not_assigned = []
    
    for ticket_id in all_ticket_ids:
        from gira.utils.ticket_utils import find_ticket
        ticket, ticket_path = find_ticket(ticket_id, root)
        if not ticket:
            missing_tickets.append(ticket_id)
            continue
        
        # Check if ticket is assigned to a sprint
        if not ticket.sprint_id:
            not_assigned.append(ticket_id)
            continue
        
        # If --from specified, check if ticket is assigned to that sprint
        if from_sprint and ticket.sprint_id != from_sprint:
            not_assigned.append(ticket_id)
            continue
        
        valid_tickets.append((ticket, ticket_path))
    
    if missing_tickets and not quiet:
        console.print(f"[yellow]Warning:[/yellow] {len(missing_tickets)} ticket(s) not found")
    
    if not_assigned and not quiet:
        console.print(f"[yellow]Info:[/yellow] {len(not_assigned)} ticket(s) not assigned to" + 
                     (f" sprint {from_sprint}" if from_sprint else " any sprint"))
    
    if not valid_tickets:
        if not quiet:
            console.print("[yellow]No tickets to unassign[/yellow]")
        raise typer.Exit(0)
    
    # Show preview if requested
    if not quiet and (len(valid_tickets) >= 5 or dry_run):
        console.print(f"\n[yellow]About to unassign {len(valid_tickets)} ticket(s):[/yellow]")
        
        table = Table(title="Tickets to Unassign", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Current Sprint", style="magenta")
        
        for ticket, _ in valid_tickets[:10]:
            table.add_row(
                ticket.id,
                ticket.title[:40] + "..." if len(ticket.title) > 40 else ticket.title,
                ticket.sprint_id or "[dim]None[/dim]"
            )
        
        if len(valid_tickets) > 10:
            table.add_row("...", f"and {len(valid_tickets) - 10} more", "...")
        
        console.print(table)
    
    if dry_run:
        console.print("\n[yellow]DRY RUN:[/yellow] No changes were made")
        return
    
    # Perform unassignments
    successful_unassignments = []
    failed_unassignments = []
    affected_sprints = set()
    
    for ticket, ticket_path in valid_tickets:
        old_sprint_id = ticket.sprint_id
        ticket.sprint_id = None
        
        try:
            ticket.save_to_json_file(str(ticket_path))
            successful_unassignments.append(ticket.id)
            affected_sprints.add(old_sprint_id)
        except Exception:
            failed_unassignments.append(ticket.id)
    
    # Update affected sprints
    for sprint_id in affected_sprints:
        sprint = load_sprint_by_id(sprint_id, root)
        if sprint:
            # Remove unassigned tickets from sprint's ticket list
            sprint.tickets = [tid for tid in sprint.tickets if tid not in successful_unassignments]
            save_sprint_with_tickets(sprint, root)
    
    # Output results
    if output == "json":
        import json
        result = {
            "summary": {
                "total_requested": len(all_ticket_ids),
                "successful": len(successful_unassignments),
                "not_assigned": len(not_assigned),
                "missing": len(missing_tickets),
                "failed": len(failed_unassignments)
            },
            "successful_unassignments": successful_unassignments,
            "not_assigned": not_assigned,
            "missing_tickets": missing_tickets,
            "failed_unassignments": failed_unassignments,
            "affected_sprints": list(affected_sprints)
        }
        console.print(json.dumps(result, indent=2))
    else:
        if not quiet:
            if successful_unassignments:
                console.print(f"\n✅ Successfully unassigned {len(successful_unassignments)} ticket(s)")
            if failed_unassignments:
                console.print(f"[red]❌ Failed to unassign {len(failed_unassignments)} ticket(s)[/red]")