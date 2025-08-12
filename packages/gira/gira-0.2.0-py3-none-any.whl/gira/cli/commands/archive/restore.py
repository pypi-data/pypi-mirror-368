"""Restore archived tickets back to the board."""

import typer
from gira.utils.console import console
from gira.utils.archive import restore_ticket as restore_ticket_util
from gira.utils.board_config import get_valid_statuses
from gira.utils.project import ensure_gira_project

def restore(
    ticket_id: str = typer.Argument(..., help="ID of the ticket to restore"),
    status: str = typer.Option("done", "--status", "-s", help="Status to restore ticket to"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    git: bool = typer.Option(None, "--git/--no-git", help="Use git operations for restoration (auto-detected if not specified)")
) -> None:
    """Restore an archived ticket back to the board."""
    ensure_gira_project()
    
    # Normalize ticket ID for display consistency
    from gira.constants import normalize_ticket_id, get_project_prefix
    try:
        prefix = get_project_prefix()
        normalized_id = normalize_ticket_id(ticket_id, prefix)
    except ValueError:
        # If we can't get prefix, just uppercase the ID
        normalized_id = ticket_id.upper()

    # Validate status
    valid_statuses = get_valid_statuses()
    if status not in valid_statuses:
        console.print(f"[red]Error:[/red] Invalid status '{status}'")
        console.print(f"Valid statuses: {', '.join(valid_statuses)}")
        raise typer.Exit(1)

    try:
        # Confirm unless forced
        if not force:
            if not typer.confirm(f"Restore ticket {normalized_id} to {status}?"):
                console.print("[yellow]Restore cancelled[/yellow]")
                raise typer.Exit(0)

        # Restore the ticket
        ticket = restore_ticket_util(ticket_id, status, use_git=git)

        console.print(f"[green]✓[/green] Restored ticket {ticket.id} to {status}")
        console.print(f"   Title: {ticket.title}")

    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Ticket {normalized_id} not found in archive")
        console.print("\nUse 'gira archive list' to see archived tickets")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error restoring ticket:[/red] {e}")
        raise typer.Exit(1)
