"""Error handling for bulk operations API."""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from gira.api.bulk.schemas import OperationError
from gira.utils.errors import GiraError


class APIError(GiraError):
    """Base API error with structured error information."""
    
    def __init__(
        self,
        message: str,
        code: str = "API_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None
    ):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.field = field
        self.error_id = str(uuid4())
    
    def to_operation_error(self, item_id: Optional[str] = None) -> OperationError:
        """Convert to OperationError for API responses."""
        return OperationError(
            code=self.code,
            message=str(self),
            details={**self.details, "error_id": self.error_id},
            field=self.field,
            item_id=item_id
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "error": {
                "code": self.code,
                "message": str(self),
                "details": self.details,
                "field": self.field,
                "error_id": self.error_id
            }
        }


class ValidationError(APIError):
    """Validation error for bulk operations."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
            field=field
        )


class ItemNotFoundError(APIError):
    """Error when an item is not found."""
    
    def __init__(self, item_id: str, item_type: str = "ticket"):
        super().__init__(
            message=f"{item_type.capitalize()} {item_id} not found",
            code="ITEM_NOT_FOUND",
            status_code=404,
            details={"item_id": item_id, "item_type": item_type}
        )


class OperationNotAllowedError(APIError):
    """Error when an operation is not allowed."""
    
    def __init__(self, message: str, reason: Optional[str] = None):
        super().__init__(
            message=message,
            code="OPERATION_NOT_ALLOWED",
            status_code=403,
            details={"reason": reason} if reason else None
        )


class BulkOperationError(APIError):
    """Error during bulk operation execution."""
    
    def __init__(
        self,
        message: str,
        failed_items: Optional[List[str]] = None,
        partial_success: bool = False
    ):
        super().__init__(
            message=message,
            code="BULK_OPERATION_ERROR",
            status_code=500 if not partial_success else 207,  # 207 Multi-Status
            details={
                "failed_items": failed_items or [],
                "partial_success": partial_success
            }
        )


class TransactionError(APIError):
    """Error during transaction processing."""
    
    def __init__(self, message: str, transaction_id: Optional[str] = None):
        super().__init__(
            message=message,
            code="TRANSACTION_ERROR",
            status_code=500,
            details={"transaction_id": transaction_id} if transaction_id else None
        )


class ErrorHandler:
    """Centralized error handler for bulk operations."""
    
    def __init__(self):
        self.error_mappings = {
            FileNotFoundError: self._handle_file_not_found,
            ValueError: self._handle_value_error,
            KeyError: self._handle_key_error,
            PermissionError: self._handle_permission_error,
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        item_id: Optional[str] = None
    ) -> OperationError:
        """Convert any exception to an OperationError."""
        # Check if it's already an APIError
        if isinstance(error, APIError):
            return error.to_operation_error(item_id)
        
        # Check mapped error types
        error_type = type(error)
        if error_type in self.error_mappings:
            handler = self.error_mappings[error_type]
            return handler(error, context, item_id)
        
        # Default handling
        return self._handle_generic_error(error, context, item_id)
    
    def _handle_file_not_found(
        self,
        error: FileNotFoundError,
        context: Optional[Dict[str, Any]],
        item_id: Optional[str]
    ) -> OperationError:
        """Handle file not found errors."""
        return OperationError(
            code="FILE_NOT_FOUND",
            message=str(error),
            details=context,
            item_id=item_id
        )
    
    def _handle_value_error(
        self,
        error: ValueError,
        context: Optional[Dict[str, Any]],
        item_id: Optional[str]
    ) -> OperationError:
        """Handle value errors."""
        return OperationError(
            code="INVALID_VALUE",
            message=str(error),
            details=context,
            item_id=item_id
        )
    
    def _handle_key_error(
        self,
        error: KeyError,
        context: Optional[Dict[str, Any]],
        item_id: Optional[str]
    ) -> OperationError:
        """Handle key errors."""
        return OperationError(
            code="MISSING_FIELD",
            message=f"Missing required field: {error}",
            field=str(error).strip("'\""),
            details=context,
            item_id=item_id
        )
    
    def _handle_permission_error(
        self,
        error: PermissionError,
        context: Optional[Dict[str, Any]],
        item_id: Optional[str]
    ) -> OperationError:
        """Handle permission errors."""
        return OperationError(
            code="PERMISSION_DENIED",
            message=str(error),
            details=context,
            item_id=item_id
        )
    
    def _handle_generic_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]],
        item_id: Optional[str]
    ) -> OperationError:
        """Handle generic errors."""
        return OperationError(
            code="INTERNAL_ERROR",
            message=str(error),
            details={
                "error_type": type(error).__name__,
                **(context or {})
            },
            item_id=item_id
        )
    
    def collect_errors(
        self,
        errors: List[OperationError],
        max_errors: int = 10
    ) -> List[OperationError]:
        """Collect and limit errors for response."""
        if len(errors) <= max_errors:
            return errors
        
        # Return first max_errors with a summary
        limited = errors[:max_errors]
        limited.append(
            OperationError(
                code="ERRORS_TRUNCATED",
                message=f"Showing first {max_errors} of {len(errors)} errors",
                details={"total_errors": len(errors), "shown": max_errors}
            )
        )
        return limited