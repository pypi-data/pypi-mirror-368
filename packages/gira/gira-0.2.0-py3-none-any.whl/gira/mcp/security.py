"""Security module for Gira MCP server.

This module provides balanced security mechanisms that protect against common
security issues while maintaining usability for legitimate use cases.
"""

import logging
import re
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union

from pydantic import ValidationError as PydanticValidationError

from gira.mcp.config import get_config
from gira.mcp.schema import OperationResult
from gira.mcp.tools import MCPToolError, ValidationError, PermissionError, NotFoundError

# Configure audit logger
audit_logger = logging.getLogger('gira.mcp.audit')
logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class MCPSecurityManager:
    """Central security manager for MCP operations.
    
    Provides balanced security controls that prevent genuine security issues
    without hampering normal usage.
    """
    
    def __init__(self, config=None):
        """Initialize security manager with configuration."""
        self.config = config or get_config()
        self.working_directory = Path(self.config.working_directory).resolve()
        self.dry_run = self.config.dry_run
        
        # Optional restrictions (configurable)
        self.blocked_operations: Set[str] = set(
            getattr(self.config, 'blocked_operations', [])
        )
        
        # Audit logging
        self.audit_enabled = getattr(self.config, 'audit_enabled', True)
        self.verbose_logging = getattr(self.config, 'verbose_logging', False)
        
        # Security patterns
        self.ticket_id_pattern = re.compile(r'^[A-Z]+-\d+$', re.IGNORECASE)
        self.epic_id_pattern = re.compile(r'^EPIC-\d+$', re.IGNORECASE)
        
        # Input sanitization
        self.max_input_length = 10000
        self.max_list_length = 1000
        
        logger.debug("MCPSecurityManager initialized")
    
    def validate_ticket_id(self, ticket_id: str) -> str:
        """Validate and normalize ticket ID format.
        
        Args:
            ticket_id: Raw ticket ID input
            
        Returns:
            Normalized ticket ID
            
        Raises:
            ValidationError: If ticket ID format is invalid
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise ValidationError("Ticket ID must be a non-empty string")
        
        # Normalize ticket ID using configurable prefix
        from gira.mcp.tools import normalize_ticket_id
        normalized = normalize_ticket_id(ticket_id)
        
        # Validate format
        if not self.ticket_id_pattern.match(normalized):
            raise ValidationError(f"Invalid ticket ID format: {ticket_id}")
        
        return normalized
    
    def validate_epic_id(self, epic_id: str) -> str:
        """Validate and normalize epic ID format.
        
        Args:
            epic_id: Raw epic ID input
            
        Returns:
            Normalized epic ID
            
        Raises:
            ValidationError: If epic ID format is invalid
        """
        if not epic_id or not isinstance(epic_id, str):
            raise ValidationError("Epic ID must be a non-empty string")
        
        # Handle numeric IDs
        if epic_id.isdigit():
            normalized = f"EPIC-{epic_id.zfill(3)}"
        elif epic_id.upper().startswith('EPIC-'):
            normalized = epic_id.upper()
        else:
            normalized = f"EPIC-{epic_id}".upper()
        
        # Validate format
        if not self.epic_id_pattern.match(normalized):
            raise ValidationError(f"Invalid epic ID format: {epic_id}")
        
        return normalized
    
    def validate_path(self, path: Union[str, Path]) -> Path:
        """Ensure path is within project directory boundaries.
        
        Args:
            path: File or directory path to validate
            
        Returns:
            Resolved, safe path within project directory
            
        Raises:
            PermissionError: If path is outside project boundaries
        """
        try:
            path_obj = Path(path)
            
            # Convert relative paths to absolute within working directory
            if not path_obj.is_absolute():
                path_obj = self.working_directory / path_obj
            
            resolved_path = path_obj.resolve()
            
            # Check if path is within working directory
            try:
                resolved_path.relative_to(self.working_directory)
                return resolved_path
            except ValueError:
                raise PermissionError(
                    f"Path '{path}' is outside project directory boundaries"
                )
        
        except (OSError, ValueError) as e:
            raise PermissionError(f"Invalid path '{path}': {str(e)}")
    
    def sanitize_input(self, value: Any, field_name: str = "input") -> Any:
        """Sanitize user input to prevent injection attacks.
        
        Args:
            value: Input value to sanitize
            field_name: Name of the field being sanitized
            
        Returns:
            Sanitized input value
            
        Raises:
            ValidationError: If input is invalid or too large
        """
        if value is None:
            return None
        
        # String sanitization
        if isinstance(value, str):
            if len(value) > self.max_input_length:
                raise ValidationError(
                    f"{field_name} exceeds maximum length of {self.max_input_length}"
                )
            
            # Remove null bytes and normalize line endings
            sanitized = value.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
            
            # Basic pattern validation for suspicious content
            suspicious_patterns = [
                r'<script[^>]*>',  # Script tags
                r'javascript:',     # JavaScript URLs
                r'data:.*base64',   # Base64 data URLs
                r'\.\./',          # Directory traversal
                r'[;\|&`$]',       # Shell metacharacters
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, sanitized, re.IGNORECASE):
                    logger.warning(f"Suspicious pattern detected in {field_name}: {pattern}")
                    # Don't block automatically, just log for audit
            
            return sanitized
        
        # List sanitization
        elif isinstance(value, list):
            if len(value) > self.max_list_length:
                raise ValidationError(
                    f"{field_name} list exceeds maximum length of {self.max_list_length}"
                )
            
            return [self.sanitize_input(item, f"{field_name}[{i}]") 
                   for i, item in enumerate(value)]
        
        # Dict sanitization
        elif isinstance(value, dict):
            if len(value) > self.max_list_length:
                raise ValidationError(
                    f"{field_name} dict exceeds maximum size of {self.max_list_length}"
                )
            
            return {
                self.sanitize_input(k, f"{field_name}.key"): 
                self.sanitize_input(v, f"{field_name}.{k}")
                for k, v in value.items()
            }
        
        # Other types pass through
        return value
    
    def check_operation_allowed(self, operation: str) -> bool:
        """Check if operation is allowed by security policy.
        
        Args:
            operation: Operation name to check
            
        Returns:
            True if operation is allowed
            
        Raises:
            PermissionError: If operation is blocked
        """
        if operation in self.blocked_operations:
            raise PermissionError(
                f"Operation '{operation}' is blocked by security policy",
                operation=operation
            )
        
        return True
    
    def log_operation(self, operation: str, details: Dict[str, Any], success: bool = True):
        """Log MCP operation for audit trail.
        
        Args:
            operation: Operation name
            details: Operation details to log
            success: Whether operation succeeded
        """
        if not self.audit_enabled:
            return
        
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'success': success,
            'dry_run': self.dry_run,
            **details
        }
        
        # Filter sensitive information from logs
        filtered_details = self._filter_sensitive_data(log_entry)
        
        if success:
            audit_logger.info(f"MCP Operation: {operation}", extra=filtered_details)
        else:
            audit_logger.warning(f"MCP Operation Failed: {operation}", extra=filtered_details)
        
        if self.verbose_logging:
            logger.debug(f"Audit log: {filtered_details}")
    
    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive information from audit logs.
        
        Args:
            data: Raw audit data
            
        Returns:
            Filtered audit data
        """
        filtered = data.copy()
        
        # Remove or mask sensitive fields
        sensitive_fields = ['password', 'token', 'secret', 'key']
        
        for field in sensitive_fields:
            if field in filtered:
                filtered[field] = '[REDACTED]'
        
        # Truncate large content
        if 'content' in filtered and isinstance(filtered['content'], str):
            if len(filtered['content']) > 500:
                filtered['content'] = filtered['content'][:497] + '...'
        
        return filtered


# Global security manager instance
_security_manager: Optional[MCPSecurityManager] = None


def get_security_manager() -> MCPSecurityManager:
    """Get the global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = MCPSecurityManager()
    return _security_manager


def set_security_manager(manager: MCPSecurityManager) -> None:
    """Set the global security manager instance."""
    global _security_manager
    _security_manager = manager


def reset_security_manager() -> None:
    """Reset the global security manager (will be reloaded on next access)."""
    global _security_manager
    _security_manager = None


def secure_operation(operation_name: str, require_project: bool = True):
    """Decorator to add security checks to MCP operations.
    
    Args:
        operation_name: Name of the operation for logging
        require_project: Whether operation requires valid Gira project
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            security = get_security_manager()
            
            # Check if operation is allowed
            security.check_operation_allowed(operation_name)
            
            # Sanitize inputs
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                try:
                    sanitized_kwargs[key] = security.sanitize_input(value, key)
                except ValidationError as e:
                    logger.warning(f"Input validation failed for {key}: {e}")
                    raise e
            
            # Validate ticket/epic IDs if present
            if 'ticket_id' in sanitized_kwargs and sanitized_kwargs['ticket_id']:
                sanitized_kwargs['ticket_id'] = security.validate_ticket_id(
                    sanitized_kwargs['ticket_id']
                )
            
            if 'epic_id' in sanitized_kwargs and sanitized_kwargs['epic_id']:
                sanitized_kwargs['epic_id'] = security.validate_epic_id(
                    sanitized_kwargs['epic_id']
                )
            
            # Validate paths if present
            for key in ['path', 'file_path', 'directory']:
                if key in sanitized_kwargs and sanitized_kwargs[key]:
                    sanitized_kwargs[key] = security.validate_path(
                        sanitized_kwargs[key]
                    )
            
            # Log operation start
            log_details = {
                'function': func.__name__,
                'operation': operation_name,
                'args_count': len(args),
                'kwargs_keys': list(sanitized_kwargs.keys())
            }
            
            if security.verbose_logging:
                log_details['kwargs_summary'] = {
                    k: str(v)[:100] + '...' if len(str(v)) > 100 else str(v)
                    for k, v in sanitized_kwargs.items()
                }
            
            security.log_operation(f"{operation_name}.start", log_details)
            
            # Execute with error handling
            try:
                result = func(*args, **sanitized_kwargs)
                
                # Log success
                success_details = log_details.copy()
                success_details['success'] = True
                if hasattr(result, 'success'):
                    success_details['result_success'] = result.success
                
                security.log_operation(f"{operation_name}.success", success_details)
                
                return result
                
            except Exception as e:
                # Log error
                error_details = log_details.copy()
                error_details['success'] = False
                error_details['error_type'] = type(e).__name__
                error_details['error_message'] = str(e)
                
                security.log_operation(f"{operation_name}.error", error_details, success=False)
                
                raise
        
        return wrapper
    return decorator


def validate_inputs(**validators):
    """Decorator to validate function inputs with custom validators.
    
    Args:
        **validators: Mapping of parameter names to validator functions
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Apply validators to kwargs
            for param, validator in validators.items():
                if param in kwargs and kwargs[param] is not None:
                    try:
                        kwargs[param] = validator(kwargs[param])
                    except (ValueError, TypeError, PydanticValidationError) as e:
                        raise ValidationError(f"Invalid {param}: {str(e)}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_gira_project(func: F) -> F:
    """Decorator to ensure operation is within a valid Gira project.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function that validates Gira project presence
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        security = get_security_manager()
        
        # Check for .gira directory in working directory
        gira_dir = security.working_directory / '.gira'
        
        if not gira_dir.exists() or not gira_dir.is_dir():
            raise PermissionError(
                f"No Gira project found in {security.working_directory}. "
                "Operations must be performed within a valid Gira project."
            )
        
        return func(*args, **kwargs)
    
    return wrapper


def rate_limit(max_calls: int = 100, window_seconds: int = 60):
    """Simple rate limiting decorator.
    
    Args:
        max_calls: Maximum calls allowed in window
        window_seconds: Time window in seconds
    """
    call_history: List[float] = []
    
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside window
            cutoff = now - window_seconds
            call_history[:] = [call_time for call_time in call_history if call_time > cutoff]
            
            # Check rate limit
            if len(call_history) >= max_calls:
                raise PermissionError(
                    f"Rate limit exceeded: {max_calls} calls per {window_seconds} seconds"
                )
            
            # Record this call
            call_history.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator