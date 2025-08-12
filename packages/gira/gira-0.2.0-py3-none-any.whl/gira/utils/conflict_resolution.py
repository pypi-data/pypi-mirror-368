"""Conflict detection and resolution utilities for Gira."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from gira.models.ticket import Ticket
from gira.utils.console import console
from gira.utils.ticket_utils import load_all_tickets


def detect_id_conflicts(root: Path) -> Dict[str, List[Ticket]]:
    """
    Detect tickets with the same display ID but different UUIDs.

    Args:
        root: Project root path

    Returns:
        Dictionary mapping duplicate display IDs to lists of conflicting tickets
    """
    all_tickets = load_all_tickets(root, include_archived=False)
    id_to_tickets: Dict[str, List[Ticket]] = {}

    # Group tickets by display ID
    for ticket in all_tickets:
        if ticket.id not in id_to_tickets:
            id_to_tickets[ticket.id] = []
        id_to_tickets[ticket.id].append(ticket)

    # Find conflicts (same ID, different UUIDs)
    conflicts = {}
    for display_id, tickets in id_to_tickets.items():
        if len(tickets) > 1:
            # Check if they have different UUIDs
            uuids = {ticket.uuid for ticket in tickets}
            if len(uuids) > 1:
                conflicts[display_id] = tickets

    return conflicts


def get_next_available_id(prefix: str, existing_ids: Set[str]) -> str:
    """
    Find the next available sequential ID.

    Args:
        prefix: Ticket ID prefix (e.g., "GCM")
        existing_ids: Set of currently used display IDs

    Returns:
        Next available ID (e.g., "GCM-127")
    """
    # Find the highest existing number
    max_number = 0
    for ticket_id in existing_ids:
        if ticket_id.startswith(f"{prefix}-"):
            try:
                number = int(ticket_id.split("-")[1])
                max_number = max(max_number, number)
            except (ValueError, IndexError):
                continue

    # Return the next available number
    return f"{prefix}-{max_number + 1}"


def resolve_id_conflicts(
    root: Path, conflicts: Dict[str, List[Ticket]], dry_run: bool = False
) -> List[str]:
    """
    Resolve ID conflicts by reassigning display IDs to conflicting tickets.

    Args:
        root: Project root path
        conflicts: Dictionary of conflicting tickets by display ID
        dry_run: If True, only show what would be changed without making changes

    Returns:
        List of changes made/would be made
    """
    changes = []

    if not conflicts:
        return changes

    # Get all existing IDs to avoid creating new conflicts
    all_tickets = load_all_tickets(root, include_archived=False)
    existing_ids = {ticket.id for ticket in all_tickets}

    # Load project config to get prefix
    config_path = root / ".gira" / "config.json"
    with open(config_path) as f:
        config_data = json.load(f)
    prefix = config_data.get("ticket_id_prefix", "GCM")

    for _conflict_id, conflicting_tickets in conflicts.items():
        # Sort by creation time to be deterministic
        conflicting_tickets.sort(key=lambda t: t.created_at)

        # Keep the first one (oldest), reassign the rest
        tickets_to_reassign = conflicting_tickets[1:]

        for ticket in tickets_to_reassign:
            old_id = ticket.id
            new_id = get_next_available_id(prefix, existing_ids)
            existing_ids.add(new_id)  # Track the new ID

            change_msg = f"Reassign {old_id} (UUID: {ticket.uuid[:8]}...) → {new_id}"
            changes.append(change_msg)

            if not dry_run:
                # Update the ticket
                old_path = find_ticket_file_path(ticket, root)
                if old_path:
                    # Update ticket object
                    ticket.id = new_id

                    # Save to new location
                    new_path = old_path.parent / f"{new_id}.json"
                    ticket.save_to_json_file(str(new_path))

                    # Remove old file
                    old_path.unlink()

                    # Update any relationships pointing to this ticket
                    update_ticket_relationships(root, old_id, new_id)

    return changes


def find_ticket_file_path(ticket: Ticket, root: Path) -> Optional[Path]:
    """Find the file path for a ticket based on its ID and UUID."""

    def _match_uuid(path: Path) -> bool:
        try:
            data = json.loads(path.read_text())
            return data.get("uuid") == ticket.uuid
        except Exception:
            return False

    # Search backlog (flat and hashed)
    backlog_dir = root / ".gira" / "backlog"
    if backlog_dir.exists():
        for candidate in backlog_dir.rglob(f"{ticket.id}.json"):
            if _match_uuid(candidate):
                return candidate

    # Search board directories
    board_dir = root / ".gira" / "board"
    if board_dir.exists():
        for status_dir in board_dir.iterdir():
            if status_dir.is_dir():
                candidate = status_dir / f"{ticket.id}.json"
                if candidate.exists() and _match_uuid(candidate):
                    return candidate

    return None


def update_ticket_relationships(root: Path, old_id: str, new_id: str) -> None:
    """
    Update all ticket relationships that reference the old ID.

    Args:
        root: Project root path
        old_id: Old ticket ID being changed
        new_id: New ticket ID to replace it with
    """
    all_tickets = load_all_tickets(root, include_archived=False)

    for ticket in all_tickets:
        updated = False

        # Update epic_id references
        if ticket.epic_id == old_id:
            ticket.epic_id = new_id
            updated = True

        # Update parent_id references
        if ticket.parent_id == old_id:
            ticket.parent_id = new_id
            updated = True

        # Update dependency references
        if old_id in ticket.blocked_by:
            ticket.blocked_by = [
                new_id if dep_id == old_id else dep_id for dep_id in ticket.blocked_by
            ]
            updated = True

        if old_id in ticket.blocks:
            ticket.blocks = [
                new_id if dep_id == old_id else dep_id for dep_id in ticket.blocks
            ]
            updated = True

        # Save the updated ticket
        if updated:
            ticket_path = find_ticket_file_path(ticket, root)
            if ticket_path:
                ticket.save_to_json_file(str(ticket_path))


def sync_project(root: Path, dry_run: bool = False) -> None:
    """
    Detect and resolve all conflicts in the project.

    Args:
        root: Project root path
        dry_run: If True, only show what would be changed
    """
    console.print("🔍 Detecting ID conflicts...", style="cyan")

    conflicts = detect_id_conflicts(root)

    if not conflicts:
        console.print("✅ No ID conflicts detected!", style="green")
        return

    console.print(f"⚠️  Found {len(conflicts)} ID conflicts:", style="yellow")
    for conflict_id, tickets in conflicts.items():
        console.print(f"  • {conflict_id}: {len(tickets)} tickets with different UUIDs")

    console.print()
    changes = resolve_id_conflicts(root, conflicts, dry_run=dry_run)

    if dry_run:
        console.print("🔮 Changes that would be made:", style="cyan")
        for change in changes:
            console.print(f"  • {change}")
    else:
        console.print("✅ Resolved conflicts:", style="green")
        for change in changes:
            console.print(f"  • {change}")
