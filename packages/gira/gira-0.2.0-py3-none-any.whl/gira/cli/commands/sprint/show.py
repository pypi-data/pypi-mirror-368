"""Show sprint command for Gira."""

from pathlib import Path
from typing import List, Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.table import Table

from gira.models import Sprint, Ticket
from gira.utils.errors import require_sprint
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets
from gira.utils.typer_completion import complete_sprint_ids

def load_sprint(sprint_id: str, root: Path) -> Optional[Sprint]:
    """Load a sprint by its ID."""
    sprints_dir = root / ".gira" / "sprints"

    # Check in all possible sprint directories
    for subdir in ["active", "completed", "planned", ""]:
        if subdir:
            sprint_file = sprints_dir / subdir / f"{sprint_id.upper()}.json"
        else:
            # Check root sprints directory
            sprint_file = sprints_dir / f"{sprint_id.upper()}.json"
            
        if sprint_file.exists():
            try:
                return Sprint.from_json_file(str(sprint_file))
            except Exception as e:
                console.print(f"[red]Error:[/red] Failed to load sprint {sprint_id}: {e}")
                return None

    return None


def get_sprint_tickets(sprint: Sprint, root: Path) -> List[Ticket]:
    """Get all tickets that belong to this sprint."""
    if not sprint.tickets:
        return []

    # Load all tickets (including archived ones since completed sprints may have archived tickets)
    all_tickets = load_all_tickets(root, include_archived=True)

    # Filter tickets that belong to this sprint
    sprint_tickets = []
    for ticket in all_tickets:
        if ticket.id in sprint.tickets:
            sprint_tickets.append(ticket)

    # Sort by ticket ID
    sprint_tickets.sort(key=lambda t: (t.id.split('-')[0], int(t.id.split('-')[1])))

    return sprint_tickets


def calculate_sprint_progress(tickets: List[Ticket]) -> dict:
    """Calculate progress statistics for the sprint."""
    from gira.utils.board_config import get_board_configuration
    
    # Load board configuration
    board = get_board_configuration()
    
    # Initialize the result with board
    result = {
        "board": board,
        "total": 0,
        "completed": 0,
        "completion_percentage": 0,
        "story_points_total": 0,
        "story_points_completed": 0,
        "story_points_percentage": 0,
        "by_status": {}
    }
    
    if not tickets:
        # Initialize by_status with zeros for all swimlanes
        for swimlane in board.swimlanes:
            result["by_status"][swimlane.id] = 0
        return result

    total = len(tickets)
    
    # Count tickets by dynamic status
    by_status = {}
    for swimlane in board.swimlanes:
        by_status[swimlane.id] = len([t for t in tickets if t.status.lower() == swimlane.id.lower()])
    
    # Completed count (tickets in "done" or similar final states)
    completed = by_status.get("done", 0)
    
    completion_percentage = (completed / total * 100) if total > 0 else 0

    # Calculate story points if available
    story_points_total = sum(t.story_points or 0 for t in tickets)
    story_points_completed = sum(t.story_points or 0 for t in tickets if t.status.lower() == "done")
    story_points_percentage = (story_points_completed / story_points_total * 100) if story_points_total > 0 else 0

    return {
        "board": board,
        "total": total,
        "completed": completed,
        "completion_percentage": completion_percentage,
        "story_points_total": story_points_total,
        "story_points_completed": story_points_completed,
        "story_points_percentage": story_points_percentage,
        "by_status": by_status
    }


def show_sprint_tickets_table(tickets: List[Ticket]) -> None:
    """Display tickets belonging to the sprint in a table format."""
    if not tickets:
        console.print("[dim]No tickets assigned to this sprint[/dim]")
        return

    table = Table(show_header=True, header_style="bold magenta")

    # Add columns
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white", width=40)
    table.add_column("Status", style="yellow")
    table.add_column("Priority", style="magenta")
    table.add_column("Assignee", style="green")
    table.add_column("Points", style="blue", justify="right")

    # Add rows
    for ticket in tickets:
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

        table.add_row(
            ticket.id,
            title,
            f"[{status_style}]{ticket.status.replace('_', ' ').title()}[/{status_style}]",
            f"[{priority_style}]{ticket.priority.title()}[/{priority_style}]",
            ticket.assignee or "-",
            str(ticket.story_points) if ticket.story_points else "-"
        )

    console.print("\n[bold]Sprint Tickets[/bold]")
    console.print(table)


def show_sprint_details(sprint: Sprint, sprint_file: Path, root: Path, show_tickets: bool = True) -> None:
    """Display detailed sprint information."""
    # Load tickets for this sprint
    tickets = get_sprint_tickets(sprint, root)
    progress = calculate_sprint_progress(tickets)

    # Build content lines
    content_lines = []

    # Header with ID and name
    content_lines.append(f"[bold cyan]{sprint.id}[/bold cyan] - [bold]{sprint.name}[/bold]")
    content_lines.append("")

    # Status and dates
    status_style = {
        "planning": "yellow",
        "active": "green",
        "closed": "blue"
    }.get(sprint.status, "white")

    content_lines.append(f"[yellow]Status:[/yellow] [{status_style}]{sprint.status.title()}[/{status_style}]")
    content_lines.append(f"[yellow]Start Date:[/yellow] {sprint.start_date}")
    content_lines.append(f"[yellow]End Date:[/yellow] {sprint.end_date}")

    # Calculate days remaining for active sprints
    if sprint.status == "active":
        from datetime import date
        today = date.today()
        days_remaining = (sprint.end_date - today).days
        if days_remaining >= 0:
            content_lines.append(f"[yellow]Days Remaining:[/yellow] {days_remaining}")
        else:
            content_lines.append(f"[yellow]Days Overdue:[/yellow] [red]{abs(days_remaining)}[/red]")

    content_lines.append("")

    # Sprint goal
    markdown_content = None
    if sprint.goal:
        from gira.utils.display import render_markdown_content
        markdown_content = render_markdown_content(sprint.goal)
        
        if markdown_content:
            # For markdown, we need to handle the layout differently
            content_lines.append("[yellow]Goal:[/yellow]")
            # We'll add the markdown content separately after creating the basic panel
        else:
            content_lines.append("[yellow]Goal:[/yellow]")
            content_lines.append(sprint.goal)
            content_lines.append("")

    # Progress information
    if tickets:
        content_lines.append(f"[yellow]Progress:[/yellow] {progress['completed']}/{progress['total']} tickets completed ({progress['completion_percentage']:.1f}%)")

        if progress['story_points_total'] > 0:
            content_lines.append(f"[yellow]Story Points:[/yellow] {progress['story_points_completed']}/{progress['story_points_total']} completed ({progress['story_points_percentage']:.1f}%)")

        content_lines.append("[yellow]Breakdown:[/yellow]")
        
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
                
                content_lines.append(f"  • [{color}]{swimlane.name}:[/{color}] {count}")
    else:
        content_lines.append("[yellow]Progress:[/yellow] No tickets assigned")

    content_lines.append("")

    # Sprint capacity/velocity if stored in extra fields
    if hasattr(sprint, 'velocity') and sprint.velocity is not None:
        content_lines.append(f"[yellow]Velocity:[/yellow] {sprint.velocity}")

    # Timestamps
    content_lines.append(f"[dim]Created: {sprint.created_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    content_lines.append(f"[dim]Updated: {sprint.updated_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    # File location
    content_lines.append("")
    content_lines.append(f"[dim]Location: {sprint_file.relative_to(root)}[/dim]")

    # Create panel
    # Check if we have markdown goal content to include
    has_markdown_goal = sprint.goal and markdown_content is not None
    
    if has_markdown_goal:
        from rich.console import Group
        # Create a group that combines the basic info and markdown goal
        basic_content = "\n".join(content_lines)
        group_content = Group(
            basic_content,
            "",  # Empty line separator
            markdown_content
        )
        
        panel = Panel(
            group_content,
            title="Sprint Details",
            border_style="cyan",
            padding=(1, 2)
        )
    else:
        panel = Panel(
            "\n".join(content_lines),
            title="Sprint Details",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print(panel)

    # Show tickets table if requested and we have tickets
    if show_tickets and tickets:
        show_sprint_tickets_table(tickets)


def show(
    sprint_id: str = typer.Argument(..., help="Sprint ID to show (e.g., SPRINT-001)", autocompletion=complete_sprint_ids),
    output_format: OutputFormat = add_format_option(OutputFormat.TEXT),
    json_flag: bool = typer.Option(False, "--json", help="Output in JSON format (shorthand for --format json)"),
    tickets: bool = typer.Option(True, "--tickets/--no-tickets", help="Show tickets belonging to this sprint"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression to filter JSON output (e.g., '$.tickets[*]')"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Show details of a specific sprint.
    
    Examples:
        # Show sprint details
        gira sprint show SPRINT-001
        
        # Show sprint without ticket list
        gira sprint show SPRINT-001 --no-tickets
        
        # Export as JSON
        gira sprint show SPRINT-001 --json
        
        # Export as JSON with JSONPath filtering
        gira sprint show SPRINT-001 --format json --filter-json '$.name'
        gira sprint show SPRINT-001 --format json --filter-json '$.tickets[*]'
    """
    root = ensure_gira_project()
    
    # Handle --json flag as shorthand for --format json
    if json_flag:
        output_format = OutputFormat.JSON

    # Load the sprint
    sprint = load_sprint(sprint_id, root)

    # Handle not found using standardized error handling
    require_sprint(sprint_id.upper(), sprint, output_format)

    # Get sprint file path
    sprints_dir = root / ".gira" / "sprints"
    sprint_file = None
    
    # Check in all possible sprint directories
    for subdir in ["active", "completed", "planned", ""]:
        if subdir:
            possible_file = sprints_dir / subdir / f"{sprint.id}.json"
        else:
            # Check root sprints directory
            possible_file = sprints_dir / f"{sprint.id}.json"
            
        if possible_file.exists():
            sprint_file = possible_file
            break
    
    # Fallback if file not found (shouldn't happen if sprint was loaded)
    if not sprint_file:
        sprint_file = sprints_dir / f"{sprint.id}.json"
    
    # Validate filter_json is only used with JSON format
    if filter_json and output_format != OutputFormat.JSON:
        console.print("[red]Error:[/red] --filter-json can only be used with --format json")
        raise typer.Exit(1)

    # Output in requested format
    if output_format in [OutputFormat.TEXT, OutputFormat.TABLE]:
        # Use the existing detailed display
        show_sprint_details(sprint, sprint_file, root, show_tickets=tickets)
    else:
        # Prepare data for other formats
        sprint_data = sprint.model_dump(mode='json')

        # Add ticket information if requested
        if tickets:
            sprint_tickets = get_sprint_tickets(sprint, root)
            sprint_data["ticket_details"] = [t.model_dump(mode='json') for t in sprint_tickets]
            progress = calculate_sprint_progress(sprint_tickets)
            # Remove the board object for JSON serialization
            sprint_data["progress"] = {k: v for k, v in progress.items() if k != "board"}

        # Use the new output system for other formats
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(sprint_data, output_format, jsonpath_filter=filter_json, **color_kwargs)
