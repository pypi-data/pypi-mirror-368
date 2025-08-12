"""Automatic archiving utilities for Gira."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from gira.utils.archive import archive_ticket
from gira.utils.console import console
from gira.utils.ticket_utils import load_all_tickets


def check_auto_archive(root: Path, verbose: bool = False) -> List[str]:
    """Check for tickets that should be automatically archived based on config.
    
    Args:
        root: Project root directory
        verbose: Show progress messages
        
    Returns:
        List of ticket IDs that were archived
    """
    from gira.utils.config_utils import load_config

    config = load_config(root)
    auto_archive_days = config.get("archive.auto_archive_after_days")

    if not auto_archive_days:
        return []

    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=auto_archive_days)

    # Get all done tickets
    tickets = load_all_tickets(root)
    done_tickets = [t for t in tickets if t.status == "done"]

    archived = []
    for ticket in done_tickets:
        # Check if ticket has been done long enough
        if ticket.updated_at < cutoff_date:
            if verbose:
                days_old = (datetime.now() - ticket.updated_at).days
                console.print(f"[dim]Auto-archiving {ticket.id} (done {days_old} days ago)[/dim]")

            archive_ticket(ticket)
            archived.append(ticket.id)

    if archived and verbose:
        console.print(f"[green]✓[/green] Auto-archived {len(archived)} tickets")

    return archived


def check_performance_threshold(root: Path) -> Optional[Tuple[int, int]]:
    """Check if active ticket count exceeds performance threshold.
    
    Returns:
        Tuple of (active_count, threshold) if threshold exceeded, None otherwise
    """
    from gira.cli.commands.config import load_config

    config = load_config(root)
    threshold = config.get("archive.performance_threshold", 1000)

    # Count active tickets
    board_dir = root / ".gira" / "board"
    if not board_dir.exists():
        return None

    active_count = 0
    for status_dir in board_dir.iterdir():
        if status_dir.is_dir() and status_dir.name != "archive":
            active_count += len(list(status_dir.glob("*.json")))

    if active_count > threshold:
        return active_count, threshold

    return None


def suggest_archivable_tickets(root: Path) -> dict:
    """Analyze project and suggest tickets to archive.
    
    Returns:
        Dictionary with suggestions by category
    """
    from gira.models.epic import Epic
    from gira.models.sprint import Sprint
    from gira.utils.config_utils import load_config

    config = load_config(root)
    suggest_done_days = config.get("archive.suggest_done_after_days", 30)
    suggest_stale_days = config.get("archive.suggest_stale_after_days", 90)

    suggestions = {
        "old_done": [],
        "completed_epics": [],
        "completed_sprints": [],
        "stale_backlog": []
    }

    tickets = load_all_tickets(root)

    # 1. Old done tickets
    cutoff_done = datetime.now() - timedelta(days=suggest_done_days)
    for ticket in tickets:
        if ticket.status == "done" and ticket.updated_at < cutoff_done:
            days_old = (datetime.now() - ticket.updated_at).days
            suggestions["old_done"].append({
                "ticket": ticket,
                "reason": f"Done {days_old} days ago"
            })

    # 2. Tickets from completed epics
    epics_dir = root / ".gira" / "epics"
    if epics_dir.exists():
        for epic_file in epics_dir.glob("*.json"):
            epic = Epic.from_json_file(str(epic_file))
            if epic.status == "done":
                # Find all tickets in this epic
                epic_tickets = [t for t in tickets if t.epic_id == epic.id]
                for ticket in epic_tickets:
                    if ticket.status == "done":
                        suggestions["completed_epics"].append({
                            "ticket": ticket,
                            "reason": f"Part of completed epic {epic.id}"
                        })

    # 3. Tickets from completed sprints
    sprints_dir = root / ".gira" / "sprints"
    if sprints_dir.exists():
        for sprint_file in sprints_dir.glob("*.json"):
            sprint = Sprint.from_json_file(str(sprint_file))
            if sprint.status == "completed":
                # Find all tickets in this sprint
                sprint_tickets = [t for t in tickets if t.sprint_id == sprint.id]
                for ticket in sprint_tickets:
                    if ticket.status == "done":
                        suggestions["completed_sprints"].append({
                            "ticket": ticket,
                            "reason": f"Part of completed sprint {sprint.name}"
                        })

    # 4. Stale backlog tickets
    cutoff_stale = datetime.now() - timedelta(days=suggest_stale_days)
    for ticket in tickets:
        if ticket.status == "backlog" and ticket.created_at < cutoff_stale:
            days_old = (datetime.now() - ticket.created_at).days
            suggestions["stale_backlog"].append({
                "ticket": ticket,
                "reason": f"In backlog for {days_old} days"
            })

    # Remove duplicates across categories
    seen_ids = set()
    for category in suggestions:
        unique_suggestions = []
        for item in suggestions[category]:
            if item["ticket"].id not in seen_ids:
                unique_suggestions.append(item)
                seen_ids.add(item["ticket"].id)
        suggestions[category] = unique_suggestions

    return suggestions
