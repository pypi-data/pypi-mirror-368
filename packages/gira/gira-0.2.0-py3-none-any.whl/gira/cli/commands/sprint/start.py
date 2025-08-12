"""Start sprint command."""

from datetime import datetime

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.text import Text

from gira.models.sprint import Sprint, SprintStatus
from gira.utils.project import ensure_gira_project

def start(
    sprint_id: str = typer.Argument(
        ...,
        help="Sprint ID to start"
    ),
) -> None:
    """Start a sprint (change status from planned to active)."""
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()

    # Find the sprint
    sprints_dir = gira_root / ".gira" / "sprints" / "active"
    sprint_path = sprints_dir / f"{sprint_id}.json"

    if not sprint_path.exists():
        console.print(f"[red]Error:[/red] Sprint {sprint_id} not found")
        raise typer.Exit(1)

    # Load sprint
    try:
        sprint = Sprint.model_validate_json(sprint_path.read_text())
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load sprint: {e}")
        raise typer.Exit(1)

    # Check status
    # Handle both enum and string status values
    current_status = sprint.status.value if hasattr(sprint.status, 'value') else sprint.status
    if current_status != "planned":
        if current_status == "active":
            console.print(f"[yellow]Sprint {sprint_id} is already active[/yellow]")
        else:
            console.print(f"[red]Error:[/red] Sprint {sprint_id} is {current_status}, cannot start")
        raise typer.Exit(1)

    # Check if another sprint is active
    for other_sprint_file in sprints_dir.glob("*.json"):
        if other_sprint_file.name != sprint_path.name:
            try:
                other_sprint = Sprint.model_validate_json(other_sprint_file.read_text())
                # Handle both enum and string status values
                other_status = other_sprint.status.value if hasattr(other_sprint.status, 'value') else other_sprint.status
                if other_status == "active":
                    console.print(
                        f"[red]Error:[/red] Sprint {other_sprint.id} is already active. "
                        "Only one sprint can be active at a time."
                    )
                    raise typer.Exit(1)
            except typer.Exit:
                raise  # Re-raise Exit exceptions
            except Exception:
                pass  # Ignore other exceptions (e.g., JSON parsing errors)

    # Update sprint
    sprint.status = SprintStatus.ACTIVE
    sprint.updated_at = datetime.now()

    # Save sprint
    sprint_path.write_text(sprint.model_dump_json(indent=2))

    # Show success
    console.print(Panel(
        Text.from_markup(
            f"[green]✓[/green] Started sprint [cyan]{sprint_id}[/cyan]\n\n"
            f"[dim]Name:[/dim] {sprint.name}\n"
            f"[dim]Goal:[/dim] {sprint.goal or '[gray]None[/gray]'}\n"
            f"[dim]Duration:[/dim] {(sprint.end_date - sprint.start_date).days + 1} days\n"
            f"[dim]Status:[/dim] [green]Active[/green]"
        ),
        title="Sprint Started",
        border_style="green"
    ))
