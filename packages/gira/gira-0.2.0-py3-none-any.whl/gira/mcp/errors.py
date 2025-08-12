"""Enhanced error handling infrastructure for Gira MCP server."""

import logging
import traceback
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for systematic classification."""
    VALIDATION = "validation"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    STORAGE = "storage"
    PROCESSING = "processing"
    INTERNAL = "internal"
    TIMEOUT = "timeout"
    RESOURCE = "resource"


class ErrorCodes(str, Enum):
    """Comprehensive error codes for systematic error handling."""
    # Validation errors (1xxx)
    VALIDATION_FAILED = "E1001"
    INVALID_PARAMETER = "E1002"
    MISSING_PARAMETER = "E1003"
    INVALID_FORMAT = "E1004"
    VALUE_OUT_OF_RANGE = "E1005"
    INVALID_TYPE = "E1006"
    
    # Permission errors (2xxx)
    ACCESS_DENIED = "E2001"
    INSUFFICIENT_PERMISSIONS = "E2002"
    AUTHENTICATION_REQUIRED = "E2003"
    OPERATION_NOT_ALLOWED = "E2004"
    
    # Resource errors (3xxx)
    RESOURCE_NOT_FOUND = "E3001"
    TICKET_NOT_FOUND = "E3002"
    EPIC_NOT_FOUND = "E3003"
    SPRINT_NOT_FOUND = "E3004"
    PROJECT_NOT_FOUND = "E3005"
    NOT_FOUND = "not_found"  # Generic not found error for backward compatibility
    
    # Legacy error codes for backward compatibility
    VALIDATION_ERROR = "validation_error"
    PERMISSION_ERROR = "permission_error"
    INTERNAL_ERROR_LEGACY = "internal_error"
    
    # Configuration errors (4xxx)
    CONFIG_MISSING = "E4001"
    CONFIG_INVALID = "E4002"
    PROJECT_NOT_INITIALIZED = "E4003"
    WORKING_DIRECTORY_INVALID = "E4004"
    
    # Network/Storage errors (5xxx)
    CONNECTION_FAILED = "E5001"
    TIMEOUT_ERROR = "E5002"
    STORAGE_ERROR = "E5003"
    FILE_SYSTEM_ERROR = "E5004"
    
    # Processing errors (6xxx)
    OPERATION_FAILED = "E6001"
    DEPENDENCY_VIOLATION = "E6002"
    CIRCULAR_DEPENDENCY = "E6003"
    CONFLICT_ERROR = "E6004"
    
    # Internal errors (9xxx)
    INTERNAL_ERROR = "E9001"
    UNKNOWN_ERROR = "E9999"


class ErrorContext(BaseModel):
    """Context information for enhanced error reporting."""
    operation: Optional[str] = Field(None, description="Operation that caused the error")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters passed to operation")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User context information")
    system_context: Optional[Dict[str, Any]] = Field(None, description="System context information")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for request tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class ErrorSuggestion(BaseModel):
    """Suggestion for fixing an error."""
    action: str = Field(description="Suggested action to fix the error")
    example: Optional[str] = Field(None, description="Example of correct usage")
    documentation_link: Optional[str] = Field(None, description="Link to relevant documentation")


class RecoveryStrategy(BaseModel):
    """Strategy for recovering from an error."""
    strategy_type: str = Field(description="Type of recovery strategy")
    auto_recoverable: bool = Field(False, description="Whether error can be auto-recovered")
    retry_count: int = Field(0, description="Number of retry attempts")
    max_retries: int = Field(3, description="Maximum retry attempts")
    backoff_seconds: float = Field(1.0, description="Backoff time between retries")


class EnhancedMCPError(Exception):
    """Enhanced MCP error with comprehensive context and recovery information."""
    
    def __init__(
        self,
        message: str,
        code: ErrorCodes = ErrorCodes.UNKNOWN_ERROR,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[ErrorContext] = None,
        suggestions: Optional[List[ErrorSuggestion]] = None,
        recovery_strategy: Optional[RecoveryStrategy] = None,
        debug_info: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize enhanced MCP error.
        
        Args:
            message: User-friendly error message
            code: Systematic error code
            category: Error category
            severity: Error severity level
            context: Error context information
            suggestions: List of suggestions for fixing the error
            recovery_strategy: Strategy for recovering from error
            debug_info: Technical debugging information
            original_exception: Original exception that caused this error
        """
        self.message = message
        self.code = code
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
        self.suggestions = suggestions or []
        self.recovery_strategy = recovery_strategy
        self.debug_info = debug_info or {}
        self.original_exception = original_exception
        
        # Add stack trace to debug info if not in production
        if original_exception and logger.isEnabledFor(logging.DEBUG):
            self.debug_info["stack_trace"] = traceback.format_exception(
                type(original_exception), original_exception, original_exception.__traceback__
            )
        
        super().__init__(message)
    
    def to_dict(self, include_debug: bool = False) -> Dict[str, Any]:
        """Convert error to dictionary representation.
        
        Args:
            include_debug: Whether to include debug information
            
        Returns:
            Dictionary representation of the error
        """
        error_dict = {
            "error": self.message,
            "code": self.code.value,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.context.timestamp.isoformat(),
            "suggestions": [suggestion.model_dump() for suggestion in self.suggestions]
        }
        
        if self.context.operation:
            error_dict["operation"] = self.context.operation
            
        if self.context.correlation_id:
            error_dict["correlation_id"] = self.context.correlation_id
        
        if self.recovery_strategy:
            error_dict["recovery_strategy"] = self.recovery_strategy.model_dump()
        
        if include_debug and self.debug_info:
            error_dict["debug_info"] = self.debug_info
            
        return error_dict
    
    def is_recoverable(self) -> bool:
        """Check if error is automatically recoverable."""
        return (
            self.recovery_strategy is not None and 
            self.recovery_strategy.auto_recoverable and
            self.recovery_strategy.retry_count < self.recovery_strategy.max_retries
        )
    
    def get_user_message(self) -> str:
        """Get user-friendly error message with suggestions."""
        message = self.message
        
        if self.suggestions:
            message += "\n\nSuggestions:"
            for i, suggestion in enumerate(self.suggestions, 1):
                message += f"\n{i}. {suggestion.action}"
                if suggestion.example:
                    message += f"\n   Example: {suggestion.example}"
        
        return message


# Specific enhanced error classes

class ValidationError(EnhancedMCPError):
    """Enhanced validation error with format examples and suggestions."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_format: Optional[str] = None,
        valid_values: Optional[List[str]] = None,
        **kwargs
    ):
        suggestions = []
        
        if expected_format:
            suggestions.append(ErrorSuggestion(
                action=f"Use the correct format for '{field}': {expected_format}",
                example=expected_format
            ))
        
        if valid_values:
            suggestions.append(ErrorSuggestion(
                action=f"Use one of the valid values: {', '.join(valid_values)}",
                example=f"{field}={valid_values[0]}" if field else valid_values[0]
            ))
        
        context = kwargs.pop('context', ErrorContext())
        if field and context.parameters is None:
            context.parameters = {"invalid_field": field, "invalid_value": value}
        
        super().__init__(
            message,
            code=ErrorCodes.VALIDATION_FAILED,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR,
            context=context,
            suggestions=suggestions,
            **kwargs
        )


class ResourceNotFoundError(EnhancedMCPError):
    """Enhanced resource not found error with search suggestions."""
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: str,
        available_resources: Optional[List[str]] = None,
        **kwargs
    ):
        suggestions = []
        
        if available_resources:
            # Find similar resources (simple string matching)
            similar = [r for r in available_resources if resource_id.lower() in r.lower()]
            if similar:
                suggestions.append(ErrorSuggestion(
                    action=f"Did you mean one of these {resource_type}s: {', '.join(similar[:3])}?",
                    example=f"Try using: {similar[0]}"
                ))
        
        suggestions.append(ErrorSuggestion(
            action=f"List available {resource_type}s to see what's available",
            example=f"gira {resource_type} list"
        ))
        
        # Map resource types to specific error codes
        code_mapping = {
            "ticket": ErrorCodes.TICKET_NOT_FOUND,
            "epic": ErrorCodes.EPIC_NOT_FOUND,
            "sprint": ErrorCodes.SPRINT_NOT_FOUND,
            "project": ErrorCodes.PROJECT_NOT_FOUND
        }
        
        super().__init__(
            message,
            code=code_mapping.get(resource_type.lower(), ErrorCodes.RESOURCE_NOT_FOUND),
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            **kwargs
        )


class ConfigurationError(EnhancedMCPError):
    """Enhanced configuration error with setup suggestions."""
    
    def __init__(self, message: str, config_type: str = "general", **kwargs):
        suggestions = []
        
        if config_type == "project":
            suggestions.extend([
                ErrorSuggestion(
                    action="Initialize a Gira project in the current directory",
                    example="gira init"
                ),
                ErrorSuggestion(
                    action="Navigate to an existing Gira project directory",
                    example="cd /path/to/gira/project"
                )
            ])
        elif config_type == "working_directory":
            suggestions.append(ErrorSuggestion(
                action="Ensure you're in a valid Gira project directory",
                example="Look for a .gira/ directory in your current path"
            ))
        
        super().__init__(
            message,
            code=ErrorCodes.CONFIG_INVALID,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            **kwargs
        )


class OperationError(EnhancedMCPError):
    """Enhanced operation error with recovery suggestions."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        can_retry: bool = False,
        rollback_available: bool = False,
        **kwargs
    ):
        suggestions = []
        recovery_strategy = None
        
        if can_retry:
            suggestions.append(ErrorSuggestion(
                action="Retry the operation after a brief delay",
                example="The operation may succeed on retry"
            ))
            recovery_strategy = RecoveryStrategy(
                strategy_type="retry",
                auto_recoverable=True,
                max_retries=3,
                backoff_seconds=2.0
            )
        
        if rollback_available:
            suggestions.append(ErrorSuggestion(
                action="Check if the operation was partially completed and needs cleanup",
                example="Some changes may have been made before the error occurred"
            ))
        
        context = kwargs.get('context', ErrorContext())
        context.operation = operation
        
        super().__init__(
            message,
            code=ErrorCodes.OPERATION_FAILED,
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.ERROR,
            context=context,
            suggestions=suggestions,
            recovery_strategy=recovery_strategy,
            **kwargs
        )


# Error message templates
ERROR_TEMPLATES = {
    ErrorCodes.VALIDATION_FAILED: "Parameter validation failed: {details}",
    ErrorCodes.INVALID_PARAMETER: "Invalid parameter '{parameter}': {reason}",
    ErrorCodes.MISSING_PARAMETER: "Missing required parameter: '{parameter}'",
    ErrorCodes.RESOURCE_NOT_FOUND: "{resource_type} '{resource_id}' not found",
    ErrorCodes.NOT_FOUND: "Resource not found: {details}",
    ErrorCodes.VALIDATION_ERROR: "Validation error: {details}",
    ErrorCodes.PERMISSION_ERROR: "Permission error: {details}",
    ErrorCodes.INTERNAL_ERROR_LEGACY: "Internal error: {details}",
    ErrorCodes.ACCESS_DENIED: "Access denied: {reason}",
    ErrorCodes.OPERATION_FAILED: "Operation '{operation}' failed: {reason}",
    ErrorCodes.CONFIG_MISSING: "Configuration missing: {config_type}",
    ErrorCodes.INTERNAL_ERROR: "An internal error occurred. Please contact support if this persists."
}


def format_error_message(code: ErrorCodes, **kwargs) -> str:
    """Format error message using template and parameters.
    
    Args:
        code: Error code
        **kwargs: Template parameters
        
    Returns:
        Formatted error message
    """
    template = ERROR_TEMPLATES.get(code, "An error occurred: {details}")
    try:
        return template.format(**kwargs)
    except KeyError:
        return f"Error {code.value}: {kwargs.get('details', 'Unknown error')}"


# Alias for backward compatibility
EnhancedValidationError = ValidationError