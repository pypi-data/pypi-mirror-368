"""Configuration utilities for Gira."""

import json
import subprocess
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

from gira.constants import DEFAULT_REPORTER
from gira.models import Board, GiraConfig
from gira.utils.project import get_gira_root


def load_config() -> Dict[str, Any]:
    """Load the Gira project configuration file."""
    try:
        config_path = get_gira_root() / ".gira" / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save the Gira project configuration file."""
    try:
        config_path = get_gira_root() / ".gira" / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


def get_global_config() -> Optional[GiraConfig]:
    """Get the Gira configuration, checking project config first, then global."""
    # Try to get project config first
    try:
        project_root = get_gira_root()
        project_config_path = project_root / ".gira" / "config.json"
        if project_config_path.exists():
            return GiraConfig.from_json_file(str(project_config_path))
    except Exception:
        pass

    # Fall back to global config
    gira_config_path = Path.home() / ".gira" / "config.json"
    if gira_config_path.exists():
        try:
            return GiraConfig.from_json_file(str(gira_config_path))
        except Exception:
            pass
    return None


def get_default_reporter() -> str:
    """Get default reporter from git config or gira config."""
    # Try git config first
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            check=True
        )
        email = result.stdout.strip()
        if email:
            return email
    except Exception:
        pass

    # Try gira global config
    config = get_global_config()
    if config and config.default_user_email:
        return config.default_user_email

    # Default
    return DEFAULT_REPORTER


def load_board_config() -> Board:
    """Load board configuration from project root or use default.
    
    DEPRECATED: Use gira.utils.board_config.get_board_configuration() instead.
    This function is maintained for backward compatibility and will be removed
    in a future version.
    """
    warnings.warn(
        "load_board_config() is deprecated. Use gira.utils.board_config.get_board_configuration() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Delegate to new unified module
    from gira.utils.board_config import get_board_configuration
    return get_board_configuration()


def get_valid_statuses() -> List[str]:
    """Get list of valid statuses from board configuration or config file.
    
    DEPRECATED: Use gira.utils.board_config.get_valid_statuses() instead.
    This function is maintained for backward compatibility and will be removed
    in a future version.
    
    Returns statuses in priority order:
    1. Board configuration swimlanes
    2. Config file statuses
    3. Default statuses
    """
    warnings.warn(
        "get_valid_statuses() is deprecated. Use gira.utils.board_config.get_valid_statuses() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Delegate to new unified module
    from gira.utils.board_config import get_valid_statuses as new_get_valid_statuses
    return new_get_valid_statuses()
