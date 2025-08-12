"""Bulk update API for tickets."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from gira.api.bulk.manager import BulkOperationManager
from gira.api.bulk.schemas import (
    BulkOperationItem,
    BulkUpdateItem,
    OperationError,
    OperationResult,
    OperationType,
)
from gira.cli.commands.ticket.update import _apply_ticket_updates
from gira.utils.ticket_utils import find_ticket
from gira.utils.transaction import atomic_operation, TransactionError


class BulkUpdateManager(BulkOperationManager):
    """Manager for bulk update operations."""
    
    def __init__(self, root: Optional[Path] = None, **kwargs):
        """Initialize bulk update manager."""
        super().__init__(
            operation_type=OperationType.BULK_UPDATE,
            root=root,
            **kwargs
        )
    
    def get_item_class(self) -> Type[BulkOperationItem]:
        """Get the item class for bulk updates."""
        return BulkUpdateItem
    
    def process_item(
        self,
        item: Union[BulkUpdateItem, Dict[str, Any]],
        options: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Process a single update item."""
        # Convert dict to BulkUpdateItem if needed
        if isinstance(item, dict):
            try:
                item = BulkUpdateItem(**item)
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
        
        # Track changes
        changes = {}
        original_data = ticket.model_dump()
        
        try:
            # Apply updates based on options
            if options.get("use_transaction", False):
                self._apply_updates_transactional(
                    ticket, ticket_path, item, options, changes
                )
            else:
                self._apply_updates_direct(
                    ticket, ticket_path, item, options, changes
                )
            
            # Calculate what changed
            for field in ["title", "description", "status", "priority", "type", 
                         "assignee", "labels", "epic_id", "parent_id", "story_points"]:
                original_value = original_data.get(field)
                new_value = getattr(ticket, field, None)
                
                if original_value != new_value:
                    changes[field] = {
                        "old": original_value,
                        "new": new_value
                    }
            
            return OperationResult(
                item_id=item.id,
                status="success",
                changes=changes
            )
            
        except Exception as e:
            error = self.error_handler.handle_error(
                e,
                context={"item": item.model_dump()},
                item_id=item.id
            )
            return OperationResult(
                item_id=item.id,
                status="failed",
                error=error
            )
    
    def _apply_updates_direct(
        self,
        ticket,
        ticket_path: Path,
        item: BulkUpdateItem,
        options: Dict[str, Any],
        changes: Dict[str, Any]
    ):
        """Apply updates directly to the ticket."""
        # Use existing update logic
        _apply_ticket_updates(
            ticket=ticket,
            ticket_path=ticket_path,
            root=self.root,
            strict=options.get("strict", False),
            title=item.title,
            description=item.description,
            status=item.status,
            priority=item.priority,
            ticket_type=item.type,
            assignee=item.assignee,
            add_labels=",".join(item.add_labels) if item.add_labels else None,
            remove_labels=",".join(item.remove_labels) if item.remove_labels else None,
            epic=item.epic,
            parent=item.parent,
            story_points=item.story_points
        )
    
    def _apply_updates_transactional(
        self,
        ticket,
        ticket_path: Path,
        item: BulkUpdateItem,
        options: Dict[str, Any],
        changes: Dict[str, Any]
    ):
        """Apply updates using transaction support."""
        from datetime import datetime, timezone
        
        with atomic_operation() as tx:
            # Create updated ticket data
            ticket_dict = ticket.model_dump()
            
            # Apply updates to dictionary
            if item.title is not None:
                ticket_dict["title"] = item.title
            if item.description is not None:
                ticket_dict["description"] = item.description
            if item.status is not None:
                ticket_dict["status"] = item.status
            if item.priority is not None:
                ticket_dict["priority"] = item.priority
            if item.type is not None:
                ticket_dict["type"] = item.type
            if item.assignee is not None:
                ticket_dict["assignee"] = None if item.assignee.lower() == "none" else item.assignee
            if item.epic is not None:
                ticket_dict["epic_id"] = None if item.epic.lower() == "none" else item.epic
            if item.parent is not None:
                ticket_dict["parent_id"] = None if item.parent.lower() == "none" else item.parent
            if item.story_points is not None:
                ticket_dict["story_points"] = None if item.story_points == 0 else item.story_points
            
            # Handle labels
            if item.add_labels:
                current_labels = set(ticket_dict.get("labels", []))
                current_labels.update(item.add_labels)
                ticket_dict["labels"] = sorted(list(current_labels))
            if item.remove_labels:
                current_labels = set(ticket_dict.get("labels", []))
                current_labels -= set(item.remove_labels)
                ticket_dict["labels"] = sorted(list(current_labels))
            
            # Update timestamp
            ticket_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Add update operation to transaction
            tx.add_update(ticket_path, ticket_dict)
            
            # Update ticket object to reflect changes
            for key, value in ticket_dict.items():
                if hasattr(ticket, key):
                    setattr(ticket, key, value)


def create_bulk_update_api(root: Optional[Path] = None, **kwargs) -> BulkUpdateManager:
    """Create a bulk update API manager.
    
    Args:
        root: Project root directory
        **kwargs: Additional arguments for BulkOperationManager
        
    Returns:
        Configured BulkUpdateManager instance
    """
    return BulkUpdateManager(root=root, **kwargs)