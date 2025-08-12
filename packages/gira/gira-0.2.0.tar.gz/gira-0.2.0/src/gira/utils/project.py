"""Project-related utilities for Gira.

This module provides backward compatibility functions that delegate to the
unified project management module. New code should use the unified functions
from gira.utils.project_management directly.
"""

from pathlib import Path
from typing import Optional

from gira.utils.project_management import (
    ensure_project_context,
    get_project_root,
)


def get_gira_root() -> Optional[Path]:
    """Find the .gira directory in current or parent directories.
    
    DEPRECATED: Use get_project_root() from gira.utils.project_management instead.
    This function is maintained for backward compatibility.
    """
    return get_project_root(use_mcp_config=False)  # CLI-only behavior


def ensure_gira_project() -> Path:
    """Ensure we're in a Gira project, exit if not.
    
    DEPRECATED: Use ensure_project_context() from gira.utils.project_management instead.
    This function is maintained for backward compatibility.
    """
    return ensure_project_context(use_mcp_config=False)  # CLI-only behavior
