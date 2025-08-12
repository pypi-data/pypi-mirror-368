"""Schema definitions for bulk operations API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class OperationType(str, Enum):
    """Types of bulk operations."""
    BULK_UPDATE = "bulk_update"
    BULK_ADD_DEPS = "bulk_add_deps"
    BULK_REMOVE_DEPS = "bulk_remove_deps"
    BULK_CLEAR_DEPS = "bulk_clear_deps"
    BULK_MOVE = "bulk_move"
    BULK_DELETE = "bulk_delete"


class OperationStatus(str, Enum):
    """Status of a bulk operation."""
    PENDING = "pending"
    VALIDATING = "validating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"
    CANCELLED = "cancelled"


class ValidationLevel(str, Enum):
    """Validation levels for bulk operations."""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"


class BulkOperationOptions(BaseModel):
    """Options for bulk operations."""
    model_config = ConfigDict(extra="allow")
    
    dry_run: bool = Field(default=False, description="Preview changes without applying them")
    validate_only: bool = Field(default=False, description="Only validate, don't execute")
    all_or_nothing: bool = Field(default=False, description="Fail entire operation if any item fails")
    use_transaction: bool = Field(default=False, description="Use atomic transactions")
    skip_invalid: bool = Field(default=False, description="Skip invalid items and continue")
    validation_level: ValidationLevel = Field(default=ValidationLevel.BASIC)
    progress_callback: Optional[str] = Field(default=None, description="Webhook URL for progress updates")


class BulkOperationItem(BaseModel):
    """Single item in a bulk operation."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="Ticket ID")
    # Additional fields depend on operation type


class BulkUpdateItem(BulkOperationItem):
    """Item for bulk update operations."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    type: Optional[str] = None
    assignee: Optional[str] = None
    add_labels: Optional[List[str]] = None
    remove_labels: Optional[List[str]] = None
    epic: Optional[str] = None
    parent: Optional[str] = None
    story_points: Optional[int] = None


class BulkDependencyItem(BulkOperationItem):
    """Item for bulk dependency operations."""
    dependency_id: Optional[str] = Field(None, description="Dependency ticket ID")
    dependencies: Optional[List[str]] = Field(None, description="List of dependency IDs")
    remove_all: bool = Field(default=False, description="Remove all dependencies")


class BulkOperationRequest(BaseModel):
    """Request for a bulk operation."""
    operation_id: Optional[str] = Field(default=None, description="Unique operation ID")
    operation_type: OperationType = Field(..., description="Type of bulk operation")
    items: List[Union[BulkOperationItem, Dict[str, Any]]] = Field(..., description="Items to process")
    options: BulkOperationOptions = Field(default_factory=BulkOperationOptions)


class ProgressInfo(BaseModel):
    """Progress information for a bulk operation."""
    completed: int = Field(default=0, description="Number of completed items")
    total: int = Field(..., description="Total number of items")
    percentage: float = Field(default=0.0, description="Completion percentage")
    current_item: Optional[str] = Field(default=None, description="Currently processing item")
    estimated_time_remaining: Optional[int] = Field(default=None, description="ETA in seconds")


class OperationError(BaseModel):
    """Error information for failed operations."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    field: Optional[str] = Field(default=None, description="Field that caused the error")
    item_id: Optional[str] = Field(default=None, description="Item that caused the error")


class OperationResult(BaseModel):
    """Result of a single item operation."""
    item_id: str = Field(..., description="Item ID")
    status: str = Field(..., description="Item operation status")
    changes: Optional[Dict[str, Any]] = Field(default=None, description="Changes applied")
    error: Optional[OperationError] = Field(default=None, description="Error if failed")


class BulkOperationResponse(BaseModel):
    """Response from a bulk operation."""
    operation_id: str = Field(..., description="Unique operation ID")
    operation_type: OperationType = Field(..., description="Type of bulk operation")
    status: OperationStatus = Field(..., description="Overall operation status")
    progress: ProgressInfo = Field(..., description="Progress information")
    results: Optional[Dict[str, List[OperationResult]]] = Field(
        default=None,
        description="Results grouped by status (successful, failed, skipped)"
    )
    errors: Optional[List[OperationError]] = Field(default=None, description="Global errors")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Operation metadata")
    
    @property
    def is_complete(self) -> bool:
        """Check if operation is complete."""
        return self.status in [
            OperationStatus.COMPLETED,
            OperationStatus.FAILED,
            OperationStatus.PARTIALLY_COMPLETED,
            OperationStatus.CANCELLED
        ]
    
    @property
    def success_count(self) -> int:
        """Get number of successful items."""
        if self.results and "successful" in self.results:
            return len(self.results["successful"])
        return 0
    
    @property
    def failure_count(self) -> int:
        """Get number of failed items."""
        if self.results and "failed" in self.results:
            return len(self.results["failed"])
        return 0


class ValidationResult(BaseModel):
    """Result of validation for a bulk operation."""
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: List[OperationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[OperationError] = Field(default_factory=list, description="Validation warnings")
    item_validations: Dict[str, List[OperationError]] = Field(
        default_factory=dict,
        description="Per-item validation errors"
    )