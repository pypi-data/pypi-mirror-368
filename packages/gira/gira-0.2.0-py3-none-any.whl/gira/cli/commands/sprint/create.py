"""Create sprint command."""

from datetime import date, timedelta
from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.text import Text

from gira.models.sprint import Sprint, SprintStatus
from gira.utils.project import ensure_gira_project

def create(
    name: str = typer.Argument(
        ...,
        help="Sprint name"
    ),
    goal: Optional[str] = typer.Option(
        None,
        "-g", "--goal",
        help="Sprint goal"
    ),
    goal_file: Optional[str] = typer.Option(
        None,
        "--goal-file",
        help="Read goal from a file"
    ),
    start_date: Optional[str] = typer.Option(
        None,
        "-s", "--start-date",
        help="Start date (YYYY-MM-DD, defaults to today)"
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "-e", "--end-date",
        help="End date (YYYY-MM-DD, overrides duration)"
    ),
    duration: int = typer.Option(
        14,
        "-d", "--duration",
        help="Duration in days (ignored if end-date is provided)"
    ),
    quiet: bool = typer.Option(
        False,
        "-q", "--quiet",
        help="Quiet mode - only show sprint ID"
    ),
) -> None:
    """Create a new sprint."""
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()
    
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

    # Parse start date
    if start_date:
        try:
            start = date.fromisoformat(start_date)
        except ValueError:
            console.print("[red]Error:[/red] Invalid date format. Use YYYY-MM-DD")
            raise typer.Exit(1)
    else:
        start = date.today()

    # Calculate end date
    if end_date:
        try:
            end = date.fromisoformat(end_date)
        except ValueError:
            console.print("[red]Error:[/red] Invalid end date format. Use YYYY-MM-DD")
            raise typer.Exit(1)

        # Validate that end date is after start date
        if end <= start:
            console.print("[red]Error:[/red] End date must be after start date")
            raise typer.Exit(1)

        # Calculate actual duration
        duration = (end - start).days + 1
    else:
        end = start + timedelta(days=duration - 1)

    # Generate sprint ID
    sprint_id = f"SPRINT-{start.isoformat()}"

    # Check if sprint already exists
    sprints_dir = gira_root / ".gira" / "sprints" / "active"
    sprint_path = sprints_dir / f"{sprint_id}.json"

    if sprint_path.exists():
        console.print(f"[red]Error:[/red] Sprint {sprint_id} already exists")
        raise typer.Exit(1)

    # Create sprint
    sprint = Sprint(
        id=sprint_id,
        name=name,
        goal=goal,
        start_date=start,
        end_date=end,
        status=SprintStatus.PLANNED,
        tickets=[],
    )

    # Save sprint
    sprints_dir.mkdir(parents=True, exist_ok=True)
    sprint_path.write_text(sprint.model_dump_json(indent=2))

    # Output
    if quiet:
        console.print(sprint_id)
    else:
        console.print(Panel(
            Text.from_markup(
                f"[green]✓[/green] Created sprint [cyan]{sprint_id}[/cyan]\n\n"
                f"[dim]Name:[/dim] {name}\n"
                f"[dim]Goal:[/dim] {goal or '[gray]None[/gray]'}\n"
                f"[dim]Start:[/dim] {start.isoformat()}\n"
                f"[dim]End:[/dim] {end.isoformat()}\n"
                f"[dim]Duration:[/dim] {duration} days\n"
                f"[dim]Status:[/dim] [yellow]Planned[/yellow]"
            ),
            title="Sprint Created",
            border_style="green"
        ))
