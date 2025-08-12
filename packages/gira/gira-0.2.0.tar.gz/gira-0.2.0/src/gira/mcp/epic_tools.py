"""Epic management tools for Gira MCP server."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from gira.mcp.schema import OperationResult
from gira.mcp.security import secure_operation, require_gira_project, rate_limit
from gira.mcp.tools import (
    MCPToolError,
    NotFoundError,
    ValidationError,
    register_tool,
)
from gira.mcp.utils import (
    recursion_guard,
    with_timeout,
    safe_model_dump,
    performance_monitor,
    create_lightweight_summary,
)
from gira.models import Epic, EpicStatus, Ticket
from gira.utils.config import get_default_reporter
from gira.utils.project_management import get_project_root
from gira.utils.ticket_utils import load_all_tickets
from gira.utils.response_formatters import (
    format_ticket_summary,
    calculate_epic_progress as format_epic_progress,
    extract_enum_value,
    format_timestamp,
)

logger = logging.getLogger(__name__)




class EpicListFilter(BaseModel):
    """Filters for listing epics."""
    status: Optional[str] = Field(None, description="Filter by status (draft, active, completed)")
    owner: Optional[str] = Field(None, description="Filter by owner email")
    labels: Optional[List[str]] = Field(None, description="Filter by labels (all must match)")
    limit: Optional[int] = Field(None, description="Maximum number of epics to return", ge=1, le=100)


class EpicCreateRequest(BaseModel):
    """Request to create a new epic."""
    title: str = Field(description="Epic title", min_length=3, max_length=200)
    description: Optional[str] = Field(None, description="Epic description")
    owner: Optional[str] = Field(None, description="Epic owner email (defaults to current user)")
    labels: Optional[List[str]] = Field(None, description="Epic labels")
    status: Optional[str] = Field("draft", description="Initial status (draft, active, completed)")


class EpicUpdateRequest(BaseModel):
    """Request to update an epic."""
    epic_id: str = Field(description="Epic ID to update")
    title: Optional[str] = Field(None, description="New title", min_length=3, max_length=200)
    description: Optional[str] = Field(None, description="New description")
    owner: Optional[str] = Field(None, description="New owner email")
    status: Optional[str] = Field(None, description="New status (draft, active, completed)")
    labels: Optional[List[str]] = Field(None, description="New labels (replaces existing)")
    add_labels: Optional[List[str]] = Field(None, description="Labels to add")
    remove_labels: Optional[List[str]] = Field(None, description="Labels to remove")


class EpicTicketRequest(BaseModel):
    """Request to manage epic-ticket associations."""
    epic_id: str = Field(description="Epic ID")
    ticket_ids: List[str] = Field(description="List of ticket IDs to associate/disassociate")


class EpicSummary(BaseModel):
    """Summary information for an epic."""
    id: str
    title: str
    status: str
    owner: str
    labels: List[str]
    ticket_count: int
    completed_tickets: int
    progress_percentage: float
    created_at: str
    updated_at: str


def load_all_epics() -> List[Epic]:
    """Load all epics from the project."""
    root = get_project_root()
    epics_dir = root / ".gira" / "epics"
    epics = []

    if epics_dir.exists():
        for epic_file in epics_dir.glob("EPIC-*.json"):
            try:
                epic = Epic.from_json_file(str(epic_file))
                epics.append(epic)
            except Exception as e:
                logger.warning(f"Failed to load epic {epic_file.name}: {e}")

    return epics


def find_epic(epic_id: str) -> Optional[Epic]:
    """Find an epic by ID."""
    root = get_project_root()
    epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
    
    if epic_path.exists():
        try:
            return Epic.from_json_file(str(epic_path))
        except Exception as e:
            logger.error(f"Error loading epic {epic_id}: {e}")
    
    return None


def save_epic(epic: Epic) -> Path:
    """Save an epic to disk."""
    root = get_project_root()
    epics_dir = root / ".gira" / "epics"
    epics_dir.mkdir(parents=True, exist_ok=True)
    
    epic_path = epics_dir / f"{epic.id}.json"
    epic.save_to_json_file(str(epic_path))
    return epic_path


# Global cache for tickets to avoid repeated loading
_tickets_cache: Optional[Dict[str, List[Ticket]]] = None
_cache_timestamp: Optional[float] = None
CACHE_TTL_SECONDS = 30  # Cache tickets for 30 seconds


def build_epic_tickets_cache(include_archived: bool = True) -> Dict[str, List[Ticket]]:
    """Build efficient cache of tickets grouped by epic_id."""
    global _tickets_cache, _cache_timestamp
    import time
    
    current_time = time.time()
    
    # Use cache if it's still valid and has the same archive setting
    # Note: For simplicity, we'll rebuild cache when include_archived changes
    # A more sophisticated approach would maintain separate caches
    if (_tickets_cache is not None and 
        _cache_timestamp is not None and 
        current_time - _cache_timestamp < CACHE_TTL_SECONDS):
        return _tickets_cache
    
    with performance_monitor("build_epic_tickets_cache"):
        root = get_project_root()
        all_tickets = load_all_tickets(root, include_archived=include_archived)
        
        # Group tickets by epic_id
        cache = {}
        for ticket in all_tickets:
            epic_id = ticket.epic_id
            if epic_id:
                if epic_id not in cache:
                    cache[epic_id] = []
                cache[epic_id].append(ticket)
        
        # Update global cache
        _tickets_cache = cache
        _cache_timestamp = current_time
        
        logger.debug(f"Built epic tickets cache with {len(cache)} epics and {len(all_tickets)} tickets")
        return cache


def get_epic_tickets_optimized(epic_id: str, tickets_cache: Optional[Dict[str, List[Ticket]]] = None, include_archived: bool = True) -> List[Ticket]:
    """Get epic tickets without loading all system tickets repeatedly."""
    if tickets_cache is None:
        tickets_cache = build_epic_tickets_cache(include_archived=include_archived)
    
    return tickets_cache.get(epic_id, [])


def clear_tickets_cache():
    """Clear the tickets cache to force reload."""
    global _tickets_cache, _cache_timestamp
    _tickets_cache = None
    _cache_timestamp = None


@recursion_guard(max_depth=3)
def calculate_epic_progress_optimized(epic: Epic, tickets_cache: Optional[Dict[str, List[Ticket]]] = None) -> Dict[str, Any]:
    """Calculate progress metrics for an epic with optimized ticket loading."""
    with performance_monitor(f"calculate_epic_progress for {epic.id}"):
        # Get tickets efficiently
        tickets = get_epic_tickets_optimized(epic.id, tickets_cache)
        
        # Use unified progress calculation
        progress = format_epic_progress(epic, tickets)
        
        # Create lightweight ticket summaries instead of full objects  
        ticket_summaries = [
            create_lightweight_summary(t, ["id", "title", "status"])
            for t in tickets
        ]
        
        # Add ticket summaries to the progress data
        progress["tickets"] = ticket_summaries
        return progress


def create_epic_summary(epic: Epic, progress: Dict[str, Any]) -> Dict[str, Any]:
    """Create epic summary without circular references."""
    summary = {
        "id": epic.id,
        "title": epic.title,
        "status": extract_enum_value(epic.status),
        "owner": epic.owner,
        "labels": epic.labels,
        "created_at": format_timestamp(epic.created_at),
        "updated_at": format_timestamp(epic.updated_at)
    }
    
    # Add progress information
    summary.update(progress)
    
    return summary


def apply_epic_filters(epics: List[Epic], status: Optional[str], owner: Optional[str], 
                      labels: Optional[List[str]], limit: Optional[int]) -> List[Epic]:
    """Apply filters to epic list efficiently."""
    filtered_epics = epics
    
    # Apply filters
    if status:
        filtered_epics = [epic for epic in filtered_epics if epic.status == status]
    
    if owner:
        filtered_epics = [epic for epic in filtered_epics if epic.owner == owner]
    
    if labels:
        filtered_epics = [
            epic for epic in filtered_epics 
            if all(label in epic.labels for label in labels)
        ]
    
    # Apply limit
    if limit:
        filtered_epics = filtered_epics[:limit]
    
    return filtered_epics


def get_epic_tickets(epic_id: str) -> List[Ticket]:
    """Get all tickets associated with an epic."""
    # Use optimized version to avoid performance issues
    return get_epic_tickets_optimized(epic_id)


def calculate_epic_progress(epic: Epic) -> Dict[str, Any]:
    """Calculate progress metrics for an epic."""
    # Use optimized version to prevent recursion issues  
    return calculate_epic_progress_optimized(epic)


@register_tool(
    name="list_epics",
    description="List epics with optional filtering",
    schema=EpicListFilter.model_json_schema(),
)
@secure_operation("epic.list")
@require_gira_project
@rate_limit(max_calls=2000, window_seconds=60)
@with_timeout(30)  # 30 second timeout
def list_epics(
    status: Optional[str] = None,
    owner: Optional[str] = None,
    labels: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> OperationResult:
    """
    List epics with optional filtering.

    Args:
        status: Filter by status (draft, active, completed)
        owner: Filter by owner email
        labels: Filter by labels (all must match)
        limit: Maximum number of epics to return (1-100)

    Returns:
        OperationResult with list of epic summaries
    """
    try:
        with performance_monitor("list_epics"):
            epics = load_all_epics()
            
            # Apply filters efficiently before expensive operations
            filtered_epics = apply_epic_filters(epics, status, owner, labels, limit)
            
            # Pre-load and cache all tickets grouped by epic_id to avoid O(n²) complexity
            tickets_cache = build_epic_tickets_cache()
            
            # Convert to summaries with optimized progress calculation
            epic_summaries = []
            for epic in filtered_epics:
                progress = calculate_epic_progress_optimized(epic, tickets_cache)
                summary = create_epic_summary(epic, progress)
                epic_summaries.append(summary)
        
        return OperationResult(
            success=True,
            message=f"Found {len(epic_summaries)} epics",
            data={
                "epics": epic_summaries,
                "total_count": len(epic_summaries),
                "filters_applied": {
                    "status": status,
                    "owner": owner,
                    "labels": labels,
                    "limit": limit
                }
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error listing epics")
        raise MCPToolError(f"Failed to list epics: {str(e)}") from e


@register_tool(
    name="get_epic",
    description="Get detailed information about a specific epic",
    schema={"type": "object", "properties": {"epic_id": {"type": "string", "description": "Epic ID to retrieve"}}},
)
@secure_operation("epic.get")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
@with_timeout(15)  # 15 second timeout for single epic
def get_epic(epic_id: str) -> OperationResult:
    """
    Get detailed information about a specific epic.

    Args:
        epic_id: The epic ID to retrieve (will be normalized)

    Returns:
        OperationResult with detailed epic information
    """
    try:
        with performance_monitor(f"get_epic {epic_id}"):
            # Normalize epic ID
            if epic_id.isdigit():
                epic_id = f"EPIC-{epic_id.zfill(3)}"
            elif not epic_id.upper().startswith("EPIC-"):
                epic_id = f"EPIC-{epic_id}".upper()
            else:
                epic_id = epic_id.upper()
            
            epic = find_epic(epic_id)
            if not epic:
                raise NotFoundError(f"Epic {epic_id} not found", resource_type="epic", resource_id=epic_id)
            
            # Get progress metrics with optimized calculation
            progress = calculate_epic_progress_optimized(epic)
            
            # Use safe serialization to prevent recursion issues
            epic_data = safe_model_dump(epic, max_depth=4)
            epic_data.update({
                "progress": progress,
                "file_path": str(get_project_root() / ".gira" / "epics" / f"{epic.id}.json")
            })
            
            return OperationResult(
                success=True,
                message=f"Retrieved epic {epic_id}",
                data=epic_data
            )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error getting epic {epic_id}")
        raise MCPToolError(f"Failed to get epic: {str(e)}") from e


@register_tool(
    name="create_epic",
    description="Create a new epic",
    schema=EpicCreateRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("epic.create")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def create_epic(
    title: str,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    labels: Optional[List[str]] = None,
    status: Optional[str] = "draft",
) -> OperationResult:
    """
    Create a new epic.

    Args:
        title: Epic title
        description: Epic description
        owner: Epic owner email (defaults to current user)
        labels: Epic labels
        status: Initial status (draft, active, completed)

    Returns:
        OperationResult with created epic information
    """
    try:
        root = get_project_root()
        
        # Get next epic ID
        epics_dir = root / ".gira" / "epics"
        epics_dir.mkdir(parents=True, exist_ok=True)
        
        existing_epics = list(epics_dir.glob("EPIC-*.json"))
        if existing_epics:
            epic_numbers = []
            for epic_file in existing_epics:
                try:
                    num = int(epic_file.stem.split("-")[1])
                    epic_numbers.append(num)
                except (IndexError, ValueError):
                    continue
            next_id = max(epic_numbers) + 1 if epic_numbers else 1
        else:
            next_id = 1
        
        epic_id = f"EPIC-{next_id:03d}"
        
        # Set default owner if not provided
        if not owner:
            owner = get_default_reporter()
        
        # Validate status
        valid_statuses = ["draft", "active", "completed"]
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        
        # Create epic
        epic = Epic(
            id=epic_id,
            title=title,
            description=description,
            owner=owner,
            labels=labels or [],
            status=status
        )
        
        # Save epic
        epic_path = save_epic(epic)
        
        logger.info(f"Created epic {epic_id}: {title}")
        
        return OperationResult(
            success=True,
            message=f"Created epic {epic_id}",
            data={
                "epic": epic.model_dump(),
                "file_path": str(epic_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error creating epic")
        raise MCPToolError(f"Failed to create epic: {str(e)}") from e


@register_tool(
    name="update_epic",
    description="Update an existing epic",
    schema=EpicUpdateRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("epic.update")
@require_gira_project
@rate_limit(max_calls=300, window_seconds=60)
def update_epic(
    epic_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    status: Optional[str] = None,
    labels: Optional[List[str]] = None,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
) -> OperationResult:
    """
    Update an existing epic.

    Args:
        epic_id: Epic ID to update
        title: New title
        description: New description  
        owner: New owner email
        status: New status
        labels: New labels (replaces existing)
        add_labels: Labels to add
        remove_labels: Labels to remove

    Returns:
        OperationResult with updated epic information
    """
    try:
        # Normalize epic ID
        if epic_id.isdigit():
            epic_id = f"EPIC-{epic_id.zfill(3)}"
        elif not epic_id.upper().startswith("EPIC-"):
            epic_id = f"EPIC-{epic_id}".upper()
        else:
            epic_id = epic_id.upper()
        
        epic = find_epic(epic_id)
        if not epic:
            raise NotFoundError(f"Epic {epic_id} not found", resource_type="epic", resource_id=epic_id)
        
        # Track changes
        changes = []
        
        # Update fields
        if title is not None:
            epic.title = title
            changes.append(f"title: '{title}'")
        
        if description is not None:
            epic.description = description
            changes.append("description updated")
        
        if owner is not None:
            epic.owner = owner
            changes.append(f"owner: {owner}")
        
        if status is not None:
            valid_statuses = ["draft", "active", "completed"]
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
            epic.status = status
            changes.append(f"status: {status}")
        
        # Handle labels
        if labels is not None:
            epic.labels = labels
            changes.append(f"labels: {labels}")
        else:
            # Handle add/remove labels
            current_labels = set(epic.labels)
            
            if add_labels:
                current_labels.update(add_labels)
                changes.append(f"added labels: {add_labels}")
            
            if remove_labels:
                current_labels.difference_update(remove_labels)
                changes.append(f"removed labels: {remove_labels}")
            
            epic.labels = list(current_labels)
        
        if not changes:
            return OperationResult(
                success=True,
                message=f"Epic {epic_id} unchanged (no updates provided)",
                data={"epic": epic.model_dump()}
            )
        
        # Update timestamp
        epic.updated_at = datetime.utcnow()
        
        # Save epic
        epic_path = save_epic(epic)
        
        logger.info(f"Updated epic {epic_id}: {', '.join(changes)}")
        
        return OperationResult(
            success=True,
            message=f"Updated epic {epic_id}: {', '.join(changes)}",
            data={
                "epic": epic.model_dump(),
                "changes": changes,
                "file_path": str(epic_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error updating epic {epic_id}")
        raise MCPToolError(f"Failed to update epic: {str(e)}") from e


@register_tool(
    name="add_tickets_to_epic",
    description="Add tickets to an epic",
    schema=EpicTicketRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("epic.add_tickets")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def add_tickets_to_epic(
    epic_id: str,
    ticket_ids: List[str]
) -> OperationResult:
    """
    Add tickets to an epic.

    Args:
        epic_id: Epic ID
        ticket_ids: List of ticket IDs to add to the epic

    Returns:
        OperationResult with operation details
    """
    try:
        # Normalize epic ID
        if epic_id.isdigit():
            epic_id = f"EPIC-{epic_id.zfill(3)}"
        elif not epic_id.upper().startswith("EPIC-"):
            epic_id = f"EPIC-{epic_id}".upper()
        else:
            epic_id = epic_id.upper()
        
        # Verify epic exists
        epic = find_epic(epic_id)
        if not epic:
            raise NotFoundError(f"Epic {epic_id} not found", resource_type="epic", resource_id=epic_id)
        
        # Load all tickets to validate and update
        from gira.utils.ticket_utils import find_ticket, save_ticket
        
        updated_tickets = []
        not_found_tickets = []
        already_assigned_tickets = []
        
        for ticket_id in ticket_ids:
            # Normalize ticket ID using configurable prefix
            from gira.mcp.tools import normalize_ticket_id
            ticket_id = normalize_ticket_id(ticket_id)
            
            root = get_project_root()
            ticket, ticket_path = find_ticket(ticket_id, root)
            if not ticket:
                not_found_tickets.append(ticket_id)
                continue
            
            if ticket.epic_id == epic_id:
                already_assigned_tickets.append(ticket_id)
                continue
            
            # Update ticket's epic
            ticket.epic_id = epic_id
            
            # Update timestamp
            ticket.updated_at = datetime.utcnow()
            
            save_ticket(ticket, ticket_path)
            updated_tickets.append(ticket_id)
        
        # Prepare result
        result_data = {
            "epic_id": epic_id,
            "updated_tickets": updated_tickets,
            "already_assigned": already_assigned_tickets,
            "not_found": not_found_tickets,
            "total_processed": len(ticket_ids),
            "successful_updates": len(updated_tickets)
        }
        
        if not_found_tickets:
            message = f"Added {len(updated_tickets)} tickets to epic {epic_id}. {len(not_found_tickets)} tickets not found."
        elif already_assigned_tickets:
            message = f"Added {len(updated_tickets)} tickets to epic {epic_id}. {len(already_assigned_tickets)} tickets already assigned."
        else:
            message = f"Successfully added {len(updated_tickets)} tickets to epic {epic_id}"
        
        logger.info(f"Added tickets to epic {epic_id}: {updated_tickets}")
        
        return OperationResult(
            success=True,
            message=message,
            data=result_data
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error adding tickets to epic {epic_id}")
        raise MCPToolError(f"Failed to add tickets to epic: {str(e)}") from e


@register_tool(
    name="remove_tickets_from_epic",
    description="Remove tickets from an epic",
    schema=EpicTicketRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("epic.remove_tickets")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def remove_tickets_from_epic(
    epic_id: str,
    ticket_ids: List[str]
) -> OperationResult:
    """
    Remove tickets from an epic.

    Args:
        epic_id: Epic ID
        ticket_ids: List of ticket IDs to remove from the epic

    Returns:
        OperationResult with operation details
    """
    try:
        # Normalize epic ID
        if epic_id.isdigit():
            epic_id = f"EPIC-{epic_id.zfill(3)}"
        elif not epic_id.upper().startswith("EPIC-"):
            epic_id = f"EPIC-{epic_id}".upper()
        else:
            epic_id = epic_id.upper()
        
        # Verify epic exists
        epic = find_epic(epic_id)
        if not epic:
            raise NotFoundError(f"Epic {epic_id} not found", resource_type="epic", resource_id=epic_id)
        
        # Load all tickets to validate and update
        from gira.utils.ticket_utils import find_ticket, save_ticket
        
        updated_tickets = []
        not_found_tickets = []
        not_in_epic_tickets = []
        
        for ticket_id in ticket_ids:
            # Normalize ticket ID using configurable prefix
            from gira.mcp.tools import normalize_ticket_id
            ticket_id = normalize_ticket_id(ticket_id)
            
            root = get_project_root()
            ticket, ticket_path = find_ticket(ticket_id, root)
            if not ticket:
                not_found_tickets.append(ticket_id)
                continue
            
            if ticket.epic_id != epic_id:
                not_in_epic_tickets.append(ticket_id)
                continue
            
            # Remove ticket from epic
            ticket.epic_id = None
            
            # Update timestamp
            ticket.updated_at = datetime.utcnow()
            
            save_ticket(ticket, ticket_path)
            updated_tickets.append(ticket_id)
        
        # Prepare result
        result_data = {
            "epic_id": epic_id,
            "updated_tickets": updated_tickets,
            "not_in_epic": not_in_epic_tickets,
            "not_found": not_found_tickets,
            "total_processed": len(ticket_ids),
            "successful_updates": len(updated_tickets)
        }
        
        if not_found_tickets:
            message = f"Removed {len(updated_tickets)} tickets from epic {epic_id}. {len(not_found_tickets)} tickets not found."
        elif not_in_epic_tickets:
            message = f"Removed {len(updated_tickets)} tickets from epic {epic_id}. {len(not_in_epic_tickets)} tickets not in this epic."
        else:
            message = f"Successfully removed {len(updated_tickets)} tickets from epic {epic_id}"
        
        logger.info(f"Removed tickets from epic {epic_id}: {updated_tickets}")
        
        return OperationResult(
            success=True,
            message=message,
            data=result_data
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error removing tickets from epic {epic_id}")
        raise MCPToolError(f"Failed to remove tickets from epic: {str(e)}") from e


@register_tool(
    name="delete_epic",
    description="Delete or archive an epic (removes epic association from all tickets)",
    schema={"type": "object", "properties": {
        "epic_id": {"type": "string", "description": "Epic ID to delete"},
        "permanent": {"type": "boolean", "description": "Permanently delete instead of archiving (default: false)", "default": False}
    }, "required": ["epic_id"]},
    is_destructive=True,
)
@secure_operation("epic.delete")
@require_gira_project
@rate_limit(max_calls=100, window_seconds=60)
def delete_epic(
    epic_id: str,
    permanent: bool = False
) -> OperationResult:
    """
    Delete or archive an epic.
    
    By default, epics are archived and can be restored later.
    Use permanent=True to permanently delete the epic.
    
    This will also remove the epic reference from all associated tickets.
    
    Args:
        epic_id: Epic ID to delete
        permanent: Whether to permanently delete (true) or archive (false)
        
    Returns:
        OperationResult with deletion details
    """
    try:
        # Normalize epic ID
        if epic_id.isdigit():
            epic_id = f"EPIC-{epic_id.zfill(3)}"
        elif not epic_id.upper().startswith("EPIC-"):
            epic_id = f"EPIC-{epic_id}".upper()
        else:
            epic_id = epic_id.upper()
        
        root = get_project_root()
        
        # Find the epic file
        epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
        archive_path = root / ".gira" / "archive" / "epics" / f"{epic_id}.json"
        
        if epic_path.exists():
            current_path = epic_path
        elif archive_path.exists():
            current_path = archive_path
        else:
            raise NotFoundError(f"Epic {epic_id} not found", resource_type="epic", resource_id=epic_id)
        
        # Load the epic
        epic = Epic.from_json_file(str(current_path))
        
        # Find all tickets that reference this epic
        affected_tickets = []
        all_tickets = load_all_tickets(root)
        for ticket in all_tickets:
            if ticket.epic_id == epic_id:
                affected_tickets.append(ticket.id)
        
        # Remove epic reference from all tickets that reference this epic
        from gira.utils.ticket_utils import find_ticket, save_ticket
        
        unlinked_count = 0
        for ticket_id in affected_tickets:
            root = get_project_root()
            ticket, ticket_path = find_ticket(ticket_id, root)
            if ticket and ticket.epic_id == epic_id:
                ticket.epic_id = None
                ticket.updated_at = datetime.utcnow()
                save_ticket(ticket, ticket_path)
                unlinked_count += 1
        
        # Delete or archive the epic
        if permanent:
            # Delete epic file
            current_path.unlink()
            action_msg = "permanently deleted"
            action = "deleted"
        else:
            # Archive the epic
            archive_dir = root / ".gira" / "archive" / "epics"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Move epic to archive
            archive_target = archive_dir / f"{epic_id}.json"
            current_path.rename(archive_target)
            action_msg = "archived"
            action = "archived"
        
        logger.info(f"{action_msg.title()} epic {epic_id} (unlinked {unlinked_count} tickets)")
        
        return OperationResult(
            success=True,
            message=f"Epic {epic_id} has been {action_msg}",
            data={
                "epic_id": epic_id,
                "action": action,
                "tickets_unlinked": unlinked_count,
                "affected_tickets": affected_tickets,
                "permanent": permanent
            }
        )
        
    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error deleting epic {epic_id}")
        raise MCPToolError(f"Failed to delete epic: {str(e)}") from e


@register_tool(
    name="get_epic_tickets",
    description="Get all tickets in an epic",
    schema={"type": "object", "properties": {
        "epic_id": {"type": "string", "description": "Epic ID"},
        "status": {"type": "string", "description": "Filter tickets by status"},
        "limit": {"type": "integer", "description": "Maximum number of tickets to return", "minimum": 1, "maximum": 100}
    }, "required": ["epic_id"]},
)
@secure_operation("epic.get_tickets")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
def get_epic_tickets(
    epic_id: str,
    status: Optional[str] = None,
    limit: Optional[int] = None,
    include_archived: bool = True,
) -> OperationResult:
    """
    Get all tickets in an epic.

    Args:
        epic_id: Epic ID
        status: Filter tickets by status
        limit: Maximum number of tickets to return

    Returns:
        OperationResult with epic tickets
    """
    try:
        # Normalize epic ID
        if epic_id.isdigit():
            epic_id = f"EPIC-{epic_id.zfill(3)}"
        elif not epic_id.upper().startswith("EPIC-"):
            epic_id = f"EPIC-{epic_id}".upper()
        else:
            epic_id = epic_id.upper()
        
        # Verify epic exists
        epic = find_epic(epic_id)
        if not epic:
            raise NotFoundError(f"Epic {epic_id} not found", resource_type="epic", resource_id=epic_id)
        
        # Get tickets
        tickets = get_epic_tickets_optimized(epic_id, include_archived=include_archived)
        
        # Apply filters
        if status:
            tickets = [ticket for ticket in tickets if ticket.status == status]
        
        if limit:
            tickets = tickets[:limit]
        
        # Convert to summaries using unified formatter
        ticket_summaries = [
            format_ticket_summary(ticket, include_fields=[
                "id", "title", "status", "type", "priority", "assignee", 
                "story_points", "created_at", "updated_at"
            ])
            for ticket in tickets
        ]
        
        return OperationResult(
            success=True,
            message=f"Found {len(ticket_summaries)} tickets in epic {epic_id}",
            data={
                "epic_id": epic_id,
                "epic_title": epic.title,
                "tickets": ticket_summaries,
                "total_count": len(ticket_summaries),
                "filters_applied": {
                    "status": status,
                    "limit": limit
                }
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error getting tickets for epic {epic_id}")
        raise MCPToolError(f"Failed to get epic tickets: {str(e)}") from e