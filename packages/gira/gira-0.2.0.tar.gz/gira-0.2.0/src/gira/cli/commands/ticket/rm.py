"""Remove ticket command alias - short form of delete."""

from typing import Optional, List
import typer

from gira.cli.commands.ticket.delete import delete as delete_ticket


def rm(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to remove (use '-' to read from stdin)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    permanent: bool = typer.Option(False, "--permanent", "-p", help="Permanently delete instead of archiving"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (json)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket IDs"),
    git: Optional[bool] = typer.Option(None, "--git/--no-git", help="Stage the archive/delete using 'git mv' or 'git rm'"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (e.g., done)"),
    older_than: Optional[str] = typer.Option(None, "--older-than", help="Filter tickets older than duration (e.g., '30 days', '2 weeks')"),
    epic: Optional[str] = typer.Option(None, "--epic", "-e", help="Filter tickets by epic ID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be archived without doing it"),
    batch_id: Optional[str] = typer.Option(None, "--batch", "-b", help="Batch ID for undo operations"),
) -> None:
    """Remove ticket(s) (alias for delete).
    
    This is a shorter Unix-style alias for the 'delete' command.
    
    By default, tickets are archived (moved to .gira/archive/) and can be restored later.
    Use --permanent to permanently delete the ticket and all associated data.
    
    Examples:
        # Remove a single ticket (archive)
        gira ticket rm TEST-1
        
        # Remove multiple tickets
        gira ticket rm TEST-1 TEST-2 TEST-3
        
        # Permanently delete (no recovery)
        gira ticket rm TEST-1 --permanent
        
        # Remove with force (no confirmation)
        gira ticket rm TEST-1 TEST-2 --force
        
        # Remove all done tickets older than 30 days
        gira ticket rm --status done --older-than "30 days"
    """
    # Simply call the delete function with the same parameters
    delete_ticket(
        ticket_ids=ticket_ids,
        force=force,
        permanent=permanent,
        output=output,
        quiet=quiet,
        git=git,
        status=status,
        older_than=older_than,
        epic=epic,
        dry_run=dry_run,
        batch_id=batch_id,
    )