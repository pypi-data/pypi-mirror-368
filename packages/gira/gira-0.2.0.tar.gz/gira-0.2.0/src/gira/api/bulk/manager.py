"""Base manager for bulk operations."""

import asyncio
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union
from uuid import uuid4

from gira.api.bulk.errors import (
    APIError,
    BulkOperationError,
    ErrorHandler,
    ValidationError,
)
from gira.api.bulk.response import ResponseFormatter
from gira.api.bulk.schemas import (
    BulkOperationItem,
    BulkOperationRequest,
    BulkOperationResponse,
    OperationError,
    OperationResult,
    OperationStatus,
    OperationType,
)
from gira.api.bulk.tracker import OperationTracker
from gira.api.bulk.validation import ValidationEngine, ValidationLevel
from gira.utils.project import ensure_gira_project


class BulkOperationManager(ABC):
    """Abstract base class for bulk operation managers."""
    
    def __init__(
        self,
        operation_type: OperationType,
        root: Optional[Path] = None,
        tracker: Optional[OperationTracker] = None,
        validator: Optional[ValidationEngine] = None,
        error_handler: Optional[ErrorHandler] = None,
        response_formatter: Optional[ResponseFormatter] = None,
        max_workers: int = 4
    ):
        """Initialize bulk operation manager.
        
        Args:
            operation_type: Type of operations this manager handles
            root: Project root directory
            tracker: Operation tracker instance (shared across managers)
            validator: Validation engine instance
            error_handler: Error handler instance
            response_formatter: Response formatter instance
            max_workers: Maximum number of concurrent workers
        """
        self.operation_type = operation_type
        self.root = root or ensure_gira_project()
        self.tracker = tracker or OperationTracker()
        self.validator = validator or ValidationEngine(self.root)
        self.error_handler = error_handler or ErrorHandler()
        self.response_formatter = response_formatter or ResponseFormatter()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    @abstractmethod
    def process_item(
        self,
        item: Union[BulkOperationItem, Dict[str, Any]],
        options: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Process a single item.
        
        This method must be implemented by subclasses.
        
        Args:
            item: Item to process
            options: Operation options
            context: Optional context for the operation
            
        Returns:
            OperationResult with success/failure information
        """
        pass
    
    @abstractmethod
    def get_item_class(self) -> Type[BulkOperationItem]:
        """Get the item class for this operation type.
        
        Returns:
            The Pydantic model class for items
        """
        pass
    
    def execute(
        self,
        request: BulkOperationRequest,
        async_mode: bool = False
    ) -> Union[BulkOperationResponse, str]:
        """Execute a bulk operation.
        
        Args:
            request: Bulk operation request
            async_mode: If True, return operation ID immediately
            
        Returns:
            BulkOperationResponse or operation ID if async
        """
        # Generate operation ID if not provided
        if not request.operation_id:
            request.operation_id = str(uuid4())
        
        # Create operation in tracker
        operation_id = self.tracker.create_operation(
            operation_type=self.operation_type,
            total_items=len(request.items),
            operation_id=request.operation_id,
            metadata={"options": request.options.model_dump()}
        )
        
        if async_mode:
            # Start async execution and return ID immediately
            asyncio.create_task(self._execute_async(request, operation_id))
            return operation_id
        else:
            # Execute synchronously
            return self._execute_sync(request, operation_id)
    
    def _execute_sync(
        self,
        request: BulkOperationRequest,
        operation_id: str
    ) -> BulkOperationResponse:
        """Execute operation synchronously."""
        try:
            # Update status to validating
            self.tracker.update_status(operation_id, OperationStatus.VALIDATING)
            
            # Validate request if not skipping validation
            if request.options.validation_level != ValidationLevel.NONE:
                validation_result = self.validator.validate_request(request)
                
                if not validation_result.is_valid:
                    # Format validation errors
                    errors = validation_result.errors
                    for item_id, item_errors in validation_result.item_validations.items():
                        errors.extend(item_errors)
                    
                    # Mark as failed and return
                    self.tracker.update_status(operation_id, OperationStatus.FAILED)
                    return self.response_formatter.format_validation_response(
                        operation_id=operation_id,
                        operation_type=self.operation_type,
                        validation_errors=errors,
                        item_count=len(request.items)
                    )
            
            # Update status to in progress
            self.tracker.update_status(operation_id, OperationStatus.IN_PROGRESS)
            
            # Process items
            if request.options.dry_run:
                results = self._process_dry_run(request, operation_id)
            else:
                results = self._process_items(request, operation_id)
            
            # Get final operation state
            operation_state = self.tracker.get_operation(operation_id)
            
            # Return formatted response
            return self.response_formatter.format_operation_response(
                operation_state=operation_state,
                include_results=True
            )
            
        except Exception as e:
            # Handle unexpected errors
            self.tracker.update_status(operation_id, OperationStatus.FAILED)
            error = self.error_handler.handle_error(e, {"operation_id": operation_id})
            
            operation_state = self.tracker.get_operation(operation_id)
            return self.response_formatter.format_operation_response(
                operation_state=operation_state,
                errors=[error]
            )
    
    async def _execute_async(
        self,
        request: BulkOperationRequest,
        operation_id: str
    ):
        """Execute operation asynchronously."""
        # This is a simplified async implementation
        # In production, this would use proper async/await throughout
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._execute_sync,
            request,
            operation_id
        )
    
    def _process_items(
        self,
        request: BulkOperationRequest,
        operation_id: str
    ) -> List[OperationResult]:
        """Process all items in the request."""
        results = []
        failed_count = 0
        
        for i, item in enumerate(request.items):
            # Check if operation was cancelled
            operation = self.tracker.get_operation(operation_id)
            if operation and operation.status == OperationStatus.CANCELLED:
                break
            
            # Get item ID
            item_id = self._get_item_id(item)
            
            try:
                # Mark item as being processed
                self.tracker.start_item(operation_id, item_id)
                
                # Process the item
                result = self.process_item(
                    item=item,
                    options=request.options.model_dump(),
                    context={"operation_id": operation_id, "item_index": i}
                )
                
                # Track completion
                self.tracker.complete_item(operation_id, result)
                results.append(result)
                
                # Check if we should fail fast
                if result.error:
                    failed_count += 1
                    if request.options.all_or_nothing:
                        # Cancel remaining items
                        self.tracker.update_status(operation_id, OperationStatus.FAILED)
                        break
                
            except Exception as e:
                # Handle item processing error
                error = self.error_handler.handle_error(
                    e,
                    context={"item_id": item_id, "item_index": i},
                    item_id=item_id
                )
                
                result = OperationResult(
                    item_id=item_id,
                    status="failed",
                    error=error
                )
                
                self.tracker.complete_item(operation_id, result)
                results.append(result)
                
                failed_count += 1
                if request.options.all_or_nothing:
                    self.tracker.update_status(operation_id, OperationStatus.FAILED)
                    break
        
        return results
    
    def _process_dry_run(
        self,
        request: BulkOperationRequest,
        operation_id: str
    ) -> List[OperationResult]:
        """Process items in dry-run mode."""
        results = []
        
        for i, item in enumerate(request.items):
            item_id = self._get_item_id(item)
            
            # Simulate processing
            self.tracker.start_item(operation_id, item_id)
            
            # Create dry-run result
            result = OperationResult(
                item_id=item_id,
                status="dry_run",
                changes={"dry_run": True, "would_process": True}
            )
            
            self.tracker.complete_item(operation_id, result)
            results.append(result)
        
        return results
    
    def _get_item_id(self, item: Union[BulkOperationItem, Dict[str, Any]]) -> str:
        """Extract item ID from an item."""
        if isinstance(item, dict):
            return item.get("id", "unknown")
        elif hasattr(item, "id"):
            return item.id
        else:
            return "unknown"
    
    def get_status(self, operation_id: str) -> Optional[BulkOperationResponse]:
        """Get the status of an operation."""
        operation = self.tracker.get_operation(operation_id)
        if operation:
            return self.response_formatter.format_operation_response(
                operation_state=operation,
                include_results=operation.status in [
                    OperationStatus.COMPLETED,
                    OperationStatus.FAILED,
                    OperationStatus.PARTIALLY_COMPLETED
                ]
            )
        return None
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an operation."""
        return self.tracker.cancel_operation(operation_id)
    
    def cleanup(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)