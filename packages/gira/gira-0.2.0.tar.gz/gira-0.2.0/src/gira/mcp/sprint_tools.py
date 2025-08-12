"""Sprint management tools for Gira MCP server."""

import json
import logging
from datetime import date, datetime, timedelta
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
from gira.models import Sprint, SprintStatus, Ticket
from gira.utils.config import get_default_reporter
from gira.utils.project_management import get_project_root
from gira.utils.ticket_utils import load_all_tickets
from gira.utils.response_formatters import (
    format_ticket_summary,
    calculate_sprint_progress as format_sprint_progress,
    extract_enum_value,
    format_timestamp,
)

logger = logging.getLogger(__name__)




class SprintListFilter(BaseModel):
    """Filters for listing sprints."""
    status: Optional[str] = Field(None, description="Filter by status (planned, active, completed)")
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    limit: Optional[int] = Field(None, description="Maximum number of sprints to return", ge=1, le=100)


class SprintCreateRequest(BaseModel):
    """Request to create a new sprint."""
    name: str = Field(description="Sprint name", min_length=1, max_length=100)
    goal: Optional[str] = Field(None, description="Sprint goal/objective", max_length=500)
    duration_days: int = Field(14, description="Sprint duration in days", ge=1, le=30)
    start_date: Optional[str] = Field(None, description="Sprint start date (ISO format: YYYY-MM-DD)")


class SprintUpdateRequest(BaseModel):
    """Request to update a sprint."""
    sprint_id: str = Field(description="Sprint ID to update")
    name: Optional[str] = Field(None, description="New name", min_length=1, max_length=100)
    goal: Optional[str] = Field(None, description="New goal", max_length=500)
    status: Optional[str] = Field(None, description="New status (planned, active, completed)")


class SprintTicketRequest(BaseModel):
    """Request to manage sprint-ticket associations."""
    sprint_id: str = Field(description="Sprint ID")
    ticket_ids: List[str] = Field(description="List of ticket IDs to associate/disassociate", max_length=100)


class SprintSummary(BaseModel):
    """Summary information for a sprint."""
    id: str
    name: str
    status: str
    goal: Optional[str]
    start_date: str
    end_date: str
    duration_days: int
    ticket_count: int
    completed_tickets: int
    progress_percentage: float
    created_at: str
    updated_at: str


def load_all_sprints() -> List[Sprint]:
    """Load all sprints from the project."""
    root = get_project_root()
    sprints_dir = root / ".gira" / "sprints"
    sprints = []

    if sprints_dir.exists():
        for sprint_file in sprints_dir.glob("SPRINT-*.json"):
            try:
                sprint = Sprint.from_json_file(str(sprint_file))
                sprints.append(sprint)
            except Exception as e:
                logger.warning(f"Failed to load sprint {sprint_file.name}: {e}")

    return sprints


def find_sprint(sprint_id: str) -> Optional[Sprint]:
    """Find a sprint by ID."""
    root = get_project_root()
    sprint_path = root / ".gira" / "sprints" / f"{sprint_id}.json"
    
    if sprint_path.exists():
        try:
            return Sprint.from_json_file(str(sprint_path))
        except Exception as e:
            logger.error(f"Error loading sprint {sprint_id}: {e}")
    
    return None


def save_sprint(sprint: Sprint) -> Path:
    """Save a sprint to disk."""
    root = get_project_root()
    sprints_dir = root / ".gira" / "sprints"
    sprints_dir.mkdir(parents=True, exist_ok=True)
    
    sprint_path = sprints_dir / f"{sprint.id}.json"
    sprint.save_to_json_file(str(sprint_path))
    return sprint_path


# Global cache for tickets to avoid repeated loading
_sprint_tickets_cache: Optional[Dict[str, List[Ticket]]] = None
_sprint_cache_timestamp: Optional[float] = None
SPRINT_CACHE_TTL_SECONDS = 30  # Cache tickets for 30 seconds


def build_sprint_tickets_cache() -> Dict[str, List[Ticket]]:
    """Build efficient cache of tickets grouped by sprint_id."""
    global _sprint_tickets_cache, _sprint_cache_timestamp
    import time
    
    current_time = time.time()
    
    # Use cache if it's still valid
    if (_sprint_tickets_cache is not None and 
        _sprint_cache_timestamp is not None and 
        current_time - _sprint_cache_timestamp < SPRINT_CACHE_TTL_SECONDS):
        return _sprint_tickets_cache
    
    with performance_monitor("build_sprint_tickets_cache"):
        root = get_project_root()
        all_tickets = load_all_tickets(root)
        
        # Group tickets by sprint_id
        cache = {}
        for ticket in all_tickets:
            sprint_id = getattr(ticket, 'sprint_id', None)
            if sprint_id:
                if sprint_id not in cache:
                    cache[sprint_id] = []
                cache[sprint_id].append(ticket)
        
        # Update global cache
        _sprint_tickets_cache = cache
        _sprint_cache_timestamp = current_time
        
        logger.debug(f"Built sprint tickets cache with {len(cache)} sprints and {len(all_tickets)} tickets")
        return cache


def get_sprint_tickets_optimized(sprint_id: str, tickets_cache: Optional[Dict[str, List[Ticket]]] = None) -> List[Ticket]:
    """Get sprint tickets without loading all system tickets repeatedly."""
    if tickets_cache is None:
        tickets_cache = build_sprint_tickets_cache()
    
    return tickets_cache.get(sprint_id, [])


def clear_sprint_tickets_cache():
    """Clear the sprint tickets cache to force reload."""
    global _sprint_tickets_cache, _sprint_cache_timestamp
    _sprint_tickets_cache = None
    _sprint_cache_timestamp = None


def get_sprint_tickets(sprint_id: str) -> List[Ticket]:
    """Get all tickets associated with a sprint."""
    # Use optimized version to avoid performance issues
    return get_sprint_tickets_optimized(sprint_id)


@recursion_guard(max_depth=3)
def calculate_sprint_progress_optimized(sprint: Sprint, tickets_cache: Optional[Dict[str, List[Ticket]]] = None) -> Dict[str, Any]:
    """Calculate progress metrics for a sprint with optimized ticket loading."""
    with performance_monitor(f"calculate_sprint_progress for {sprint.id}"):
        # Get tickets efficiently
        tickets = get_sprint_tickets_optimized(sprint.id, tickets_cache)
        
        # Use unified progress calculation
        progress = format_sprint_progress(sprint, tickets)
        
        # Calculate velocity (story points per day)
        days_elapsed = 0
        if sprint.status == SprintStatus.ACTIVE:
            days_elapsed = (date.today() - sprint.start_date).days + 1
        elif sprint.status == SprintStatus.COMPLETED:
            days_elapsed = (sprint.end_date - sprint.start_date).days + 1
        
        velocity = progress["completed_story_points"] / days_elapsed if days_elapsed > 0 else 0.0
        
        # Create lightweight ticket summaries instead of full objects
        ticket_summaries = [
            create_lightweight_summary(t, ["id", "title", "status"])
            for t in tickets
        ]
        
        # Add sprint-specific metrics to the unified progress data
        progress["velocity"] = round(velocity, 2)
        progress["days_elapsed"] = days_elapsed
        progress["tickets"] = ticket_summaries
        
        return progress


def calculate_sprint_progress(sprint: Sprint) -> Dict[str, Any]:
    """Calculate progress metrics for a sprint."""
    # Use optimized version to prevent recursion issues
    return calculate_sprint_progress_optimized(sprint)


@register_tool(
    name="list_sprints",
    description="List sprints with optional filtering",
    schema=SprintListFilter.model_json_schema(),
)
@secure_operation("sprint.list")
@require_gira_project
@rate_limit(max_calls=2000, window_seconds=60)
def list_sprints(
    status: Optional[str] = None,
    name: Optional[str] = None,
    limit: Optional[int] = None,
) -> OperationResult:
    """
    List sprints with optional filtering.

    Args:
        status: Filter by status (planned, active, completed)
        name: Filter by name (partial match)
        limit: Maximum number of sprints to return (1-100)

    Returns:
        OperationResult with list of sprint summaries
    """
    try:
        sprints = load_all_sprints()
        
        # Apply filters
        if status:
            sprints = [sprint for sprint in sprints if sprint.status == status]
        
        if name:
            sprints = [sprint for sprint in sprints if name.lower() in sprint.name.lower()]
        
        # Sort by start date (most recent first)
        sprints.sort(key=lambda s: s.start_date, reverse=True)
        
        # Apply limit
        if limit:
            sprints = sprints[:limit]
        
        # Convert to summaries
        sprint_summaries = []
        for sprint in sprints:
            progress = calculate_sprint_progress(sprint)
            summary = SprintSummary(
                id=sprint.id,
                name=sprint.name,
                status=sprint.status,
                goal=sprint.goal,
                start_date=sprint.start_date.isoformat(),
                end_date=sprint.end_date.isoformat(),
                duration_days=(sprint.end_date - sprint.start_date).days + 1,
                ticket_count=progress["total_tickets"],
                completed_tickets=progress["completed_tickets"],
                progress_percentage=progress["progress_percentage"],
                created_at=sprint.created_at.isoformat(),
                updated_at=sprint.updated_at.isoformat()
            )
            sprint_summaries.append(summary.model_dump())
        
        return OperationResult(
            success=True,
            message=f"Found {len(sprint_summaries)} sprints",
            data={
                "sprints": sprint_summaries,
                "total_count": len(sprint_summaries),
                "filters_applied": {
                    "status": status,
                    "name": name,
                    "limit": limit
                }
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error listing sprints")
        raise MCPToolError(f"Failed to list sprints: {str(e)}") from e


@register_tool(
    name="get_sprint",
    description="Get detailed information about a specific sprint",
    schema={"type": "object", "properties": {"sprint_id": {"type": "string", "description": "Sprint ID to retrieve"}}},
)
@secure_operation("sprint.get")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
def get_sprint(sprint_id: str) -> OperationResult:
    """
    Get detailed information about a specific sprint.

    Args:
        sprint_id: The sprint ID to retrieve

    Returns:
        OperationResult with detailed sprint information
    """
    try:
        sprint = find_sprint(sprint_id)
        if not sprint:
            raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
        
        # Get progress metrics
        progress = calculate_sprint_progress(sprint)
        
        sprint_data = sprint.model_dump()
        sprint_data.update({
            "progress": progress,
            "file_path": str(get_project_root() / ".gira" / "sprints" / f"{sprint.id}.json")
        })
        
        return OperationResult(
            success=True,
            message=f"Retrieved sprint {sprint_id}",
            data=sprint_data
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error getting sprint {sprint_id}")
        raise MCPToolError(f"Failed to get sprint: {str(e)}") from e


@register_tool(
    name="create_sprint",
    description="Create a new sprint",
    schema=SprintCreateRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("sprint.create")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def create_sprint(
    name: str,
    goal: Optional[str] = None,
    duration_days: int = 14,
    start_date: Optional[str] = None,
) -> OperationResult:
    """
    Create a new sprint.

    Args:
        name: Sprint name
        goal: Sprint goal/objective
        duration_days: Sprint duration in days (1-30)
        start_date: Sprint start date (ISO format: YYYY-MM-DD, defaults to today)

    Returns:
        OperationResult with created sprint information
    """
    try:
        # Parse start date
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError(f"Invalid start date format '{start_date}'. Use YYYY-MM-DD format.")
        else:
            start_date_obj = date.today()
        
        # Calculate end date
        end_date_obj = start_date_obj + timedelta(days=duration_days - 1)
        
        # Generate sprint ID
        sprint_id = f"SPRINT-{start_date_obj.isoformat()}"
        
        # Check if sprint with this ID already exists
        if find_sprint(sprint_id):
            raise ValidationError(f"Sprint with ID {sprint_id} already exists")
        
        # Validate duration
        if duration_days < 1 or duration_days > 30:
            raise ValidationError(f"Duration must be between 1 and 30 days, got {duration_days}")
        
        # Create sprint
        sprint = Sprint(
            id=sprint_id,
            name=name,
            goal=goal,
            start_date=start_date_obj,
            end_date=end_date_obj,
            status=SprintStatus.PLANNED
        )
        
        # Save sprint
        sprint_path = save_sprint(sprint)
        
        logger.info(f"Created sprint {sprint_id}: {name}")
        
        return OperationResult(
            success=True,
            message=f"Created sprint {sprint_id}",
            data={
                "sprint": sprint.model_dump(),
                "file_path": str(sprint_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error creating sprint")
        raise MCPToolError(f"Failed to create sprint: {str(e)}") from e


@register_tool(
    name="start_sprint",
    description="Start a planned sprint",
    schema={"type": "object", "properties": {"sprint_id": {"type": "string", "description": "Sprint ID to start"}}},
    is_destructive=True,
)
@secure_operation("sprint.start")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def start_sprint(sprint_id: str) -> OperationResult:
    """
    Start a planned sprint.

    Args:
        sprint_id: Sprint ID to start

    Returns:
        OperationResult with updated sprint information
    """
    try:
        sprint = find_sprint(sprint_id)
        if not sprint:
            raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
        
        if sprint.status != SprintStatus.PLANNED:
            raise ValidationError(f"Cannot start sprint {sprint_id} with status '{sprint.status}'. Only planned sprints can be started.")
        
        # Check if there's already an active sprint
        sprints = load_all_sprints()
        active_sprints = [s for s in sprints if s.status == SprintStatus.ACTIVE]
        
        if active_sprints:
            active_sprint_names = [s.name for s in active_sprints]
            raise ValidationError(f"Cannot start sprint - active sprint(s) already exist: {', '.join(active_sprint_names)}")
        
        # Update sprint status
        sprint.status = SprintStatus.ACTIVE
        sprint.updated_at = datetime.utcnow()
        
        # Save sprint
        sprint_path = save_sprint(sprint)
        
        logger.info(f"Started sprint {sprint_id}: {sprint.name}")
        
        return OperationResult(
            success=True,
            message=f"Started sprint {sprint_id}",
            data={
                "sprint": sprint.model_dump(),
                "file_path": str(sprint_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error starting sprint {sprint_id}")
        raise MCPToolError(f"Failed to start sprint: {str(e)}") from e


@register_tool(
    name="complete_sprint",
    description="Complete an active sprint",
    schema={"type": "object", "properties": {"sprint_id": {"type": "string", "description": "Sprint ID to complete"}}},
    is_destructive=True,
)
@secure_operation("sprint.complete")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def complete_sprint(sprint_id: str) -> OperationResult:
    """
    Complete an active sprint.

    Args:
        sprint_id: Sprint ID to complete

    Returns:
        OperationResult with completed sprint information and metrics
    """
    try:
        sprint = find_sprint(sprint_id)
        if not sprint:
            raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
        
        if sprint.status != SprintStatus.ACTIVE:
            raise ValidationError(f"Cannot complete sprint {sprint_id} with status '{sprint.status}'. Only active sprints can be completed.")
        
        # Calculate final metrics
        final_metrics = calculate_sprint_progress(sprint)
        
        # Update sprint status
        sprint.status = SprintStatus.COMPLETED
        sprint.updated_at = datetime.utcnow()
        
        # Save sprint
        sprint_path = save_sprint(sprint)
        
        logger.info(f"Completed sprint {sprint_id}: {sprint.name}")
        
        return OperationResult(
            success=True,
            message=f"Completed sprint {sprint_id}",
            data={
                "sprint": sprint.model_dump(),
                "final_metrics": final_metrics,
                "file_path": str(sprint_path)
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error completing sprint {sprint_id}")
        raise MCPToolError(f"Failed to complete sprint: {str(e)}") from e


@register_tool(
    name="add_tickets_to_sprint",
    description="Add tickets to a sprint",
    schema=SprintTicketRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("sprint.add_tickets")
@require_gira_project
@rate_limit(max_calls=300, window_seconds=60)
def add_tickets_to_sprint(
    sprint_id: str,
    ticket_ids: List[str]
) -> OperationResult:
    """
    Add tickets to a sprint.

    Args:
        sprint_id: Sprint ID
        ticket_ids: List of ticket IDs to add to the sprint

    Returns:
        OperationResult with operation details
    """
    try:
        # Verify sprint exists
        sprint = find_sprint(sprint_id)
        if not sprint:
            raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
        
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
            
            current_sprint = getattr(ticket, 'sprint_id', None)
            if current_sprint == sprint_id:
                already_assigned_tickets.append(ticket_id)
                continue
            
            # Update ticket's sprint
            ticket.sprint_id = sprint_id
            
            # Update timestamp
            ticket.updated_at = datetime.utcnow()
            
            save_ticket(ticket, ticket_path)
            updated_tickets.append(ticket_id)
        
        # Prepare result
        result_data = {
            "sprint_id": sprint_id,
            "updated_tickets": updated_tickets,
            "already_assigned": already_assigned_tickets,
            "not_found": not_found_tickets,
            "total_processed": len(ticket_ids),
            "successful_updates": len(updated_tickets)
        }
        
        if not_found_tickets:
            message = f"Added {len(updated_tickets)} tickets to sprint {sprint_id}. {len(not_found_tickets)} tickets not found."
        elif already_assigned_tickets:
            message = f"Added {len(updated_tickets)} tickets to sprint {sprint_id}. {len(already_assigned_tickets)} tickets already assigned."
        else:
            message = f"Successfully added {len(updated_tickets)} tickets to sprint {sprint_id}"
        
        logger.info(f"Added tickets to sprint {sprint_id}: {updated_tickets}")
        
        return OperationResult(
            success=True,
            message=message,
            data=result_data
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error adding tickets to sprint {sprint_id}")
        raise MCPToolError(f"Failed to add tickets to sprint: {str(e)}") from e


@register_tool(
    name="remove_tickets_from_sprint",
    description="Remove tickets from a sprint",
    schema=SprintTicketRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("sprint.remove_tickets")
@require_gira_project
@rate_limit(max_calls=300, window_seconds=60)
def remove_tickets_from_sprint(
    sprint_id: str,
    ticket_ids: List[str]
) -> OperationResult:
    """
    Remove tickets from a sprint.

    Args:
        sprint_id: Sprint ID
        ticket_ids: List of ticket IDs to remove from the sprint

    Returns:
        OperationResult with operation details
    """
    try:
        # Verify sprint exists
        sprint = find_sprint(sprint_id)
        if not sprint:
            raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
        
        # Load all tickets to validate and update
        from gira.utils.ticket_utils import find_ticket, save_ticket
        
        updated_tickets = []
        not_found_tickets = []
        not_in_sprint_tickets = []
        
        for ticket_id in ticket_ids:
            # Normalize ticket ID using configurable prefix
            from gira.mcp.tools import normalize_ticket_id
            ticket_id = normalize_ticket_id(ticket_id)
            
            root = get_project_root()
            ticket, ticket_path = find_ticket(ticket_id, root)
            if not ticket:
                not_found_tickets.append(ticket_id)
                continue
            
            current_sprint = getattr(ticket, 'sprint_id', None)
            if current_sprint != sprint_id:
                not_in_sprint_tickets.append(ticket_id)
                continue
            
            # Remove ticket from sprint
            ticket.sprint_id = None
            
            # Update timestamp
            ticket.updated_at = datetime.utcnow()
            
            save_ticket(ticket, ticket_path)
            updated_tickets.append(ticket_id)
        
        # Prepare result
        result_data = {
            "sprint_id": sprint_id,
            "updated_tickets": updated_tickets,
            "not_in_sprint": not_in_sprint_tickets,
            "not_found": not_found_tickets,
            "total_processed": len(ticket_ids),
            "successful_updates": len(updated_tickets)
        }
        
        if not_found_tickets:
            message = f"Removed {len(updated_tickets)} tickets from sprint {sprint_id}. {len(not_found_tickets)} tickets not found."
        elif not_in_sprint_tickets:
            message = f"Removed {len(updated_tickets)} tickets from sprint {sprint_id}. {len(not_in_sprint_tickets)} tickets not in this sprint."
        else:
            message = f"Successfully removed {len(updated_tickets)} tickets from sprint {sprint_id}"
        
        logger.info(f"Removed tickets from sprint {sprint_id}: {updated_tickets}")
        
        return OperationResult(
            success=True,
            message=message,
            data=result_data
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error removing tickets from sprint {sprint_id}")
        raise MCPToolError(f"Failed to remove tickets from sprint: {str(e)}") from e


@register_tool(
    name="get_sprint_tickets",
    description="Get all tickets in a sprint",
    schema={"type": "object", "properties": {
        "sprint_id": {"type": "string", "description": "Sprint ID"},
        "status": {"type": "string", "description": "Filter tickets by status"},
        "limit": {"type": "integer", "description": "Maximum number of tickets to return", "minimum": 1, "maximum": 100}
    }, "required": ["sprint_id"]},
)
@secure_operation("sprint.get_tickets")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
def get_sprint_tickets(
    sprint_id: str,
    status: Optional[str] = None,
    limit: Optional[int] = None,
) -> OperationResult:
    """
    Get all tickets in a sprint.

    Args:
        sprint_id: Sprint ID
        status: Filter tickets by status
        limit: Maximum number of tickets to return

    Returns:
        OperationResult with sprint tickets
    """
    try:
        # Verify sprint exists
        sprint = find_sprint(sprint_id)
        if not sprint:
            raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
        
        # Get tickets
        tickets = get_sprint_tickets_optimized(sprint_id)
        
        # Apply filters
        if status:
            tickets = [ticket for ticket in tickets if ticket.status == status]
        
        if limit:
            tickets = tickets[:limit]
        
        # Convert to summaries using unified formatter
        ticket_summaries = [
            format_ticket_summary(ticket, include_fields=[
                "id", "title", "status", "type", "priority", "assignee", 
                "epic_id", "story_points", "created_at", "updated_at"
            ])
            for ticket in tickets
        ]
        
        return OperationResult(
            success=True,
            message=f"Found {len(ticket_summaries)} tickets in sprint {sprint_id}",
            data={
                "sprint_id": sprint_id,
                "sprint_name": sprint.name,
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
        logger.exception(f"Error getting tickets for sprint {sprint_id}")
        raise MCPToolError(f"Failed to get sprint tickets: {str(e)}") from e


@register_tool(
    name="get_sprint_metrics",
    description="Get detailed metrics for a sprint",
    schema={"type": "object", "properties": {"sprint_id": {"type": "string", "description": "Sprint ID"}}},
)
@secure_operation("sprint.metrics")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
@with_timeout(30)  # 30 second timeout for metrics calculation
def get_sprint_metrics(sprint_id: str) -> OperationResult:
    """
    Get detailed metrics for a sprint including velocity and burndown data.

    Args:
        sprint_id: Sprint ID

    Returns:
        OperationResult with sprint metrics
    """
    try:
        with performance_monitor(f"get_sprint_metrics {sprint_id}"):
            # Verify sprint exists
            sprint = find_sprint(sprint_id)
            if not sprint:
                raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
            
            # Pre-build and cache all tickets grouped by sprint_id to avoid repeated loading
            tickets_cache = build_sprint_tickets_cache()
            
            # Calculate comprehensive metrics with optimized calculation
            progress = calculate_sprint_progress_optimized(sprint, tickets_cache)
            tickets = get_sprint_tickets_optimized(sprint_id, tickets_cache)
            
            # Status breakdown
            status_breakdown = {}
            for ticket in tickets:
                status = ticket.status
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            # Priority breakdown
            priority_breakdown = {}
            for ticket in tickets:
                priority = ticket.priority
                priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
            
            # Type breakdown
            type_breakdown = {}
            for ticket in tickets:
                ticket_type = ticket.type
                type_breakdown[ticket_type] = type_breakdown.get(ticket_type, 0) + 1
            
            # Calculate remaining work
            remaining_tickets = progress["total_tickets"] - progress["completed_tickets"]
            remaining_story_points = progress["total_story_points"] - progress["completed_story_points"]
            
            # Time metrics
            today = date.today()
            days_remaining = max(0, (sprint.end_date - today).days)
            
            metrics = {
                "sprint_info": {
                    "id": sprint.id,
                    "name": sprint.name,
                    "status": sprint.status,
                    "start_date": sprint.start_date.isoformat(),
                    "end_date": sprint.end_date.isoformat(),
                    "duration_days": (sprint.end_date - sprint.start_date).days + 1,
                    "days_elapsed": progress["days_elapsed"],
                    "days_remaining": days_remaining
                },
                "progress": progress,
                "remaining_work": {
                    "tickets": remaining_tickets,
                    "story_points": remaining_story_points
                },
                "breakdowns": {
                    "by_status": status_breakdown,
                    "by_priority": priority_breakdown,
                    "by_type": type_breakdown
                },
                "velocity": {
                    "story_points_per_day": progress["velocity"],
                    "projected_completion": remaining_story_points / max(progress["velocity"], 0.1) if progress["velocity"] > 0 else None
                }
            }
        
        return OperationResult(
            success=True,
            message=f"Retrieved metrics for sprint {sprint_id}",
            data=safe_model_dump(metrics, max_depth=4)
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error getting metrics for sprint {sprint_id}")
        raise MCPToolError(f"Failed to get sprint metrics: {str(e)}") from e


@register_tool(
    name="update_sprint",
    description="Update an existing sprint",
    schema={
        "type": "object",
        "properties": {
            "sprint_id": {"type": "string", "description": "Sprint ID to update"},
            "name": {"type": "string", "description": "New sprint name"},
            "goal": {"type": "string", "description": "New sprint goal"},
            "status": {"type": "string", "description": "New sprint status", "enum": ["planning", "active", "completed"]},
            "start_date": {"type": "string", "description": "New start date (ISO format)"},
            "end_date": {"type": "string", "description": "New end date (ISO format)"}
        },
        "required": ["sprint_id"]
    },
    is_destructive=True,
)
@secure_operation("sprint.update")
@require_gira_project
@rate_limit(max_calls=300, window_seconds=60)
def update_sprint(
    sprint_id: str,
    name: Optional[str] = None,
    goal: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> OperationResult:
    """
    Update an existing sprint.

    Args:
        sprint_id: Sprint ID to update
        name: New sprint name
        goal: New sprint goal
        status: New sprint status (planning, active, completed)
        start_date: New start date (ISO format)
        end_date: New end date (ISO format)

    Returns:
        OperationResult with updated sprint information
    """
    try:
        with performance_monitor(f"update_sprint {sprint_id}"):
            # Normalize sprint ID
            if sprint_id.isdigit():
                sprint_id = f"SPRINT-{sprint_id.zfill(3)}"
            elif not sprint_id.upper().startswith("SPRINT-"):
                sprint_id = f"SPRINT-{sprint_id}".upper()
            else:
                sprint_id = sprint_id.upper()
            
            # Find the sprint
            sprint = find_sprint(sprint_id)
            if not sprint:
                raise NotFoundError(f"Sprint {sprint_id} not found", resource_type="sprint", resource_id=sprint_id)
            
            # Track changes
            changes = []
            
            # Update fields
            if name is not None:
                sprint.name = name
                changes.append(f"name: '{name}'")
            
            if goal is not None:
                sprint.goal = goal
                changes.append("goal updated")
            
            if status is not None:
                valid_statuses = ["planning", "active", "completed"]
                if status not in valid_statuses:
                    raise ValidationError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
                sprint.status = status
                changes.append(f"status: {status}")
            
            if start_date is not None:
                try:
                    parsed_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    sprint.start_date = parsed_date
                    changes.append(f"start_date: {start_date}")
                except ValueError as e:
                    raise ValidationError(f"Invalid start_date format: {e}")
            
            if end_date is not None:
                try:
                    parsed_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    sprint.end_date = parsed_date
                    changes.append(f"end_date: {end_date}")
                except ValueError as e:
                    raise ValidationError(f"Invalid end_date format: {e}")
            
            if not changes:
                return OperationResult(
                    success=True,
                    message=f"Sprint {sprint_id} unchanged (no updates provided)",
                    data=safe_model_dump(sprint, max_depth=4)
                )
            
            # Update timestamp
            sprint.updated_at = datetime.utcnow()
            
            # Save sprint
            sprint_path = save_sprint(sprint)
            
            logger.info(f"Updated sprint {sprint_id}: {', '.join(changes)}")
            
            return OperationResult(
                success=True,
                message=f"Updated sprint {sprint_id}: {', '.join(changes)}",
                data={
                    "sprint": safe_model_dump(sprint, max_depth=4),
                    "changes": changes,
                    "file_path": str(sprint_path)
                }
            )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error updating sprint {sprint_id}")
        raise MCPToolError(f"Failed to update sprint: {str(e)}") from e