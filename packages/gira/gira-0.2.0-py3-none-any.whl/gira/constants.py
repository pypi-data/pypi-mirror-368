"""Constants used throughout the Gira application."""

# Status aliases for user-friendly input
STATUS_ALIASES = {
    "in-progress": "in_progress",
    "inprogress": "in_progress",
    "in progress": "in_progress",
    "to-do": "todo",
    "to do": "todo",
    "to_do": "todo",
    "back-log": "backlog",
    "back log": "backlog",
    "back_log": "backlog",
}

def normalize_status(status: str) -> str:
    """Normalize status input to valid status value."""
    status_lower = status.lower().strip()
    return STATUS_ALIASES.get(status_lower, status_lower)

def normalize_epic_id(epic_id: str) -> str:
    """Normalize epic ID to use zero-padded format (e.g., EPIC-1 -> EPIC-001)."""
    import re

    epic_id = epic_id.upper().strip()

    # Handle case where user provides just the number
    if epic_id.isdigit():
        return f"EPIC-{int(epic_id):03d}"

    # Handle EPIC-N format
    if epic_id.startswith("EPIC-"):
        match = re.match(r"^EPIC-(\d+)$", epic_id)
        if match:
            number = int(match.group(1))
            return f"EPIC-{number:03d}"

    # If it doesn't match expected format, return as-is
    return epic_id


def normalize_ticket_id(ticket_id: str, prefix: str = None) -> str:
    """Normalize ticket ID by adding project prefix if needed.
    
    Args:
        ticket_id: The ticket ID to normalize (e.g., "673" or "GCM-673")
        prefix: The project prefix to use. If None, must be provided in config.
        
    Returns:
        Normalized ticket ID (e.g., "GCM-673")
        
    Examples:
        normalize_ticket_id("673", "GCM") -> "GCM-673"
        normalize_ticket_id("GCM-673", "GCM") -> "GCM-673"
        normalize_ticket_id("ABC-123", "GCM") -> "ABC-123" (preserves existing prefix)
    """
    import re
    
    if not ticket_id:
        return ticket_id
        
    ticket_id = ticket_id.upper().strip()
    
    # If it's just a number, add the prefix
    if ticket_id.isdigit() and prefix:
        return f"{prefix}-{ticket_id}"
    
    # If it already has a prefix (contains hyphen), return as-is
    if "-" in ticket_id:
        return ticket_id
        
    # If no prefix provided and not a full ID, return as-is
    return ticket_id


def parse_ticket_id_pattern(pattern: str, prefix: str = None) -> str:
    """Parse ticket ID patterns, adding prefix to number-only patterns.
    
    Handles:
    - Single IDs: "673" -> "GCM-673"
    - Ranges: "670..673" -> "GCM-670..673"
    - Wildcards: "67*" -> "GCM-67*"
    - Mixed: "GCM-670..673" -> "GCM-670..673" (unchanged)
    
    Args:
        pattern: The pattern to parse
        prefix: The project prefix to use
        
    Returns:
        Normalized pattern with prefix added where needed
    """
    import re
    
    if not pattern or not prefix:
        return pattern
        
    pattern = pattern.strip()
    
    # Handle range patterns (e.g., "670..673")
    if ".." in pattern:
        parts = pattern.split("..", 1)
        if len(parts) == 2:
            # Check if the first part is just numbers
            if parts[0].isdigit():
                # It's a number-only range, add prefix
                return f"{prefix}-{parts[0]}..{parts[1]}"
            else:
                # Already has prefix or is complex, return as-is
                return pattern.upper()
    
    # Handle wildcard patterns (e.g., "67*")
    elif "*" in pattern:
        # Find the part before the wildcard
        base = pattern.split("*")[0]
        if base.isdigit():
            # It's a number-only wildcard, add prefix
            return f"{prefix}-{pattern}".upper()
        else:
            return pattern.upper()
    
    # Handle single IDs
    else:
        return normalize_ticket_id(pattern, prefix)

def get_project_prefix() -> str:
    """Get the current project's ticket ID prefix from config.
    
    Returns:
        The ticket ID prefix (e.g., "GCM")
        
    Raises:
        ValueError: If not in a Gira project or config is invalid
    """
    from pathlib import Path
    import json
    
    # Find project root
    current = Path.cwd()
    while current != current.parent:
        if (current / ".gira").is_dir():
            config_path = current / ".gira" / "config.json"
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                        return config.get("ticket_id_prefix", "")
                except (json.JSONDecodeError, KeyError):
                    raise ValueError("Invalid project configuration")
            break
        current = current.parent
    
    raise ValueError("Not in a Gira project")


# Valid ticket priorities
VALID_PRIORITIES = ["low", "medium", "high", "critical", "blocker"]

# Valid ticket types
VALID_TYPES = ["story", "task", "bug", "epic", "feature", "subtask"]

# Priority order for sorting
PRIORITY_ORDER = {"blocker": 0, "critical": 1, "high": 2, "medium": 3, "low": 4}

# Default reporter email
DEFAULT_REPORTER = "unknown@example.com"

# Story points constraints
MIN_STORY_POINTS = 0
MAX_STORY_POINTS = 100

# Ticket title display constraints
TITLE_MAX_LENGTH = 50
TITLE_TRUNCATE_LENGTH = 47

# Board display settings
SWIMLANE_WIDTH = 25
COMPACT_TITLE_LENGTH = 20
FULL_TITLE_LENGTH = 25

# Base directories for Gira project (board directories are created dynamically)
GIRA_BASE_DIRECTORIES = [
    ".gira",
    ".gira/board",
    ".gira/epics",
    ".gira/sprints",
    ".gira/archive",
    ".gira/comments",
]
