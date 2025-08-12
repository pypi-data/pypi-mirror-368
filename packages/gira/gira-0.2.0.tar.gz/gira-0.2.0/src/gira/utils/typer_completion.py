"""Typer autocompletion functions for Gira.

This module provides dynamic completion functions for ticket IDs, epic IDs, 
sprint IDs, and other values that can be used with Typer's autocompletion parameter.
"""

from typing import List, Tuple, Union

import typer

from gira.utils.project import get_gira_root


def complete_ticket_ids(incomplete: str) -> List[Tuple[str, str]]:
    """Complete ticket IDs from the current project.
    
    Supports both full IDs (GCM-123) and number-only completion (123).
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    try:
        from gira.utils.ticket_utils import load_all_tickets
        from gira.constants import get_project_prefix
        
        tickets = load_all_tickets(include_archived=False)  # Focus on active tickets
        results = []
        
        # Get project prefix for number-only completion
        try:
            prefix = get_project_prefix()
        except:
            prefix = None
        
        for ticket in tickets:
            # Standard full ID completion (GCM-123)
            if ticket.id.upper().startswith(incomplete.upper()):
                title_help = ticket.title[:50] + "..." if len(ticket.title) > 50 else ticket.title
                results.append((ticket.id, title_help))
            
            # Number-only completion (123 -> GCM-123)
            elif prefix and incomplete.isdigit() and len(incomplete) > 0:
                # Extract number from ticket ID (GCM-123 -> 123)
                if '-' in ticket.id:
                    ticket_number = ticket.id.split('-', 1)[1]
                    if ticket_number.startswith(incomplete):
                        title_help = f"{ticket.id}: {ticket.title[:40]}" + ("..." if len(ticket.title) > 40 else "")
                        results.append((ticket_number, title_help))
        
        return results[:20]  # Limit to 20 results for performance
    except Exception:
        # If we can't load tickets (not in project, etc.), return empty
        return []


def complete_epic_ids(incomplete: str) -> List[Tuple[str, str]]:
    """Complete epic IDs from the current project.
    
    Supports both full IDs (EPIC-001) and number-only completion (001).
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    try:
        root = get_gira_root()
        if not root:
            return []
            
        from gira.cli.commands.epic.list import load_all_epics
        epics = load_all_epics(root)
        results = []
        
        for epic in epics:
            # Standard full ID completion (EPIC-001)
            if epic.id.upper().startswith(incomplete.upper()):
                title_help = epic.title[:50] + "..." if len(epic.title) > 50 else epic.title
                results.append((epic.id, title_help))
            
            # Number-only completion (001 -> EPIC-001)
            elif incomplete.isdigit() and len(incomplete) > 0:
                # Extract number from epic ID (EPIC-001 -> 001)
                if '-' in epic.id:
                    epic_number = epic.id.split('-', 1)[1]
                    if epic_number.startswith(incomplete):
                        title_help = f"{epic.id}: {epic.title[:40]}" + ("..." if len(epic.title) > 40 else "")
                        results.append((epic_number, title_help))
        
        return results[:20]  # Limit to 20 results
    except Exception:
        return []


def complete_sprint_ids(incomplete: str) -> List[Tuple[str, str]]:
    """Complete sprint IDs from the current project.
    
    Supports both full IDs (SPRINT-2025-08-01) and partial completion.
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    try:
        root = get_gira_root()
        if not root:
            return []
            
        # Load sprints from the sprints directory
        sprints_dir = root / ".gira" / "sprints"
        if not sprints_dir.exists():
            return []
            
        sprint_files = list(sprints_dir.glob("*.json"))
        sprint_ids = [f.stem for f in sprint_files]
        results = []
        
        for sprint_id in sprint_ids:
            # Standard full ID completion (SPRINT-2025-08-01)
            if sprint_id.upper().startswith(incomplete.upper()):
                results.append((sprint_id, "Sprint"))
            
            # Date-only completion for sprints (20250801 -> SPRINT-2025-08-01)
            elif incomplete.isdigit() and len(incomplete) >= 4:
                # Extract date from sprint ID (SPRINT-2025-08-01 -> 20250801)
                if sprint_id.startswith("SPRINT-") and len(sprint_id) >= 17:
                    # Convert SPRINT-2025-08-01 to 20250801
                    date_part = sprint_id[7:].replace("-", "")  # Remove "SPRINT-" and dashes
                    if date_part.startswith(incomplete):
                        results.append((date_part, f"{sprint_id}: Sprint"))
        
        return results[:20]  # Limit to 20 results
    except Exception:
        return []


def complete_status_values(incomplete: str) -> List[Tuple[str, str]]:
    """Complete status values from project configuration.
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    try:
        from gira.utils.board_config import get_valid_statuses
        statuses = get_valid_statuses()
        return [
            (status, f"Status: {status}")
            for status in statuses
            if status.lower().startswith(incomplete.lower())
        ]
    except Exception:
        # Fallback to common statuses
        default_statuses = ["backlog", "todo", "in_progress", "review", "done"]
        return [
            (status, f"Status: {status}")
            for status in default_statuses
            if status.lower().startswith(incomplete.lower())
        ]


def complete_priority_values(incomplete: str) -> List[Tuple[str, str]]:
    """Complete priority values.
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    priorities = ["low", "medium", "high", "critical", "blocker"]
    return [
        (priority, f"Priority: {priority}")
        for priority in priorities
        if priority.lower().startswith(incomplete.lower())
    ]


def complete_type_values(incomplete: str) -> List[Tuple[str, str]]:
    """Complete ticket type values.
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    types = ["story", "task", "bug", "feature", "subtask", "epic"]
    return [
        (type_val, f"Type: {type_val}")
        for type_val in types
        if type_val.lower().startswith(incomplete.lower())
    ]


def complete_format_values(incomplete: str) -> List[Tuple[str, str]]:
    """Complete output format values.
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    formats = ["table", "json", "yaml", "csv", "tsv", "text", "ids"]
    return [
        (fmt, f"Output format: {fmt}")
        for fmt in formats
        if fmt.lower().startswith(incomplete.lower())
    ]


def complete_ticket_or_epic_ids(incomplete: str) -> List[Tuple[str, str]]:
    """Complete both ticket IDs and epic IDs for commands that accept either.
    
    Args:
        incomplete: The partial input string to complete
        
    Returns:
        List of (value, help_text) tuples for completion
    """
    try:
        # Get ticket completions
        ticket_completions = complete_ticket_ids(incomplete)
        
        # Get epic completions
        epic_completions = complete_epic_ids(incomplete)
        
        # Combine and limit to 20 total results
        combined = ticket_completions + epic_completions
        return combined[:20]
    except Exception:
        return []