"""Validation engine for bulk operations."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

from gira.api.bulk.errors import ValidationError
from gira.api.bulk.schemas import (
    BulkDependencyItem,
    BulkOperationItem,
    BulkOperationRequest,
    BulkUpdateItem,
    OperationError,
    OperationType,
    ValidationLevel,
    ValidationResult,
)
from gira.models import TicketPriority, TicketStatus, TicketType
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, field: Optional[str] = None, message: Optional[str] = None):
        self.field = field
        self.message = message or "Validation failed"
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[OperationError]:
        """Validate a value. Return None if valid, OperationError if invalid."""
        raise NotImplementedError


class RequiredFieldRule(ValidationRule):
    """Validates that a field is present and not empty."""
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[OperationError]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return OperationError(
                code="REQUIRED_FIELD",
                message=f"{self.field} is required" if self.field else self.message,
                field=self.field
            )
        return None


class EnumFieldRule(ValidationRule):
    """Validates that a value is in a set of allowed values."""
    
    def __init__(self, allowed_values: Set[str], field: Optional[str] = None, message: Optional[str] = None):
        super().__init__(field, message)
        self.allowed_values = {v.lower() for v in allowed_values}
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[OperationError]:
        if value is None:
            return None
        
        if isinstance(value, str) and value.lower() not in self.allowed_values:
            return OperationError(
                code="INVALID_ENUM_VALUE",
                message=f"Invalid value for {self.field}: {value}. Allowed values: {', '.join(sorted(self.allowed_values))}",
                field=self.field,
                details={"allowed_values": sorted(self.allowed_values), "provided_value": value}
            )
        return None


class TicketExistsRule(ValidationRule):
    """Validates that a ticket exists."""
    
    def __init__(self, root: Path, field: Optional[str] = None):
        super().__init__(field, "Ticket not found")
        self.root = root
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[OperationError]:
        if value is None:
            return None
        
        if isinstance(value, str):
            ticket, _ = find_ticket(value, self.root)
            if not ticket:
                return OperationError(
                    code="TICKET_NOT_FOUND",
                    message=f"Ticket {value} not found",
                    field=self.field,
                    details={"ticket_id": value}
                )
        return None


class CircularDependencyRule(ValidationRule):
    """Validates that adding a dependency won't create a circular dependency."""
    
    def __init__(self, root: Path):
        super().__init__(None, "Circular dependency detected")
        self.root = root
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[OperationError]:
        if not context or "ticket_id" not in context or "dependency_id" not in context:
            return None
        
        ticket_id = context["ticket_id"]
        dependency_id = context["dependency_id"]
        
        if ticket_id == dependency_id:
            return OperationError(
                code="SELF_DEPENDENCY",
                message="A ticket cannot depend on itself",
                details={"ticket_id": ticket_id}
            )
        
        # Check for circular dependencies
        if self._would_create_cycle(ticket_id, dependency_id):
            return OperationError(
                code="CIRCULAR_DEPENDENCY",
                message=f"Adding {dependency_id} as dependency of {ticket_id} would create a circular dependency",
                details={"ticket_id": ticket_id, "dependency_id": dependency_id}
            )
        
        return None
    
    def _would_create_cycle(self, ticket_id: str, dependency_id: str) -> bool:
        """Check if adding a dependency would create a cycle."""
        visited = set()
        
        def has_path(from_id: str, to_id: str) -> bool:
            if from_id == to_id:
                return True
            if from_id in visited:
                return False
            visited.add(from_id)
            
            ticket, _ = find_ticket(from_id, self.root)
            if ticket:
                for dep_id in ticket.blocked_by:
                    if has_path(dep_id, to_id):
                        return True
            return False
        
        return has_path(dependency_id, ticket_id)


class ValidationEngine:
    """Engine for validating bulk operations."""
    
    def __init__(self, root: Optional[Path] = None):
        self.root = root or ensure_gira_project()
        self._setup_validators()
    
    def _setup_validators(self):
        """Set up validators for different operation types."""
        # Status values
        status_values = {s.value for s in TicketStatus}
        priority_values = {p.value for p in TicketPriority}
        type_values = {t.value for t in TicketType}
        
        # Common validators
        self.ticket_exists_validator = TicketExistsRule(self.root, "id")
        
        # Field validators for bulk update
        self.update_validators = {
            "status": EnumFieldRule(status_values, "status"),
            "priority": EnumFieldRule(priority_values, "priority"),
            "type": EnumFieldRule(type_values, "type"),
            "epic": TicketExistsRule(self.root, "epic"),
            "parent": TicketExistsRule(self.root, "parent"),
        }
        
        # Dependency validators
        self.dependency_validators = {
            "circular": CircularDependencyRule(self.root),
            "dependency_exists": TicketExistsRule(self.root, "dependency_id"),
        }
    
    def validate_request(
        self,
        request: BulkOperationRequest,
        level: Optional[ValidationLevel] = None
    ) -> ValidationResult:
        """Validate a bulk operation request."""
        level = level or request.options.validation_level
        
        errors = []
        warnings = []
        item_validations = {}
        
        # Basic validation - just check required fields
        if level == ValidationLevel.NONE:
            return ValidationResult(is_valid=True)
        
        # Validate operation type specific rules
        if request.operation_type == OperationType.BULK_UPDATE:
            self._validate_bulk_update(request, errors, warnings, item_validations, level)
        elif request.operation_type in [OperationType.BULK_ADD_DEPS, OperationType.BULK_REMOVE_DEPS]:
            self._validate_bulk_dependencies(request, errors, warnings, item_validations, level)
        elif request.operation_type == OperationType.BULK_CLEAR_DEPS:
            self._validate_bulk_clear_deps(request, errors, warnings, item_validations, level)
        
        # Compile results
        is_valid = len(errors) == 0 and all(
            len(errs) == 0 for errs in item_validations.values()
        )
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            item_validations=item_validations
        )
    
    def _validate_bulk_update(
        self,
        request: BulkOperationRequest,
        errors: List[OperationError],
        warnings: List[OperationError],
        item_validations: Dict[str, List[OperationError]],
        level: ValidationLevel
    ):
        """Validate bulk update request."""
        for item in request.items:
            item_errors = []
            
            # Convert dict to BulkUpdateItem if needed
            if isinstance(item, dict):
                try:
                    item = BulkUpdateItem(**item)
                except Exception as e:
                    item_errors.append(OperationError(
                        code="INVALID_ITEM_FORMAT",
                        message=str(e),
                        item_id=item.get("id", "unknown")
                    ))
                    continue
            
            # Validate ticket exists
            if level != ValidationLevel.NONE:
                if error := self.ticket_exists_validator.validate(item.id):
                    error.item_id = item.id
                    item_errors.append(error)
                    continue
            
            # Validate fields if strict
            if level == ValidationLevel.STRICT:
                for field, validator in self.update_validators.items():
                    value = getattr(item, field, None)
                    if value is not None:
                        if error := validator.validate(value):
                            error.item_id = item.id
                            item_errors.append(error)
            
            if item_errors:
                item_validations[item.id] = item_errors
    
    def _validate_bulk_dependencies(
        self,
        request: BulkOperationRequest,
        errors: List[OperationError],
        warnings: List[OperationError],
        item_validations: Dict[str, List[OperationError]],
        level: ValidationLevel
    ):
        """Validate bulk dependency operations."""
        for item in request.items:
            item_errors = []
            
            # Convert dict to BulkDependencyItem if needed
            if isinstance(item, dict):
                try:
                    item = BulkDependencyItem(**item)
                except Exception as e:
                    item_errors.append(OperationError(
                        code="INVALID_ITEM_FORMAT",
                        message=str(e),
                        item_id=item.get("id", "unknown")
                    ))
                    continue
            
            # Validate ticket exists
            if error := self.ticket_exists_validator.validate(item.id):
                error.item_id = item.id
                item_errors.append(error)
                continue
            
            # Validate dependencies
            if level == ValidationLevel.STRICT:
                # Check dependency exists
                if item.dependency_id:
                    if error := self.dependency_validators["dependency_exists"].validate(item.dependency_id):
                        error.item_id = item.id
                        item_errors.append(error)
                    
                    # Check circular dependency for add operations
                    if request.operation_type == OperationType.BULK_ADD_DEPS:
                        context = {"ticket_id": item.id, "dependency_id": item.dependency_id}
                        if error := self.dependency_validators["circular"].validate(None, context):
                            error.item_id = item.id
                            item_errors.append(error)
                
                # Check multiple dependencies
                if item.dependencies:
                    for dep_id in item.dependencies:
                        if error := self.dependency_validators["dependency_exists"].validate(dep_id):
                            error.item_id = item.id
                            error.details = {"dependency_id": dep_id}
                            item_errors.append(error)
            
            if item_errors:
                item_validations[item.id] = item_errors
    
    def _validate_bulk_clear_deps(
        self,
        request: BulkOperationRequest,
        errors: List[OperationError],
        warnings: List[OperationError],
        item_validations: Dict[str, List[OperationError]],
        level: ValidationLevel
    ):
        """Validate bulk clear dependencies request."""
        for item in request.items:
            item_errors = []
            
            # Get item ID
            item_id = item.get("id") if isinstance(item, dict) else item.id
            
            # Validate ticket exists
            if error := self.ticket_exists_validator.validate(item_id):
                error.item_id = item_id
                item_errors.append(error)
            
            if item_errors:
                item_validations[item_id] = item_errors
    
    def validate_field(
        self,
        field_name: str,
        value: Any,
        operation_type: OperationType,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[OperationError]:
        """Validate a single field value."""
        if operation_type == OperationType.BULK_UPDATE and field_name in self.update_validators:
            return self.update_validators[field_name].validate(value, context)
        
        return None