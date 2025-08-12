"""Persistent file-based cache for metrics git history operations."""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional

from gira.utils.project import get_gira_root


class MetricsGitCache:
    """File-based cache for git history extraction in metrics."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the metrics cache.
        
        Args:
            cache_dir: Directory to store cache files. If None, uses .gira/cache/metrics/
        """
        if cache_dir is None:
            root = get_gira_root()
            if root:
                cache_dir = root / ".gira" / "cache" / "metrics"
            else:
                # Use temp directory if not in a gira project (for tests)
                import tempfile
                cache_dir = Path(tempfile.gettempdir()) / ".gira_cache" / "metrics"

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for organization
        self.history_dir = self.cache_dir / "history"
        self.history_dir.mkdir(exist_ok=True)

        self.meta_file = self.cache_dir / "cache_meta.json"
        self._load_metadata()
        # Ensure meta file exists
        if not self.meta_file.exists():
            self._save_metadata()

    def _load_metadata(self):
        """Load cache metadata."""
        if self.meta_file.exists():
            try:
                with open(self.meta_file) as f:
                    self.metadata = json.load(f)
            except Exception:
                self.metadata = {}
        else:
            self.metadata = {}

    def _save_metadata(self):
        """Save cache metadata."""
        with open(self.meta_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _get_cache_key(self, ticket_id: str) -> str:
        """Generate a cache key for a ticket."""
        return hashlib.md5(ticket_id.encode()).hexdigest()

    def _get_last_commit_for_ticket(self, ticket_id: str) -> Optional[str]:
        """Get the last commit that affected a ticket file."""
        try:
            # Get the last commit that touched this ticket
            cmd = [
                "git", "log", "-1", "--format=%H", "--", f"**/{ticket_id}.json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_history(self, ticket_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached history for a ticket.
        
        Returns None if cache miss or stale.
        """
        cache_key = self._get_cache_key(ticket_id)
        cache_file = self.history_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        # Check if cache is still valid by comparing last commit
        current_commit = self._get_last_commit_for_ticket(ticket_id)
        if not current_commit:
            return None

        try:
            with open(cache_file) as f:
                cached_data = json.load(f)

            # Validate cache
            if cached_data.get("last_commit") != current_commit:
                # Cache is stale
                return None

            # Get history and convert timestamp strings back to datetime objects
            history = cached_data.get("history", [])
            for entry in history:
                if 'timestamp' in entry and isinstance(entry['timestamp'], str):
                    # Parse ISO format timestamp
                    entry['timestamp'] = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))

            return history

        except Exception:
            # Cache file corrupted or invalid
            return None

    def set_history(self, ticket_id: str, history: List[Dict[str, Any]]):
        """Cache history for a ticket."""
        cache_key = self._get_cache_key(ticket_id)
        cache_file = self.history_dir / f"{cache_key}.json"

        # Get current commit for validation
        current_commit = self._get_last_commit_for_ticket(ticket_id)

        cache_data = {
            "ticket_id": ticket_id,
            "last_commit": current_commit,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "history": history
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)

            # Update metadata
            self.metadata[ticket_id] = {
                "cache_key": cache_key,
                "cached_at": cache_data["cached_at"],
                "last_commit": current_commit
            }
            self._save_metadata()

        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Failed to cache history for {ticket_id}: {e}")

    def clear(self):
        """Clear all cached data."""
        # Remove all cache files
        for cache_file in self.history_dir.glob("*.json"):
            cache_file.unlink()

        # Clear metadata
        self.metadata = {}
        self._save_metadata()

    def clear_ticket(self, ticket_id: str):
        """Clear cache for a specific ticket."""
        cache_key = self._get_cache_key(ticket_id)
        cache_file = self.history_dir / f"{cache_key}.json"

        if cache_file.exists():
            cache_file.unlink()

        # Remove from metadata
        self.metadata.pop(ticket_id, None)
        self._save_metadata()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.history_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "cached_tickets": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(self.cache_dir),
            "oldest_cache": min(
                (f.stat().st_mtime for f in cache_files),
                default=None
            ),
            "newest_cache": max(
                (f.stat().st_mtime for f in cache_files),
                default=None
            )
        }


# Global cache instance
_metrics_cache: Optional[MetricsGitCache] = None


def get_metrics_cache() -> MetricsGitCache:
    """Get or create the global metrics cache instance."""
    global _metrics_cache
    if _metrics_cache is None:
        _metrics_cache = MetricsGitCache()
    return _metrics_cache


def cached_git_history(no_cache: bool = False):
    """Decorator to cache git history extraction.
    
    Args:
        no_cache: If True, bypass cache for this operation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract ticket_id from args (first argument)
            if not args:
                return func(*args, **kwargs)

            ticket_id = args[0]

            # Check if caching is disabled
            override_no_cache = kwargs.get('no_cache', no_cache)
            if override_no_cache:
                return func(*args, **kwargs)

            # Try to get from cache
            cache = get_metrics_cache()
            cached_history = cache.get_history(ticket_id)

            if cached_history is not None:
                return cached_history

            # Call function and cache result
            result = func(*args, **kwargs)

            # Only cache if we got a result
            if result:
                cache.set_history(ticket_id, result)

            return result

        return wrapper
    return decorator


def clear_metrics_cache():
    """Clear the metrics cache."""
    cache = get_metrics_cache()
    cache.clear()


def clear_metrics_cache_for_ticket(ticket_id: str):
    """Clear cache for a specific ticket."""
    cache = get_metrics_cache()
    cache.clear_ticket(ticket_id)
