"""Ticket-related utilities for Gira."""

from pathlib import Path
from typing import List, Optional, Tuple

from gira.models import Ticket
from gira.utils.cache import cached, invalidate_ticket_cache
from gira.utils.hybrid_storage import (
    find_ticket_in_flat_backlog,
    find_ticket_in_hashed_backlog,
    get_ticket_storage_path,
    is_hybrid_structure_enabled,
    load_tickets_from_hashed_directory,
)


def find_ticket(ticket_id: str, root: Path, include_archived: bool = False) -> Tuple[Optional[Ticket], Optional[Path]]:
    """
    Find a ticket by ID in the project.

    Args:
        ticket_id: The ticket ID to find (will be normalized to uppercase)
        root: The project root path
        include_archived: Whether to search in archived tickets (default: False)

    Returns:
        Tuple of (ticket, ticket_path) or (None, None) if not found
    """
    # Normalize the ticket ID (add prefix if needed)
    from gira.constants import normalize_ticket_id, get_project_prefix
    try:
        prefix = get_project_prefix()
        ticket_id = normalize_ticket_id(ticket_id, prefix)
    except ValueError:
        # If we can't get prefix, just uppercase the ID
        ticket_id = ticket_id.upper()

    # Check if this is a historical ticket ID and map to current
    from gira.utils.prefix_history import PrefixHistory
    history = PrefixHistory(root)

    # If it's a valid historical ID, also search for the current mapped ID
    search_ids = [ticket_id]
    if history.is_valid_historical_id(ticket_id):
        current_id = history.map_old_to_current(ticket_id)
        if current_id != ticket_id:
            search_ids.append(current_id)

    # Try each possible ID (original and mapped)
    for search_id in search_ids:
        # Check tickets directory first
        tickets_path = root / ".gira" / "tickets" / f"{search_id}.json"
        if tickets_path.exists():
            try:
                ticket = Ticket.from_json_file(str(tickets_path))
                # If found with a historical ID, show a deprecation notice
                if search_id != ticket_id:
                    from gira.utils.console import console
                    console.print(f"[yellow]Note:[/yellow] Found ticket using current ID '{search_id}' (searched for historical ID '{ticket_id}')")
                return ticket, tickets_path
            except Exception:
                pass

        # Check backlog (try hashed structure first if enabled, then flat)
        if is_hybrid_structure_enabled(root):
            # Try hashed structure first
            hashed_path = find_ticket_in_hashed_backlog(search_id, root)
            if hashed_path:
                try:
                    ticket = Ticket.from_json_file(str(hashed_path))
                    if search_id != ticket_id:
                        from gira.utils.console import console
                        console.print(f"[yellow]Note:[/yellow] Found ticket using current ID '{search_id}' (searched for historical ID '{ticket_id}')")
                    return ticket, hashed_path
                except Exception:
                    pass

        # Try flat structure (legacy or fallback)
        flat_path = find_ticket_in_flat_backlog(search_id, root)
        if flat_path:
            try:
                ticket = Ticket.from_json_file(str(flat_path))
                if search_id != ticket_id:
                    from gira.utils.console import console
                    console.print(f"[yellow]Note:[/yellow] Found ticket using current ID '{search_id}' (searched for historical ID '{ticket_id}')")
                return ticket, flat_path
            except Exception:
                pass

        # Check board directories
        board_dir = root / ".gira" / "board"
        if board_dir.exists():
            for status_dir in board_dir.iterdir():
                if status_dir.is_dir():
                    candidate_path = status_dir / f"{search_id}.json"
                    if candidate_path.exists():
                        try:
                            ticket = Ticket.from_json_file(str(candidate_path))
                            if search_id != ticket_id:
                                from gira.utils.console import console
                                console.print(f"[yellow]Note:[/yellow] Found ticket using current ID '{search_id}' (searched for historical ID '{ticket_id}')")
                            return ticket, candidate_path
                        except Exception:
                            continue

        # Check archive directories if requested
        if include_archived:
            archive_dir = root / ".gira" / "archive"
            if archive_dir.exists():
                for month_dir in archive_dir.iterdir():
                    if month_dir.is_dir():
                        candidate_path = month_dir / f"{search_id}.json"
                        if candidate_path.exists():
                            try:
                                ticket = Ticket.from_json_file(str(candidate_path))
                                if search_id != ticket_id:
                                    from gira.utils.console import console
                                    console.print(f"[yellow]Note:[/yellow] Found ticket using current ID '{search_id}' (searched for historical ID '{ticket_id}')")
                                return ticket, candidate_path
                            except Exception:
                                continue

    return None, None


def is_ticket_archived(ticket_path: Path) -> bool:
    """
    Check if a ticket is archived based on its file path.
    
    Args:
        ticket_path: The path to the ticket file
        
    Returns:
        True if the ticket is in the archive directory, False otherwise
    """
    return ".gira/archive/" in str(ticket_path)


@cached(ttl=900)  # Cache for 15 minutes
def load_all_tickets(root: Optional[Path] = None, include_archived: bool = False) -> List[Ticket]:
    """
    Load all tickets from the project.

    Args:
        root: The project root path (optional, will auto-detect if not provided)
        include_archived: Whether to include archived tickets (default: False)

    Returns:
        List of all tickets in the project
    """
    if root is None:
        from gira.utils.project import get_gira_root
        root = get_gira_root()
    if root is None:
        raise ValueError("Not in a Gira project")

    tickets = []

    # Search in backlog (handle both flat and hashed structures)
    backlog_dir = root / ".gira" / "backlog"
    if backlog_dir.exists():
        if is_hybrid_structure_enabled(root):
            # If hybrid structure is enabled, ONLY load from hashed directories
            hashed_tickets = load_tickets_from_hashed_directory(backlog_dir)
            for ticket, _ in hashed_tickets:
                tickets.append(ticket)
        else:
            # Otherwise, load from flat structure
            for ticket_file in backlog_dir.glob("*.json"):
                try:
                    ticket = Ticket.from_json_file(str(ticket_file))
                    tickets.append(ticket)
                except Exception:
                    continue

    # Search in board directories
    board_dir = root / ".gira" / "board"
    if board_dir.exists():
        for status_dir in board_dir.iterdir():
            if status_dir.is_dir():
                for ticket_file in status_dir.glob("*.json"):
                    try:
                        ticket = Ticket.from_json_file(str(ticket_file))
                        tickets.append(ticket)
                    except Exception:
                        continue

    # Search in archive directories if requested
    if include_archived:
        archive_dir = root / ".gira" / "archive"
        if archive_dir.exists():
            for month_dir in archive_dir.iterdir():
                if month_dir.is_dir():
                    for ticket_file in month_dir.glob("*.json"):
                        try:
                            ticket = Ticket.from_json_file(str(ticket_file))
                            tickets.append(ticket)
                        except Exception:
                            continue

    return tickets


def get_ticket_path(ticket_id: str, status: str, root: Path) -> Path:
    """
    Get the file path for a ticket based on its ID and status.

    Args:
        ticket_id: The ticket ID
        status: The ticket status
        root: The project root path

    Returns:
        Path where the ticket should be stored
    """
    return get_ticket_storage_path(ticket_id, status, root)


@cached(ttl=900)  # Cache for 15 minutes
def load_tickets_by_status(status: str) -> List[Ticket]:
    """
    Load all tickets with a specific status.

    Args:
        status: The status to filter by

    Returns:
        List of tickets with the given status
    """
    from gira.utils.project import get_gira_root

    root = get_gira_root()
    if root is None:
        raise ValueError("Not in a Gira project")
    tickets = []

    if status == "backlog":
        backlog_dir = root / ".gira" / "backlog"
        if backlog_dir.exists():
            if is_hybrid_structure_enabled(root):
                # If hybrid structure is enabled, ONLY load from hashed directories
                hashed_tickets = load_tickets_from_hashed_directory(backlog_dir)
                for ticket, _ in hashed_tickets:
                    tickets.append(ticket)
            else:
                # Otherwise, load from flat structure
                for ticket_file in backlog_dir.glob("*.json"):
                    try:
                        ticket = Ticket.from_json_file(str(ticket_file))
                        tickets.append(ticket)
                    except Exception:
                        continue
    else:
        status_dir = root / ".gira" / "board" / status
        if status_dir.exists():
            for ticket_file in status_dir.glob("*.json"):
                try:
                    ticket = Ticket.from_json_file(str(ticket_file))
                    tickets.append(ticket)
                except Exception:
                    continue

    return tickets


def load_tickets_by_ids(ticket_ids: List[str], root: Optional[Path] = None, include_archived: bool = False) -> List[Ticket]:
    """
    Load specific tickets by their IDs efficiently.
    
    This is much more efficient than load_all_tickets() when you only need
    specific tickets, as it avoids loading the entire project.

    Args:
        ticket_ids: List of ticket IDs to load
        root: The project root path (optional, will auto-detect if not provided)
        include_archived: Whether to include archived tickets (default: False)

    Returns:
        List of tickets found (may be shorter than input if some tickets don't exist)
    """
    if root is None:
        from gira.utils.project import get_gira_root
        root = get_gira_root()
    if root is None:
        raise ValueError("Not in a Gira project")

    tickets = []
    for ticket_id in ticket_ids:
        ticket, _ = find_ticket(ticket_id, root, include_archived=include_archived)
        if ticket:
            tickets.append(ticket)

    return tickets


def load_ticket(ticket_id: str) -> Ticket:
    """
    Load a ticket by ID.

    Args:
        ticket_id: The ticket ID to load

    Returns:
        The ticket object

    Raises:
        FileNotFoundError: If ticket not found
    """
    from gira.utils.project import get_gira_root

    root = get_gira_root()
    if root is None:
        raise ValueError("Not in a Gira project")
    ticket, _ = find_ticket(ticket_id, root)

    if ticket is None:
        raise FileNotFoundError(f"Ticket {ticket_id} not found")

    return ticket


def save_ticket(ticket: Ticket, ticket_path: Path) -> None:
    """
    Save a ticket to its file path.

    Args:
        ticket: The ticket to save
        ticket_path: The path where to save the ticket
    """
    # Ensure parent directory exists
    ticket_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the ticket
    ticket.save_to_json_file(str(ticket_path))

    # Invalidate cache since we modified a ticket
    invalidate_ticket_cache()


def _would_create_parent_cycle(ticket_id: str, new_parent_id: str, root: Path) -> bool:
    """
    Check if setting new_parent_id as the parent of ticket_id would create a circular dependency.
    
    Args:
        ticket_id: The ticket that would get a new parent
        new_parent_id: The proposed parent ticket ID
        root: Gira project root directory
        
    Returns:
        True if setting the parent would create a cycle, False otherwise
    """
    if ticket_id == new_parent_id:
        return True  # Self-reference
    
    visited = set()
    
    def has_ancestor_path(current_id: str, target_id: str) -> bool:
        """Check if target_id is an ancestor of current_id."""
        if current_id == target_id:
            return True
        if current_id in visited:
            return False  # Prevent infinite loops in existing cycles
        visited.add(current_id)
        
        ticket, _ = find_ticket(current_id, root)
        if ticket and ticket.parent_id:
            return has_ancestor_path(ticket.parent_id, target_id)
        return False
    
    # Check if ticket_id is already an ancestor of new_parent_id
    # If so, making new_parent_id the parent of ticket_id would create a cycle
    return has_ancestor_path(new_parent_id, ticket_id)
