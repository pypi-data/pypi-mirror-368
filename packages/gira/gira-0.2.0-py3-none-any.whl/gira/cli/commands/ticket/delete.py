"""Delete ticket command for Gira."""

import json
import shutil
import sys
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import re

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from gira.models.ticket import Ticket
from gira.models.board import Board
from gira.utils.epic_utils import remove_ticket_from_epic
from gira.utils.git_ops import should_use_git, move_with_git_fallback, remove_with_git_fallback
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, process_bulk_operation
from gira.utils.confirmations import should_skip_confirmation
from gira.utils.typer_completion import complete_ticket_ids, complete_status_values, complete_epic_ids

def delete(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to delete (use '-' to read from stdin)", autocompletion=complete_ticket_ids),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    confirm: bool = typer.Option(False, "--confirm", help="Force confirmation prompts even when skip is configured"),
    permanent: bool = typer.Option(False, "--permanent", "-p", help="Permanently delete instead of archiving"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (json)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket IDs"),
    git: Optional[bool] = typer.Option(None, "--git/--no-git", help="Stage the archive/delete using 'git mv' or 'git rm'"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (e.g., done)", autocompletion=complete_status_values),
    older_than: Optional[str] = typer.Option(None, "--older-than", help="Filter tickets older than duration (e.g., '30 days', '2 weeks')"),
    epic: Optional[str] = typer.Option(None, "--epic", "-e", help="Filter tickets by epic ID", autocompletion=complete_epic_ids),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be archived without doing it"),
    batch_id: Optional[str] = typer.Option(None, "--batch", "-b", help="Batch ID for undo operations"),
) -> None:
    """Delete or archive ticket(s).
    
    By default, tickets are archived (moved to .gira/archive/) and can be restored later.
    Use --permanent to permanently delete the ticket and all associated data.
    
    Can accept multiple ticket IDs as arguments, read from stdin, or filter by criteria.
    
    This will also:
    - Remove the ticket from any epics
    - Remove the ticket from any sprints
    - Delete all comments associated with the ticket
    - Remove any dependency relationships
    
    Git Integration:
        By default, archive/delete operations are automatically staged with 'git mv' or 'git rm' if .gira is tracked.
        Control this behavior with:
        - --git / --no-git flags
        - GIRA_AUTO_GIT_MV environment variable
        - git.auto_stage_archives or git.auto_stage_deletes in config.json
    
    Examples:
        # Archive a single ticket
        gira ticket delete TEST-1
        
        # Archive multiple tickets
        gira ticket delete TEST-1 TEST-2 TEST-3
        
        # Archive with force (no confirmation)
        gira ticket delete TEST-1 TEST-2 --force
        
        # Permanently delete
        gira ticket delete TEST-1 --permanent
        
        # Archive all done tickets older than 30 days
        gira ticket delete --status done --older-than "30 days"
        
        # Archive all done tickets in an epic
        gira ticket delete --epic EPIC-001 --status done
        
        # Dry run to see what would be archived
        gira ticket delete --status done --dry-run
        
        # Archive multiple tickets from stdin
        gira query "type:bug AND status:done" --format ids | gira ticket delete -
        
        # Pattern matching (supports wildcards and ranges)
        gira ticket delete "TEST-1*"  # TEST-10, TEST-11, etc.
        gira ticket delete "TEST-1..10"  # TEST-1 through TEST-10
    """
    root = ensure_gira_project()
    
    # Determine whether to use git operations
    use_git = should_use_git(root, git, "archive" if not permanent else "delete")
    
    # Debug output
    # print(f"DEBUG: ticket_ids = {ticket_ids}, type = {type(ticket_ids)}")
    
    # Collect ticket IDs from various sources
    tickets_to_delete = []
    
    # Check if we should read from stdin
    if ticket_ids and len(ticket_ids) == 1 and ticket_ids[0] == "-":
        return _delete_bulk_from_stdin(root, force, confirm, permanent, output, quiet, use_git, dry_run, batch_id)
    
    # Check for filter-based deletion
    if status or older_than or epic:
        tickets_to_delete.extend(_find_tickets_by_filter(root, status, older_than, epic))
    
    # Process provided ticket IDs (could include patterns)
    if ticket_ids:
        for ticket_id in ticket_ids:
            tickets_to_delete.extend(_expand_ticket_pattern(root, ticket_id))
    
    # If no tickets specified and no filters, check stdin
    if not tickets_to_delete and not ticket_ids and not sys.stdin.isatty():
        return _delete_bulk_from_stdin(root, force, confirm, permanent, output, quiet, use_git, dry_run, batch_id)
    
    # Validate we have tickets to delete
    if not tickets_to_delete:
        console.print("[red]Error:[/red] No tickets specified for deletion")
        console.print("Provide ticket IDs, use filters (--status, --older-than, --epic), or use '-' to read from stdin")
        raise typer.Exit(1)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tickets = []
    for ticket_id in tickets_to_delete:
        if ticket_id not in seen:
            seen.add(ticket_id)
            unique_tickets.append(ticket_id)
    tickets_to_delete = unique_tickets
    
    # Dry run mode - just show what would be deleted
    if dry_run:
        _show_dry_run_preview(root, tickets_to_delete, permanent, output)
        return
    
    # If only one ticket and confirmations not skipped, use single ticket flow for better UX
    if len(tickets_to_delete) == 1 and not should_skip_confirmation(force, confirm):
        ticket_id = tickets_to_delete[0]
        return _delete_single_ticket_interactive(ticket_id, permanent, output, quiet, root, use_git, confirm)
    
    # Multiple tickets - use bulk deletion
    return _delete_bulk_tickets(root, tickets_to_delete, force, confirm, permanent, output, quiet, use_git, batch_id)


def _delete_bulk_from_stdin(root, force: bool, confirm: bool, permanent: bool, output: Optional[str], quiet: bool, use_git: bool, dry_run: bool, batch_id: Optional[str]) -> None:
    """Delete multiple tickets from stdin input (one ticket ID per line)."""
    # Read ticket IDs from stdin using StdinReader
    stdin_reader = StdinReader()
    ticket_ids = stdin_reader.read_lines()
    
    if not ticket_ids:
        console.print("[yellow]Warning:[/yellow] No ticket IDs provided on stdin")
        return
    
    # Dry run mode
    if dry_run:
        _show_dry_run_preview(root, ticket_ids, permanent, output)
        return
    
    # Use bulk deletion
    _delete_bulk_tickets(root, ticket_ids, force, confirm, permanent, output, quiet, use_git, batch_id)


def _get_swimlane_ids(root: Path) -> List[str]:
    """Get swimlane IDs from board configuration and actual directories."""
    swimlane_ids = set()
    
    # Get configured swimlanes from board config
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        board = Board.model_validate_json(board_config_path.read_text())
        swimlane_ids.update(swimlane.id for swimlane in board.swimlanes)
    
    # Also include any actual directories that exist in board/
    board_dir = root / ".gira" / "board"
    if board_dir.exists():
        for item in board_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                swimlane_ids.add(item.name)
    
    # If nothing found, use defaults
    if not swimlane_ids:
        swimlane_ids = {"backlog", "todo", "in_progress", "review", "done"}
    
    return list(swimlane_ids)


def _delete_single_ticket(ticket_id: str, permanent: bool, root, use_git: bool) -> dict:
    """Delete a single ticket and return result data."""
    # Get swimlane IDs dynamically
    swimlane_ids = _get_swimlane_ids(root)
    
    # Find the ticket file
    ticket_path = None
    for status_dir in swimlane_ids:
        potential_path = root / ".gira" / "board" / status_dir / f"{ticket_id}.json"
        if potential_path.exists():
            ticket_path = potential_path
            break
    
    # Also check archive directory
    if not ticket_path:
        archive_path = root / ".gira" / "archive" / "tickets" / f"{ticket_id}.json"
        if archive_path.exists():
            ticket_path = archive_path
    
    if not ticket_path:
        raise ValueError(f"Ticket '{ticket_id}' not found")
    
    # Load the ticket
    ticket = Ticket.from_json_file(str(ticket_path))
    
    # Remove ticket from epic if it belongs to one
    if ticket.epic_id:
        remove_ticket_from_epic(ticket_id, ticket.epic_id, root)
    
    # Remove ticket from any sprints
    sprints_dir = root / ".gira" / "sprints"
    if sprints_dir.exists():
        from gira.models.sprint import Sprint
        for sprint_file in sprints_dir.glob("*.json"):
            sprint = Sprint.from_json_file(str(sprint_file))
            if ticket_id in sprint.tickets:
                sprint.tickets.remove(ticket_id)
                sprint.save_to_json_file(str(sprint_file))
    
    # Remove dependency relationships
    if ticket.blocked_by or ticket.blocks:
        # Remove this ticket from other tickets' blocks lists
        for status_dir in swimlane_ids:
            status_path = root / ".gira" / "board" / status_dir
            if status_path.exists():
                for other_ticket_file in status_path.glob("*.json"):
                    other_ticket = Ticket.from_json_file(str(other_ticket_file))
                    if ticket_id in other_ticket.blocks:
                        other_ticket.blocks.remove(ticket_id)
                        other_ticket.save_to_json_file(str(other_ticket_file))
                    if ticket_id in other_ticket.blocked_by:
                        other_ticket.blocked_by.remove(ticket_id)
                        other_ticket.save_to_json_file(str(other_ticket_file))
    
    # Delete or archive the ticket
    if permanent:
        # Delete ticket file
        remove_with_git_fallback(ticket_path, root, use_git, silent=True)
        
        # Delete comments directory
        comments_dir = root / ".gira" / "comments" / ticket_id
        if comments_dir.exists():
            if use_git:
                # Try to remove all files in the directory with git rm
                for comment_file in comments_dir.glob("*.json"):
                    remove_with_git_fallback(comment_file, root, use_git, silent=True)
            # Remove the directory itself (git doesn't track empty directories)
            shutil.rmtree(comments_dir)
        
        action = "deleted"
    else:
        # Archive the ticket
        archive_dir = root / ".gira" / "archive" / "tickets"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Move ticket to archive
        archive_path = archive_dir / f"{ticket_id}.json"
        if ticket_path != archive_path:  # Only move if not already archived
            move_with_git_fallback(ticket_path, archive_path, root, use_git, silent=True)
        
        # Archive comments
        comments_dir = root / ".gira" / "comments" / ticket_id
        if comments_dir.exists():
            archive_comments_dir = root / ".gira" / "archive" / "comments" / ticket_id
            archive_comments_dir.parent.mkdir(parents=True, exist_ok=True)
            if not archive_comments_dir.exists():  # Only move if not already archived
                if use_git:
                    # Move each comment file with git mv
                    for comment_file in comments_dir.glob("*.json"):
                        archive_comment_path = archive_comments_dir / comment_file.name
                        move_with_git_fallback(comment_file, archive_comment_path, root, use_git, silent=True)
                    # Remove the now-empty directory
                    if comments_dir.exists() and not any(comments_dir.iterdir()):
                        comments_dir.rmdir()
                else:
                    # Use regular move for the entire directory
                    shutil.move(str(comments_dir), str(archive_comments_dir))
        
        action = "archived"
    
    return {
        "id": ticket_id,
        "title": ticket.title,
        "action": action
    }


def _expand_ticket_pattern(root: Path, pattern: str) -> List[str]:
    """Expand ticket pattern to list of ticket IDs.
    
    Supports:
    - Wildcards: TEST-1* matches TEST-10, TEST-11, etc.
    - Ranges: TEST-1..10 matches TEST-1 through TEST-10
    - Single IDs: TEST-1 returns [TEST-1]
    - Number-only: 673 returns [GCM-673] (using project prefix)
    """
    from gira.constants import parse_ticket_id_pattern, get_project_prefix
    
    # Normalize the pattern to add prefix if needed
    try:
        prefix = get_project_prefix()
        pattern = parse_ticket_id_pattern(pattern, prefix)
    except ValueError:
        # If we can't get prefix, use pattern as-is
        pass
    
    tickets = []
    
    # Check for range pattern (e.g., TEST-1..10)
    if ".." in pattern:
        prefix, range_part = pattern.rsplit("-", 1)
        if ".." in range_part:
            start_str, end_str = range_part.split("..", 1)
            try:
                start = int(start_str)
                end = int(end_str)
                for i in range(start, end + 1):
                    ticket_id = f"{prefix}-{i}"
                    if _ticket_exists(root, ticket_id):
                        tickets.append(ticket_id)
            except ValueError:
                # Not a valid range, treat as literal
                if _ticket_exists(root, pattern):
                    tickets.append(pattern)
        else:
            # No range, treat as literal
            if _ticket_exists(root, pattern):
                tickets.append(pattern)
    
    # Check for wildcard pattern
    elif "*" in pattern:
        # Convert wildcard to regex
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")
        
        # Get swimlane IDs dynamically
        swimlane_ids = _get_swimlane_ids(root)
        
        # Search all ticket locations
        locations = [f"board/{swimlane}" for swimlane in swimlane_ids] + ["archive/tickets"]
        for location in locations:
            ticket_dir = root / ".gira" / location
            if ticket_dir.exists():
                for ticket_file in ticket_dir.glob("*.json"):
                    ticket_id = ticket_file.stem
                    if regex.match(ticket_id):
                        tickets.append(ticket_id)
    
    # Regular ticket ID
    else:
        if _ticket_exists(root, pattern):
            tickets.append(pattern)
    
    return tickets


def _find_tickets_by_filter(root: Path, status: Optional[str], older_than: Optional[str], epic: Optional[str]) -> List[str]:
    """Find tickets matching filter criteria."""
    matching_tickets = []
    
    # Parse older_than duration
    cutoff_date = None
    if older_than:
        cutoff_date = _parse_duration(older_than)
    
    # Get swimlane IDs dynamically
    swimlane_ids = _get_swimlane_ids(root)
    
    # Search all ticket locations
    locations = []
    if status:
        # Only search in the specified status
        if status == "archived":
            locations.append("archive/tickets")
        else:
            locations.append(f"board/{status}")
    else:
        # Search all locations
        locations = [f"board/{swimlane}" for swimlane in swimlane_ids] + ["archive/tickets"]
    
    for location in locations:
        ticket_dir = root / ".gira" / location
        if ticket_dir.exists():
            for ticket_file in ticket_dir.glob("*.json"):
                try:
                    ticket = Ticket.from_json_file(str(ticket_file))
                    
                    # Check epic filter
                    if epic and ticket.epic_id != epic:
                        continue
                    
                    # Check age filter
                    if cutoff_date:
                        # Use updated_at if available, otherwise created_at
                        ticket_date = ticket.updated_at or ticket.created_at
                        if hasattr(ticket_date, 'tzinfo') and ticket_date.tzinfo is not None:
                            ticket_date = ticket_date.replace(tzinfo=None)
                        if ticket_date > cutoff_date:
                            continue
                    
                    matching_tickets.append(ticket.id)
                
                except Exception:
                    # Skip invalid ticket files
                    continue
    
    return matching_tickets


def _parse_duration(duration_str: str) -> datetime:
    """Parse duration string like '30 days' or '2 weeks' into a cutoff datetime."""
    parts = duration_str.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    try:
        amount = int(parts[0])
    except ValueError:
        raise ValueError(f"Invalid duration amount: {parts[0]}")
    
    unit = parts[1].lower().rstrip('s')  # Remove trailing 's'
    
    if unit in ['day', 'days']:
        delta = timedelta(days=amount)
    elif unit in ['week', 'weeks']:
        delta = timedelta(weeks=amount)
    elif unit in ['month', 'months']:
        delta = timedelta(days=amount * 30)  # Approximate
    elif unit in ['year', 'years']:
        delta = timedelta(days=amount * 365)  # Approximate
    else:
        raise ValueError(f"Unknown duration unit: {unit}")
    
    return datetime.now() - delta


def _ticket_exists(root: Path, ticket_id: str) -> bool:
    """Check if a ticket exists in any location."""
    # Get swimlane IDs dynamically
    swimlane_ids = _get_swimlane_ids(root)
    
    locations = [root / ".gira" / "board" / swimlane / f"{ticket_id}.json" for swimlane in swimlane_ids]
    locations.append(root / ".gira" / "archive" / "tickets" / f"{ticket_id}.json")
    
    # Debug
    # print(f"DEBUG _ticket_exists: checking {ticket_id}")
    # print(f"DEBUG _ticket_exists: swimlane_ids = {swimlane_ids}")
    # for loc in locations:
    #     print(f"DEBUG _ticket_exists: {loc} exists? {loc.exists()}")
    
    return any(path.exists() for path in locations)


def _show_dry_run_preview(root: Path, ticket_ids: List[str], permanent: bool, output: Optional[str]) -> None:
    """Show preview of what would be deleted/archived."""
    action = "delete" if permanent else "archive"
    
    if output == "json":
        # Load ticket details for JSON output
        tickets = []
        for ticket_id in ticket_ids:
            try:
                ticket_path = _find_ticket_path(root, ticket_id)
                if ticket_path:
                    ticket = Ticket.from_json_file(str(ticket_path))
                    tickets.append({
                        "id": ticket.id,
                        "title": ticket.title,
                        "status": ticket.status,
                        "type": ticket.type
                    })
            except Exception:
                tickets.append({"id": ticket_id, "error": "Not found"})
        
        console.print_json(data={
            "dry_run": True,
            "action": action,
            "tickets": tickets,
            "count": len(tickets)
        })
    else:
        console.print(f"\n[bold]Dry Run - Would {action} {len(ticket_ids)} ticket(s):[/bold]")
        
        # Create a table for better display
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Status", style="yellow")
        table.add_column("Type", style="green")
        
        for ticket_id in ticket_ids[:20]:  # Show first 20
            try:
                ticket_path = _find_ticket_path(root, ticket_id)
                if ticket_path:
                    ticket = Ticket.from_json_file(str(ticket_path))
                    table.add_row(ticket.id, ticket.title[:50], ticket.status, ticket.type)
                else:
                    table.add_row(ticket_id, "[red]Not found[/red]", "-", "-")
            except Exception:
                table.add_row(ticket_id, "[red]Error loading[/red]", "-", "-")
        
        console.print(table)
        
        if len(ticket_ids) > 20:
            console.print(f"\n... and {len(ticket_ids) - 20} more tickets")
        
        console.print(f"\n[dim]No changes made. Remove --dry-run to perform {action}.[/dim]")


def _find_ticket_path(root: Path, ticket_id: str) -> Optional[Path]:
    """Find the path to a ticket file."""
    # Get swimlane IDs dynamically
    swimlane_ids = _get_swimlane_ids(root)
    
    locations = [root / ".gira" / "board" / swimlane / f"{ticket_id}.json" for swimlane in swimlane_ids]
    locations.append(root / ".gira" / "archive" / "tickets" / f"{ticket_id}.json")
    
    for path in locations:
        if path.exists():
            return path
    return None


def _delete_single_ticket_interactive(ticket_id: str, permanent: bool, output: Optional[str], quiet: bool, root: Path, use_git: bool, confirm: bool = False) -> None:
    """Delete a single ticket with interactive confirmation."""
    # Find the ticket file
    ticket_path = _find_ticket_path(root, ticket_id)
    
    if not ticket_path:
        if output == "json":
            console.print_json(data={"error": f"Ticket '{ticket_id}' not found"})
        else:
            console.print(f"[red]Error:[/red] Ticket '{ticket_id}' not found")
        raise typer.Exit(1)
    
    # Load the ticket
    ticket = Ticket.from_json_file(str(ticket_path))
    
    # Show ticket details and what will be affected
    if output != "json":
        console.print(Panel(
            f"[bold]{ticket.id}[/bold] - {ticket.title}\n"
            f"Status: {ticket.status}\n"
            f"Type: {ticket.type}\n"
            f"Priority: {ticket.priority or 'None'}\n"
            f"Epic: {ticket.epic_id or 'None'}",
            title="[red]Ticket to Delete[/red]",
            border_style="red"
        ))
        
        # Check for comments
        comments_dir = root / ".gira" / "comments" / ticket_id
        comment_count = len(list(comments_dir.glob("*.json"))) if comments_dir.exists() else 0
        if comment_count > 0:
            console.print(f"\n[yellow]Warning:[/yellow] This ticket has {comment_count} comment(s) that will be deleted.")
        
        # Check for dependencies
        if ticket.blocked_by or ticket.blocks:
            console.print(f"\n[yellow]Warning:[/yellow] This ticket has dependency relationships that will be removed.")
        
        action = "permanently delete" if permanent else "archive"
        if not should_skip_confirmation(confirm=confirm) and not Confirm.ask(f"\nAre you sure you want to {action} this ticket?"):
            raise typer.Exit(0)
    
    # Delete the ticket
    result = _delete_single_ticket(ticket_id, permanent, root, use_git)
    
    if output == "json":
        console.print_json(data={
            "success": True,
            "ticket_id": result["id"],
            "action": result["action"],
            "message": f"Ticket {result['id']} has been {result['action']}"
        })
    elif quiet:
        console.print(ticket_id)
    else:
        console.print(f"✅ Ticket '{result['id']}' has been {result['action']}", style="green")


def _delete_bulk_tickets(root: Path, ticket_ids: List[str], force: bool, confirm: bool, permanent: bool, output: Optional[str], quiet: bool, use_git: bool, batch_id: Optional[str]) -> None:
    """Delete multiple tickets with progress feedback."""
    # Generate batch ID if not provided
    if not batch_id and len(ticket_ids) > 1:
        batch_id = f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Confirm bulk deletion if confirmations not skipped
    if not should_skip_confirmation(force, confirm) and output != "json":
        action = "permanently delete" if permanent else "archive"
        console.print(f"\n[yellow]About to {action} {len(ticket_ids)} ticket(s):[/yellow]")
        
        # Show preview of tickets to be deleted
        preview_count = min(10, len(ticket_ids))
        for i, ticket_id in enumerate(ticket_ids[:preview_count]):
            ticket_path = _find_ticket_path(root, ticket_id)
            if ticket_path:
                try:
                    ticket = Ticket.from_json_file(str(ticket_path))
                    console.print(f"  - [cyan]{ticket.id}[/cyan]: {ticket.title[:50]}{'...' if len(ticket.title) > 50 else ''}")
                except Exception:
                    console.print(f"  - [cyan]{ticket_id}[/cyan]: [red]Error loading ticket[/red]")
            else:
                console.print(f"  - [cyan]{ticket_id}[/cyan]: [red]Not found[/red]")
        
        if len(ticket_ids) > preview_count:
            console.print(f"  ... and {len(ticket_ids) - preview_count} more")
        
        # Check for dependencies
        tickets_with_deps = []
        for ticket_id in ticket_ids:
            ticket_path = _find_ticket_path(root, ticket_id)
            if ticket_path:
                try:
                    ticket = Ticket.from_json_file(str(ticket_path))
                    if ticket.blocked_by or ticket.blocks:
                        tickets_with_deps.append((ticket.id, ticket.blocks))
                except Exception:
                    pass
        
        if tickets_with_deps:
            console.print(f"\n[yellow]Warning:[/yellow] {len(tickets_with_deps)} ticket(s) have dependencies that will be affected:")
            for ticket_id, blocks in tickets_with_deps[:5]:
                if blocks:
                    console.print(f"  - {ticket_id} blocks: {', '.join(blocks)}")
            if len(tickets_with_deps) > 5:
                console.print(f"  ... and {len(tickets_with_deps) - 5} more")
        
        if not Confirm.ask(f"\nAre you sure you want to {action} these tickets?"):
            raise typer.Exit(0)
    
    # Record batch operation if batch_id provided
    if batch_id:
        _record_batch_operation(root, batch_id, ticket_ids, permanent)
    
    # Convert to format expected by process_bulk_operation
    items = [{"id": ticket_id} for ticket_id in ticket_ids]
    
    # Process bulk deletion
    def delete_single_ticket(item):
        ticket_id = item["id"]
        return _delete_single_ticket(ticket_id, permanent, root, use_git)
    
    result = process_bulk_operation(
        items,
        delete_single_ticket,
        f"ticket {'deletion' if permanent else 'archival'}",
        show_progress=not quiet and len(items) > 1 and output != "json"
    )
    
    # Output results
    if output == "json":
        output_data = result.to_dict()
        if batch_id:
            output_data["batch_id"] = batch_id
        console.print_json(data=output_data)
    elif quiet:
        # Output only successfully deleted ticket IDs
        for success in result.successful:
            console.print(success["result"]["id"])
    else:
        result.print_summary(f"ticket {'deletion' if permanent else 'archival'}")
        
        if batch_id and result.success_count > 0:
            console.print(f"\n[dim]Batch ID: {batch_id}[/dim]")
            if not permanent:
                console.print(f"[dim]To restore: gira ticket undelete --batch {batch_id}[/dim]")
        
        # Show successful deletions
        if result.successful and len(result.successful) <= 10:
            action_verb = "deleted" if permanent else "archived"
            console.print(f"\n✅ **{action_verb.title()} Tickets:**")
            for success in result.successful:
                ticket_data = success["result"]
                console.print(f"  - [cyan]{ticket_data['id']}[/cyan]: {ticket_data['title']}")
        elif result.successful:
            action_verb = "deleted" if permanent else "archived"
            console.print(f"\n✅ {action_verb.title()} {len(result.successful)} tickets")
    
    # Exit with error code if any failures
    if result.failure_count > 0:
        raise typer.Exit(1)


def _record_batch_operation(root: Path, batch_id: str, ticket_ids: List[str], permanent: bool) -> None:
    """Record batch operation for potential undo."""
    batch_dir = root / ".gira" / "batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    batch_file = batch_dir / f"{batch_id}.json"
    batch_data = {
        "id": batch_id,
        "timestamp": datetime.now().isoformat(),
        "operation": "delete" if permanent else "archive",
        "tickets": ticket_ids,
        "permanent": permanent
    }
    
    batch_file.write_text(json.dumps(batch_data, indent=2))