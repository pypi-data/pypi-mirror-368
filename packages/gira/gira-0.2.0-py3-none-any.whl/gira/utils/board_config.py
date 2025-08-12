"""Unified board configuration and status validation utilities for Gira.

This module provides a single source of truth for board configuration access
and status validation across CLI and MCP interfaces, eliminating duplication
and ensuring consistent behavior.
"""

import json
from pathlib import Path
from typing import List, Optional
from functools import lru_cache

from gira.models import Board, GiraConfig
from gira.utils.project import get_gira_root
from gira.constants import normalize_status


# Cache board configuration to avoid repeated file I/O
_board_cache: Optional[Board] = None
_cache_invalidated = False


def invalidate_cache() -> None:
    """Invalidate the board configuration cache.
    
    Call this when board configuration files are modified to ensure
    fresh data is loaded on next access.
    """
    global _board_cache, _cache_invalidated
    _board_cache = None
    _cache_invalidated = True
    # Clear the LRU cache as well
    get_board_configuration.cache_clear()


def get_board_configuration() -> Board:
    """Get board configuration with caching.
    
    Returns the board configuration from .gira/.board.json if it exists,
    otherwise returns a default board configuration.
    
    The result is cached to improve performance across multiple calls.
    
    Returns:
        Board: The board configuration object
        
    Raises:
        Exception: If there are critical errors loading the configuration
    """
    global _board_cache, _cache_invalidated
    
    # Return cached version if available and not invalidated
    if _board_cache is not None and not _cache_invalidated:
        return _board_cache
    
    # Load fresh configuration
    _board_cache = _load_board_config_uncached()
    _cache_invalidated = False
    return _board_cache


@lru_cache(maxsize=1)
def _load_board_config_uncached() -> Board:
    """Load board configuration without caching (used internally)."""
    try:
        board_path = get_gira_root() / ".gira" / ".board.json"
        if board_path.exists():
            return Board.from_json_file(str(board_path))
    except Exception:
        # If loading fails, fall back to default
        pass

    # Return default board configuration
    return Board.create_default()


def get_valid_statuses() -> List[str]:
    """Get list of valid statuses from board configuration.
    
    Returns statuses in priority order:
    1. Board configuration swimlanes
    2. Config file statuses (fallback)
    3. Default statuses (final fallback)
    
    Returns:
        List[str]: List of valid status names
    """
    try:
        # Get board configuration
        board = get_board_configuration()
        statuses = board.get_valid_statuses()

        # Always include backlog if not present (for backward compatibility)
        if "backlog" not in statuses:
            statuses = ["backlog"] + statuses

        return statuses
    except Exception:
        # Fallback to config file statuses
        pass

    # Try config file statuses as fallback
    try:
        from gira.utils.config import get_global_config
        config = get_global_config()
        if config and config.statuses:
            return config.statuses
    except Exception:
        pass

    # Final fallback to default statuses
    return ["backlog", "todo", "in_progress", "review", "done"]


def validate_status(status: str) -> bool:
    """Validate if a status is valid (case-insensitive).
    
    Args:
        status: The status to validate
        
    Returns:
        bool: True if the status is valid, False otherwise
    """
    try:
        board = get_board_configuration()
        normalized_status = normalize_status(status)
        
        # Special case for backlog - always valid even if not in board swimlanes
        if normalized_status == "backlog":
            return True
            
        return board.is_valid_status(normalized_status)
    except Exception:
        # Fallback: check against list of valid statuses
        normalized_status = normalize_status(status)
        valid_statuses = get_valid_statuses()
        return normalized_status in [normalize_status(s) for s in valid_statuses]


def normalize_status_safe(status: str) -> str:
    """Safely normalize a status string.
    
    Args:
        status: The status to normalize
        
    Returns:
        str: The normalized status (lowercase, stripped)
    """
    return normalize_status(status)


def get_status_validation_error(status: str) -> str:
    """Get a consistent validation error message for an invalid status.
    
    Args:
        status: The invalid status
        
    Returns:
        str: A formatted error message with valid statuses listed
    """
    valid_statuses = get_valid_statuses()
    return f"Invalid status '{status}'. Valid statuses: {', '.join(valid_statuses)}"


def is_status_transition_valid(from_status: str, to_status: str) -> bool:
    """Check if a status transition is valid according to board workflow rules.
    
    Args:
        from_status: The source status
        to_status: The target status
        
    Returns:
        bool: True if the transition is valid, False otherwise
    """
    try:
        board = get_board_configuration()
        normalized_from = normalize_status(from_status)
        normalized_to = normalize_status(to_status)
        
        # If no transitions defined, allow all transitions
        if not board.transitions:
            return True
            
        # Check if transition is explicitly allowed
        allowed_transitions = board.transitions.get(normalized_from, [])
        return normalized_to in [normalize_status(s) for s in allowed_transitions]
    except Exception:
        # If we can't load board config, allow all transitions
        return True


def get_valid_transitions_from_status(status: str) -> List[str]:
    """Get list of valid transitions from a given status.
    
    Args:
        status: The source status
        
    Returns:
        List[str]: List of valid target statuses
    """
    try:
        board = get_board_configuration()
        normalized_status = normalize_status(status)
        
        # If no transitions defined, return all statuses
        if not board.transitions:
            return get_valid_statuses()
            
        # Return defined transitions or empty list
        return board.transitions.get(normalized_status, [])
    except Exception:
        # Fallback: return all valid statuses
        return get_valid_statuses()


def get_board_config_file_path() -> Path:
    """Get the path to the board configuration file.
    
    Returns:
        Path: Path to .gira/.board.json
    """
    return get_gira_root() / ".gira" / ".board.json"


def board_config_exists() -> bool:
    """Check if a board configuration file exists.
    
    Returns:
        bool: True if .gira/.board.json exists
    """
    return get_board_config_file_path().exists()


# Backward compatibility functions
def load_board_config() -> Board:
    """Load board configuration (backward compatibility wrapper).
    
    This function is deprecated. Use get_board_configuration() instead.
    
    Returns:
        Board: The board configuration object
    """
    return get_board_configuration()