"""Board and visualization tools for Gira MCP server."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from gira.mcp.config import get_config
from gira.mcp.schema import OperationResult
from gira.mcp.security import secure_operation, require_gira_project, rate_limit
from gira.mcp.tools import (
    MCPToolError,
    ValidationError,
    register_tool,
)
from gira.mcp.utils import performance_monitor
from gira.utils.project_management import get_project_root
from gira.utils.ticket_utils import load_all_tickets
from gira.utils.git_ops import move_with_git_fallback
from gira.utils.hybrid_storage import get_ticket_storage_path
from gira.utils.response_formatters import (
    format_board_statistics,
    format_status_distribution,
    format_swimlane_data,
    format_ticket_summary,
    format_operation_result,
)

logger = logging.getLogger(__name__)


def _should_use_git_for_mcp() -> bool:
    """Determine if git operations should be used for MCP operations.
    
    Uses the MCP server configuration which respects environment variables
    and defaults to git-enabled behavior for AI-friendly operations.
    
    Returns:
        Whether to use git operations for file moves
    """
    config = get_config()
    return config.should_use_git_operations()


class BoardStateRequest(BaseModel):
    """Request parameters for board state."""
    include_counts: bool = Field(True, description="Include ticket counts per status")
    include_tickets: bool = Field(False, description="Include full ticket details")
    include_epic_context: bool = Field(True, description="Include epic information")
    include_sprint_context: bool = Field(True, description="Include sprint information")
    status_filter: Optional[List[str]] = Field(None, description="Filter by specific statuses")


class SwimlaneMoveRequest(BaseModel):
    """Request to move tickets between swimlanes."""
    ticket_ids: List[str] = Field(description="List of ticket IDs to move", max_length=50)
    target_status: str = Field(description="Target status/swimlane")
    comment: Optional[str] = Field(None, description="Optional comment for the move")


@register_tool(
    name="get_enhanced_board_state",
    description="Get enhanced board state with epic and sprint context",
    schema=BoardStateRequest.model_json_schema(),
)
@secure_operation("board.enhanced_state")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
def get_enhanced_board_state(
    include_counts: bool = True,
    include_tickets: bool = False,
    include_epic_context: bool = True,
    include_sprint_context: bool = True,
    status_filter: Optional[List[str]] = None,
) -> OperationResult:
    """
    Get enhanced board state with epic and sprint context.

    Args:
        include_counts: Include ticket counts per status
        include_tickets: Include full ticket details
        include_epic_context: Include epic information
        include_sprint_context: Include sprint information
        status_filter: Filter by specific statuses

    Returns:
        OperationResult with enhanced board state
    """
    try:
        # Load all tickets using project root
        root = get_project_root()
        tickets = load_all_tickets(root)
        
        # Filter by status if specified
        if status_filter:
            tickets = [ticket for ticket in tickets if ticket.status in status_filter]
        
        # Group tickets by status
        board_state = {}
        status_counts = {}
        
        # Standard statuses
        standard_statuses = ["backlog", "todo", "in_progress", "review", "done"]
        
        for status in standard_statuses:
            status_tickets = [ticket for ticket in tickets if ticket.status == status]
            status_counts[status] = len(status_tickets)
            
            board_state[status] = {
                "count": len(status_tickets),
                "tickets": []
            }
            
            if include_tickets:
                for ticket in status_tickets:
                    # Use unified formatter for consistent ticket data
                    ticket_data = format_ticket_summary(ticket, include_fields=[
                        "id", "title", "type", "priority", "assignee", "story_points", 
                        "created_at", "updated_at"
                    ])
                    
                    # Add epic context if requested
                    if include_epic_context and ticket.epic_id:
                        from gira.mcp.epic_tools import find_epic
                        epic = find_epic(ticket.epic_id)
                        if epic:
                            ticket_data["epic"] = {
                                "id": epic.id,
                                "title": epic.title,
                                "status": epic.status
                            }
                    
                    # Add sprint context if requested
                    if include_sprint_context and hasattr(ticket, 'sprint_id') and ticket.sprint_id:
                        from gira.mcp.sprint_tools import find_sprint
                        sprint = find_sprint(ticket.sprint_id)
                        if sprint:
                            ticket_data["sprint"] = {
                                "id": sprint.id,
                                "name": sprint.name,
                                "status": sprint.status
                            }
                    
                    board_state[status]["tickets"].append(ticket_data)
        
        # Use unified formatter for board statistics
        board_stats = format_board_statistics(tickets)
        
        # Epic and sprint summaries
        epic_summary = {}
        sprint_summary = {}
        
        if include_epic_context:
            epic_tickets = {}
            for ticket in tickets:
                if ticket.epic_id:
                    if ticket.epic_id not in epic_tickets:
                        epic_tickets[ticket.epic_id] = []
                    epic_tickets[ticket.epic_id].append(ticket)
            
            for epic_id, epic_ticket_list in epic_tickets.items():
                from gira.mcp.epic_tools import find_epic
                epic = find_epic(epic_id)
                if epic:
                    completed_epic_tickets = len([t for t in epic_ticket_list if t.status == "done"])
                    epic_summary[epic_id] = {
                        "title": epic.title,
                        "status": epic.status,
                        "total_tickets": len(epic_ticket_list),
                        "completed_tickets": completed_epic_tickets,
                        "progress_percentage": round((completed_epic_tickets / len(epic_ticket_list)) * 100, 1) if epic_ticket_list else 0
                    }
        
        if include_sprint_context:
            sprint_tickets = {}
            for ticket in tickets:
                sprint_id = getattr(ticket, 'sprint_id', None)
                if sprint_id:
                    if sprint_id not in sprint_tickets:
                        sprint_tickets[sprint_id] = []
                    sprint_tickets[sprint_id].append(ticket)
            
            for sprint_id, sprint_ticket_list in sprint_tickets.items():
                from gira.mcp.sprint_tools import find_sprint
                sprint = find_sprint(sprint_id)
                if sprint:
                    completed_sprint_tickets = len([t for t in sprint_ticket_list if t.status == "done"])
                    sprint_summary[sprint_id] = {
                        "name": sprint.name,
                        "status": sprint.status,
                        "total_tickets": len(sprint_ticket_list),
                        "completed_tickets": completed_sprint_tickets,
                        "progress_percentage": round((completed_sprint_tickets / len(sprint_ticket_list)) * 100, 1) if sprint_ticket_list else 0
                    }
        
        result_data = {
            "board": board_state,
            "summary": {
                "total_tickets": board_stats["total_tickets"],
                "completed_tickets": board_stats["completed_tickets"], 
                "in_progress_tickets": board_stats["in_progress_tickets"],
                "completion_percentage": board_stats["completion_rate"]
            }
        }
        
        if include_epic_context:
            result_data["epics"] = epic_summary
        
        if include_sprint_context:
            result_data["sprints"] = sprint_summary
        
        if status_filter:
            result_data["filters_applied"] = {"status_filter": status_filter}
        
        return OperationResult(
            success=True,
            message=f"Retrieved enhanced board state with {board_stats['total_tickets']} tickets",
            data=result_data
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception("Error getting enhanced board state")
        raise MCPToolError(f"Failed to get enhanced board state: {str(e)}") from e


@register_tool(
    name="get_swimlane_tickets",
    description="Get tickets by status/swimlane with epic grouping",
    schema={"type": "object", "properties": {
        "status": {"type": "string", "description": "Status/swimlane to retrieve"},
        "group_by_epic": {"type": "boolean", "description": "Group tickets by epic", "default": True},
        "limit": {"type": "integer", "description": "Maximum number of tickets to return", "minimum": 1, "maximum": 100}
    }, "required": ["status"]},
)
@secure_operation("board.swimlane_tickets")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
def get_swimlane_tickets(
    status: str,
    group_by_epic: bool = True,
    limit: Optional[int] = None,
) -> OperationResult:
    """
    Get tickets by status/swimlane with optional epic grouping.

    Args:
        status: Status/swimlane to retrieve tickets from
        group_by_epic: Group tickets by epic
        limit: Maximum number of tickets to return

    Returns:
        OperationResult with swimlane tickets
    """
    try:
        # Load all tickets using project root
        root = get_project_root()
        tickets = load_all_tickets(root)
        
        # Filter by status
        status_tickets = [ticket for ticket in tickets if ticket.status == status]
        
        # Apply limit
        if limit:
            status_tickets = status_tickets[:limit]
        
        if not group_by_epic:
            # Simple list of tickets
            ticket_list = []
            for ticket in status_tickets:
                ticket_data = format_ticket_summary(ticket, include_fields=[
                    "id", "title", "type", "priority", "assignee", "epic_id", 
                    "story_points", "created_at", "updated_at"
                ])
                ticket_list.append(ticket_data)
            
            return OperationResult(
                success=True,
                message=f"Found {len(ticket_list)} tickets in {status} status",
                data={
                    "status": status,
                    "tickets": ticket_list,
                    "total_count": len(ticket_list),
                    "grouped_by_epic": False
                }
            )
        
        # Group by epic
        epic_groups = {}
        no_epic_tickets = []
        
        for ticket in status_tickets:
            ticket_data = format_ticket_summary(ticket, include_fields=[
                "id", "title", "type", "priority", "assignee", "story_points", 
                "created_at", "updated_at"
            ])
            
            if ticket.epic_id:
                if ticket.epic_id not in epic_groups:
                    # Get epic info
                    from gira.mcp.epic_tools import find_epic
                    epic = find_epic(ticket.epic_id)
                    epic_groups[ticket.epic_id] = {
                        "epic_info": {
                            "id": ticket.epic_id,
                            "title": epic.title if epic else "Unknown Epic",
                            "status": epic.status if epic else "unknown"
                        },
                        "tickets": []
                    }
                epic_groups[ticket.epic_id]["tickets"].append(ticket_data)
            else:
                no_epic_tickets.append(ticket_data)
        
        # Convert to list format
        grouped_tickets = []
        for epic_id, group_data in epic_groups.items():
            grouped_tickets.append(group_data)
        
        if no_epic_tickets:
            grouped_tickets.append({
                "epic_info": {
                    "id": None,
                    "title": "No Epic",
                    "status": None
                },
                "tickets": no_epic_tickets
            })
        
        return OperationResult(
            success=True,
            message=f"Found {len(status_tickets)} tickets in {status} status grouped by {len(grouped_tickets)} epics",
            data={
                "status": status,
                "epic_groups": grouped_tickets,
                "total_count": len(status_tickets),
                "epic_count": len(grouped_tickets),
                "grouped_by_epic": True
            }
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error getting swimlane tickets for status {status}")
        raise MCPToolError(f"Failed to get swimlane tickets: {str(e)}") from e


@register_tool(
    name="move_tickets_bulk",
    description="Move multiple tickets between swimlanes/statuses",
    schema=SwimlaneMoveRequest.model_json_schema(),
    is_destructive=True,
)
@secure_operation("board.bulk_move")
@require_gira_project
@rate_limit(max_calls=200, window_seconds=60)
def move_tickets_bulk(
    ticket_ids: List[str],
    target_status: str,
    comment: Optional[str] = None,
) -> OperationResult:
    """
    Move multiple tickets between swimlanes/statuses.

    Args:
        ticket_ids: List of ticket IDs to move
        target_status: Target status/swimlane
        comment: Optional comment for the move

    Returns:
        OperationResult with move operation details
    """
    try:
        # Validate target status
        valid_statuses = ["backlog", "todo", "in_progress", "review", "done"]
        if target_status not in valid_statuses:
            raise ValidationError(f"Invalid target status '{target_status}'. Must be one of: {valid_statuses}")
        
        # Load and update tickets
        from gira.utils.ticket_utils import find_ticket, save_ticket
        
        updated_tickets = []
        not_found_tickets = []
        already_in_status_tickets = []
        
        for ticket_id in ticket_ids:
            # Normalize ticket ID using configurable prefix
            from gira.mcp.tools import normalize_ticket_id
            ticket_id = normalize_ticket_id(ticket_id)
            
            root = get_project_root()
            ticket, ticket_path = find_ticket(ticket_id, root)
            if not ticket:
                not_found_tickets.append(ticket_id)
                continue
            
            if ticket.status == target_status:
                already_in_status_tickets.append(ticket_id)
                continue
            
            # Track the old status for logging
            old_status = ticket.status
            
            # Update ticket status
            ticket.status = target_status
            ticket.updated_at = datetime.utcnow()
            
            # Add comment if provided
            if comment:
                from gira.models import Comment
                
                new_comment = Comment(
                    id=f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}",
                    ticket_id=ticket.id,
                    content=f"Moved from {old_status} to {target_status}: {comment}",
                    author=getattr(ticket, 'assignee', 'system') or 'system'
                )
                
                # Add comment to ticket
                if not hasattr(ticket, 'comments') or not ticket.comments:
                    ticket.comments = []
                ticket.comments.append(new_comment)
                ticket.comment_count = len(ticket.comments)
            
            # Migrate ticket to correct directory based on new status using git-aware operations
            new_path = get_ticket_storage_path(ticket.id, target_status, root)
            
            # Create parent directory if needed
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use git-aware move if enabled, otherwise fall back to regular move
            if ticket_path != new_path:
                use_git = _should_use_git_for_mcp()
                try:
                    # Move file with git-aware operations and fallback
                    new_path = move_with_git_fallback(
                        source=ticket_path,
                        destination=new_path,
                        root=root,
                        use_git=use_git,
                        silent=True  # Suppress warnings in bulk operations
                    )
                except Exception as e:
                    # If git operation fails, fall back to basic file move
                    logger.warning(f"Git operation failed for {ticket_id}, using file system move: {e}")
                    ticket_path.rename(new_path)
            
            # Save ticket to new location
            ticket.save_to_json_file(str(new_path))
            
            updated_tickets.append({
                "ticket_id": ticket_id,
                "old_status": old_status,
                "new_status": target_status
            })
        
        # Prepare result
        result_data = {
            "target_status": target_status,
            "updated_tickets": updated_tickets,
            "already_in_status": already_in_status_tickets,
            "not_found": not_found_tickets,
            "total_processed": len(ticket_ids),
            "successful_updates": len(updated_tickets),
            "comment": comment
        }
        
        if not_found_tickets:
            message = f"Moved {len(updated_tickets)} tickets to {target_status}. {len(not_found_tickets)} tickets not found."
        elif already_in_status_tickets:
            message = f"Moved {len(updated_tickets)} tickets to {target_status}. {len(already_in_status_tickets)} tickets already in target status."
        else:
            message = f"Successfully moved {len(updated_tickets)} tickets to {target_status}"
        
        logger.info(f"Bulk moved tickets to {target_status}: {[t['ticket_id'] for t in updated_tickets]}")
        
        return OperationResult(
            success=True,
            message=message,
            data=result_data
        )

    except MCPToolError:
        raise
    except Exception as e:
        logger.exception(f"Error moving tickets in bulk to {target_status}")
        raise MCPToolError(f"Failed to move tickets in bulk: {str(e)}") from e


# Aliases for backward compatibility
get_board = get_enhanced_board_state


@register_tool(
    name="get_board_stats",
    description="Get basic board statistics",
    schema={"type": "object", "properties": {}},
)
@secure_operation("board.stats")
@require_gira_project
@rate_limit(max_calls=1000, window_seconds=60)
def get_board_stats() -> OperationResult:
    """
    Get basic board statistics.
    
    Returns:
        OperationResult with board statistics
    """
    try:
        with performance_monitor("get_board_stats"):
            # Get board state data
            board_result = get_enhanced_board_state()
            if not board_result.success:
                return board_result
                
            board_data = board_result.data
            
            # Calculate basic statistics
            stats = {
                "total_tickets": board_data.get("total_tickets", 0),
                "status_counts": board_data.get("status_counts", {}),
                "priority_distribution": board_data.get("priority_distribution", {}),
                "type_distribution": board_data.get("type_distribution", {}),
                "assignee_workload": board_data.get("assignee_workload", {}),
            }
            
            return OperationResult(
                success=True,
                message="Retrieved board statistics",
                data=stats
            )
    
    except MCPToolError:
        raise
    except Exception as e:
        logger.exception("Error retrieving board statistics")        
        raise MCPToolError(f"Failed to get board statistics: {str(e)}") from e