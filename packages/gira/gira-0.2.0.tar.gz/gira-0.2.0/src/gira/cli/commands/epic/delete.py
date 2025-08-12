"""Delete epic command for Gira."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.prompt import Confirm

from gira.models.epic import Epic
from gira.models.ticket import Ticket
from gira.utils.git_ops import should_use_git, move_with_git_fallback, remove_with_git_fallback
from gira.utils.project import ensure_gira_project

def delete(
    epic_id: str = typer.Argument(..., help="Epic ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    permanent: bool = typer.Option(False, "--permanent", "-p", help="Permanently delete instead of archiving"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (json)"),
    git: Optional[bool] = typer.Option(None, "--git/--no-git", help="Stage the archive/delete using 'git mv' or 'git rm'"),
) -> None:
    """Delete or archive an epic.
    
    By default, epics are archived (moved to .gira/archive/) and can be restored later.
    Use --permanent to permanently delete the epic.
    
    This will also remove the epic reference from all associated tickets.
    
    Git Integration:
        By default, archive/delete operations are automatically staged with 'git mv' or 'git rm' if .gira is tracked.
        Control this behavior with:
        - --git / --no-git flags
        - GIRA_AUTO_GIT_MV environment variable
        - git.auto_stage_archives or git.auto_stage_deletes in config.json
    """
    root = ensure_gira_project()
    
    # Determine whether to use git operations
    use_git = should_use_git(root, git, "archive" if not permanent else "delete")
    
    # Find the epic file
    epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
    archive_path = root / ".gira" / "archive" / "epics" / f"{epic_id}.json"
    
    if epic_path.exists():
        current_path = epic_path
    elif archive_path.exists():
        current_path = archive_path
    else:
        if output == "json":
            console.print_json(data={"error": f"Epic '{epic_id}' not found"})
        else:
            console.print(f"[red]Error:[/red] Epic '{epic_id}' not found")
        raise typer.Exit(1)
    
    # Load the epic
    epic = Epic.from_json_file(str(current_path))
    
    # Find all tickets that reference this epic (not just those in epic.tickets)
    affected_tickets = []
    for status_dir in ["todo", "in_progress", "review", "done"]:
        status_path = root / ".gira" / "board" / status_dir
        if status_path.exists():
            for ticket_file in status_path.glob("*.json"):
                try:
                    ticket = Ticket.from_json_file(str(ticket_file))
                    if ticket.epic_id == epic_id:
                        affected_tickets.append(ticket.id)
                except Exception:
                    # Skip corrupted files
                    continue
    
    # Also check archived tickets
    archive_tickets_path = root / ".gira" / "archive" / "tickets"
    if archive_tickets_path.exists():
        for ticket_file in archive_tickets_path.glob("*.json"):
            try:
                ticket = Ticket.from_json_file(str(ticket_file))
                if ticket.epic_id == epic_id:
                    affected_tickets.append(ticket.id)
            except Exception:
                # Skip corrupted files
                continue
    
    # Show epic details and what will be affected
    if not force and output != "json":
        console.print(Panel(
            f"[bold]{epic.id}[/bold] - {epic.title}\n"
            f"Status: {epic.status}\n"
            f"Owner: {epic.owner or 'None'}\n"
            f"Tickets: {len(affected_tickets)} ticket(s)",
            title="[red]Epic to Delete[/red]",
            border_style="red"
        ))
        
        if affected_tickets:
            console.print(f"\n[yellow]Warning:[/yellow] This epic has {len(affected_tickets)} ticket(s) that will be unlinked.")
        
        action = "permanently delete" if permanent else "archive"
        if not Confirm.ask(f"\nAre you sure you want to {action} this epic?"):
            raise typer.Exit(0)
    
    # Remove epic reference from all tickets that reference this epic
    unlinked_count = 0
    for status_dir in ["todo", "in_progress", "review", "done"]:
        status_path = root / ".gira" / "board" / status_dir
        if status_path.exists():
            for ticket_file in status_path.glob("*.json"):
                try:
                    ticket = Ticket.from_json_file(str(ticket_file))
                    if ticket.epic_id == epic_id:
                        ticket.epic_id = None
                        ticket.save_to_json_file(str(ticket_file))
                        unlinked_count += 1
                except Exception:
                    # Skip corrupted files
                    continue
    
    # Also unlink from archived tickets
    archive_tickets_path = root / ".gira" / "archive" / "tickets"
    if archive_tickets_path.exists():
        for ticket_file in archive_tickets_path.glob("*.json"):
            try:
                ticket = Ticket.from_json_file(str(ticket_file))
                if ticket.epic_id == epic_id:
                    ticket.epic_id = None
                    ticket.save_to_json_file(str(ticket_file))
                    unlinked_count += 1
            except Exception:
                # Skip corrupted files
                continue
    
    # Delete or archive the epic
    if permanent:
        # Delete epic file
        remove_with_git_fallback(current_path, root, use_git)
        action_msg = "permanently deleted"
    else:
        # Archive the epic
        archive_dir = root / ".gira" / "archive" / "epics"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Move epic to archive
        archive_path = archive_dir / f"{epic_id}.json"
        move_with_git_fallback(current_path, archive_path, root, use_git)
        action_msg = "archived"
    
    if output == "json":
        console.print_json(data={
            "success": True,
            "epic_id": epic_id,
            "action": "deleted" if permanent else "archived",
            "tickets_unlinked": unlinked_count,
            "message": f"Epic {epic_id} has been {action_msg}"
        })
    else:
        console.print(f"✅ Epic '{epic_id}' has been {action_msg}", style="green")
        if unlinked_count > 0:
            console.print(f"   {unlinked_count} ticket(s) have been unlinked from the epic")