"""Prefix history management for ticket ID changes."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from gira.utils.console import console


class PrefixHistory:
    """Manages the history of ticket prefix changes."""

    def __init__(self, root: Path):
        self.root = root
        self.history_file = root / ".gira" / "prefix_history.json"
        self.history = self._load_history()

    def _load_history(self) -> Dict[str, List[Dict[str, str]]]:
        """Load prefix history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Failed to load prefix history: {e}")
                return {"prefixes": []}
        return {"prefixes": []}

    def _save_history(self) -> None:
        """Save prefix history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def add_prefix(self, prefix: str, timestamp: Optional[str] = None) -> None:
        """Add a new prefix to the history.
        
        Args:
            prefix: The ticket prefix (e.g., "GCM", "NEW")
            timestamp: ISO format timestamp, or None for current time
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Check if prefix already exists in recent history
        if self.history["prefixes"]:
            latest = self.history["prefixes"][-1]
            if latest["prefix"] == prefix:
                return  # Don't add duplicate

        self.history["prefixes"].append({
            "prefix": prefix,
            "timestamp": timestamp
        })
        self._save_history()

    def get_all_prefixes(self) -> List[str]:
        """Get all unique prefixes in chronological order."""
        seen = set()
        prefixes = []
        for entry in self.history["prefixes"]:
            prefix = entry["prefix"]
            if prefix not in seen:
                seen.add(prefix)
                prefixes.append(prefix)
        return prefixes

    def get_current_prefix(self) -> Optional[str]:
        """Get the most recent prefix."""
        if self.history["prefixes"]:
            return self.history["prefixes"][-1]["prefix"]
        return None

    def get_prefix_at_date(self, date: datetime) -> Optional[str]:
        """Get the prefix that was active at a specific date.
        
        Args:
            date: The date to check
            
        Returns:
            The prefix active at that date, or None if no history
        """
        active_prefix = None
        for entry in self.history["prefixes"]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date <= date:
                active_prefix = entry["prefix"]
            else:
                break
        return active_prefix

    def generate_regex_patterns(self) -> List[str]:
        """Generate regex patterns that match all historical prefixes.
        
        Returns:
            List of regex patterns for git commit scanning
        """
        prefixes = self.get_all_prefixes()
        if not prefixes:
            return []

        # Create a pattern that matches any of the prefixes
        prefix_group = "|".join(prefixes)

        patterns = [
            # feat(GCM-123): style in subject
            f"^\\w+\\(((?:{prefix_group})-\\d+)\\):",
            # Gira: GCM-123, NEW-456 in body
            f"Gira:\\s*((?:{prefix_group})-\\d+(?:,\\s*(?:{prefix_group})-\\d+)*)",
            # Ticket: GCM-123 in body
            f"Ticket:\\s*((?:{prefix_group})-\\d+(?:,\\s*(?:{prefix_group})-\\d+)*)",
            # Closes: GCM-123 in body
            f"Closes:\\s*((?:{prefix_group})-\\d+(?:,\\s*(?:{prefix_group})-\\d+)*)",
            # Fixes: GCM-123 in body
            f"Fixes:\\s*((?:{prefix_group})-\\d+(?:,\\s*(?:{prefix_group})-\\d+)*)",
            # Generic #GCM-123 references
            f"#((?:{prefix_group})-\\d+)",
            # General text references like "fixes NEW-456" or "addresses GCM-123"
            f"\\b((?:{prefix_group})-\\d+)\\b"
        ]

        return patterns

    def map_old_to_current(self, ticket_id: str) -> str:
        """Map an old ticket ID to the current prefix format.
        
        Args:
            ticket_id: A ticket ID with any historical prefix
            
        Returns:
            The ticket ID with the current prefix
        """
        current_prefix = self.get_current_prefix()
        if not current_prefix:
            return ticket_id

        # Extract the numeric part from the ticket ID
        for prefix in self.get_all_prefixes():
            if ticket_id.startswith(f"{prefix}-"):
                number = ticket_id[len(prefix) + 1:]
                return f"{current_prefix}-{number}"

        # If no match found, return as-is
        return ticket_id

    def is_valid_historical_id(self, ticket_id: str) -> bool:
        """Check if a ticket ID uses any historical prefix.
        
        Args:
            ticket_id: The ticket ID to check
            
        Returns:
            True if the ID uses a known historical prefix
        """
        for prefix in self.get_all_prefixes():
            if ticket_id.startswith(f"{prefix}-"):
                return True
        return False
