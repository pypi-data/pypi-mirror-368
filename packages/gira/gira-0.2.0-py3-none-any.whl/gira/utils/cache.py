"""Simple in-memory cache for Gira operations."""

import time
from collections import OrderedDict
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Global cache storage
_cache: Dict[str, Tuple[Any, float]] = {}

# Git-specific cache storage with LRU eviction
_git_cache: "LRUCache" = None

# Cache TTL in seconds (5 minutes)
CACHE_TTL = 300

# Git cache settings
GIT_CACHE_TTL = 900  # 15 minutes for git operations
GIT_CACHE_MAX_SIZE = 1000  # Maximum number of cached git entries


def clear_cache() -> None:
    """Clear the entire cache."""
    global _cache
    _cache = {}


def cache_key(*args) -> str:
    """Generate a cache key from arguments."""
    return ":".join(str(arg) for arg in args)


def cached(ttl: int = CACHE_TTL):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = cache_key(*key_parts)

            # Check cache
            if key in _cache:
                value, timestamp = _cache[key]
                if time.time() - timestamp < ttl:
                    return value

            # Call function and cache result
            result = func(*args, **kwargs)
            _cache[key] = (result, time.time())
            return result

        # Add method to invalidate cache for this function
        wrapper.invalidate = lambda: invalidate_function_cache(func.__name__)
        return wrapper
    return decorator


def invalidate_function_cache(func_name: str) -> None:
    """Invalidate all cache entries for a specific function."""
    global _cache
    keys_to_remove = [k for k in _cache if k.startswith(f"{func_name}:")]
    for key in keys_to_remove:
        del _cache[key]


def invalidate_ticket_cache() -> None:
    """Invalidate all ticket-related caches."""
    invalidate_function_cache("load_all_tickets")
    invalidate_function_cache("load_tickets_by_status")
    invalidate_function_cache("find_ticket")


class LRUCache:
    """Least Recently Used cache with size limit."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str, ttl: int = GIT_CACHE_TTL) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return value
            else:
                # Expired, remove it
                del self.cache[key]

        self.misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp."""
        # Remove oldest item if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache and self.max_size > 0:
            self.cache.popitem(last=False)

        self.cache[key] = (value, time.time())
        self.cache.move_to_end(key)

    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching a pattern."""
        keys_to_remove = [k for k in self.cache if pattern in k]
        for key in keys_to_remove:
            del self.cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total_requests
        }


def get_git_cache() -> LRUCache:
    """Get or create the git cache instance."""
    global _git_cache

    # Always re-evaluate config if in a project, to support dynamic changes
    from gira.models.config import ProjectConfig
    from gira.utils.project import get_gira_root

    root = get_gira_root()
    if root:
        config_path = root / ".gira" / "config.json"
        if config_path.exists():
            try:
                config = ProjectConfig.from_json_file(str(config_path))
                if not config.commit_cache_enabled:
                    # Return a dummy cache if disabled
                    return LRUCache(max_size=0)
            except Exception:
                pass  # Fallback to default cache if config is invalid

    # If cache is not yet created or config has changed to enabled
    if _git_cache is None or _git_cache.max_size == 0:
        _git_cache = LRUCache(max_size=GIT_CACHE_MAX_SIZE)

    return _git_cache


def cached_git_operation(ttl: Optional[int] = None):
    """
    Decorator for caching git operations.
    
    Args:
        ttl: Time to live in seconds (defaults to GIT_CACHE_TTL)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if caching is enabled
            cache = get_git_cache()
            if cache.max_size == 0:
                return func(*args, **kwargs)

            # Generate cache key
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = cache_key(*key_parts)

            # Try to get from cache
            cached_value = cache.get(key, ttl or GIT_CACHE_TTL)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        # Add cache management methods
        wrapper.invalidate = lambda: get_git_cache().invalidate_pattern(func.__name__)
        wrapper.get_stats = lambda: get_git_cache().get_stats()
        return wrapper
    return decorator


def clear_git_cache() -> None:
    """Clear the git-specific cache."""
    cache = get_git_cache()
    cache.clear()


def invalidate_git_cache_for_ticket(ticket_id: str) -> None:
    """Invalidate git cache entries related to a specific ticket."""
    cache = get_git_cache()
    cache.invalidate_pattern(ticket_id)


def get_git_cache_stats() -> Dict[str, Any]:
    """Get statistics about the git cache."""
    cache = get_git_cache()
    return cache.get_stats()


# Blame-specific cache instance
_blame_cache: Optional[LRUCache] = None


def get_blame_cache() -> LRUCache:
    """Get or create the blame cache instance."""
    global _blame_cache

    from gira.models.config import ProjectConfig
    from gira.utils.project import get_gira_root

    root = get_gira_root()
    if root:
        config_path = root / ".gira" / "config.json"
        if config_path.exists():
            try:
                config = ProjectConfig.from_json_file(str(config_path))
                if not config.blame_config.cache_enabled:
                    # Return a dummy cache if disabled
                    return LRUCache(max_size=0)

                # Calculate max entries based on max size in MB
                # Estimate ~5KB per blame result entry
                max_entries = (config.blame_config.cache_max_size_mb * 1024 * 1024) // 5120

                if _blame_cache is None or _blame_cache.max_size != max_entries:
                    _blame_cache = LRUCache(max_size=max_entries)

                return _blame_cache
            except Exception:
                pass  # Fallback to default cache if config is invalid

    # Default cache if no config found
    if _blame_cache is None:
        _blame_cache = LRUCache(max_size=1000)

    return _blame_cache


def cached_blame_operation(no_cache: bool = False):
    """
    Decorator for caching blame operations.
    
    Args:
        no_cache: If True, bypass cache for this operation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract no_cache from kwargs if present
            override_no_cache = kwargs.pop('no_cache', no_cache)

            # Check if caching is enabled and not overridden
            cache = get_blame_cache()
            if cache.max_size == 0 or override_no_cache:
                return func(*args, **kwargs)

            # Generate cache key including git HEAD for invalidation
            from gira.utils.git_utils import get_current_head_sha

            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

            # Add git HEAD to key for automatic invalidation on new commits
            try:
                head_sha = get_current_head_sha()
                if head_sha:
                    key_parts.append(f"head={head_sha[:8]}")
            except Exception:
                pass  # If we can't get HEAD, proceed without it

            key = cache_key(*key_parts)

            # Try to get from cache
            from gira.models.config import ProjectConfig
            from gira.utils.project import get_gira_root

            ttl = CACHE_TTL  # Default TTL
            root = get_gira_root()
            if root:
                config_path = root / ".gira" / "config.json"
                if config_path.exists():
                    try:
                        config = ProjectConfig.from_json_file(str(config_path))
                        ttl = config.blame_config.cache_ttl_seconds
                    except Exception:
                        pass

            cached_value = cache.get(key, ttl)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        # Add cache management methods
        wrapper.invalidate = lambda: get_blame_cache().invalidate_pattern(func.__name__)
        wrapper.get_stats = lambda: get_blame_cache().get_stats()
        return wrapper
    return decorator


def clear_blame_cache() -> None:
    """Clear the blame-specific cache."""
    cache = get_blame_cache()
    cache.clear()


def get_blame_cache_stats() -> Dict[str, Any]:
    """Get statistics about the blame cache."""
    cache = get_blame_cache()
    return cache.get_stats()


class FileSystemCache:
    """Cache that monitors file system changes."""

    def __init__(self):
        self._mtimes: Dict[str, float] = {}

    def has_changed(self, path: Path) -> bool:
        """Check if a file or directory has changed since last check."""
        if not path.exists():
            return True

        current_mtime = path.stat().st_mtime
        cached_mtime = self._mtimes.get(str(path))

        if cached_mtime is None or current_mtime > cached_mtime:
            self._mtimes[str(path)] = current_mtime
            return True

        return False

    def mark_unchanged(self, path: Path) -> None:
        """Mark a path as unchanged."""
        if path.exists():
            self._mtimes[str(path)] = path.stat().st_mtime
