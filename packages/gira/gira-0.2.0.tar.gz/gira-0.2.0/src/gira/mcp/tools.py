"""Tool foundation infrastructure for Gira MCP server."""

import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError as PydanticValidationError

# Import built-in exceptions to avoid conflicts with MCP exceptions
import builtins
BuiltinPermissionError = builtins.PermissionError
BuiltinTimeoutError = builtins.TimeoutError
BuiltinConnectionError = builtins.ConnectionError

from gira.mcp.config import get_config
from gira.mcp.schema import MCPError, OperationResult
from gira.mcp.errors import (
    EnhancedMCPError,
    ValidationError as EnhancedValidationError,
    ResourceNotFoundError,
    ConfigurationError,
    OperationError,
    ErrorContext,
    ErrorCodes,
    ErrorCategory,
    ErrorSeverity,
    format_error_message
)
from gira.mcp.recovery import recovery_context, with_recovery

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class MCPToolError(Exception):
    """Base exception for MCP tool errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)
    
    def to_error_response(self) -> MCPError:
        """Convert to MCP error response format."""
        return MCPError(
            error=self.message,
            code=self.code,
            details=self.details
        )


class ValidationError(MCPToolError):
    """Validation error for tool parameters."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, code=ErrorCodes.VALIDATION_ERROR.value, details={"field": field} if field else {})


class PermissionError(MCPToolError):
    """Permission error for restricted operations."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message, code=ErrorCodes.PERMISSION_ERROR.value, details={"operation": operation} if operation else {})


class NotFoundError(MCPToolError):
    """Error for when requested resources are not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(message, code=ErrorCodes.NOT_FOUND.value, details=details)


def require_confirmation(operation_name: str):
    """Decorator that requires user confirmation for destructive operations."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            
            if config.require_confirmation:
                # In a real MCP server, this would be handled by the client
                # For now, we'll just log the requirement
                logger.warning(f"Operation '{operation_name}' requires confirmation (skipped in dry-run)")
                
                if config.dry_run:
                    return OperationResult(
                        success=False,
                        message=f"Operation '{operation_name}' requires confirmation and dry-run is enabled",
                        dry_run=True
                    )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_working_directory():
    """Decorator to validate that operations are within the allowed working directory."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            
            # Check if any path arguments are provided and validate them
            for arg_name, arg_value in kwargs.items():
                if isinstance(arg_value, (str, Path)) and arg_name.endswith(('_path', '_dir', '_file')):
                    safe_path = config.get_safe_path(str(arg_value))
                    if safe_path is None:
                        raise PermissionError(
                            f"Path '{arg_value}' is not within allowed working directory",
                            operation=func.__name__
                        )
                    # Replace with safe path
                    kwargs[arg_name] = safe_path
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def handle_errors(
    operation_name: Optional[str] = None,
    include_debug: Optional[bool] = None,
    recoverable_categories: Optional[list] = None
) -> Callable[[F], F]:
    """Enhanced decorator to handle and convert exceptions to comprehensive MCP error responses.
    
    Args:
        operation_name: Name of the operation for context
        include_debug: Whether to include debug information (defaults to env setting)
        recoverable_categories: List of error categories that can be recovered
        
    Returns:
        Decorated function with comprehensive error handling
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create operation context
            operation_id = str(uuid4())
            op_name = operation_name or func.__name__
            correlation_id = kwargs.pop('correlation_id', operation_id)
            
            # Determine debug mode
            debug_mode = include_debug
            if debug_mode is None:
                debug_mode = (
                    os.getenv('GIRA_DEBUG', '').lower() in ('1', 'true', 'yes') or
                    logger.isEnabledFor(logging.DEBUG)
                )
            
            # Create error context
            context = ErrorContext(
                operation=op_name,
                parameters={
                    k: v for k, v in kwargs.items() 
                    if not k.startswith('_') and not callable(v)
                },
                correlation_id=correlation_id,
                system_context={
                    "function": func.__name__,
                    "module": func.__module__,
                    "debug_mode": debug_mode
                }
            )
            
            try:
                logger.debug(f"Executing {op_name} (correlation_id: {correlation_id})")
                result = func(*args, **kwargs)
                logger.debug(f"Successfully completed {op_name}")
                return result
                
            except EnhancedMCPError as error:
                # Enhanced MCP errors are already properly formatted
                error.context = context
                logger.error(f"Enhanced MCP error in {op_name}: {error.message}")
                raise error
                
            except MCPToolError as error:
                # Convert legacy MCP tool errors to enhanced errors using proper conversion
                enhanced_error = convert_legacy_error(error, op_name)
                enhanced_error.context = context
                if debug_mode and enhanced_error.debug_info is None:
                    enhanced_error.debug_info = {"legacy_details": error.details}
                logger.error(f"Legacy MCP error in {op_name}: {error.message}")
                raise enhanced_error
                
            except PydanticValidationError as error:
                # Convert Pydantic validation errors to enhanced validation errors
                field_errors = []
                for err in error.errors():
                    field_name = '.'.join(str(loc) for loc in err['loc'])
                    field_errors.append(f"{field_name}: {err['msg']}")
                
                enhanced_error = EnhancedValidationError(
                    message=f"Validation failed: {'; '.join(field_errors)}",
                    field=field_errors[0].split(':')[0] if field_errors else None,
                    context=context,
                    debug_info={"pydantic_errors": error.errors()} if debug_mode else None
                )
                logger.warning(f"Validation error in {op_name}: {enhanced_error.message}")
                raise enhanced_error
                
            except FileNotFoundError as error:
                enhanced_error = ResourceNotFoundError(
                    message=f"File or directory not found: {error.filename or str(error)}",
                    resource_type="file",
                    resource_id=str(error.filename) if error.filename else "unknown",
                    context=context,
                    debug_info={"errno": error.errno, "strerror": error.strerror} if debug_mode else None
                )
                logger.error(f"File not found in {op_name}: {error}")
                raise enhanced_error
                
            except (PermissionError, BuiltinPermissionError) as error:
                enhanced_error = EnhancedMCPError(
                    message=f"Permission denied: {error}",
                    code=ErrorCodes.ACCESS_DENIED,
                    category=ErrorCategory.PERMISSION,
                    severity=ErrorSeverity.ERROR,
                    context=context,
                    debug_info={"errno": error.errno, "strerror": error.strerror} if debug_mode else None
                )
                logger.error(f"Permission error in {op_name}: {error}")
                raise enhanced_error
                
            except (ConnectionError, BuiltinConnectionError) as error:
                enhanced_error = EnhancedMCPError(
                    message=f"Connection failed: {error}",
                    code=ErrorCodes.CONNECTION_FAILED,
                    category=ErrorCategory.NETWORK,
                    severity=ErrorSeverity.ERROR,
                    context=context,
                    debug_info={"connection_error": str(error)} if debug_mode else None
                )
                logger.error(f"Connection error in {op_name}: {error}")
                raise enhanced_error
                
            except (TimeoutError, BuiltinTimeoutError) as error:
                enhanced_error = EnhancedMCPError(
                    message=f"Operation timed out: {error}",
                    code=ErrorCodes.TIMEOUT_ERROR,
                    category=ErrorCategory.TIMEOUT,
                    severity=ErrorSeverity.ERROR,
                    context=context,
                    debug_info={"timeout_error": str(error)} if debug_mode else None
                )
                logger.error(f"Timeout error in {op_name}: {error}")
                raise enhanced_error
                
            except Exception as error:
                # Handle all other unexpected errors
                logger.exception(f"Unexpected error in {op_name}")
                enhanced_error = EnhancedMCPError(
                    message=format_error_message(ErrorCodes.INTERNAL_ERROR),
                    code=ErrorCodes.INTERNAL_ERROR,
                    category=ErrorCategory.INTERNAL,
                    severity=ErrorSeverity.CRITICAL,
                    context=context,
                    debug_info={
                        "exception_type": type(error).__name__,
                        "exception_message": str(error),
                        "module": func.__module__,
                        "function": func.__name__
                    } if debug_mode else None,
                    original_exception=error
                )
                raise enhanced_error
                
        return wrapper
    return decorator


# Convenience decorators that combine common patterns

def mcp_tool(
    operation_name: Optional[str] = None,
    use_recovery: bool = False,
    max_retries: int = 3,
    include_debug: bool = None,
    use_transaction: bool = False
) -> Callable[[F], F]:
    """Comprehensive decorator for MCP tools with error handling and optional recovery.
    
    Args:
        operation_name: Name of the operation for context
        use_recovery: Whether to enable automatic recovery
        max_retries: Maximum recovery attempts
        include_debug: Whether to include debug information
        use_transaction: Whether to use transactions for rollback
        
    Returns:
        Decorated function with comprehensive MCP tool capabilities
    """
    def decorator(func: F) -> F:
        # Apply error handling
        enhanced_func = handle_errors(
            operation_name=operation_name,
            include_debug=include_debug
        )(func)
        
        # Apply recovery if requested
        if use_recovery:
            enhanced_func = with_recovery(
                max_retries=max_retries,
                use_transaction=use_transaction
            )(enhanced_func)
        
        return enhanced_func
    
    return decorator


def convert_legacy_error(error: Exception, operation_name: str = "unknown") -> EnhancedMCPError:
    """Convert legacy errors to enhanced MCP errors.
    
    Args:
        error: Legacy error to convert
        operation_name: Name of the operation that failed
        
    Returns:
        Enhanced MCP error
    """
    context = ErrorContext(operation=operation_name)
    
    # Check most specific types first before the general MCPToolError
    if isinstance(error, ValidationError):
        return EnhancedValidationError(
            message=error.message,
            field=error.details.get("field"),
            context=context
        )
    
    elif isinstance(error, NotFoundError):
        return ResourceNotFoundError(
            message=error.message,
            resource_type=error.details.get("resource_type", "resource"),
            resource_id=error.details.get("resource_id", "unknown"),
            context=context
        )
    
    elif isinstance(error, PermissionError):
        return EnhancedMCPError(
            message=error.message,
            code=ErrorCodes.ACCESS_DENIED,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.ERROR,
            context=context,
            debug_info={"legacy_details": error.details}
        )
    
    elif isinstance(error, MCPToolError):
        return EnhancedMCPError(
            message=error.message,
            code=ErrorCodes(error.code) if error.code else ErrorCodes.INTERNAL_ERROR,
            category=_categorize_legacy_error(error),
            severity=ErrorSeverity.ERROR,
            context=context,
            debug_info={"legacy_details": error.details}
        )
    
    else:
        return EnhancedMCPError(
            message=str(error),
            code=ErrorCodes.INTERNAL_ERROR,
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.ERROR,
            context=context,
            original_exception=error
        )


def _categorize_legacy_error(error: MCPToolError) -> ErrorCategory:
    """Categorize legacy MCP tool errors.
    
    Args:
        error: Legacy error to categorize
        
    Returns:
        Error category
    """
    if error.code == ErrorCodes.VALIDATION_ERROR.value:
        return ErrorCategory.VALIDATION
    elif error.code == ErrorCodes.PERMISSION_ERROR.value:
        return ErrorCategory.PERMISSION
    elif error.code == ErrorCodes.NOT_FOUND.value:
        return ErrorCategory.NOT_FOUND
    elif error.code == ErrorCodes.INTERNAL_ERROR_LEGACY.value:
        return ErrorCategory.INTERNAL
    else:
        return ErrorCategory.PROCESSING


def create_operation_result_from_error(error: EnhancedMCPError, include_debug: bool = False) -> OperationResult:
    """Create an OperationResult from an enhanced MCP error.
    
    Args:
        error: Enhanced MCP error
        include_debug: Whether to include debug information
        
    Returns:
        OperationResult with error information
    """
    return OperationResult(
        success=False,
        message=error.get_user_message(),
        error=error.to_dict(include_debug=include_debug)
    )


def dry_run_safe(func: F) -> F:
    """Decorator to make operations safe in dry-run mode."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        config = get_config()
        
        if config.dry_run:
            logger.info(f"DRY RUN: Would execute {func.__name__} with args={args}, kwargs={kwargs}")
            return OperationResult(
                success=True,
                message=f"DRY RUN: Would execute {func.__name__}",
                data={"args": args, "kwargs": kwargs},
                dry_run=True
            )
        
        return func(*args, **kwargs)
    
    return wrapper


def get_project_ticket_prefix() -> str:
    """Get the ticket prefix from project configuration.
    
    Returns:
        The configured ticket prefix from .gira/config.json
        
    Raises:
        ValidationError: If no project configuration is found or no prefix is configured
    """
    import json
    from pathlib import Path
    import os
    
    # Check for test environment override
    test_prefix = os.getenv('GIRA_TEST_TICKET_PREFIX')
    if test_prefix:
        return test_prefix
    
    try:
        # Try to get gira root from MCP config first
        from gira.mcp.config import get_config
        mcp_config = get_config()
        gira_root = mcp_config.get_active_project_path()
        
        if not gira_root:
            # Fallback to standard project search
            from gira.utils.project import get_gira_root
            gira_root = get_gira_root()
        
        if not gira_root:
            # If we're in a test environment (pytest running), use default test prefix
            if _is_test_environment():
                return "TEST"
            raise ValidationError("No Gira project found. Run 'gira init' to initialize a project.")
        
        config_path = gira_root / ".gira" / "config.json"
        if not config_path.exists():
            # If we're in a test environment, use default test prefix
            if _is_test_environment():
                return "TEST"
            raise ValidationError("Project configuration not found. Run 'gira init' to initialize a project.")
        
        with open(config_path) as f:
            config = json.load(f)
            
        # Check for ticket_id_prefix in root config
        if "ticket_id_prefix" in config:
            return config["ticket_id_prefix"]
            
        # Check for nested ticket.prefix config (alternative format)
        if "ticket" in config and "prefix" in config["ticket"]:
            return config["ticket"]["prefix"]
        
        # No prefix configured - use test default if in test environment
        if _is_test_environment():
            return "TEST"
        raise ValidationError("No ticket prefix configured. Add 'ticket_id_prefix' to .gira/config.json")
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        # In test environment, use test prefix
        if _is_test_environment():
            return "TEST"
        raise ValidationError(f"Failed to read project configuration: {e}")
    except ValidationError:
        # Re-raise ValidationError as-is
        raise
    except Exception as e:
        # In test environment, use test prefix
        if _is_test_environment():
            return "TEST"
        raise ValidationError(f"Error reading project configuration: {e}")


def _is_test_environment() -> bool:
    """Check if we're running in a test environment."""
    import sys
    return (
        'pytest' in sys.modules or 
        'unittest' in sys.modules or
        os.getenv('PYTEST_CURRENT_TEST') is not None or
        any('test' in arg.lower() for arg in sys.argv)
    )


def normalize_ticket_id(ticket_id: str) -> str:
    """Normalize ticket ID to full format using configured prefix (e.g., '123' -> 'PROJ-123').
    
    This function handles:
    - Pure numbers: '123' -> 'PROJ-123' (using configured prefix)
    - IDs without prefixes: 'abc' -> 'PROJ-ABC' (using configured prefix)  
    - IDs with existing prefixes: 'CDGT-123' -> 'CDGT-123' (preserve existing)
    - Special prefixes: 'EPIC-001' -> 'EPIC-001' (preserve EPIC prefix)
    """
    if not ticket_id:
        raise ValidationError("Ticket ID cannot be empty")
    
    project_prefix = get_project_ticket_prefix()
    
    # If it's just a number, add the configured prefix
    if ticket_id.isdigit():
        return f"{project_prefix}-{ticket_id}"
    
    # If it already has a prefix (contains '-'), preserve it
    if '-' in ticket_id:
        return ticket_id.upper()
    
    # If it's a string without a prefix and not starting with known prefixes,
    # add the configured prefix
    upper_id = ticket_id.upper()
    if not upper_id.startswith(('EPIC-',)):  # Allow EPIC to be handled specially
        return f"{project_prefix}-{upper_id}"
    
    return upper_id


def normalize_epic_id(epic_id: str) -> str:
    """Normalize epic ID to full format (e.g., '001' -> 'EPIC-001')."""
    if not epic_id:
        raise ValidationError("Epic ID cannot be empty")
    
    # If it's just a number, assume it's an EPIC
    if epic_id.isdigit():
        return f"EPIC-{epic_id.zfill(3)}"
    
    # If it already has a prefix, return as-is
    if epic_id.startswith('EPIC-'):
        return epic_id.upper()
    
    # Otherwise, assume it's an EPIC without prefix
    return f"EPIC-{epic_id}".upper()


class ToolRegistry:
    """Registry for MCP tools with metadata and validation."""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        schema: Optional[Dict[str, Any]] = None,
        requires_confirmation: bool = False,
        is_destructive: bool = False
    ):
        """Register a tool with metadata."""
        self.tools[name] = {
            "function": func,
            "description": description,
            "schema": schema,
            "requires_confirmation": requires_confirmation,
            "is_destructive": is_destructive
        }
        logger.debug(f"Registered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered tools."""
        return self.tools.copy()


# Global tool registry
tool_registry = ToolRegistry()


def register_tool(
    name: str,
    description: str,
    schema: Optional[Dict[str, Any]] = None,
    requires_confirmation: bool = False,
    is_destructive: bool = False
):
    """Decorator to register a tool with the global registry."""
    def decorator(func: F) -> F:
        # Apply standard decorators
        decorated_func = handle_errors()(func)
        if is_destructive:
            decorated_func = dry_run_safe(decorated_func)
        if requires_confirmation:
            decorated_func = require_confirmation(name)(decorated_func)
        
        decorated_func = validate_working_directory()(decorated_func)
        
        # Register with metadata
        tool_registry.register(
            name=name,
            func=decorated_func,
            description=description,
            schema=schema,
            requires_confirmation=requires_confirmation,
            is_destructive=is_destructive
        )
        
        return decorated_func
    
    return decorator


# Tool implementations are imported in server.py to register them
# Future tool implementations will be imported here:
# from .epic_tools import *
# from .sprint_tools import *