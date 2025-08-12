"""Archive a single ticket."""

import typer
from gira.utils.console import console
from gira.utils.archive import archive_ticket as archive_ticket_util
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_ticket

def archive_ticket(
    ticket_id: str = typer.Argument(..., help="ID of the ticket to archive"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview the archive operation without performing it"),
    git: bool = typer.Option(None, "--git/--no-git", help="Use git operations for archiving (auto-detected if not specified)")
) -> None:
    """Archive a single ticket."""
    root = ensure_gira_project()

    try:
        # Load the ticket
        ticket = load_ticket(ticket_id)

        # If dry-run, show what would happen
        if dry_run:
            console.print("[yellow]DRY RUN:[/yellow] The following archive operation would be performed:")
            console.print(f"\nTicket: [cyan]{ticket.id}[/cyan] - {ticket.title}")
            console.print(f"  • Status: {ticket.status}")
            console.print(f"  • Type: {ticket.type}")
            console.print(f"  • Priority: {ticket.priority}")
            
            # Determine archive path
            archive_dir = root / ".gira" / ".archive" / ticket.status
            archive_path = archive_dir / f"{ticket.id}.json"
            
            console.print(f"\n[dim]Ticket would be moved to:[/dim]")
            console.print(f"  {archive_path.relative_to(root)}")
            
            console.print("\n[dim]No changes were made (dry run)[/dim]")
            return

        # Confirm unless forced
        if not force:
            if not typer.confirm(f"Archive ticket {ticket.id}: {ticket.title}?"):
                console.print("[yellow]Archive cancelled[/yellow]")
                raise typer.Exit(0)

        # Archive the ticket
        archive_path = archive_ticket_util(ticket, use_git=git)

        console.print(f"[green]✓[/green] Archived ticket {ticket.id} to {archive_path.parent.name}/")

    except FileNotFoundError:
        # Normalize ticket ID for display (same as other commands)
        from gira.constants import normalize_ticket_id, get_project_prefix
        try:
            prefix = get_project_prefix()
            normalized_id = normalize_ticket_id(ticket_id, prefix)
        except ValueError:
            # If we can't get prefix, just uppercase the ID
            normalized_id = ticket_id.upper()
        console.print(f"[red]Error:[/red] Ticket {normalized_id} not found")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error archiving ticket:[/red] {e}")
        raise typer.Exit(1)
