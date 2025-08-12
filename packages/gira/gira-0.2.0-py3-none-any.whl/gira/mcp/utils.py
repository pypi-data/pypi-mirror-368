"""Utility functions for MCP server operations."""

import functools
import logging
import signal
import threading
from typing import Any, Dict, List, Optional, Set
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class RecursionError(Exception):
    """Raised when recursion depth is exceeded."""
    pass


class TimeoutError(Exception):
    """Raised when operation times out."""
    pass


class CircularReferenceDetector:
    """Utility to detect and prevent circular references in serialization."""
    
    def __init__(self):
        self._visited: Set[id] = set()
        self._path: List[str] = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._visited.clear()
        self._path.clear()
    
    def check_object(self, obj: Any, name: str = "object") -> bool:
        """Check if object creates circular reference."""
        obj_id = id(obj)
        if obj_id in self._visited:
            logger.warning(f"Circular reference detected: {' -> '.join(self._path)} -> {name}")
            return True
        return False
    
    def visit_object(self, obj: Any, name: str = "object"):
        """Mark object as visited in current path."""
        self._visited.add(id(obj))
        self._path.append(name)
    
    def unvisit_object(self, obj: Any):
        """Remove object from current path."""
        self._visited.discard(id(obj))
        if self._path:
            self._path.pop()


def recursion_guard(max_depth: int = 10):
    """Decorator to prevent recursion beyond specified depth."""
    def decorator(func):
        # Use thread-local storage to track recursion depth per thread
        local_data = threading.local()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize depth counter for this thread if not exists
            if not hasattr(local_data, 'depth'):
                local_data.depth = 0
            
            # Check recursion depth
            if local_data.depth >= max_depth:
                error_msg = f"Maximum recursion depth ({max_depth}) exceeded in {func.__name__}"
                logger.error(error_msg)
                raise RecursionError(error_msg)
            
            # Increment depth and call function
            local_data.depth += 1
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                local_data.depth -= 1
        
        return wrapper
    return decorator


def with_timeout(seconds: int):
    """Decorator to add timeout protection to operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # For non-Unix systems, we'll implement a basic timeout
            import time
            start_time = time.time()
            
            def timeout_handler():
                if time.time() - start_time > seconds:
                    raise TimeoutError(f"Operation {func.__name__} timed out after {seconds} seconds")
            
            try:
                result = func(*args, **kwargs)
                timeout_handler()  # Check if we exceeded time during execution
                return result
            except TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds} seconds")
                raise
        
        return wrapper
    return decorator


def safe_model_dump(model: Any, max_depth: int = 5, exclude_circular: bool = True) -> Dict[str, Any]:
    """Safe model serialization with depth limiting and circular reference detection."""
    
    def _serialize_with_depth(obj: Any, current_depth: int = 0) -> Any:
        # Check depth limit
        if current_depth >= max_depth:
            if hasattr(obj, 'id'):
                return {"id": getattr(obj, 'id'), "_truncated": True}
            return {"_truncated": f"Max depth {max_depth} reached"}
        
        # Handle None
        if obj is None:
            return None
        
        # Handle basic types
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        # Handle lists
        if isinstance(obj, list):
            return [_serialize_with_depth(item, current_depth + 1) for item in obj]
        
        # Handle dictionaries
        if isinstance(obj, dict):
            return {
                key: _serialize_with_depth(value, current_depth + 1)
                for key, value in obj.items()
            }
        
        # Handle Pydantic models
        if hasattr(obj, 'model_dump'):
            try:
                # Get the raw dict representation
                data = obj.model_dump()
                
                # Recursively serialize nested objects
                result = {}
                for key, value in data.items():
                    # Skip circular references in known problematic fields
                    if exclude_circular and key in ['tickets', 'comments'] and current_depth > 2:
                        if isinstance(value, list) and len(value) > 0:
                            result[key] = [{"id": item.get('id', 'unknown'), "_truncated": True} if isinstance(item, dict) else item for item in value[:3]]
                            if len(value) > 3:
                                result[key].append({"_more": len(value) - 3})
                        else:
                            result[key] = value
                    else:
                        result[key] = _serialize_with_depth(value, current_depth + 1)
                
                return result
            except Exception as e:
                logger.warning(f"Error serializing model {type(obj).__name__}: {e}")
                return {"_error": f"Serialization failed: {str(e)}"}
        
        # Handle other objects by converting to string
        try:
            return str(obj)
        except Exception:
            return f"<{type(obj).__name__} object>"
    
    try:
        return _serialize_with_depth(model)
    except Exception as e:
        logger.error(f"Failed to safely serialize object: {e}")
        return {"_error": f"Serialization completely failed: {str(e)}"}


@contextmanager
def performance_monitor(operation_name: str, warn_threshold_ms: int = 1000):
    """Context manager to monitor operation performance."""
    import time
    start_time = time.time()
    
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        if duration_ms > warn_threshold_ms:
            logger.warning(f"Operation '{operation_name}' took {duration_ms:.1f}ms (threshold: {warn_threshold_ms}ms)")
        else:
            logger.debug(f"Operation '{operation_name}' completed in {duration_ms:.1f}ms")


def create_lightweight_summary(obj: Any, fields: List[str]) -> Dict[str, Any]:
    """Create lightweight summary of an object with only specified fields."""
    summary = {}
    for field in fields:
        if hasattr(obj, field):
            value = getattr(obj, field)
            # Convert datetime objects to ISO strings
            if hasattr(value, 'isoformat'):
                summary[field] = value.isoformat()
            else:
                summary[field] = value
        else:
            summary[field] = None
    return summary