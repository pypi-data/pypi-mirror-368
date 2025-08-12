"""Core ticket management tools for Gira MCP server."""

import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from gira.mcp.schema import OperationResult
from gira.mcp.security import secure_operation, require_gira_project, rate_limit
from gira.mcp.tools import (
    MCPToolError,
    NotFoundError,
    ValidationError,
    normalize_ticket_id,
    register_tool,
)
from gira.models import ProjectConfig, Ticket
from gira.models.ticket import TicketPriority, TicketType
from gira.utils.config import get_default_reporter
from gira.utils.project_management import get_project_root
from gira.utils.response_formatters import (
    format_ticket_summary,
    format_ticket_details,
    format_ticket_list,
    format_operation_result,
    format_bulk_operation_result,
)
from gira.utils.ticket_creation import (
    determine_initial_status,
    parse_labels,
    resolve_assignee,
    validate_ticket_fields,
)
from gira.utils.ticket_utils import (
    find_ticket,
    get_ticket_path,
    load_all_tickets,
    save_ticket,
)
from gira.utils.ticket_operations import create_ticket_with_validation

logger = logging.getLogger(__name__)




# Import from the new location for backward compatibility
from gira.utils.ticket_utils import _would_create_parent_cycle


class TicketListFilter(BaseModel):
    """Filters for listing tickets."""
    status: Optional[str] = Field(None, description="Filter by status (e.g., 'todo', 'in_progress', 'done')")
    assignee: Optional[str] = Field(None, description="Filter by assignee email or name")
    priority: Optional[str] = Field(None, description="Filter by priority (low, medium, high, critical)")
    type: Optional[str] = Field(None, description="Filter by type (task, bug, feature, epic, subtask)")
    epic: Optional[str] = Field(None, description="Filter by epic ID")
    labels: Optional[List[str]] = Field(None, description="Filter by labels (must contain all specified labels)")
    limit: Optional[int] = Field(None, description="Maximum number of tickets to return", ge=1, le=1000)


class TicketSummary(BaseModel):
    """Summary information for a ticket."""
    id: str
    title: str
    status: str
    priority: str
    type: str
    assignee: Optional[str] = None
    epic_id: Optional[str] = None
    labels: List[str] = []
    created_at: str
    updated_at: str


class TicketDetail(BaseModel):
    """Detailed information for a ticket."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    type: str
    reporter: Optional[str] = None
    assignee: Optional[str] = None
    epic_id: Optional[str] = None
    parent_id: Optional[str] = None
    labels: List[str] = []
    story_points: Optional[int] = None
    custom_fields: Dict[str, Any] = {}
    created_at: str
    updated_at: str


class TicketCreateRequest(BaseModel):
    """Request to create a new ticket."""
    title: str = Field(..., description="Ticket title", min_length=1, max_length=200)
    description: str = Field("", description="Ticket description")
    priority: str = Field("medium", description="Priority level (low, medium, high, critical)")
    type: str = Field("task", description="Ticket type (task, bug, feature, epic, subtask)")
    assignee: Optional[str] = Field(None, description="Assignee email or name")
    epic: Optional[str] = Field(None, description="Epic ID to associate with")
    parent: Optional[str] = Field(None, description="Parent ticket ID for subtasks")
    labels: Optional[List[str]] = Field(None, description="List of labels")
    story_points: Optional[int] = Field(None, description="Story points estimate", ge=0, le=100)
    status: Optional[str] = Field(None, description="Initial status (defaults to project default)")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom field values")


@register_tool(
    name="list_tickets",
    description="List tickets with optional filtering",
    schema=TicketListFilter.model_json_schema(),
)
@secure_operation("ticket.list")
@require_gira_project
@rate_limit(max_calls=2000, window_seconds=60)
def list_tickets(
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    type: Optional[str] = None,
    epic: Optional[str] = None,
    labels: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> OperationResult:
    """
    List tickets with optional filtering.

    Args:
        status: Filter by status (e.g., 'todo', 'in_progress', 'done')
        assignee: Filter by assignee email or name
        priority: Filter by priority (low, medium, high, critical)
        type: Filter by type (task, bug, feature, epic, subtask)
        epic: Filter by epic ID
        labels: Filter by labels (must contain all specified labels)
        limit: Maximum number of tickets to return (1-1000)

    Returns:
        OperationResult with list of ticket summaries
    """
    try:
        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Load all tickets
        all_tickets = load_all_tickets(root)

        # Apply filters
        filtered_tickets = []
        for ticket in all_tickets:
            # Status filter
            if status and ticket.status.lower() != status.lower():
                continue

            # Assignee filter
            if assignee and (
                not ticket.assignee or
                (assignee.lower() not in ticket.assignee.lower())
            ):
                continue

            # Priority filter
            if priority:
                ticket_priority = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
                if ticket_priority.lower() != priority.lower():
                    continue

            # Type filter
            if type:
                ticket_type = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)
                if ticket_type.lower() != type.lower():
                    continue

            # Epic filter
            if epic and (not ticket.epic_id or ticket.epic_id.upper() != normalize_epic_id(epic)):
                continue

            # Labels filter (must contain all specified labels)
            if labels and not all(label in ticket.labels for label in labels):
                continue

            filtered_tickets.append(ticket)

        # Apply limit
        if limit and limit > 0:
            filtered_tickets = filtered_tickets[:limit]

        # Convert to summaries
        summaries = []
        for ticket in filtered_tickets:
            # Handle both enum and string values
            priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
            type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)

            # Use unified formatter for consistent ticket summary
            summary = format_ticket_summary(ticket, include_fields=[
                "id", "title", "status", "priority", "type", "assignee", 
                "epic_id", "labels", "created_at", "updated_at"
            ])
            summaries.append(summary)

        return OperationResult(
            success=True,
            message=f"Found {len(summaries)} tickets",
            data={"tickets": summaries, "total_count": len(summaries)}
        )

    except (ValidationError, NotFoundError, PermissionError) as e:
        # Re-raise specific errors that should be handled by enhanced error handler
        raise
    except Exception as e:
        logger.exception("Error listing tickets")
        raise MCPToolError(f"Failed to list tickets: {str(e)}") from e


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


@register_tool(
    name="get_ticket",
    description="Get detailed information about a specific ticket",
    schema={"type": "object", "properties": {"ticket_id": {"type": "string", "description": "Ticket ID to retrieve"}}},
)
@secure_operation("ticket.get")
@require_gira_project
@rate_limit(max_calls=2000, window_seconds=60)
def get_ticket(ticket_id: str) -> OperationResult:
    """
    Get detailed information about a specific ticket.

    Args:
        ticket_id: The ticket ID to retrieve (will be normalized)

    Returns:
        OperationResult with detailed ticket information
    """
    try:
        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Normalize ticket ID
        normalized_id = normalize_ticket_id(ticket_id)

        # Find the ticket
        ticket, ticket_path = find_ticket(normalized_id, root)
        if not ticket:
            raise NotFoundError(f"Ticket {normalized_id} not found", "ticket", normalized_id)

        # Convert to detailed format
        # Handle both enum and string values
        priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
        type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)

        # Use unified formatter for consistent ticket details
        detail = format_ticket_details(ticket, include_context=True)

        return OperationResult(
            success=True,
            message=f"Retrieved ticket {normalized_id}",
            data={
                "ticket": detail,
                "file_path": str(ticket_path) if ticket_path else None
            }
        )

    except (ValidationError, NotFoundError, PermissionError, ConnectionError, TimeoutError, 
            OSError, FileNotFoundError) as e:
        # Re-raise specific errors that should be handled by enhanced error handler
        raise
    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error getting ticket {ticket_id}")
        raise MCPToolError(f"Failed to get ticket: {str(e)}") from e


@register_tool(
    name="create_ticket",
    description="Create a new ticket",
    schema=TicketCreateRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("ticket.create")
@require_gira_project
@rate_limit(max_calls=500, window_seconds=60)
def create_ticket(
    title: str,
    description: str = "",
    priority: str = "medium",
    type: str = "task",
    assignee: Optional[str] = None,
    epic: Optional[str] = None,
    parent: Optional[str] = None,
    labels: Optional[List[str]] = None,
    story_points: Optional[int] = None,
    status: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> OperationResult:
    """
    Create a new ticket using shared validation and creation logic.

    Args:
        title: Ticket title (required)
        description: Ticket description
        priority: Priority level (low, medium, high, critical)
        type: Ticket type (task, bug, feature, epic, subtask)
        assignee: Assignee email or name
        epic: Epic ID to associate with
        parent: Parent ticket ID for subtasks
        labels: List of labels
        story_points: Story points estimate (0-100)
        status: Initial status (defaults to project default)
        custom_fields: Custom field values

    Returns:
        OperationResult with created ticket information
    """
    try:
        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")
        
        # Use shared ticket creation logic with MCP interface type
        result = create_ticket_with_validation(
            title=title,
            root=root,
            description=description,
            priority=priority,
            ticket_type=type,
            assignee=assignee,
            epic=epic,
            parent=parent,
            labels=labels,
            story_points=story_points,
            status=status,
            custom_fields=custom_fields,
            interface_type="mcp",
            strict_assignee=False,
            interactive_fields=False
        )
        
        # Check for errors and convert to MCP exceptions
        if not result.success or result.errors:
            error_messages = "; ".join(result.errors)
            raise ValidationError(error_messages)
        
        ticket = result.ticket
        ticket_path = result.ticket_path
        
        # Convert warnings to logged messages (MCP style)
        for warning in result.warnings:
            logger.warning(f"Ticket creation warning: {warning}")
        
        # Convert to detail format for response
        # Handle both enum and string values
        priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
        type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)

        # Use unified formatter for consistent ticket details
        detail = format_ticket_details(ticket, include_context=True)
        
        # Include warnings in response message if any
        base_message = f"Created ticket {ticket.id}"
        if result.warnings:
            warning_summary = f" (warnings: {len(result.warnings)} issues)"
            message = base_message + warning_summary
        else:
            message = base_message

        return OperationResult(
            success=True,
            message=message,
            data={
                "ticket": detail,
                "file_path": str(ticket_path),
                "warnings": result.warnings if result.warnings else []
            }
        )

    except (ValidationError, NotFoundError, PermissionError, ConnectionError, TimeoutError, 
            OSError, FileNotFoundError) as e:
        # Re-raise specific errors that should be handled by enhanced error handler
        raise
    except MCPToolError:
        raise
    except Exception as e:
        logger.exception("Error creating ticket")
        raise MCPToolError(f"Failed to create ticket: {str(e)}") from e


# Additional Pydantic schemas for new tools
class TicketUpdateRequest(BaseModel):
    """Request to update an existing ticket."""
    ticket_id: str = Field(..., description="Ticket ID to update")
    title: Optional[str] = Field(None, description="New title", max_length=200)
    description: Optional[str] = Field(None, description="New description")
    priority: Optional[str] = Field(None, description="New priority (low, medium, high, critical)")
    type: Optional[str] = Field(None, description="New ticket type (task, bug, feature, epic, subtask)")
    assignee: Optional[str] = Field(None, description="New assignee email or name (use 'none' to clear)")
    epic: Optional[str] = Field(None, description="New epic ID (use 'none' to clear)")
    parent: Optional[str] = Field(None, description="New parent ticket ID (use 'none' to clear)")
    labels: Optional[List[str]] = Field(None, description="Complete list of labels (replaces existing)")
    add_labels: Optional[List[str]] = Field(None, description="Labels to add")
    remove_labels: Optional[List[str]] = Field(None, description="Labels to remove")
    story_points: Optional[int] = Field(None, description="Story points estimate (0 to clear)", ge=0, le=100)
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom field values to update")


class TicketMoveRequest(BaseModel):
    """Request to move ticket to different status."""
    ticket_id: str = Field(..., description="Ticket ID to move")
    status: str = Field(..., description="New status/swimlane")
    comment: Optional[str] = Field(None, description="Optional comment about the move")


class TicketAssignRequest(BaseModel):
    """Request to assign ticket to someone."""
    ticket_id: str = Field(..., description="Ticket ID to assign")
    assignee: str = Field(..., description="Assignee email or name (use 'none' to clear)")


class CommentAddRequest(BaseModel):
    """Request to add a comment to a ticket."""
    ticket_id: str = Field(..., description="Ticket ID to comment on")
    content: str = Field(..., description="Comment content", min_length=1)
    mentions: Optional[List[str]] = Field(None, description="List of users to mention (@username)")


class TicketSearchRequest(BaseModel):
    """Request to search tickets with full-text search."""
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(20, description="Maximum results to return", ge=1, le=100)
    include_archived: bool = Field(False, description="Include archived tickets in search")


class AdvancedFilterRequest(BaseModel):
    """Request for advanced ticket filtering."""
    status: Optional[List[str]] = Field(None, description="Filter by multiple statuses")
    assignee: Optional[List[str]] = Field(None, description="Filter by multiple assignees")
    priority: Optional[List[str]] = Field(None, description="Filter by multiple priorities")
    type: Optional[List[str]] = Field(None, description="Filter by multiple types")
    epic: Optional[List[str]] = Field(None, description="Filter by multiple epics")
    labels: Optional[List[str]] = Field(None, description="Filter by labels (OR logic)")
    labels_all: Optional[List[str]] = Field(None, description="Filter by labels (AND logic - must have all)")
    created_after: Optional[str] = Field(None, description="Created after date (ISO format)")
    created_before: Optional[str] = Field(None, description="Created before date (ISO format)")
    updated_after: Optional[str] = Field(None, description="Updated after date (ISO format)")
    updated_before: Optional[str] = Field(None, description="Updated before date (ISO format)")
    limit: Optional[int] = Field(None, description="Maximum results to return", ge=1, le=1000)


class BulkUpdateRequest(BaseModel):
    """Request to bulk update multiple tickets."""
    ticket_ids: List[str] = Field(..., description="List of ticket IDs to update", min_length=1)
    title: Optional[str] = Field(None, description="New title for all tickets")
    status: Optional[str] = Field(None, description="New status for all tickets")
    priority: Optional[str] = Field(None, description="New priority for all tickets")
    assignee: Optional[str] = Field(None, description="New assignee for all tickets")
    add_labels: Optional[List[str]] = Field(None, description="Labels to add to all tickets")
    remove_labels: Optional[List[str]] = Field(None, description="Labels to remove from all tickets")
    epic: Optional[str] = Field(None, description="New epic for all tickets")


# Phase 1: Update Operations
@register_tool(
    name="update_ticket",
    description="Update an existing ticket's fields",
    schema=TicketUpdateRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("ticket.update")
@require_gira_project
@rate_limit(max_calls=500, window_seconds=60)
def update_ticket(
    ticket_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    type: Optional[str] = None,
    assignee: Optional[str] = None,
    epic: Optional[str] = None,
    parent: Optional[str] = None,
    labels: Optional[List[str]] = None,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
    story_points: Optional[int] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> OperationResult:
    """
    Update an existing ticket's fields.

    Args:
        ticket_id: The ticket ID to update
        title: New title
        description: New description
        priority: New priority (low, medium, high, critical)
        type: New ticket type (task, bug, feature, epic, subtask)
        assignee: New assignee email or name (use 'none' to clear)
        epic: New epic ID (use 'none' to clear)
        parent: New parent ticket ID (use 'none' to clear)
        labels: Complete list of labels (replaces existing)
        add_labels: Labels to add to existing labels
        remove_labels: Labels to remove from existing labels
        story_points: Story points estimate (0 to clear)
        custom_fields: Custom field values to update

    Returns:
        OperationResult with updated ticket information
    """
    try:
        from gira.utils.ticket_creation import resolve_assignee
        from gira.constants import VALID_PRIORITIES, VALID_TYPES, normalize_status
        from gira.utils.board_config import get_board_configuration
        from datetime import datetime, timezone

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Normalize ticket ID
        normalized_id = normalize_ticket_id(ticket_id)

        # Find the ticket
        ticket, ticket_path = find_ticket(normalized_id, root)
        if not ticket:
            raise NotFoundError(f"Ticket {normalized_id} not found", "ticket", normalized_id)

        # Check if any changes requested
        has_changes = any([
            title is not None,
            description is not None,
            priority is not None,
            type is not None,
            assignee is not None,
            epic is not None,
            parent is not None,
            labels is not None,
            add_labels is not None,
            remove_labels is not None,
            story_points is not None,
            custom_fields is not None
        ])

        if not has_changes:
            return OperationResult(
                success=True,
                message=f"No changes specified for ticket {normalized_id}",
                data={"ticket_id": normalized_id}
            )

        original_status = ticket.status
        original_epic_id = ticket.epic_id
        changes = []

        # Apply updates
        if title is not None:
            if not title.strip():
                raise ValidationError("Title cannot be empty")
            if len(title) > 200:
                raise ValidationError("Title cannot exceed 200 characters")
            ticket.title = title.strip()
            changes.append("title")

        if description is not None:
            ticket.description = description
            changes.append("description")

        if priority is not None:
            if priority.lower() not in VALID_PRIORITIES:
                raise ValidationError(f"Invalid priority '{priority}'. Valid: {', '.join(VALID_PRIORITIES)}")
            ticket.priority = TicketPriority(priority.lower())
            changes.append("priority")

        if type is not None:
            if type.lower() not in VALID_TYPES:
                raise ValidationError(f"Invalid type '{type}'. Valid: {', '.join(VALID_TYPES)}")
            ticket.type = TicketType(type.lower())
            changes.append("type")

        if assignee is not None:
            if assignee.lower() == "none":
                ticket.assignee = None
                changes.append("assignee (cleared)")
            else:
                try:
                    resolved_assignee, warnings = resolve_assignee(assignee, root, strict=False)
                    ticket.assignee = resolved_assignee
                    changes.append("assignee")
                    # Log warnings but don't fail
                    for warning in warnings:
                        logger.warning(f"Assignee warning: {warning}")
                except ValueError as e:
                    raise ValidationError(f"Assignee error: {str(e)}") from e

        if epic is not None:
            if epic.lower() == "none":
                ticket.epic_id = None
                changes.append("epic (cleared)")
            else:
                # Normalize epic ID
                normalized_epic = normalize_epic_id(epic)
                ticket.epic_id = normalized_epic
                changes.append("epic")

        if parent is not None:
            if parent.lower() == "none":
                ticket.parent_id = None
                changes.append("parent (cleared)")
            else:
                normalized_parent = normalize_ticket_id(parent)
                
                # Check if the proposed parent exists
                parent_ticket, _ = find_ticket(normalized_parent, root)
                if not parent_ticket:
                    raise NotFoundError(f"Parent ticket {normalized_parent} not found", "ticket", normalized_parent)
                
                # Check for circular dependency
                if _would_create_parent_cycle(normalized_id, normalized_parent, root):
                    raise ValidationError(
                        f"Cannot set {normalized_parent} as parent of {normalized_id}: "
                        f"this would create a circular parent-child dependency"
                    )
                
                ticket.parent_id = normalized_parent
                changes.append("parent")

        # Handle labels - either replace completely or add/remove
        if labels is not None:
            # Replace all labels
            ticket.labels = [label.lower().strip() for label in labels if label.strip()]
            changes.append("labels (replaced)")
        else:
            # Add/remove specific labels
            if add_labels is not None:
                new_labels = [lbl.strip().lower() for lbl in add_labels if lbl.strip()]
                for label in new_labels:
                    if label not in [lbl.lower() for lbl in ticket.labels]:
                        ticket.labels.append(label)
                if new_labels:
                    changes.append(f"added labels: {', '.join(new_labels)}")

            if remove_labels is not None:
                labels_to_remove = [lbl.strip().lower() for lbl in remove_labels if lbl.strip()]
                original_count = len(ticket.labels)
                ticket.labels = [lbl for lbl in ticket.labels if lbl.lower() not in labels_to_remove]
                if len(ticket.labels) < original_count:
                    changes.append(f"removed labels: {', '.join(labels_to_remove)}")

        if story_points is not None:
            if story_points == 0:
                ticket.story_points = None
                changes.append("story_points (cleared)")
            else:
                if not (0 <= story_points <= 100):
                    raise ValidationError("Story points must be between 0 and 100")
                ticket.story_points = story_points
                changes.append("story_points")

        if custom_fields is not None:
            # Merge with existing custom fields
            ticket.custom_fields = {**ticket.custom_fields, **custom_fields}
            changes.append("custom_fields")

        # Update timestamp
        ticket.updated_at = datetime.now(timezone.utc)

        # Sync epic-ticket relationship if epic was changed
        if epic is not None:
            from gira.utils.epic_utils import sync_epic_ticket_relationship
            sync_epic_ticket_relationship(
                ticket.id,
                original_epic_id,
                ticket.epic_id,
                root
            )

        # Save ticket (no status change, so save in place)
        save_ticket(ticket, ticket_path)

        # Use unified formatter for consistent ticket details
        detail = format_ticket_details(ticket, include_context=True)

        return OperationResult(
            success=True,
            message=f"Updated ticket {normalized_id}: {', '.join(changes) if changes else 'no changes'}",
            data={
                "ticket": detail,
                "changes": changes,
                "file_path": str(ticket_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error updating ticket {ticket_id}")
        raise MCPToolError(f"Failed to update ticket: {str(e)}") from e


@register_tool(
    name="move_ticket",
    description="Move a ticket to a different status/swimlane",
    schema=TicketMoveRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("ticket.move")
@require_gira_project
@rate_limit(max_calls=500, window_seconds=60)
def move_ticket(
    ticket_id: str,
    status: str,
    comment: Optional[str] = None,
    use_git: Optional[bool] = None,
) -> OperationResult:
    """
    Move a ticket to a different status/swimlane.

    Args:
        ticket_id: The ticket ID to move
        status: New status/swimlane
        comment: Optional comment about the move
        use_git: Use git operations for moving (auto-detected if None)

    Returns:
        OperationResult with updated ticket information
    """
    try:
        from gira.constants import normalize_status
        from gira.utils.board_config import get_board_configuration
        from datetime import datetime, timezone

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Normalize ticket ID
        normalized_id = normalize_ticket_id(ticket_id)

        # Find the ticket
        ticket, ticket_path = find_ticket(normalized_id, root)
        if not ticket:
            raise NotFoundError(f"Ticket {normalized_id} not found", "ticket", normalized_id)

        # Validate status
        board = get_board_configuration()
        normalized_status = normalize_status(status)
        if not board.is_valid_status(normalized_status):
            valid_statuses = board.get_valid_statuses()
            raise ValidationError(f"Invalid status '{status}'. Valid: {', '.join(valid_statuses)}")

        original_status = ticket.status

        # Check if status is actually changing
        if ticket.status == normalized_status:
            return OperationResult(
                success=True,
                message=f"Ticket {normalized_id} is already in status '{normalized_status}'",
                data={"ticket_id": normalized_id, "status": normalized_status}
            )

        # Update status and timestamp
        ticket.status = normalized_status
        ticket.updated_at = datetime.now(timezone.utc)

        # Get new path based on status
        new_path = get_ticket_path(ticket.id, ticket.status, root)

        # Move file with git-aware operations when appropriate
        if ticket_path != new_path:
            # Import git operations
            from gira.utils.git_ops import should_use_git, move_with_git_fallback
            
            # Determine if we should use git operations
            if use_git is None:
                use_git = should_use_git(root, operation="move")
            
            # Use git-aware move with fallback
            new_path = move_with_git_fallback(
                source=ticket_path,
                destination=new_path,
                root=root,
                use_git=use_git,
                silent=True  # Suppress warnings for internal operations
            )

        # Save updated ticket data to the new location
        save_ticket(ticket, new_path)

        # Add comment about the move if provided
        if comment:
            try:
                from gira.models.comment import Comment
                from gira.utils.config import get_default_reporter

                author = get_default_reporter()
                move_comment = Comment(
                    id=Comment.generate_id(),
                    ticket_id=ticket.id,
                    author=author,
                    content=f"**Status changed**: {original_status} → {normalized_status}\n\n{comment}",
                )
                
                # Add comment to ticket
                ticket.comments.append(move_comment)
                ticket.comment_count = len(ticket.comments)
                
                # Save again with comment
                save_ticket(ticket, new_path)
            except Exception as e:
                logger.warning(f"Failed to add move comment: {e}")

        # Use unified formatter for consistent ticket details
        detail = format_ticket_details(ticket, include_context=True)

        return OperationResult(
            success=True,
            message=f"Moved ticket {normalized_id} from '{original_status}' to '{normalized_status}'",
            data={
                "ticket": detail,
                "original_status": original_status,
                "new_status": normalized_status,
                "file_path": str(new_path),
                "comment_added": comment is not None
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error moving ticket {ticket_id}")
        raise MCPToolError(f"Failed to move ticket: {str(e)}") from e


@register_tool(
    name="assign_ticket",
    description="Assign a ticket to someone",
    schema=TicketAssignRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("ticket.assign")
@require_gira_project
@rate_limit(max_calls=500, window_seconds=60)
def assign_ticket(
    ticket_id: str,
    assignee: str,
) -> OperationResult:
    """
    Assign a ticket to someone.

    Args:
        ticket_id: The ticket ID to assign
        assignee: Assignee email or name (use 'none' to clear)

    Returns:
        OperationResult with updated ticket information
    """
    try:
        from gira.utils.ticket_creation import resolve_assignee
        from datetime import datetime, timezone

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Normalize ticket ID
        normalized_id = normalize_ticket_id(ticket_id)

        # Find the ticket
        ticket, ticket_path = find_ticket(normalized_id, root)
        if not ticket:
            raise NotFoundError(f"Ticket {normalized_id} not found", "ticket", normalized_id)

        original_assignee = ticket.assignee

        # Handle assignment
        if assignee.lower() == "none":
            ticket.assignee = None
            assignment_message = f"Cleared assignee for ticket {normalized_id}"
        else:
            try:
                resolved_assignee, warnings = resolve_assignee(assignee, root, strict=False)
                ticket.assignee = resolved_assignee
                assignment_message = f"Assigned ticket {normalized_id} to {resolved_assignee}"
                # Log warnings but don't fail
                for warning in warnings:
                    logger.warning(f"Assignee warning: {warning}")
            except ValueError as e:
                raise ValidationError(f"Assignee error: {str(e)}") from e

        # Update timestamp
        ticket.updated_at = datetime.now(timezone.utc)

        # Save ticket
        save_ticket(ticket, ticket_path)

        # Use unified formatter for consistent ticket details
        detail = format_ticket_details(ticket, include_context=True)

        return OperationResult(
            success=True,
            message=assignment_message,
            data={
                "ticket": detail,
                "original_assignee": original_assignee,
                "new_assignee": ticket.assignee,
                "file_path": str(ticket_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error assigning ticket {ticket_id}")
        raise MCPToolError(f"Failed to assign ticket: {str(e)}") from e


# Phase 2: Comment Operations
@register_tool(
    name="add_comment",
    description="Add a comment to a ticket",
    schema=CommentAddRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("comment.add")
@require_gira_project
@rate_limit(max_calls=500, window_seconds=60)
def add_comment(
    ticket_id: str,
    content: str,
    mentions: Optional[List[str]] = None,
) -> OperationResult:
    """
    Add a comment to a ticket.

    Args:
        ticket_id: The ticket ID to comment on
        content: Comment content
        mentions: List of users to mention (@username)

    Returns:
        OperationResult with comment information
    """
    try:
        from gira.models.comment import Comment
        from gira.utils.config import get_default_reporter
        from datetime import datetime, timezone

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Normalize ticket ID
        normalized_id = normalize_ticket_id(ticket_id)

        # Find the ticket
        ticket, ticket_path = find_ticket(normalized_id, root)
        if not ticket:
            raise NotFoundError(f"Ticket {normalized_id} not found", "ticket", normalized_id)

        # Validate content
        if not content or not content.strip():
            raise ValidationError("Comment content cannot be empty")

        # Get author
        author = get_default_reporter()

        # Process mentions if provided
        processed_content = content
        if mentions:
            # Simple mention processing - just ensure @ prefix
            for mention in mentions:
                username = mention.lstrip('@')
                if f"@{username}" not in processed_content:
                    processed_content += f"\n\n@{username}"

        # Create comment
        comment = Comment(
            id=Comment.generate_id(),
            ticket_id=ticket.id,
            author=author,
            content=processed_content.strip(),
        )

        # Add comment to ticket
        ticket.comments.append(comment)
        ticket.comment_count = len(ticket.comments)
        ticket.updated_at = datetime.now(timezone.utc)

        # Save ticket
        save_ticket(ticket, ticket_path)

        # Convert comment to dict for response
        comment_data = {
            "id": comment.id,
            "ticket_id": comment.ticket_id,
            "author": comment.author,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
            "edited": comment.edited,
            "edit_count": comment.edit_count,
            "is_ai_generated": comment.is_ai_generated,
            "attachments": comment.attachments,
            "attachment_count": comment.attachment_count,
        }

        return OperationResult(
            success=True,
            message=f"Added comment to ticket {normalized_id}",
            data={
                "comment": comment_data,
                "ticket_id": normalized_id,
                "total_comments": ticket.comment_count,
                "mentions": mentions or [],
                "file_path": str(ticket_path)
            }
        )

    except (ValidationError, NotFoundError, PermissionError, ConnectionError, TimeoutError, 
            OSError, FileNotFoundError) as e:
        # Re-raise specific errors that should be handled by enhanced error handler
        raise
    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error adding comment to ticket {ticket_id}")
        raise MCPToolError(f"Failed to add comment: {str(e)}") from e


@register_tool(
    name="list_comments",
    description="List comments for a ticket",
    schema={"type": "object", "properties": {
        "ticket_id": {"type": "string", "description": "Ticket ID to get comments for"},
        "limit": {"type": "integer", "description": "Maximum number of comments to return", "minimum": 1, "maximum": 100}
    }, "required": ["ticket_id"]},
)
@secure_operation("comment.list")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
def list_comments(
    ticket_id: str,
    limit: Optional[int] = None,
) -> OperationResult:
    """
    List comments for a ticket.

    Args:
        ticket_id: The ticket ID to get comments for
        limit: Maximum number of comments to return

    Returns:
        OperationResult with list of comments
    """
    try:
        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Normalize ticket ID
        normalized_id = normalize_ticket_id(ticket_id)

        # Find the ticket
        ticket, ticket_path = find_ticket(normalized_id, root)
        if not ticket:
            raise NotFoundError(f"Ticket {normalized_id} not found", "ticket", normalized_id)

        # Get comments
        comments = ticket.comments or []

        # Apply limit if specified
        if limit and limit > 0:
            comments = comments[-limit:]  # Get most recent comments

        # Convert comments to dict format
        comment_data = []
        for comment in comments:
            comment_dict = {
                "id": comment.id,
                "ticket_id": comment.ticket_id,
                "author": comment.author,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "updated_at": comment.updated_at.isoformat(),
                "edited": comment.edited,
                "edit_count": comment.edit_count,
                "is_ai_generated": comment.is_ai_generated,
                "attachments": comment.attachments,
                "attachment_count": comment.attachment_count,
            }
            comment_data.append(comment_dict)

        return OperationResult(
            success=True,
            message=f"Retrieved {len(comment_data)} comments for ticket {normalized_id}",
            data={
                "comments": comment_data,
                "ticket_id": normalized_id,
                "total_comments": ticket.comment_count,
                "returned_count": len(comment_data),
                "file_path": str(ticket_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error listing comments for ticket {ticket_id}")
        raise MCPToolError(f"Failed to list comments: {str(e)}") from e


# Phase 3: Advanced Queries
@register_tool(
    name="search_tickets",
    description="Search tickets using full-text search",
    schema=TicketSearchRequest.model_json_schema(),
)
@secure_operation("ticket.search")
@require_gira_project
@rate_limit(max_calls=1500, window_seconds=60)
def search_tickets(
    query: str,
    limit: Optional[int] = 20,
    include_archived: bool = False,
) -> OperationResult:
    """
    Search tickets using full-text search.

    Args:
        query: Search query
        limit: Maximum results to return (1-100)
        include_archived: Include archived tickets in search

    Returns:
        OperationResult with list of matching tickets
    """
    try:
        import re
        from datetime import datetime, timezone

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Validate inputs
        if not query or not query.strip():
            raise ValidationError("Search query cannot be empty")

        if limit is None or limit <= 0:
            limit = 20
        elif limit > 100:
            limit = 100

        # Load all tickets
        all_tickets = load_all_tickets(root, include_archived=include_archived)

        # Simple full-text search implementation
        query_lower = query.lower().strip()
        query_words = re.findall(r'\b\w+\b', query_lower)
        
        matching_tickets = []
        
        for ticket in all_tickets:
            # Search in title, description, and comments
            searchable_text = ""
            searchable_text += (ticket.title or "").lower()
            searchable_text += " " + (ticket.description or "").lower()
            
            # Include comment content in search
            for comment in (ticket.comments or []):
                searchable_text += " " + (comment.content or "").lower()
            
            # Include labels and epic info
            searchable_text += " " + " ".join(ticket.labels or [])
            if ticket.epic_id:
                searchable_text += " " + ticket.epic_id.lower()
            
            # Check if any query words match
            matches = 0
            for word in query_words:
                if word in searchable_text:
                    matches += 1
            
            # Calculate relevance score (percentage of query words that match)
            if matches > 0:
                relevance = matches / len(query_words) if query_words else 0
                matching_tickets.append((ticket, relevance))

        # Sort by relevance (highest first)
        matching_tickets.sort(key=lambda x: x[1], reverse=True)
        
        # Apply limit
        limited_tickets = matching_tickets[:limit]

        # Convert to summaries
        summaries = []
        for ticket, relevance in limited_tickets:
            # Handle both enum and string values
            priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
            type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)

            # Use unified formatter for consistent ticket summary
            summary = format_ticket_summary(ticket, include_fields=[
                "id", "title", "status", "priority", "type", "assignee", 
                "epic_id", "labels", "created_at", "updated_at"
            ])
            summary["relevance_score"] = round(relevance, 3)
            summaries.append(summary)

        return OperationResult(
            success=True,
            message=f"Found {len(summaries)} tickets matching '{query}'",
            data={
                "tickets": summaries,
                "query": query,
                "total_matches": len(matching_tickets),
                "returned_count": len(summaries),
                "include_archived": include_archived,
                "limit": limit
            }
        )

    except (ValidationError, NotFoundError, PermissionError, ConnectionError, TimeoutError, 
            OSError, FileNotFoundError) as e:
        # Re-raise specific errors that should be handled by enhanced error handler
        raise
    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error searching tickets with query '{query}'")
        raise MCPToolError(f"Failed to search tickets: {str(e)}") from e


@register_tool(
    name="filter_tickets",
    description="Advanced filtering of tickets with multiple criteria",
    schema=AdvancedFilterRequest.model_json_schema(),
)
@secure_operation("ticket.filter")
@require_gira_project
@rate_limit(max_calls=500, window_seconds=60)
def filter_tickets(
    status: Optional[List[str]] = None,
    assignee: Optional[List[str]] = None,
    priority: Optional[List[str]] = None,
    type: Optional[List[str]] = None,
    epic: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    labels_all: Optional[List[str]] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    limit: Optional[int] = None,
) -> OperationResult:
    """
    Advanced filtering of tickets with multiple criteria.

    Args:
        status: Filter by multiple statuses
        assignee: Filter by multiple assignees
        priority: Filter by multiple priorities
        type: Filter by multiple types
        epic: Filter by multiple epics
        labels: Filter by labels (OR logic)
        labels_all: Filter by labels (AND logic - must have all)
        created_after: Created after date (ISO format)
        created_before: Created before date (ISO format)
        updated_after: Updated after date (ISO format)
        updated_before: Updated before date (ISO format)
        limit: Maximum results to return

    Returns:
        OperationResult with filtered tickets
    """
    try:
        from datetime import datetime

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Parse date filters
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                # Try ISO format first
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try common date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                    raise ValueError(f"Unable to parse date: {date_str}")
                except ValueError as e:
                    raise ValidationError(f"Invalid date format '{date_str}': {str(e)}")

        created_after_dt = parse_date(created_after)
        created_before_dt = parse_date(created_before)
        updated_after_dt = parse_date(updated_after)
        updated_before_dt = parse_date(updated_before)

        # Load all tickets
        all_tickets = load_all_tickets(root)

        # Apply filters
        filtered_tickets = []
        for ticket in all_tickets:
            # Status filter
            if status and ticket.status.lower() not in [s.lower() for s in status]:
                continue

            # Assignee filter
            if assignee:
                if not ticket.assignee:
                    # No assignee, check if "none" or "unassigned" is in filter
                    if not any(a.lower() in ['none', 'unassigned', ''] for a in assignee):
                        continue
                else:
                    # Has assignee, check if it matches any filter
                    assignee_match = False
                    for a in assignee:
                        if a.lower() in ticket.assignee.lower():
                            assignee_match = True
                            break
                    if not assignee_match:
                        continue

            # Priority filter
            if priority:
                ticket_priority = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
                if ticket_priority.lower() not in [p.lower() for p in priority]:
                    continue

            # Type filter
            if type:
                ticket_type = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)
                if ticket_type.lower() not in [t.lower() for t in type]:
                    continue

            # Epic filter
            if epic:
                if not ticket.epic_id:
                    # No epic, check if "none" is in filter
                    if not any(e.lower() in ['none', ''] for e in epic):
                        continue
                else:
                    # Has epic, normalize and check
                    epic_match = False
                    for e in epic:
                        try:
                            normalized_epic = normalize_epic_id(e) if e.lower() not in ['none', ''] else None
                            if ticket.epic_id == normalized_epic:
                                epic_match = True
                                break
                        except (ValidationError, ValueError):
                            # Skip invalid epic IDs
                            continue
                    if not epic_match:
                        continue

            # Labels filter (OR logic)
            if labels:
                ticket_labels_lower = [lbl.lower() for lbl in ticket.labels]
                if not any(lbl.lower() in ticket_labels_lower for lbl in labels):
                    continue

            # Labels filter (AND logic - must have all)
            if labels_all:
                ticket_labels_lower = [lbl.lower() for lbl in ticket.labels]
                if not all(lbl.lower() in ticket_labels_lower for lbl in labels_all):
                    continue

            # Date filters
            if created_after_dt and ticket.created_at < created_after_dt:
                continue
            if created_before_dt and ticket.created_at > created_before_dt:
                continue
            if updated_after_dt and ticket.updated_at < updated_after_dt:
                continue
            if updated_before_dt and ticket.updated_at > updated_before_dt:
                continue

            filtered_tickets.append(ticket)

        # Apply limit
        if limit and limit > 0:
            filtered_tickets = filtered_tickets[:limit]

        # Convert to summaries
        summaries = []
        for ticket in filtered_tickets:
            # Handle both enum and string values
            priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
            type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)

            # Use unified formatter for consistent ticket summary
            summary = format_ticket_summary(ticket, include_fields=[
                "id", "title", "status", "priority", "type", "assignee", 
                "epic_id", "labels", "created_at", "updated_at"
            ])
            summaries.append(summary)

        return OperationResult(
            success=True,
            message=f"Filtered {len(summaries)} tickets with advanced criteria",
            data={
                "tickets": summaries,
                "total_count": len(summaries),
                "filters_applied": {
                    "status": status,
                    "assignee": assignee,
                    "priority": priority,
                    "type": type,
                    "epic": epic,
                    "labels": labels,
                    "labels_all": labels_all,
                    "created_after": created_after,
                    "created_before": created_before,
                    "updated_after": updated_after,
                    "updated_before": updated_before,
                    "limit": limit
                }
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception("Error filtering tickets")
        raise MCPToolError(f"Failed to filter tickets: {str(e)}") from e


@register_tool(
    name="get_board_state",
    description="Get current board state visualization",
    schema={"type": "object", "properties": {
        "include_counts": {"type": "boolean", "description": "Include ticket counts per status", "default": True},
        "include_tickets": {"type": "boolean", "description": "Include ticket details in each status", "default": False}
    }},
)
@secure_operation("board.state")
@require_gira_project
@rate_limit(max_calls=500, window_seconds=60)
def get_board_state(
    include_counts: bool = True,
    include_tickets: bool = False,
) -> OperationResult:
    """
    Get current board state visualization.

    Args:
        include_counts: Include ticket counts per status
        include_tickets: Include ticket details in each status

    Returns:
        OperationResult with board state information
    """
    try:
        from gira.utils.board_config import get_board_configuration
        from collections import defaultdict

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Load board configuration
        board = get_board_configuration()
        
        # Load all tickets
        all_tickets = load_all_tickets(root)

        # Group tickets by status
        tickets_by_status = defaultdict(list)
        for ticket in all_tickets:
            tickets_by_status[ticket.status].append(ticket)

        # Build board state
        board_state = {
            "swimlanes": [],
            "total_tickets": len(all_tickets)
        }

        for swimlane in board.swimlanes:
            tickets_in_status = tickets_by_status.get(swimlane.id, [])
            
            swimlane_data = {
                "id": swimlane.id,
                "name": swimlane.name,
                "description": swimlane.description
            }

            if include_counts:
                swimlane_data["ticket_count"] = len(tickets_in_status)

            if include_tickets:
                # Convert tickets to summaries
                ticket_summaries = []
                for ticket in tickets_in_status:
                    priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
                    type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)

                    # Use unified formatter for consistent ticket summary
                    summary = format_ticket_summary(ticket, include_fields=[
                        "id", "title", "status", "priority", "type", "assignee", 
                        "epic_id", "labels", "created_at", "updated_at"
                    ])
                    ticket_summaries.append(summary)
                
                swimlane_data["tickets"] = ticket_summaries

            board_state["swimlanes"].append(swimlane_data)

        # Add summary statistics
        if include_counts:
            board_state["summary"] = {
                "total_tickets": len(all_tickets),
                "tickets_by_status": {
                    swimlane.id: len(tickets_by_status.get(swimlane.id, []))
                    for swimlane in board.swimlanes
                },
                "tickets_by_priority": {},
                "tickets_by_type": {},
                "assigned_vs_unassigned": {
                    "assigned": len([t for t in all_tickets if t.assignee]),
                    "unassigned": len([t for t in all_tickets if not t.assignee])
                }
            }

            # Count by priority
            priority_counts = defaultdict(int)
            for ticket in all_tickets:
                priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
                priority_counts[priority_value] += 1
            board_state["summary"]["tickets_by_priority"] = dict(priority_counts)

            # Count by type
            type_counts = defaultdict(int)
            for ticket in all_tickets:
                type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)
                type_counts[type_value] += 1
            board_state["summary"]["tickets_by_type"] = dict(type_counts)

        return OperationResult(
            success=True,
            message=f"Retrieved board state with {len(board.swimlanes)} swimlanes and {len(all_tickets)} tickets",
            data={
                "board_state": board_state,
                "include_counts": include_counts,
                "include_tickets": include_tickets
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception("Error getting board state")
        raise MCPToolError(f"Failed to get board state: {str(e)}") from e


# Phase 4: Bulk Operations
@register_tool(
    name="bulk_update",
    description="Update multiple tickets with the same changes",
    schema=BulkUpdateRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("ticket.bulk_update")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def bulk_update(
    ticket_ids: List[str],
    title: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
    epic: Optional[str] = None,
) -> OperationResult:
    """
    Update multiple tickets with the same changes.

    Args:
        ticket_ids: List of ticket IDs to update
        title: New title for all tickets
        status: New status for all tickets
        priority: New priority for all tickets
        assignee: New assignee for all tickets
        add_labels: Labels to add to all tickets
        remove_labels: Labels to remove from all tickets
        epic: New epic for all tickets

    Returns:
        OperationResult with bulk update results
    """
    try:
        from gira.utils.ticket_creation import resolve_assignee
        from gira.constants import VALID_PRIORITIES, VALID_TYPES, normalize_status
        from gira.utils.board_config import get_board_configuration
        from datetime import datetime, timezone

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Validate inputs
        if not ticket_ids:
            raise ValidationError("No ticket IDs provided")

        # Check if any changes requested
        has_changes = any([
            title is not None,
            status is not None,
            priority is not None,
            assignee is not None,
            add_labels is not None,
            remove_labels is not None,
            epic is not None
        ])

        if not has_changes:
            raise ValidationError("No changes specified")

        # Validate change parameters before processing any tickets
        if status is not None:
            board = get_board_configuration()
            normalized_status = normalize_status(status)
            if not board.is_valid_status(normalized_status):
                valid_statuses = board.get_valid_statuses()
                raise ValidationError(f"Invalid status '{status}'. Valid: {', '.join(valid_statuses)}")

        if priority is not None:
            if priority.lower() not in VALID_PRIORITIES:
                raise ValidationError(f"Invalid priority '{priority}'. Valid: {', '.join(VALID_PRIORITIES)}")

        # Resolve assignee once if specified
        resolved_assignee = None
        if assignee is not None:
            if assignee.lower() != "none":
                try:
                    resolved_assignee, warnings = resolve_assignee(assignee, root, strict=False)
                    # Log warnings but don't fail
                    for warning in warnings:
                        logger.warning(f"Assignee warning: {warning}")
                except ValueError as e:
                    raise ValidationError(f"Assignee error: {str(e)}") from e

        # Process tickets
        successful_updates = []
        failed_updates = []
        moved_files = []

        for ticket_id in ticket_ids:
            try:
                # Normalize ticket ID
                normalized_id = normalize_ticket_id(ticket_id)

                # Find the ticket
                ticket, ticket_path = find_ticket(normalized_id, root)
                if not ticket:
                    failed_updates.append({
                        "ticket_id": normalized_id,
                        "error": f"Ticket {normalized_id} not found"
                    })
                    continue

                original_status = ticket.status
                changes = []

                # Apply updates
                if title is not None:
                    if not title.strip():
                        failed_updates.append({
                            "ticket_id": normalized_id,
                            "error": "Title cannot be empty"
                        })
                        continue
                    if len(title) > 200:
                        failed_updates.append({
                            "ticket_id": normalized_id,
                            "error": "Title cannot exceed 200 characters"
                        })
                        continue
                    ticket.title = title.strip()
                    changes.append("title")

                if status is not None:
                    ticket.status = normalized_status
                    changes.append("status")

                if priority is not None:
                    ticket.priority = TicketPriority(priority.lower())
                    changes.append("priority")

                if assignee is not None:
                    if assignee.lower() == "none":
                        ticket.assignee = None
                        changes.append("assignee (cleared)")
                    else:
                        ticket.assignee = resolved_assignee
                        changes.append("assignee")

                if add_labels is not None:
                    new_labels = [lbl.strip().lower() for lbl in add_labels if lbl.strip()]
                    for label in new_labels:
                        if label not in [lbl.lower() for lbl in ticket.labels]:
                            ticket.labels.append(label)
                    if new_labels:
                        changes.append(f"added labels: {', '.join(new_labels)}")

                if remove_labels is not None:
                    labels_to_remove = [lbl.strip().lower() for lbl in remove_labels if lbl.strip()]
                    original_count = len(ticket.labels)
                    ticket.labels = [lbl for lbl in ticket.labels if lbl.lower() not in labels_to_remove]
                    if len(ticket.labels) < original_count:
                        changes.append(f"removed labels: {', '.join(labels_to_remove)}")

                if epic is not None:
                    if epic.lower() == "none":
                        ticket.epic_id = None
                        changes.append("epic (cleared)")
                    else:
                        # Normalize epic ID
                        normalized_epic = normalize_epic_id(epic)
                        ticket.epic_id = normalized_epic
                        changes.append("epic")

                # Update timestamp
                ticket.updated_at = datetime.now(timezone.utc)

                # Handle status change (file movement)
                if status is not None and ticket.status != original_status:
                    # Get new path based on status
                    new_path = get_ticket_path(ticket.id, ticket.status, root)

                    # Save to new location
                    save_ticket(ticket, new_path)

                    # Track file movement for cleanup
                    if ticket_path != new_path:
                        moved_files.append((ticket_path, new_path))
                else:
                    # Save in place
                    save_ticket(ticket, ticket_path)

                successful_updates.append({
                    "ticket_id": normalized_id,
                    "changes": changes,
                    "status_changed": status is not None and ticket.status != original_status
                })

            except Exception as e:
                failed_updates.append({
                    "ticket_id": ticket_id,
                    "error": str(e)
                })

        # Clean up moved files after all updates are successful
        for old_path, new_path in moved_files:
            if old_path.exists() and old_path != new_path:
                old_path.unlink()

        return OperationResult(
            success=len(successful_updates) > 0,
            message=f"Bulk update completed: {len(successful_updates)} successful, {len(failed_updates)} failed",
            data={
                "summary": {
                    "total_tickets": len(ticket_ids),
                    "successful": len(successful_updates),
                    "failed": len(failed_updates)
                },
                "successful_updates": successful_updates,
                "failed_updates": failed_updates,
                "changes_applied": {
                    "title": title,
                    "status": status,
                    "priority": priority,
                    "assignee": assignee,
                    "add_labels": add_labels,
                    "remove_labels": remove_labels,
                    "epic": epic
                }
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception("Error in bulk update")
        raise MCPToolError(f"Failed to perform bulk update: {str(e)}") from e


@register_tool(
    name="archive_tickets",
    description="Archive completed tickets",
    schema={"type": "object", "properties": {
        "ticket_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific ticket IDs to archive"},
        "status": {"type": "array", "items": {"type": "string"}, "description": "Archive all tickets with these statuses"},
        "older_than_days": {"type": "integer", "description": "Archive tickets older than X days", "minimum": 1},
        "dry_run": {"type": "boolean", "description": "Preview what would be archived without doing it", "default": False}
    }},
    is_destructive=True,
)

@secure_operation("ticket.archive")
@require_gira_project
@rate_limit(max_calls=100, window_seconds=60)
def archive_tickets(
    ticket_ids: Optional[List[str]] = None,
    status: Optional[List[str]] = None,
    older_than_days: Optional[int] = None,
    dry_run: bool = False,
    use_git: Optional[bool] = None,
) -> OperationResult:
    """
    Archive completed tickets.

    Args:
        ticket_ids: Specific ticket IDs to archive
        status: Archive all tickets with these statuses
        older_than_days: Archive tickets older than X days
        dry_run: Preview what would be archived without doing it
        use_git: Use git operations for archiving (auto-detected if None)

    Returns:
        OperationResult with archival results
    """
    try:
        from datetime import datetime, timezone, timedelta
        from pathlib import Path

        root = get_project_root()
        if not root:
            raise MCPToolError("Not in a Gira project directory")

        # Validate inputs
        if not any([ticket_ids, status, older_than_days]):
            raise ValidationError("Must specify ticket_ids, status, or older_than_days")

        # Load all tickets (excluding already archived)
        all_tickets = load_all_tickets(root, include_archived=False)

        # Filter tickets to archive
        tickets_to_archive = []
        
        if ticket_ids:
            # Archive specific tickets
            for ticket_id in ticket_ids:
                normalized_id = normalize_ticket_id(ticket_id)
                for ticket in all_tickets:
                    if ticket.id == normalized_id:
                        tickets_to_archive.append(ticket)
                        break
        else:
            # Filter by criteria
            for ticket in all_tickets:
                should_archive = True

                # Status filter
                if status:
                    if ticket.status.lower() not in [s.lower() for s in status]:
                        should_archive = False

                # Age filter
                if older_than_days and should_archive:
                    cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
                    # Normalize ticket.updated_at to UTC timezone-aware datetime
                    if ticket.updated_at.tzinfo is None:
                        # Naive datetime, assume it's UTC
                        ticket_updated_at = ticket.updated_at.replace(tzinfo=timezone.utc)
                    else:
                        # Already timezone-aware, convert to UTC
                        ticket_updated_at = ticket.updated_at.astimezone(timezone.utc)
                    
                    if ticket_updated_at > cutoff_date:
                        should_archive = False

                if should_archive:
                    tickets_to_archive.append(ticket)

        if not tickets_to_archive:
            return OperationResult(
                success=True,
                message="No tickets found matching archive criteria",
                data={
                    "summary": {
                        "total_candidates": len(all_tickets),
                        "archived": 0,
                        "failed": 0
                    },
                    "criteria": {
                        "ticket_ids": ticket_ids,
                        "status": status,
                        "older_than_days": older_than_days
                    },
                    "dry_run": dry_run
                }
            )

        # Preview mode
        if dry_run:
            preview_data = []
            for ticket in tickets_to_archive:
                priority_value = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
                type_value = ticket.type.value if hasattr(ticket.type, 'value') else str(ticket.type)

                # Normalize ticket.updated_at to UTC timezone-aware datetime
                if ticket.updated_at.tzinfo is None:
                    # Naive datetime, assume it's UTC
                    ticket_updated_at = ticket.updated_at.replace(tzinfo=timezone.utc)
                else:
                    # Already timezone-aware, convert to UTC
                    ticket_updated_at = ticket.updated_at.astimezone(timezone.utc)
                
                preview_data.append({
                    "id": ticket.id,
                    "title": ticket.title,
                    "status": ticket.status,
                    "priority": priority_value,
                    "type": type_value,
                    "updated_at": ticket_updated_at.isoformat(),
                    "age_days": (datetime.now(timezone.utc) - ticket_updated_at).days
                })

            return OperationResult(
                success=True,
                message=f"Dry run: {len(tickets_to_archive)} tickets would be archived",
                data={
                    "summary": {
                        "total_candidates": len(all_tickets),
                        "would_archive": len(tickets_to_archive),
                        "failed": 0
                    },
                    "tickets_to_archive": preview_data,
                    "criteria": {
                        "ticket_ids": ticket_ids,
                        "status": status,
                        "older_than_days": older_than_days
                    },
                    "dry_run": True
                }
            )

        # Actually archive tickets
        archived_tickets = []
        failed_archives = []

        # Import git-aware archive function
        from gira.utils.archive import archive_ticket

        for ticket in tickets_to_archive:
            try:
                # Use git-aware archive function (same as CLI)
                archive_path = archive_ticket(ticket, use_git=use_git)

                archived_tickets.append({
                    "ticket_id": ticket.id,
                    "title": ticket.title,
                    "status": ticket.status,
                    "archive_path": str(archive_path)
                })

            except Exception as e:
                failed_archives.append({
                    "ticket_id": ticket.id,
                    "error": str(e)
                })

        return OperationResult(
            success=len(archived_tickets) > 0,
            message=f"Archived {len(archived_tickets)} tickets, {len(failed_archives)} failed",
            data={
                "summary": {
                    "total_candidates": len(all_tickets),
                    "archived": len(archived_tickets),
                    "failed": len(failed_archives)
                },
                "archived_tickets": archived_tickets,
                "failed_archives": failed_archives,
                "criteria": {
                    "ticket_ids": ticket_ids,
                    "status": status,
                    "older_than_days": older_than_days
                },
                "dry_run": False
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception("Error archiving tickets")
        raise MCPToolError(f"Failed to archive tickets: {str(e)}") from e
