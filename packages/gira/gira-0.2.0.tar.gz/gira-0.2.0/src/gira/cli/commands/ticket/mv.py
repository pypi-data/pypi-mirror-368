"""Move ticket command alias - short form of move."""

from typing import List, Optional
import typer

from gira.cli.commands.ticket.move import move as move_ticket


def mv(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to move (use '-' to read from stdin)"),
    target_status: str = typer.Argument(..., help="Target status to move ticket to"),
    position: Optional[int] = typer.Option(None, "--position", "-p", help="Position in new column (1-based)"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket ID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview the move without performing it"),
    git: Optional[bool] = typer.Option(None, "--git/--no-git", help="Stage the move using 'git mv'"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    force_transition: bool = typer.Option(False, "--force-transition", help="Skip workflow validation and force the transition"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Filter by assignee (use 'me' for current user)"),
    from_status: Optional[str] = typer.Option(None, "--from", help="Only move tickets from this status"),
    epic_id: Optional[str] = typer.Option(None, "--epic", "-e", help="Filter tickets by epic ID"),
    sprint_id: Optional[str] = typer.Option(None, "--sprint", "-s", help="Filter tickets by sprint ID (use 'current' for active sprint)"),
    comment: Optional[str] = typer.Option(None, "--comment", "-c", help="Add comment to moved tickets"),
    assign: Optional[str] = typer.Option(None, "--assign", help="Assign tickets to user while moving"),
    add_label: Optional[str] = typer.Option(None, "--add-label", help="Add label to moved tickets"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Update priority while moving"),
    check_deps: bool = typer.Option(False, "--check-dependencies", help="Check for blocking dependencies"),
    batch_id: Optional[str] = typer.Option(None, "--batch", "-b", help="Batch ID for undo operations"),
) -> None:
    """Move ticket(s) to a different status (alias for move).
    
    This is a shorter alias for the 'move' command using Unix-style naming.
    
    Examples:
        # Move a single ticket
        gira ticket mv TEST-1 done
        
        # Move multiple tickets
        gira ticket mv TEST-1 TEST-2 TEST-3 "in progress"
        
        # Move with force (no confirmation)
        gira ticket mv TEST-1 TEST-2 done --force
        
        # Move tickets from a specific status
        gira ticket mv --from todo "in progress" --assignee me
        
        # Force transition bypassing workflow rules
        gira ticket mv TEST-1 done --force-transition
    """
    # Simply call the move function with the same parameters
    move_ticket(
        ticket_ids=ticket_ids,
        target_status=target_status,
        position=position,
        output=output,
        quiet=quiet,
        dry_run=dry_run,
        git=git,
        force=force,
        force_transition=force_transition,
        assignee=assignee,
        from_status=from_status,
        epic_id=epic_id,
        sprint_id=sprint_id,
        comment=comment,
        assign=assign,
        add_label=add_label,
        priority=priority,
        check_deps=check_deps,
        batch_id=batch_id,
    )