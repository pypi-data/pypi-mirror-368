"""Configuration utilities for Gira."""

import json
from pathlib import Path
from typing import Any, Dict

from gira.utils.console import console

# Default configuration values
DEFAULT_CONFIG = {
    "user.name": "",
    "user.email": "",
    "ticket.default_type": "feature",
    "ticket.default_priority": "medium",
    "ticket.default_status": "todo",
    "sprint.duration_days": 14,
    "board.columns": ["backlog", "todo", "in_progress", "review", "done"],
    "display.truncate_title": 50,
    "display.date_format": "%Y-%m-%d",
    "render_markdown": True,
    "archive.auto_archive_after_days": None,
    "archive.performance_threshold": 1000,
    "archive.suggest_done_after_days": 30,
    "archive.suggest_stale_after_days": 90,
    "git.auto_stage_moves": True,
    "git.auto_stage_archives": True,
    "git.auto_stage_deletes": True,
    "storage.enabled": False,
    "storage.provider": None,
    "storage.bucket": None,
    "storage.region": None,
    "storage.base_path": None,
    "storage.max_file_size_mb": 100,
    "storage.credential_source": "environment",
    "storage.retention_days": None,
    "output.json_highlighting": False,
    "output.json_theme": "monokai",
    "skip_confirmations": False,
    "project.name": "",
    "project.ticket_prefix": "",
}


def get_config_file(root: Path) -> Path:
    """Get the path to the configuration file."""
    return root / ".gira" / "config.json"


def load_config(root: Path) -> Dict[str, Any]:
    """Load configuration from file or create default."""
    config_file = get_config_file(root)

    if config_file.exists():
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to load config: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        # Create default config
        save_config(root, DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()


def save_config(root: Path, config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_file = get_config_file(root)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
