"""Utilities for handling confirmation prompts."""

import os
from typing import Optional
from pathlib import Path

from gira.utils.config import load_config, get_global_config
from gira.utils.project import get_gira_root


def should_skip_confirmation(force: bool = False, confirm: bool = False) -> bool:
    """Check if confirmation prompts should be skipped.
    
    Priority order (highest to lowest):
    1. Explicit --confirm flag (forces confirmations)
    2. Explicit --force flag (skips confirmations)
    3. Environment variable GIRA_SKIP_CONFIRMATIONS
    4. Project config skip_confirmations
    5. Global config skip_confirmations
    
    Args:
        force: Whether the --force flag was explicitly provided
        confirm: Whether the --confirm flag was explicitly provided (overrides skip settings)
        
    Returns:
        True if confirmations should be skipped, False otherwise
    """
    # Ensure parameters are booleans (in case they're passed as other types)
    force = bool(force) if force is not None else False
    confirm = bool(confirm) if confirm is not None else False
    
    # 1. Explicit --confirm flag forces confirmations (highest priority)
    if confirm:
        return False
    
    # 2. Explicit --force flag has next highest priority
    if force:
        return True
    
    # 3. Check environment variable
    env_skip = os.environ.get("GIRA_SKIP_CONFIRMATIONS", "").lower()
    if env_skip in ("1", "true", "yes", "on"):
        return True
    
    # 4. Check project config
    try:
        project_config = load_config()
        if project_config.get("skip_confirmations", False):
            return True
    except Exception:
        # Not in a project or config error - continue to global config
        pass
    
    # 5. Check global config
    try:
        global_config = get_global_config()
        if global_config and global_config.skip_confirmations:
            return True
    except Exception:
        # No global config or error reading it
        pass
    
    # Default: don't skip confirmations
    return False


def check_confirm_override(confirm: bool = False) -> bool:
    """Check if the --confirm flag was used to override skip settings.
    
    Args:
        confirm: Whether the --confirm flag was provided
        
    Returns:
        True if confirmations should be forced despite skip settings
    """
    return confirm