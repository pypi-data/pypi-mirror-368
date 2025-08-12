"""Unified project management and configuration loading for Gira.

This module provides centralized project root detection and configuration loading
that works consistently across CLI and MCP interfaces, eliminating the duplication
of project detection logic scattered throughout the codebase.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Union

from gira.utils.console import console
from gira.utils.error_codes import ErrorCode, handle_error

logger = logging.getLogger(__name__)


class ProjectError(Exception):
    """Exception raised when project operations fail."""
    pass


class ConfigurationError(Exception):
    """Exception raised when configuration loading fails."""
    pass


def get_project_root(
    start_path: Optional[Path] = None,
    use_mcp_config: bool = True
) -> Optional[Path]:
    """Find the Gira project root directory.
    
    This function provides unified project root detection that works for both
    CLI and MCP contexts. It searches for .gira directories using multiple
    strategies:
    
    1. If use_mcp_config=True, try MCP configuration first
    2. Search from start_path (or current directory) upward
    3. Return None if no project found
    
    Args:
        start_path: Starting directory for search (defaults to current working directory)
        use_mcp_config: Whether to check MCP configuration for active project path
        
    Returns:
        Path to project root directory containing .gira folder, or None if not found
    """
    # Strategy 1: Try MCP configuration if enabled
    if use_mcp_config:
        try:
            from gira.mcp.config import get_config
            config = get_config()
            mcp_root = config.get_active_project_path()
            if mcp_root and (mcp_root / ".gira").exists():
                logger.debug(f"Found project root via MCP config: {mcp_root}")
                return mcp_root
        except (ImportError, Exception) as e:
            # MCP config not available or failed, continue with directory search
            logger.debug(f"MCP config unavailable, using directory search: {e}")
    
    # Strategy 2: Directory traversal search
    current = Path(start_path) if start_path else Path.cwd()
    
    while current != current.parent:
        gira_dir = current / ".gira"
        if gira_dir.exists() and gira_dir.is_dir():
            logger.debug(f"Found project root via directory search: {current}")
            return current
        current = current.parent
    
    logger.debug("No Gira project root found")
    return None


def ensure_project_context(
    start_path: Optional[Path] = None,
    use_mcp_config: bool = True
) -> Path:
    """Ensure we're in a Gira project context, exit if not.
    
    This function is the unified replacement for ensure_gira_project() that
    works for both CLI and MCP contexts.
    
    Args:
        start_path: Starting directory for search (defaults to current working directory)  
        use_mcp_config: Whether to check MCP configuration for active project path
        
    Returns:
        Path to project root directory
        
    Raises:
        SystemExit: If not in a Gira project (via handle_error)
    """
    root = get_project_root(start_path=start_path, use_mcp_config=use_mcp_config)
    if not root:
        current_dir = start_path or Path.cwd()
        handle_error(
            code=ErrorCode.NOT_IN_GIRA_PROJECT,
            message="Not in a Gira project. Run 'gira init' to create one.",
            details={"current_directory": str(current_dir)},
            console=console
        )
    return root


@lru_cache(maxsize=8)
def load_project_config(project_root: Union[str, Path]) -> Dict:
    """Load project configuration with caching and proper error handling.
    
    This function provides unified configuration loading that replaces ad-hoc
    json.load() calls scattered throughout the codebase. It includes proper
    error handling, default value resolution, and caching for performance.
    
    Args:
        project_root: Path to project root directory
        
    Returns:
        Dictionary containing project configuration
        
    Raises:
        ConfigurationError: If configuration cannot be loaded
    """
    if isinstance(project_root, str):
        project_root = Path(project_root)
    
    config_file = project_root / ".gira" / "config.json"
    
    if not config_file.exists():
        logger.warning(f"Configuration file not found: {config_file}")
        return _get_default_config()
    
    try:
        with config_file.open('r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.debug(f"Loaded configuration from: {config_file}")
        
        # Apply default values for missing keys
        default_config = _get_default_config()
        for key, default_value in default_config.items():
            if key not in config:
                config[key] = default_value
                
        return config
        
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid JSON in configuration file {config_file}: {e}"
        ) from e
    except (OSError, IOError) as e:
        raise ConfigurationError(
            f"Failed to read configuration file {config_file}: {e}"
        ) from e


def _get_default_config() -> Dict:
    """Get default configuration values.
    
    Returns:
        Dictionary with default configuration values
    """
    return {
        "version": "1.0",
        "ticket_prefix": "GCM",
        "default_reporter": "user@example.com",
        "default_assignee": "user@example.com",
        "board": {
            "statuses": ["todo", "in_progress", "in_review", "done"],
            "default_status": "todo"
        },
        "git": {
            "auto_git_mv": True,
            "auto_git_add": True
        },
        "storage": {
            "enabled": False
        },
        "hooks": {
            "enabled": True,
            "timeout": 30,
            "silent": False,
            "on_failure": "warn"
        }
    }


def clear_config_cache() -> None:
    """Clear the configuration cache.
    
    This is useful for testing or when configuration files are updated
    and need to be reloaded.
    """
    load_project_config.cache_clear()
    logger.debug("Configuration cache cleared")


# Backward compatibility functions for MCP
def get_mcp_gira_root() -> Optional[Path]:
    """Get Gira root directory using MCP server configuration.
    
    This is a backward compatibility function that delegates to the unified
    get_project_root() function. This function is deprecated and should be
    replaced with get_project_root() calls.
    
    Returns:
        Path to project root, or None if not found
    """
    logger.warning(
        "get_mcp_gira_root() is deprecated, use get_project_root() instead"
    )
    return get_project_root(use_mcp_config=True)