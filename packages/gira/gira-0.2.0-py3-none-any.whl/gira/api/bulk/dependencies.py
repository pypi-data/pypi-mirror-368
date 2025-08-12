"""Bulk dependency operations API."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from gira.api.bulk.manager import BulkOperationManager
from gira.api.bulk.schemas import (
    BulkDependencyItem,
    BulkOperationItem,
    OperationError,
    OperationResult,
    OperationType,
)
from gira.utils.ticket_utils import find_ticket
from gira.utils.transaction import atomic_operation


class BulkDependencyManager(BulkOperationManager):
    """Base manager for bulk dependency operations."""
    
    def get_item_class(self) -> Type[BulkOperationItem]:
        """Get the item class for dependency operations."""
        return BulkDependencyItem
    
    def _get_dependencies_from_item(
        self, 
        item: Union[BulkDependencyItem, Dict[str, Any]]
    ) -> List[str]:
        """Extract dependency IDs from an item."""
        if isinstance(item, dict):
            # Handle various formats
            if item.get("remove_all", False):
                return ["*"]
            elif "dependency_id" in item and item["dependency_id"]:
                return [item["dependency_id"]]
            elif "dependencies" in item and item["dependencies"]:
                return item["dependencies"]
            else:
                return []
        else:
            if item.remove_all:
                return ["*"]
            elif item.dependency_id:
                return [item.dependency_id]
            elif item.dependencies:
                return item.dependencies
            else:
                return []


class BulkAddDependenciesManager(BulkDependencyManager):
    """Manager for bulk add dependencies operations."""
    
    def __init__(self, root: Optional[Path] = None, **kwargs):
        """Initialize bulk add dependencies manager."""
        super().__init__(
            operation_type=OperationType.BULK_ADD_DEPS,
            root=root,
            **kwargs
        )
    
    def process_item(
        self,
        item: Union[BulkDependencyItem, Dict[str, Any]],
        options: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Process a single add dependency item."""
        # Convert dict to BulkDependencyItem if needed
        if isinstance(item, dict):
            try:
                item = BulkDependencyItem(**item)
            except Exception as e:
                return OperationResult(
                    item_id=item.get("id", "unknown"),
                    status="failed",
                    error=OperationError(
                        code="INVALID_ITEM_FORMAT",
                        message=str(e),
                        item_id=item.get("id", "unknown")
                    )
                )
        
        # Find the ticket
        ticket, ticket_path = find_ticket(item.id, self.root)
        if not ticket:
            return OperationResult(
                item_id=item.id,
                status="failed",
                error=OperationError(
                    code="TICKET_NOT_FOUND",
                    message=f"Ticket {item.id} not found",
                    item_id=item.id
                )
            )
        
        # Get dependencies to add
        dependencies = self._get_dependencies_from_item(item)
        if not dependencies:
            return OperationResult(
                item_id=item.id,
                status="skipped",
                changes={"message": "No dependencies to add"}
            )
        
        # Track changes
        changes = {
            "added_dependencies": [],
            "reciprocal_updates": []
        }
        
        try:
            if options.get("use_transaction", False):
                self._add_dependencies_transactional(
                    ticket, ticket_path, dependencies, 
                    options.get("no_reciprocal", False), changes
                )
            else:
                self._add_dependencies_direct(
                    ticket, ticket_path, dependencies,
                    options.get("no_reciprocal", False), changes
                )
            
            return OperationResult(
                item_id=item.id,
                status="success",
                changes=changes
            )
            
        except Exception as e:
            error = self.error_handler.handle_error(
                e,
                context={"item": item.model_dump(), "dependencies": dependencies},
                item_id=item.id
            )
            return OperationResult(
                item_id=item.id,
                status="failed",
                error=error
            )
    
    def _add_dependencies_direct(
        self,
        ticket,
        ticket_path: Path,
        dependencies: List[str],
        no_reciprocal: bool,
        changes: Dict[str, Any]
    ):
        """Add dependencies directly."""
        modified_tickets = []
        
        for dep_id in dependencies:
            # Check if already exists
            if dep_id in ticket.blocked_by:
                continue
            
            # Find dependency ticket
            dep_ticket, dep_path = find_ticket(dep_id, self.root)
            if not dep_ticket:
                raise ValueError(f"Dependency ticket {dep_id} not found")
            
            # Add dependency
            ticket.blocked_by.append(dep_id)
            changes["added_dependencies"].append(dep_id)
            
            # Add reciprocal if needed
            if not no_reciprocal and ticket.id not in dep_ticket.blocks:
                dep_ticket.blocks.append(ticket.id)
                modified_tickets.append((dep_ticket, dep_path))
                changes["reciprocal_updates"].append(dep_id)
        
        # Sort and deduplicate
        ticket.blocked_by = sorted(list(set(ticket.blocked_by)))
        
        # Update timestamps and save
        timestamp = datetime.now(timezone.utc)
        ticket.updated_at = timestamp
        ticket.save_to_json_file(str(ticket_path))
        
        # Save modified dependency tickets
        for dep_ticket, dep_path in modified_tickets:
            dep_ticket.blocks = sorted(list(set(dep_ticket.blocks)))
            dep_ticket.updated_at = timestamp
            dep_ticket.save_to_json_file(str(dep_path))
    
    def _add_dependencies_transactional(
        self,
        ticket,
        ticket_path: Path,
        dependencies: List[str],
        no_reciprocal: bool,
        changes: Dict[str, Any]
    ):
        """Add dependencies using transaction support."""
        with atomic_operation() as tx:
            # Prepare ticket updates
            ticket_dict = ticket.model_dump()
            modified_deps = {}
            
            for dep_id in dependencies:
                # Check if already exists
                if dep_id in ticket_dict["blocked_by"]:
                    continue
                
                # Find dependency ticket
                dep_ticket, dep_path = find_ticket(dep_id, self.root)
                if not dep_ticket:
                    raise ValueError(f"Dependency ticket {dep_id} not found")
                
                # Add dependency
                ticket_dict["blocked_by"].append(dep_id)
                changes["added_dependencies"].append(dep_id)
                
                # Prepare reciprocal update if needed
                if not no_reciprocal and ticket.id not in dep_ticket.blocks:
                    if dep_id not in modified_deps:
                        modified_deps[dep_id] = (dep_ticket.model_dump(), dep_path)
                    modified_deps[dep_id][0]["blocks"].append(ticket.id)
                    changes["reciprocal_updates"].append(dep_id)
            
            # Sort and deduplicate
            ticket_dict["blocked_by"] = sorted(list(set(ticket_dict["blocked_by"])))
            
            # Update timestamps
            timestamp = datetime.now(timezone.utc).isoformat()
            ticket_dict["updated_at"] = timestamp
            
            # Add main ticket update to transaction
            tx.add_update(ticket_path, ticket_dict)
            
            # Add dependency updates to transaction
            for dep_id, (dep_dict, dep_path) in modified_deps.items():
                dep_dict["blocks"] = sorted(list(set(dep_dict["blocks"])))
                dep_dict["updated_at"] = timestamp
                tx.add_update(dep_path, dep_dict)


class BulkRemoveDependenciesManager(BulkDependencyManager):
    """Manager for bulk remove dependencies operations."""
    
    def __init__(self, root: Optional[Path] = None, **kwargs):
        """Initialize bulk remove dependencies manager."""
        super().__init__(
            operation_type=OperationType.BULK_REMOVE_DEPS,
            root=root,
            **kwargs
        )
    
    def process_item(
        self,
        item: Union[BulkDependencyItem, Dict[str, Any]],
        options: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Process a single remove dependency item."""
        # Convert dict to BulkDependencyItem if needed
        if isinstance(item, dict):
            try:
                item = BulkDependencyItem(**item)
            except Exception as e:
                return OperationResult(
                    item_id=item.get("id", "unknown"),
                    status="failed",
                    error=OperationError(
                        code="INVALID_ITEM_FORMAT",
                        message=str(e),
                        item_id=item.get("id", "unknown")
                    )
                )
        
        # Find the ticket
        ticket, ticket_path = find_ticket(item.id, self.root)
        if not ticket:
            return OperationResult(
                item_id=item.id,
                status="failed",
                error=OperationError(
                    code="TICKET_NOT_FOUND",
                    message=f"Ticket {item.id} not found",
                    item_id=item.id
                )
            )
        
        # Get dependencies to remove
        dependencies = self._get_dependencies_from_item(item)
        remove_all = dependencies == ["*"]
        
        if not dependencies or (not remove_all and not ticket.blocked_by):
            return OperationResult(
                item_id=item.id,
                status="skipped",
                changes={"message": "No dependencies to remove"}
            )
        
        # Track changes
        changes = {
            "removed_dependencies": [],
            "reciprocal_updates": []
        }
        
        try:
            if options.get("use_transaction", False):
                self._remove_dependencies_transactional(
                    ticket, ticket_path, dependencies, remove_all,
                    options.get("no_reciprocal", False), changes
                )
            else:
                self._remove_dependencies_direct(
                    ticket, ticket_path, dependencies, remove_all,
                    options.get("no_reciprocal", False), changes
                )
            
            return OperationResult(
                item_id=item.id,
                status="success",
                changes=changes
            )
            
        except Exception as e:
            error = self.error_handler.handle_error(
                e,
                context={"item": item.model_dump(), "dependencies": dependencies},
                item_id=item.id
            )
            return OperationResult(
                item_id=item.id,
                status="failed",
                error=error
            )
    
    def _remove_dependencies_direct(
        self,
        ticket,
        ticket_path: Path,
        dependencies: List[str],
        remove_all: bool,
        no_reciprocal: bool,
        changes: Dict[str, Any]
    ):
        """Remove dependencies directly."""
        modified_tickets = []
        
        if remove_all:
            # Remove all dependencies
            removed_deps = ticket.blocked_by.copy()
            ticket.blocked_by = []
            changes["removed_dependencies"] = removed_deps
            
            # Handle reciprocals
            if not no_reciprocal:
                for dep_id in removed_deps:
                    dep_ticket, dep_path = find_ticket(dep_id, self.root)
                    if dep_ticket and ticket.id in dep_ticket.blocks:
                        dep_ticket.blocks.remove(ticket.id)
                        modified_tickets.append((dep_ticket, dep_path))
                        changes["reciprocal_updates"].append(dep_id)
        else:
            # Remove specific dependencies
            for dep_id in dependencies:
                if dep_id in ticket.blocked_by:
                    ticket.blocked_by.remove(dep_id)
                    changes["removed_dependencies"].append(dep_id)
                    
                    # Handle reciprocal
                    if not no_reciprocal:
                        dep_ticket, dep_path = find_ticket(dep_id, self.root)
                        if dep_ticket and ticket.id in dep_ticket.blocks:
                            dep_ticket.blocks.remove(ticket.id)
                            modified_tickets.append((dep_ticket, dep_path))
                            changes["reciprocal_updates"].append(dep_id)
        
        # Update timestamps and save
        timestamp = datetime.now(timezone.utc)
        ticket.updated_at = timestamp
        ticket.save_to_json_file(str(ticket_path))
        
        # Save modified dependency tickets
        for dep_ticket, dep_path in modified_tickets:
            dep_ticket.updated_at = timestamp
            dep_ticket.save_to_json_file(str(dep_path))
    
    def _remove_dependencies_transactional(
        self,
        ticket,
        ticket_path: Path,
        dependencies: List[str],
        remove_all: bool,
        no_reciprocal: bool,
        changes: Dict[str, Any]
    ):
        """Remove dependencies using transaction support."""
        with atomic_operation() as tx:
            # Prepare ticket updates
            ticket_dict = ticket.model_dump()
            modified_deps = {}
            
            if remove_all:
                # Remove all dependencies
                removed_deps = ticket_dict["blocked_by"].copy()
                ticket_dict["blocked_by"] = []
                changes["removed_dependencies"] = removed_deps
                
                # Prepare reciprocal updates
                if not no_reciprocal:
                    for dep_id in removed_deps:
                        dep_ticket, dep_path = find_ticket(dep_id, self.root)
                        if dep_ticket and ticket.id in dep_ticket.blocks:
                            if dep_id not in modified_deps:
                                modified_deps[dep_id] = (dep_ticket.model_dump(), dep_path)
                            modified_deps[dep_id][0]["blocks"].remove(ticket.id)
                            changes["reciprocal_updates"].append(dep_id)
            else:
                # Remove specific dependencies
                for dep_id in dependencies:
                    if dep_id in ticket_dict["blocked_by"]:
                        ticket_dict["blocked_by"].remove(dep_id)
                        changes["removed_dependencies"].append(dep_id)
                        
                        # Prepare reciprocal update
                        if not no_reciprocal:
                            dep_ticket, dep_path = find_ticket(dep_id, self.root)
                            if dep_ticket and ticket.id in dep_ticket.blocks:
                                if dep_id not in modified_deps:
                                    modified_deps[dep_id] = (dep_ticket.model_dump(), dep_path)
                                modified_deps[dep_id][0]["blocks"].remove(ticket.id)
                                changes["reciprocal_updates"].append(dep_id)
            
            # Update timestamps
            timestamp = datetime.now(timezone.utc).isoformat()
            ticket_dict["updated_at"] = timestamp
            
            # Add main ticket update to transaction
            tx.add_update(ticket_path, ticket_dict)
            
            # Add dependency updates to transaction
            for dep_id, (dep_dict, dep_path) in modified_deps.items():
                dep_dict["updated_at"] = timestamp
                tx.add_update(dep_path, dep_dict)


class BulkClearDependenciesManager(BulkRemoveDependenciesManager):
    """Manager for bulk clear dependencies operations."""
    
    def __init__(self, root: Optional[Path] = None, **kwargs):
        """Initialize bulk clear dependencies manager."""
        # Call BulkDependencyManager.__init__ directly to set correct operation type
        BulkDependencyManager.__init__(
            self,
            operation_type=OperationType.BULK_CLEAR_DEPS,
            root=root,
            **kwargs
        )
    
    def process_item(
        self,
        item: Union[BulkDependencyItem, Dict[str, Any]],
        options: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Process a clear dependencies item."""
        # Force remove_all flag
        if isinstance(item, dict):
            item["remove_all"] = True
        else:
            item.remove_all = True
        
        # Use parent's process_item with remove_all set
        return super().process_item(item, options, context)


def create_bulk_add_deps_api(root: Optional[Path] = None, **kwargs) -> BulkAddDependenciesManager:
    """Create a bulk add dependencies API manager."""
    return BulkAddDependenciesManager(root=root, **kwargs)


def create_bulk_remove_deps_api(root: Optional[Path] = None, **kwargs) -> BulkRemoveDependenciesManager:
    """Create a bulk remove dependencies API manager."""
    return BulkRemoveDependenciesManager(root=root, **kwargs)


def create_bulk_clear_deps_api(root: Optional[Path] = None, **kwargs) -> BulkClearDependenciesManager:
    """Create a bulk clear dependencies API manager."""
    return BulkClearDependenciesManager(root=root, **kwargs)