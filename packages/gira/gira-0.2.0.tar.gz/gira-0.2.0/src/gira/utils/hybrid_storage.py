"""Hybrid storage system for Gira tickets.

This module implements a hybrid directory structure:
- Active board tickets (todo, in_progress, review, done) use flat structure
- Backlog tickets use hashed directory structure for scalability
"""

import hashlib
from pathlib import Path
from typing import List, Optional, Tuple

from gira.models import Ticket

BOARD_STATUSES = {"todo", "in_progress", "review", "done"}
BACKLOG_STATUS = "backlog"


def get_hash_path(ticket_id: str) -> str:
    """
    Generate a hashed directory path for a ticket ID.

    Uses a 2-level directory structure based on the ticket ID:
    - First level: First 2 characters after prefix (or hash if ID is short)
    - Second level: Next 2 characters (or hash if needed)

    Examples:
        GCM-123 -> GC/M-/GCM-123.json
        EPIC-001 -> EP/IC/EPIC-001.json
        AB-1 -> AB/-1/AB-1.json

    Args:
        ticket_id: The ticket ID

    Returns:
        The hashed directory path components (e.g., "GC/M-")
    """
    # Normalize ticket ID
    ticket_id = ticket_id.upper()

    # Extract parts for hashing
    # Most ticket IDs follow pattern PREFIX-NUMBER
    if "-" in ticket_id:
        prefix, number = ticket_id.split("-", 1)

        # Use first 2 chars of prefix
        level1 = prefix[:2] if len(prefix) >= 2 else prefix.ljust(2, "0")

        # Use next 2 chars of prefix or start of number
        if len(prefix) >= 4:
            level2 = prefix[2:4]
        elif len(prefix) == 3:
            level2 = prefix[2] + "-"
        elif len(prefix) == 2:
            # For 2-char prefix like "AB", use first char of number
            level2 = "-" + number[0] if number else "--"
        else:
            # Very short prefix, pad and use dash
            level2 = prefix.ljust(1, "0") + "-"
    else:
        # Non-standard ticket ID, use hash
        hash_val = hashlib.md5(ticket_id.encode()).hexdigest()
        level1 = hash_val[:2]
        level2 = hash_val[2:4]

    return f"{level1}/{level2}"


def get_ticket_storage_path(ticket_id: str, status: str, root: Path) -> Path:
    """
    Get the storage path for a ticket based on its status.

    Args:
        ticket_id: The ticket ID
        status: The ticket status
        root: The project root path

    Returns:
        The full path where the ticket should be stored
    """
    ticket_id = ticket_id.upper()

    if status in BOARD_STATUSES:
        # Active board tickets use flat structure
        return root / ".gira" / "board" / status / f"{ticket_id}.json"
    elif status == BACKLOG_STATUS:
        # Backlog tickets use hashed structure
        hash_path = get_hash_path(ticket_id)
        return root / ".gira" / "backlog" / hash_path / f"{ticket_id}.json"
    else:
        # Unknown status, fallback to board structure
        return root / ".gira" / "board" / status / f"{ticket_id}.json"


def find_ticket_in_hashed_backlog(ticket_id: str, root: Path) -> Optional[Path]:
    """
    Find a ticket in the hashed backlog structure.

    Args:
        ticket_id: The ticket ID to find
        root: The project root path

    Returns:
        The path to the ticket file if found, None otherwise
    """
    ticket_id = ticket_id.upper()
    hash_path = get_hash_path(ticket_id)
    ticket_path = root / ".gira" / "backlog" / hash_path / f"{ticket_id}.json"

    if ticket_path.exists():
        return ticket_path
    return None


def find_ticket_in_flat_backlog(ticket_id: str, root: Path) -> Optional[Path]:
    """
    Find a ticket in the legacy flat backlog structure.

    Args:
        ticket_id: The ticket ID to find
        root: The project root path

    Returns:
        The path to the ticket file if found, None otherwise
    """
    ticket_id = ticket_id.upper()
    ticket_path = root / ".gira" / "backlog" / f"{ticket_id}.json"

    if ticket_path.exists():
        return ticket_path
    return None


def load_tickets_from_hashed_directory(base_dir: Path) -> List[Tuple[Ticket, Path]]:
    """
    Load all tickets from a hashed directory structure.

    Args:
        base_dir: The base directory containing hashed subdirectories

    Returns:
        List of (ticket, path) tuples
    """
    tickets = []

    if not base_dir.exists():
        return tickets

    # Traverse the 2-level hash structure
    for level1_dir in base_dir.iterdir():
        if level1_dir.is_dir() and len(level1_dir.name) == 2:
            for level2_dir in level1_dir.iterdir():
                if level2_dir.is_dir() and len(level2_dir.name) == 2:
                    # Load all JSON files in this directory
                    for ticket_file in level2_dir.glob("*.json"):
                        try:
                            ticket = Ticket.from_json_file(str(ticket_file))
                            tickets.append((ticket, ticket_file))
                        except Exception:
                            # Skip invalid ticket files
                            continue

    return tickets


def migrate_ticket_location(
    ticket: Ticket, old_path: Path, new_status: str, root: Path, use_git: Optional[bool] = None
) -> Path:
    """
    Migrate a ticket file from its current location to the new location based on status.

    This handles the physical file move when a ticket changes status.

    Args:
        ticket: The ticket object
        old_path: The current path of the ticket file
        new_status: The new status of the ticket
        root: The project root path
        use_git: Whether to use git operations (auto-detected if None)

    Returns:
        The new path where the ticket was moved
    """
    # Get the new path based on the new status
    new_path = get_ticket_storage_path(ticket.id, new_status, root)

    # Create parent directory if needed
    new_path.parent.mkdir(parents=True, exist_ok=True)

    # Move the file with git-aware operations when appropriate
    if old_path != new_path:
        # Import git operations
        from gira.utils.git_ops import should_use_git, move_with_git_fallback
        
        # Determine if we should use git operations
        if use_git is None:
            use_git = should_use_git(root, operation="move")
        
        # Use git-aware move with fallback to regular file operations
        new_path = move_with_git_fallback(
            source=old_path,
            destination=new_path,
            root=root,
            use_git=use_git,
            silent=True  # Suppress warnings for internal operations
        )

    return new_path


def is_hybrid_structure_enabled(root: Path) -> bool:
    """
    Check if the hybrid directory structure is enabled for this project.

    This is determined by checking for the presence of hashed directories
    in the backlog folder.

    Args:
        root: The project root path

    Returns:
        True if hybrid structure is enabled, False otherwise
    """
    backlog_dir = root / ".gira" / "backlog"
    if not backlog_dir.exists():
        return False

    # Check if there are any 2-character directories (hash structure)
    return any(item.is_dir() and len(item.name) == 2 for item in backlog_dir.iterdir())


def get_backlog_ticket_count(root: Path) -> Tuple[int, int]:
    """
    Get the count of backlog tickets in flat vs hashed structure.

    Args:
        root: The project root path

    Returns:
        Tuple of (flat_count, hashed_count)
    """
    backlog_dir = root / ".gira" / "backlog"
    if not backlog_dir.exists():
        return 0, 0

    flat_count = 0
    hashed_count = 0

    # Count flat structure tickets
    for item in backlog_dir.iterdir():
        if item.is_file() and item.suffix == ".json":
            flat_count += 1

    # Count hashed structure tickets
    for level1_dir in backlog_dir.iterdir():
        if level1_dir.is_dir() and len(level1_dir.name) == 2:
            for level2_dir in level1_dir.iterdir():
                if level2_dir.is_dir() and len(level2_dir.name) == 2:
                    hashed_count += len(list(level2_dir.glob("*.json")))

    return flat_count, hashed_count
