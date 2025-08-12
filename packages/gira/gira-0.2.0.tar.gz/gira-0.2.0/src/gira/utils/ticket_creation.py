"""Shared utilities for ticket creation."""

import json
from pathlib import Path
from typing import List, Optional, Tuple

from gira.constants import VALID_PRIORITIES, VALID_TYPES
from gira.models import ProjectConfig, Ticket
from gira.models.ticket import TicketPriority, TicketType
from gira.utils.board_config import get_valid_statuses
from gira.utils.team_utils import find_assignee


def determine_initial_status(
    provided_status: Optional[str],
    config: ProjectConfig,
    root: Path
) -> str:
    """Determine the initial status for a ticket.
    
    Priority order:
    1. Explicitly provided status
    2. ProjectConfig default_ticket_status field
    3. Config file ticket.default_status key
    4. Fallback to 'todo'
    """
    initial_status = provided_status

    if initial_status is None:
        # Check for default status in config
        # First check the ProjectConfig field
        initial_status = getattr(config, 'default_ticket_status', None)

        # If not set, check the raw config data for ticket.default_status
        if initial_status is None:
            try:
                config_json_path = root / ".gira" / "config.json"
                if config_json_path.exists():
                    with open(config_json_path) as f:
                        config_data = json.load(f)
                        # Check for the ticket.default_status key
                        initial_status = config_data.get('ticket.default_status')
            except Exception:
                pass

    if initial_status is None:
        # Fall back to 'todo'
        initial_status = 'todo'

    return initial_status.lower()


def validate_ticket_fields(
    ticket_type: str,
    priority: str,
    initial_status: str,
    story_points: Optional[int] = None
) -> List[str]:
    """Validate ticket field values.
    
    Returns a list of error messages. Empty list means all fields are valid.
    """
    errors = []

    # Validate ticket type
    if ticket_type.lower() not in VALID_TYPES:
        errors.append(f"Invalid ticket type '{ticket_type}'. Valid types: {', '.join(VALID_TYPES)}")

    # Validate priority
    if priority.lower() not in VALID_PRIORITIES:
        errors.append(f"Invalid priority '{priority}'. Valid priorities: {', '.join(VALID_PRIORITIES)}")

    # Validate status
    valid_statuses = get_valid_statuses()
    if initial_status not in valid_statuses:
        errors.append(f"Invalid status '{initial_status}'. Valid statuses: {', '.join(valid_statuses)}")

    # Validate story points
    if story_points is not None and not (0 <= story_points <= 100):
        errors.append("Story points must be between 0 and 100")

    return errors


def resolve_assignee(
    assignee: Optional[str],
    root: Path,
    strict: bool = False
) -> Tuple[Optional[str], List[str]]:
    """Resolve assignee to email address.
    
    Returns:
        Tuple of (resolved_email, warnings)
        - resolved_email: Email address or None
        - warnings: List of warning messages
    """
    if not assignee:
        return None, []

    warnings = []
    resolved_email, team = find_assignee(assignee, root)

    if resolved_email:
        # Check if this is a known team member or external assignee
        is_team_member = team and team.find_member(assignee) is not None
        if not is_team_member:
            warnings.append(f"Unknown assignee '{assignee}'")
            # Check strict mode or team setting
            if strict or (team and not team.allow_external_assignees):
                if strict:
                    raise ValueError("Unknown assignee not allowed in strict mode. Use 'gira team add' to add team members.")
                else:
                    raise ValueError("External assignees not allowed. Use 'gira team add' to add team members.")
        return resolved_email, warnings
    else:
        raise ValueError(f"Unknown assignee '{assignee}' not allowed")


def parse_labels(labels: Optional[str]) -> List[str]:
    """Parse labels from string or list format.
    
    Args:
        labels: Comma-separated string, list of strings, or None
        
    Returns:
        List of label strings
    """
    if not labels:
        return []

    if isinstance(labels, list):
        return labels

    return [lbl.strip() for lbl in str(labels).split(",") if lbl.strip()]


def create_ticket_dict(
    ticket: Ticket,
    initial_status: str
) -> dict:
    """Create a dictionary representation of a ticket for output."""
    # Ensure we get string values for enums
    priority_value = ticket.priority.value if isinstance(ticket.priority, TicketPriority) else str(ticket.priority)
    type_value = ticket.type.value if isinstance(ticket.type, TicketType) else str(ticket.type)

    return {
        "id": ticket.id,
        "title": ticket.title,
        "status": initial_status,
        "priority": priority_value,
        "type": type_value
    }
