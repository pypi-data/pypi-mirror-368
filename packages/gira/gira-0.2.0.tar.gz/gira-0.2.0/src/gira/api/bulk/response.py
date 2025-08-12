"""Response formatting for bulk operations API."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from gira.api.bulk.schemas import (
    BulkOperationResponse,
    OperationError,
    OperationResult,
    OperationStatus,
    OperationType,
    ProgressInfo,
)
from gira.api.bulk.tracker import OperationState


class ResponseFormatter:
    """Formats responses for bulk operations API."""
    
    def __init__(self, pretty_print: bool = False, include_metadata: bool = True):
        """Initialize response formatter.
        
        Args:
            pretty_print: Whether to pretty print JSON responses
            include_metadata: Whether to include metadata in responses
        """
        self.pretty_print = pretty_print
        self.include_metadata = include_metadata
    
    def format_operation_response(
        self,
        operation_state: OperationState,
        include_results: bool = True,
        errors: Optional[List[OperationError]] = None
    ) -> BulkOperationResponse:
        """Format an operation state as a response."""
        # Build metadata
        metadata = {
            "created_at": operation_state.created_at.isoformat(),
            "updated_at": operation_state.updated_at.isoformat(),
        }
        
        if operation_state.started_at:
            metadata["started_at"] = operation_state.started_at.isoformat()
        
        if operation_state.completed_at:
            metadata["completed_at"] = operation_state.completed_at.isoformat()
            if operation_state.started_at:
                duration_ms = int(
                    (operation_state.completed_at - operation_state.started_at).total_seconds() * 1000
                )
                metadata["duration_ms"] = duration_ms
        
        # Add custom metadata
        if self.include_metadata:
            metadata.update(operation_state.metadata)
        
        # Build response
        response = BulkOperationResponse(
            operation_id=operation_state.operation_id,
            operation_type=operation_state.operation_type,
            status=operation_state.status,
            progress=operation_state.progress,
            results=operation_state.results if include_results else None,
            errors=errors,
            metadata=metadata
        )
        
        return response
    
    def format_validation_response(
        self,
        operation_id: str,
        operation_type: OperationType,
        validation_errors: List[OperationError],
        item_count: int
    ) -> BulkOperationResponse:
        """Format a validation failure response."""
        return BulkOperationResponse(
            operation_id=operation_id,
            operation_type=operation_type,
            status=OperationStatus.FAILED,
            progress=ProgressInfo(completed=0, total=item_count, percentage=0.0),
            errors=validation_errors,
            metadata={
                "failure_reason": "validation_failed",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def format_error_response(
        self,
        operation_id: str,
        operation_type: OperationType,
        error: Exception,
        status_code: int = 500
    ) -> Dict[str, Any]:
        """Format an error response."""
        error_data = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(error),
                "type": type(error).__name__,
                "operation_id": operation_id,
                "operation_type": operation_type.value
            },
            "status_code": status_code
        }
        
        if self.include_metadata:
            error_data["error"]["timestamp"] = datetime.now().isoformat()
        
        return error_data
    
    def format_success_response(
        self,
        operation_id: str,
        operation_type: OperationType,
        results: List[OperationResult],
        metadata: Optional[Dict[str, Any]] = None
    ) -> BulkOperationResponse:
        """Format a successful operation response."""
        return BulkOperationResponse(
            operation_id=operation_id,
            operation_type=operation_type,
            status=OperationStatus.COMPLETED,
            progress=ProgressInfo(
                completed=len(results),
                total=len(results),
                percentage=100.0
            ),
            results={"successful": results, "failed": [], "skipped": []},
            metadata=metadata or {}
        )
    
    def format_partial_success_response(
        self,
        operation_id: str,
        operation_type: OperationType,
        successful: List[OperationResult],
        failed: List[OperationResult],
        skipped: Optional[List[OperationResult]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BulkOperationResponse:
        """Format a partial success response."""
        total = len(successful) + len(failed) + len(skipped or [])
        
        return BulkOperationResponse(
            operation_id=operation_id,
            operation_type=operation_type,
            status=OperationStatus.PARTIALLY_COMPLETED,
            progress=ProgressInfo(
                completed=total,
                total=total,
                percentage=100.0
            ),
            results={
                "successful": successful,
                "failed": failed,
                "skipped": skipped or []
            },
            metadata=metadata or {}
        )
    
    def to_json(self, response: Union[BulkOperationResponse, Dict[str, Any]]) -> str:
        """Convert response to JSON string."""
        if isinstance(response, BulkOperationResponse):
            data = response.model_dump(exclude_none=True)
        else:
            data = response
        
        if self.pretty_print:
            return json.dumps(data, indent=2, default=self._json_encoder)
        else:
            return json.dumps(data, default=self._json_encoder)
    
    def to_dict(self, response: BulkOperationResponse) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return response.model_dump(exclude_none=True)
    
    def format_summary(self, response: BulkOperationResponse) -> Dict[str, Any]:
        """Format a summary of the operation."""
        summary = {
            "operation_id": response.operation_id,
            "status": response.status.value,
            "progress": {
                "completed": response.progress.completed,
                "total": response.progress.total,
                "percentage": response.progress.percentage
            }
        }
        
        if response.results:
            summary["results"] = {
                "successful": response.success_count,
                "failed": response.failure_count,
                "skipped": len(response.results.get("skipped", []))
            }
        
        if response.metadata and "duration_ms" in response.metadata:
            summary["duration_ms"] = response.metadata["duration_ms"]
        
        return summary
    
    def format_cli_output(self, response: BulkOperationResponse) -> str:
        """Format response for CLI output."""
        lines = []
        
        # Header
        lines.append(f"Operation: {response.operation_type.value}")
        lines.append(f"ID: {response.operation_id}")
        lines.append(f"Status: {response.status.value}")
        
        # Progress
        if response.progress:
            lines.append(
                f"Progress: {response.progress.completed}/{response.progress.total} "
                f"({response.progress.percentage}%)"
            )
        
        # Results summary
        if response.results:
            lines.append("\nResults:")
            lines.append(f"  Successful: {response.success_count}")
            lines.append(f"  Failed: {response.failure_count}")
            
            skipped = len(response.results.get("skipped", []))
            if skipped > 0:
                lines.append(f"  Skipped: {skipped}")
        
        # Errors
        if response.errors:
            lines.append(f"\nErrors: {len(response.errors)}")
            for i, error in enumerate(response.errors[:5]):  # Show first 5
                lines.append(f"  {i+1}. {error.code}: {error.message}")
            if len(response.errors) > 5:
                lines.append(f"  ... and {len(response.errors) - 5} more")
        
        # Duration
        if response.metadata and "duration_ms" in response.metadata:
            duration = response.metadata["duration_ms"] / 1000
            lines.append(f"\nDuration: {duration:.2f}s")
        
        return "\n".join(lines)
    
    def _json_encoder(self, obj):
        """Custom JSON encoder for special types."""
        if isinstance(obj, (UUID, datetime)):
            return str(obj)
        elif hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "to_dict"):
            return obj.to_dict()
        return obj