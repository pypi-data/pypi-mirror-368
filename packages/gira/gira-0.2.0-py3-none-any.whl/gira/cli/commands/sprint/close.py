"""Close sprint command."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from gira.models.sprint import Sprint, SprintStatus
from gira.models.ticket import Ticket
from gira.utils.board_config import get_board_configuration
from gira.utils.git_ops import should_use_git, move_with_git_fallback
from gira.utils.project import ensure_gira_project

def close(
    sprint_id: str = typer.Argument(
        ...,
        help="Sprint ID to close"
    ),
    retrospective: bool = typer.Option(
        True,
        "--retrospective/--no-retrospective",
        help="Include retrospective"
    ),
    git: Optional[bool] = typer.Option(
        None,
        "--git/--no-git",
        help="Stage the sprint move using 'git mv'"
    ),
) -> None:
    """Close a sprint (change status to completed).
    
    Moves the sprint from active to completed directory and optionally
    collects retrospective feedback.
    
    Git Integration:
        By default, sprint moves are automatically staged with 'git mv' if .gira is tracked.
        Control this behavior with:
        - --git / --no-git flags
        - GIRA_AUTO_GIT_MV environment variable
        - git.auto_stage_moves in config.json
    """
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()

    # Find the sprint
    active_dir = gira_root / ".gira" / "sprints" / "active"
    sprint_path = active_dir / f"{sprint_id}.json"

    if not sprint_path.exists():
        console.print(f"[red]Error:[/red] Sprint {sprint_id} not found in active sprints")
        raise typer.Exit(1)

    # Load sprint
    try:
        sprint = Sprint.model_validate_json(sprint_path.read_text())
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load sprint: {e}")
        raise typer.Exit(1)

    # Check status
    if sprint.status != SprintStatus.ACTIVE:
        status_str = sprint.status.value if hasattr(sprint.status, 'value') else sprint.status
        console.print(f"[red]Error:[/red] Sprint {sprint_id} is not active (status: {status_str})")
        raise typer.Exit(1)

    # Get retrospective if requested
    if retrospective:
        console.print("\n[bold]Sprint Retrospective[/bold]\n")

        what_went_well = Prompt.ask(
            "[green]What went well?[/green]",
            default=""
        )

        what_went_wrong = Prompt.ask(
            "[red]What didn't go well?[/red]",
            default=""
        )

        action_items = Prompt.ask(
            "[yellow]Action items for next sprint?[/yellow]",
            default=""
        )

        sprint.retrospective = {
            "what_went_well": what_went_well.split(";") if what_went_well else [],
            "what_went_wrong": what_went_wrong.split(";") if what_went_wrong else [],
            "action_items": action_items.split(";") if action_items else []
        }

    # Update sprint
    sprint.status = SprintStatus.COMPLETED
    sprint.updated_at = datetime.now()

    # Determine whether to use git operations
    use_git = should_use_git(gira_root, git, "move")

    # Move to completed directory
    completed_dir = gira_root / ".gira" / "sprints" / "completed"
    completed_dir.mkdir(parents=True, exist_ok=True)

    # Save updated sprint data to the current file first
    sprint_path.write_text(sprint.model_dump_json(indent=2))

    # Move sprint file to completed directory
    new_path = completed_dir / f"{sprint_id}.json"
    move_with_git_fallback(sprint_path, new_path, gira_root, use_git)

    # Show summary
    _show_sprint_summary(sprint, gira_root)


def _show_sprint_summary(sprint: Sprint, gira_root: Path) -> None:
    """Show sprint closure summary."""
    # Load board config to get valid statuses
    board = get_board_configuration()
    
    # Initialize ticket counts based on board swimlanes
    ticket_counts = {swimlane.id: 0 for swimlane in board.swimlanes}

    tickets_dir = gira_root / ".gira" / "tickets"
    if tickets_dir.exists() and sprint.tickets:
        for ticket_id in sprint.tickets:
            ticket_path = tickets_dir / f"{ticket_id}.json"
            if ticket_path.exists():
                try:
                    ticket = Ticket.model_validate_json(ticket_path.read_text())
                    # Handle both enum and string status values
                    status = ticket.status.value if hasattr(ticket.status, 'value') else ticket.status
                    if status in ticket_counts:
                        ticket_counts[status] += 1
                except Exception:
                    pass

    # Create summary panel
    summary_lines = [
        f"[green]✓[/green] Closed sprint [cyan]{sprint.id}[/cyan]\n",
        f"[dim]Name:[/dim] {sprint.name}",
        f"[dim]Duration:[/dim] {(sprint.end_date - sprint.start_date).days + 1} days",
        "[dim]Status:[/dim] [blue]Completed[/blue]\n",
        "[bold]Ticket Summary:[/bold]"
    ]
    
    # Add status counts based on board configuration
    for swimlane in board.swimlanes:
        count = ticket_counts.get(swimlane.id, 0)
        if count > 0 or swimlane.id in ["done", "todo", "in_progress"]:  # Always show key statuses
            summary_lines.append(f"  • {swimlane.name}: {count}")
    
    summary_lines.append(f"  • Total: {sum(ticket_counts.values())}")

    if sprint.retrospective:
        summary_lines.append("\n[bold]Retrospective:[/bold]")

        if sprint.retrospective.get("what_went_well"):
            summary_lines.append("[green]What went well:[/green]")
            for item in sprint.retrospective["what_went_well"]:
                if item.strip():
                    summary_lines.append(f"  • {item.strip()}")

        if sprint.retrospective.get("what_went_wrong"):
            summary_lines.append("[red]What didn't go well:[/red]")
            for item in sprint.retrospective["what_went_wrong"]:
                if item.strip():
                    summary_lines.append(f"  • {item.strip()}")

        if sprint.retrospective.get("action_items"):
            summary_lines.append("[yellow]Action items:[/yellow]")
            for item in sprint.retrospective["action_items"]:
                if item.strip():
                    summary_lines.append(f"  • {item.strip()}")

    console.print(Panel(
        Text.from_markup("\n".join(summary_lines)),
        title="Sprint Closed",
        border_style="green"
    ))
