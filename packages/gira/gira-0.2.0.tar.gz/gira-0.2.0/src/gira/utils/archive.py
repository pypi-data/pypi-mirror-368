"""Archive utilities for managing archived tickets."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from gira.models import Ticket
from gira.utils.project import get_gira_root
from gira.utils.git_ops import should_use_git, move_with_git_fallback


def get_archive_dir() -> Path:
    """Get the archive directory path."""
    root = get_gira_root()
    if root is None:
        raise ValueError("Not in a Gira project")
    archive_dir = root / ".gira" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir


def get_archive_month_dir(date: datetime) -> Path:
    """Get or create archive directory for a specific month."""
    archive_dir = get_archive_dir()
    month_dir = archive_dir / date.strftime("%Y-%m")
    month_dir.mkdir(parents=True, exist_ok=True)
    return month_dir


def archive_ticket(ticket: Ticket, archive_date: Optional[datetime] = None, use_git: Optional[bool] = None) -> Path:
    """Archive a ticket to the appropriate month directory.
    
    Args:
        ticket: The ticket to archive
        archive_date: Date to use for archiving (defaults to now)
        use_git: Whether to use git mv (auto-detected if None)
        
    Returns:
        Path to the archived ticket file
    """
    if archive_date is None:
        archive_date = datetime.now()

    # Get the month directory
    month_dir = get_archive_month_dir(archive_date)

    # Get root path
    root = get_gira_root()
    if root is None:
        raise ValueError("Not in a Gira project")

    # Find the source ticket file using comprehensive search
    from gira.utils.ticket_utils import find_ticket
    _, source_path = find_ticket(ticket.id, root)
    
    if source_path is None:
        raise FileNotFoundError(f"Ticket file not found for {ticket.id}")

    dest_path = month_dir / f"{ticket.id}.json"

    # Determine whether to use git operations
    if use_git is None:
        use_git = should_use_git(root, operation="archive")

    if use_git:
        # Use git mv for cleaner history, then add metadata
        from gira.utils.git_ops import git_move
        
        # First, move the file using git mv
        success, error = git_move(source_path, dest_path, root, silent=False)
        
        if success:
            # Now add archive metadata to the moved file
            ticket_data = ticket.to_json_dict()
            ticket_data["_archive_metadata"] = {
                "archived_at": archive_date.isoformat(),
                "archived_from_status": ticket.status,
                "archived_by": "gira-cli"
            }
            
            # Update the file with metadata
            with open(dest_path, "w") as f:
                json.dump(ticket_data, f, indent=2, default=str)
                
            # Stage the metadata changes
            from gira.utils.git_ops import git_add
            git_add(dest_path, root)
        else:
            # Fallback to the old method if git mv fails
            from gira.utils.console import console
            console.print(f"[yellow]Warning:[/yellow] git mv failed: {error}")
            console.print("[dim]Using regular file copy and delete instead[/dim]")
            
            # Add archive metadata to ticket
            ticket_data = ticket.to_json_dict()
            ticket_data["_archive_metadata"] = {
                "archived_at": archive_date.isoformat(),
                "archived_from_status": ticket.status,
                "archived_by": "gira-cli"
            }

            # Write to archive with metadata
            with open(dest_path, "w") as f:
                json.dump(ticket_data, f, indent=2, default=str)
                
            # Add the new file and remove the old one
            from gira.utils.git_ops import git_add, remove_with_git_fallback
            git_add(dest_path, root)
            remove_with_git_fallback(source_path, root, use_git=True, silent=False)
    else:
        # Non-git approach: create new file with metadata and remove original
        ticket_data = ticket.to_json_dict()
        ticket_data["_archive_metadata"] = {
            "archived_at": archive_date.isoformat(),
            "archived_from_status": ticket.status,
            "archived_by": "gira-cli"
        }

        # Write to archive with metadata
        with open(dest_path, "w") as f:
            json.dump(ticket_data, f, indent=2, default=str)

        # Remove from original location
        if source_path.exists():
            source_path.unlink()

    return dest_path


def restore_ticket(ticket_id: str, target_status: str = "done", use_git: Optional[bool] = None) -> Ticket:
    """Restore an archived ticket back to the board.
    
    Args:
        ticket_id: ID of the ticket to restore
        target_status: Status to restore the ticket to
        use_git: Whether to use git mv (auto-detected if None)
        
    Returns:
        The restored ticket
        
    Raises:
        FileNotFoundError: If ticket not found in archive
    """
    # Normalize ticket ID for file searching
    from gira.constants import normalize_ticket_id, get_project_prefix
    try:
        prefix = get_project_prefix()
        normalized_id = normalize_ticket_id(ticket_id, prefix)
    except ValueError:
        # If we can't get prefix, just uppercase the ID
        normalized_id = ticket_id.upper()
    
    # Search for ticket in archive
    archive_dir = get_archive_dir()

    for month_dir in sorted(archive_dir.iterdir(), reverse=True):
        if not month_dir.is_dir():
            continue

        ticket_path = month_dir / f"{normalized_id}.json"
        if ticket_path.exists():
            # Load ticket data
            with open(ticket_path) as f:
                data = json.load(f)

            # Remove archive metadata
            data.pop("_archive_metadata", None)

            # Create ticket object with new status
            data["status"] = target_status
            ticket = Ticket(**data)

            # Get root path
            root = get_gira_root()
            if root is None:
                raise ValueError("Not in a Gira project")

            # Determine whether to use git operations
            if use_git is None:
                use_git = should_use_git(root, operation="archive")

            # Prepare destination
            board_dir = root / ".gira" / "board" / target_status
            board_dir.mkdir(parents=True, exist_ok=True)
            dest_path = board_dir / f"{normalized_id}.json"

            # Save ticket to destination
            with open(dest_path, "w") as f:
                json.dump(ticket.to_json_dict(), f, indent=2, default=str)

            # Remove from archive using git or regular delete
            if use_git:
                from gira.utils.git_ops import remove_with_git_fallback
                remove_with_git_fallback(ticket_path, root, use_git=True, silent=False)
            else:
                ticket_path.unlink()

            # Clean up empty month directory
            if not any(month_dir.iterdir()):
                month_dir.rmdir()

            return ticket

    raise FileNotFoundError(f"Ticket {ticket_id} not found in archive")


def list_archived_tickets(
    month: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """List archived tickets with optional filtering.
    
    Args:
        month: Filter by specific month (YYYY-MM format)
        search: Search term for filtering tickets
        limit: Maximum number of tickets to return
        
    Returns:
        List of archived ticket info dictionaries
    """
    archive_dir = get_archive_dir()
    archived_tickets = []

    # Determine which directories to search
    if month:
        month_dirs = [archive_dir / month] if (archive_dir / month).exists() else []
    else:
        month_dirs = sorted(
            [d for d in archive_dir.iterdir() if d.is_dir()],
            reverse=True
        )

    for month_dir in month_dirs:
        for ticket_file in sorted(month_dir.glob("*.json")):
            with open(ticket_file) as f:
                data = json.load(f)

            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                if not any(
                    search_lower in str(v).lower()
                    for k, v in data.items()
                    if k in ["id", "title", "description", "type", "labels"]
                ):
                    continue

            # Create ticket info
            ticket_info = {
                "id": data["id"],
                "title": data["title"],
                "type": data.get("type", "task"),
                "priority": data.get("priority", "medium"),
                "archived_at": data.get("_archive_metadata", {}).get("archived_at"),
                "archived_from": data.get("_archive_metadata", {}).get("archived_from_status"),
                "month": month_dir.name
            }

            archived_tickets.append(ticket_info)

            # Apply limit if specified
            if limit and len(archived_tickets) >= limit:
                return archived_tickets

    return archived_tickets


def get_archive_stats() -> Dict[str, Any]:
    """Get statistics about archived tickets.
    
    Returns:
        Dictionary with archive statistics
    """
    archive_dir = get_archive_dir()
    stats = {
        "total_archived": 0,
        "months": 0,
        "by_month": {}
    }

    for month_dir in archive_dir.iterdir():
        if not month_dir.is_dir():
            continue

        ticket_count = len(list(month_dir.glob("*.json")))
        if ticket_count > 0:
            stats["months"] += 1
            stats["total_archived"] += ticket_count
            stats["by_month"][month_dir.name] = ticket_count

    return stats
