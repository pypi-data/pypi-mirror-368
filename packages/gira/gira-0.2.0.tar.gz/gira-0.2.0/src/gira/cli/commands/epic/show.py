"""Show epic command for Gira."""

from pathlib import Path
from typing import List, Optional, Tuple

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.table import Table

from gira.models import Epic, Ticket
from gira.utils.board_config import get_board_configuration
from gira.utils.errors import require_epic
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_tickets_by_ids, find_ticket
from gira.utils.typer_completion import complete_epic_ids

def load_epic(epic_id: str, root: Path) -> Optional[Epic]:
    """Load an epic by its ID."""
    from gira.constants import normalize_epic_id
    
    # Normalize the epic ID (handles number-only input)
    epic_id = normalize_epic_id(epic_id)
    
    epics_dir = root / ".gira" / "epics"
    epic_file = epics_dir / f"{epic_id}.json"

    if not epic_file.exists():
        return None

    try:
        return Epic.from_json_file(str(epic_file))
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load epic {epic_id}: {e}")
        return None


def get_epic_tickets(epic: Epic, root: Path) -> List[Ticket]:
    """Get all tickets that belong to this epic, including archived tickets."""
    tickets_dict = {}  # Use dict with ticket ID as key to avoid duplicates
    
    # First, load tickets from the epic's tickets array
    if epic.tickets:
        epic_tickets = load_tickets_by_ids(epic.tickets, root, include_archived=True)
        for ticket in epic_tickets:
            tickets_dict[ticket.id] = ticket
    
    # Also search for tickets that have this epic_id but might not be in the tickets array
    # This is important for finding archived tickets that were removed from the epic's tickets list
    from gira.utils.ticket_utils import load_all_tickets
    all_tickets = load_all_tickets(root, include_archived=True)
    
    for ticket in all_tickets:
        if hasattr(ticket, 'epic_id') and ticket.epic_id == epic.id:
            tickets_dict[ticket.id] = ticket
    
    # Convert to list and sort by ticket ID
    epic_tickets = list(tickets_dict.values())
    epic_tickets.sort(key=lambda t: (t.id.split('-')[0], int(t.id.split('-')[1])))

    return epic_tickets


def separate_active_and_archived_tickets(tickets: List[Ticket], root: Path) -> Tuple[List[Ticket], List[Ticket]]:
    """Separate tickets into active and archived lists."""
    active_tickets = []
    archived_tickets = []
    
    for ticket in tickets:
        # Check if ticket is archived by trying to find it in active directories
        active_ticket, _ = find_ticket(ticket.id, root, include_archived=False)
        if active_ticket is None:
            archived_tickets.append(ticket)
        else:
            active_tickets.append(ticket)
    
    return active_tickets, archived_tickets


def calculate_epic_progress(tickets: List[Ticket], root: Path) -> dict:
    """Calculate progress statistics for the epic."""
    if not tickets:
        return {
            "total": 0,
            "by_status": {},
            "completed": 0,
            "todo": 0,
            "completion_percentage": 0,
            "archived": 0,
            "total_story_points": 0,
            "completed_story_points": 0,
            "remaining_story_points": 0,
            "points_completion_percentage": 0
        }

    # Load board config to get valid statuses
    board = get_board_configuration()
    
    # Count tickets by status and check archive status
    status_counts = {}
    archived_count = 0
    total_story_points = 0
    completed_story_points = 0
    
    for swimlane in board.swimlanes:
        status_counts[swimlane.id] = 0
    
    # Determine completed status (typically "done" but check board config)
    completed_statuses = [s.id for s in board.swimlanes if s.id in ["done", "completed", "closed"]]
    if not completed_statuses and board.swimlanes:
        # If no typical completed status, use the last swimlane as completed
        completed_statuses = [board.swimlanes[-1].id]
    
    for ticket in tickets:
        # Get story points (default to 0 if not set)
        story_points = getattr(ticket, 'story_points', 0) or 0
        total_story_points += story_points
        
        # Check if ticket is archived
        active_ticket, _ = find_ticket(ticket.id, root, include_archived=False)
        is_archived = active_ticket is None
        
        if is_archived:
            archived_count += 1
            completed_story_points += story_points
        else:
            # Only count non-archived tickets in status counts
            if ticket.status in status_counts:
                status_counts[ticket.status] += 1
                # Add to completed story points if in completed status
                if ticket.status in completed_statuses:
                    completed_story_points += story_points
    
    total = len(tickets)
    
    # Count archived tickets as completed
    completed = sum(status_counts.get(status, 0) for status in completed_statuses) + archived_count
    completion_percentage = (completed / total * 100) if total > 0 else 0
    
    # Calculate todo count (includes todo and backlog statuses)
    todo_statuses = ["todo", "backlog"]
    todo_count = sum(status_counts.get(status, 0) for status in todo_statuses)
    
    # Calculate remaining story points
    remaining_story_points = total_story_points - completed_story_points
    points_completion_percentage = (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0

    return {
        "total": total,
        "by_status": status_counts,
        "completed": completed,
        "todo": todo_count,
        "completion_percentage": completion_percentage,
        "board": board,
        "archived": archived_count,
        "total_story_points": total_story_points,
        "completed_story_points": completed_story_points,
        "remaining_story_points": remaining_story_points,
        "points_completion_percentage": points_completion_percentage
    }


def show_epic_tickets_table(tickets: List[Ticket], root: Path, show_as_one_table: bool = False) -> None:
    """Display tickets belonging to the epic in a table format."""
    if not tickets:
        console.print("[dim]No tickets assigned to this epic[/dim]")
        return

    # Separate active and archived tickets
    active_tickets, archived_tickets = separate_active_and_archived_tickets(tickets, root)
    
    def create_ticket_table() -> Table:
        """Create a new ticket table with standard columns."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="white", width=40)
        table.add_column("Status", style="yellow")
        table.add_column("Priority", style="magenta")
        table.add_column("Points", style="blue", justify="right")
        table.add_column("Assignee", style="green")
        return table
    
    def add_ticket_to_table(table: Table, ticket: Ticket, is_archived: bool = False) -> None:
        """Add a ticket row to the table."""
        # Truncate title if too long
        title = ticket.title
        if len(title) > 40:
            title = title[:37] + "..."

        # Style status
        status_style = {
            "todo": "yellow",
            "backlog": "dim yellow",
            "in_progress": "blue",
            "review": "magenta",
            "done": "green"
        }.get(ticket.status, "white")

        # Style priority
        priority_style = {
            "high": "red",
            "medium": "yellow",
            "low": "green"
        }.get(ticket.priority, "white")

        # Format status with archived indicator
        status_display = ticket.status.replace('_', ' ').title()
        if is_archived:
            status_display = f"{status_display} [dim](Archived)[/dim]"
        
        # Get story points
        story_points = getattr(ticket, 'story_points', None)
        points_display = str(story_points) if story_points else "-"

        table.add_row(
            ticket.id,
            title,
            f"[{status_style}]{status_display}[/{status_style}]",
            f"[{priority_style}]{ticket.priority.title()}[/{priority_style}]",
            points_display,
            ticket.assignee or "-"
        )
    
    if show_as_one_table:
        # Show all tickets in one table (legacy behavior)
        table = create_ticket_table()
        for ticket in tickets:
            is_archived = ticket in archived_tickets
            add_ticket_to_table(table, ticket, is_archived)
        console.print("\n[bold]Epic Tickets[/bold]")
        console.print(table)
    else:
        # Show active and archived tickets separately
        if active_tickets:
            console.print(f"\n[bold]Active Tickets ({len(active_tickets)})[/bold]")
            active_table = create_ticket_table()
            for ticket in active_tickets:
                add_ticket_to_table(active_table, ticket, is_archived=False)
            console.print(active_table)
        
        if archived_tickets:
            console.print(f"\n[bold dim]Archived Tickets ({len(archived_tickets)})[/bold dim]")
            archived_table = create_ticket_table()
            for ticket in archived_tickets:
                add_ticket_to_table(archived_table, ticket, is_archived=True)
            console.print(archived_table)


def show_epic_details(epic: Epic, epic_file: Path, root: Path, show_tickets: bool = True) -> None:
    """Display detailed epic information."""
    from rich.console import Group

    from gira.utils.config import get_global_config
    from gira.utils.display import render_markdown_content

    # Load tickets for this epic
    tickets = get_epic_tickets(epic, root) if show_tickets else []
    progress = calculate_epic_progress(tickets, root)

    # Build content lines
    content_lines = []

    # Header with ID and title
    content_lines.append(f"[bold cyan]{epic.id}[/bold cyan] - [bold]{epic.title}[/bold]")
    content_lines.append("")

    # Status and ownership
    status_style = {
        "draft": "yellow",
        "active": "green",
        "completed": "blue"
    }.get(epic.status, "white")

    content_lines.append(f"[yellow]Status:[/yellow] [{status_style}]{epic.status.title()}[/{status_style}]")
    content_lines.append(f"[yellow]Owner:[/yellow] {epic.owner}")
    content_lines.append("")

    # Progress information
    if tickets:
        content_lines.append(f"[yellow]Progress:[/yellow] {progress['completed']}/{progress['total']} tickets completed ({progress['completion_percentage']:.1f}%)")
        
        # Show story points if any tickets have them
        if progress['total_story_points'] > 0:
            content_lines.append(f"[yellow]Story Points:[/yellow] {progress['completed_story_points']}/{progress['total_story_points']} points completed ({progress['points_completion_percentage']:.1f}%)")
            content_lines.append(f"  • [green]Completed:[/green] {progress['completed_story_points']} points")
            content_lines.append(f"  • [yellow]Remaining:[/yellow] {progress['remaining_story_points']} points")
        
        content_lines.append("")
        content_lines.append("[yellow]Ticket Breakdown:[/yellow]")
        
        # Display archived tickets if any
        if progress['archived'] > 0:
            content_lines.append(f"  • [dim]Archived:[/dim] {progress['archived']} tickets")
        
        # Display status breakdown based on board configuration
        board = progress['board']
        for swimlane in board.swimlanes:
            count = progress['by_status'].get(swimlane.id, 0)
            if count > 0:
                # Determine color based on common status names
                if swimlane.id in ["done", "completed", "closed"]:
                    color = "green"
                elif swimlane.id in ["review", "testing", "qa"]:
                    color = "magenta"
                elif swimlane.id in ["in_progress", "active", "doing"]:
                    color = "blue"
                elif swimlane.id in ["todo", "ready", "backlog", "planned"]:
                    color = "yellow"
                else:
                    color = "white"
                
                content_lines.append(f"  • [{color}]{swimlane.name}:[/{color}] {count} tickets")
    else:
        content_lines.append("[yellow]Progress:[/yellow] No tickets assigned")

    content_lines.append("")

    # Target date
    if epic.target_date:
        content_lines.append(f"[yellow]Target Date:[/yellow] {epic.target_date}")
        content_lines.append("")

    # Custom fields
    if hasattr(epic, 'custom_fields') and epic.custom_fields:
        content_lines.append("[yellow]Custom Fields:[/yellow]")
        
        # Try to load config to get field definitions for better display
        try:
            from gira.models.config import ProjectConfig
            config = ProjectConfig.from_json_file(str(root / ".gira" / "config.json"))
            
            for field_name, field_value in sorted(epic.custom_fields.items()):
                field_def = config.custom_fields.get_field_by_name(field_name)
                display_name = field_def.display_name if field_def else field_name
                
                # Format value based on type
                if isinstance(field_value, bool):
                    display_value = "Yes" if field_value else "No"
                else:
                    display_value = str(field_value)
                
                content_lines.append(f"  [dim]{display_name}:[/dim] {display_value}")
        except Exception:
            # Fallback to simple display if config can't be loaded
            for field_name, field_value in sorted(epic.custom_fields.items()):
                # Format boolean values
                if isinstance(field_value, bool):
                    display_value = "Yes" if field_value else "No"
                else:
                    display_value = str(field_value)
                
                content_lines.append(f"  [dim]{field_name}:[/dim] {display_value}")
        
        content_lines.append("")

    # Timestamps
    content_lines.append(f"[dim]Created: {epic.created_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    content_lines.append(f"[dim]Updated: {epic.updated_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    # Tickets section - show all tickets including those found via epic_id
    if tickets:
        content_lines.append("")
        content_lines.append(f"[yellow]Tickets ({len(tickets)}):[/yellow]")
        for ticket in tickets:
            content_lines.append(f"  • {ticket.id}")

    # File location
    content_lines.append("")
    content_lines.append(f"[dim]Location: {epic_file.relative_to(root)}[/dim]")

    # Check if we have a description and should render markdown
    has_markdown_description = False
    markdown_content = None
    if epic.description:
        config = get_global_config()
        render_markdown = True
        if config is not None:
            render_markdown = config.render_markdown

        if render_markdown:
            markdown_content = render_markdown_content(epic.description)
            has_markdown_description = markdown_content is not None

    if has_markdown_description and markdown_content:
        # Add description header to content
        content_lines.append("")
        content_lines.append("[yellow]Description:[/yellow]")

        # Create the basic panel without description
        basic_content = "\n".join(content_lines)

        # Create a group that combines the basic info and markdown
        group_content = Group(
            basic_content,
            markdown_content  # No padding - align with other content
        )

        # Create panel with the group
        panel = Panel(
            group_content,
            title="Epic Details",
            border_style="cyan",
            padding=(1, 2)
        )
    else:
        # No markdown or plain text mode
        if epic.description:
            content_lines.append("")
            content_lines.append("[yellow]Description:[/yellow]")
            content_lines.append("")
            content_lines.append(epic.description)

        # Create panel with plain text
        panel = Panel(
            "\n".join(content_lines),
            title="Epic Details",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print(panel)

    # Show tickets table if we have tickets and show_tickets is True
    if show_tickets and tickets:
        show_epic_tickets_table(tickets, root)


def show(
    epic_id: str = typer.Argument(..., help="Epic ID to show (e.g., EPIC-001)", autocompletion=complete_epic_ids),
    output_format: OutputFormat = add_format_option(OutputFormat.TEXT),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON (shorthand for --format json)"),
    tickets: bool = typer.Option(True, "--tickets/--no-tickets", help="Show tickets belonging to this epic"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression to filter JSON output (e.g., '$.tickets[*]')"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Show details of a specific epic.
    
    Examples:
        # Show epic details
        gira epic show EPIC-001
        
        # Show epic without ticket list
        gira epic show EPIC-001 --no-tickets
        
        # Export as JSON
        gira epic show EPIC-001 --format json
        gira epic show EPIC-001 --json
        
        # Export as JSON with JSONPath filtering
        gira epic show EPIC-001 --json --filter-json '$.title'
        gira epic show EPIC-001 --format json --filter-json '$.ticket_details[*].id'
    """
    root = ensure_gira_project()
    
    # Handle --json flag as shorthand for --format json
    if json_output:
        output_format = OutputFormat.JSON

    # Load the epic
    epic = load_epic(epic_id, root)

    # Handle not found using standardized error handling
    require_epic(epic_id.upper(), epic, output_format)

    # Get epic file path
    epics_dir = root / ".gira" / "epics"
    epic_file = epics_dir / f"{epic.id}.json"
    
    # Validate filter_json is only used with JSON format
    if filter_json and output_format != OutputFormat.JSON:
        console.print("[red]Error:[/red] --filter-json can only be used with --format json or --json")
        raise typer.Exit(1)

    # Output in requested format
    if output_format in [OutputFormat.TEXT, OutputFormat.TABLE]:
        # Use the existing detailed display
        show_epic_details(epic, epic_file, root, show_tickets=tickets)
    else:
        # Prepare data for other formats
        epic_data = epic.model_dump(mode='json')

        # Add ticket information if requested
        if tickets:
            epic_tickets = get_epic_tickets(epic, root)
            epic_data["ticket_details"] = [t.model_dump(mode='json') for t in epic_tickets]
            progress = calculate_epic_progress(epic_tickets, root)
            # Remove the board object from progress for JSON serialization
            epic_data["progress"] = {
                "total": progress["total"],
                "completed": progress["completed"],
                "todo": progress["todo"],
                "completion_percentage": progress["completion_percentage"],
                "by_status": progress["by_status"],
                "archived": progress["archived"],
                "story_points": {
                    "total": progress["total_story_points"],
                    "completed": progress["completed_story_points"],
                    "remaining": progress["remaining_story_points"],
                    "completion_percentage": progress["points_completion_percentage"]
                }
            }

        # Use the new output system for other formats
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(epic_data, output_format, jsonpath_filter=filter_json, **color_kwargs)
