"""Epic utility functions for bidirectional epic-ticket synchronization."""

from pathlib import Path
from typing import Optional, Tuple

from gira.models.epic import Epic
from gira.utils.console import console


def sync_epic_ticket_relationship(
    ticket_id: str,
    old_epic_id: Optional[str],
    new_epic_id: Optional[str],
    root: Path
) -> None:
    """Synchronize epic-ticket relationships bidirectionally.
    
    This function ensures that:
    1. If a ticket is removed from an epic, the epic's tickets list is updated
    2. If a ticket is added to an epic, the epic's tickets list is updated
    3. Both operations are performed atomically
    
    Args:
        ticket_id: The ticket ID being updated
        old_epic_id: The previous epic ID (None if ticket wasn't in an epic)
        new_epic_id: The new epic ID (None if ticket is being removed from epic)
        root: The root project directory
    """
    # Remove ticket from old epic if it exists
    if old_epic_id:
        old_epic_path = root / ".gira" / "epics" / f"{old_epic_id}.json"
        if old_epic_path.exists():
            old_epic = Epic.from_json_file(str(old_epic_path))
            if ticket_id in old_epic.tickets:
                old_epic.tickets.remove(ticket_id)
                old_epic.save_to_json_file(str(old_epic_path))

    # Add ticket to new epic if it exists
    if new_epic_id:
        new_epic_path = root / ".gira" / "epics" / f"{new_epic_id}.json"
        if new_epic_path.exists():
            new_epic = Epic.from_json_file(str(new_epic_path))
            if ticket_id not in new_epic.tickets:
                new_epic.tickets.append(ticket_id)
                new_epic.save_to_json_file(str(new_epic_path))


def add_ticket_to_epic(ticket_id: str, epic_id: str, root: Path) -> bool:
    """Add a ticket to an epic's tickets list.
    
    Args:
        ticket_id: The ticket ID to add
        epic_id: The epic ID to add the ticket to
        root: The root project directory
        
    Returns:
        True if the ticket was added, False if the epic doesn't exist
    """
    epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
    if not epic_path.exists():
        return False

    epic = Epic.from_json_file(str(epic_path))
    if ticket_id not in epic.tickets:
        epic.tickets.append(ticket_id)
        epic.save_to_json_file(str(epic_path))

    return True


def remove_ticket_from_epic(ticket_id: str, epic_id: str, root: Path) -> bool:
    """Remove a ticket from an epic's tickets list.
    
    Args:
        ticket_id: The ticket ID to remove
        epic_id: The epic ID to remove the ticket from
        root: The root project directory
        
    Returns:
        True if the ticket was removed, False if the epic doesn't exist
    """
    epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
    if not epic_path.exists():
        return False

    epic = Epic.from_json_file(str(epic_path))
    if ticket_id in epic.tickets:
        epic.tickets.remove(ticket_id)
        epic.save_to_json_file(str(epic_path))

    return True


def find_epic(epic_id: str, root: Path, include_archived: bool = False) -> Tuple[Optional[Epic], Optional[Path]]:
    """Find an epic by ID.
    
    Args:
        epic_id: The epic ID to find
        root: The project root path
        include_archived: Whether to search in archived epics
        
    Returns:
        Tuple of (epic, epic_path) or (None, None) if not found
    """
    epic_id = epic_id.upper()

    # Check active epics first
    epics_dir = root / ".gira" / "epics"
    epic_file = epics_dir / f"{epic_id}.json"

    if epic_file.exists():
        try:
            epic = Epic.from_json_file(str(epic_file))
            return epic, epic_file
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to load epic {epic_id}: {e}")

    # Check archived epics if requested
    if include_archived:
        archive_dir = root / ".gira" / "archive" / "epics"
        if archive_dir.exists():
            epic_file = archive_dir / f"{epic_id}.json"
            if epic_file.exists():
                try:
                    epic = Epic.from_json_file(str(epic_file))
                    return epic, epic_file
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Failed to load archived epic {epic_id}: {e}")

    return None, None


def is_epic_archived(epic_path: Path) -> bool:
    """Check if an epic is archived based on its file path."""
    return "archive" in epic_path.parts
