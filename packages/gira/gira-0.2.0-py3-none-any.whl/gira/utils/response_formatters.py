"""Shared response formatting and data transformation utilities for Gira.

This module provides unified formatting functions that eliminate duplication between
CLI output and MCP responses, ensuring consistent data formats across all interfaces.
"""

import logging
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# ============================================================================
# Ticket Formatting Functions  
# ============================================================================

def format_ticket_summary(ticket: Any, include_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create standardized ticket summary with consistent field formatting.
    
    Args:
        ticket: Ticket object to format
        include_fields: Optional list of specific fields to include. If None, includes standard fields.
        
    Returns:
        Dictionary with formatted ticket summary
    """
    if include_fields is None:
        include_fields = ["id", "title", "status", "priority", "type", "assignee", "story_points"]
    
    summary = {}
    
    # Always include core identification
    summary["id"] = getattr(ticket, 'id', None)
    summary["title"] = getattr(ticket, 'title', None)
    
    # Include requested fields
    for field in include_fields:
        if field in ["id", "title"]:  # Already handled above
            continue
            
        value = getattr(ticket, field, None)
        
        # Special handling for specific fields
        if field in ["created_at", "updated_at"] and value:
            summary[field] = format_timestamp(value)
        elif field == "story_points":
            # Handle both attribute and method access patterns
            summary[field] = getattr(ticket, 'story_points', None)
        else:
            summary[field] = extract_enum_value(value) if hasattr(value, 'value') else value
    
    return summary


def format_ticket_details(ticket: Any, include_context: bool = True) -> Dict[str, Any]:
    """Create detailed ticket information with optional epic/sprint context.
    
    Args:
        ticket: Ticket object to format
        include_context: Whether to include epic and sprint context information
        
    Returns:
        Dictionary with comprehensive ticket details
    """
    details = {
        "id": ticket.id,
        "title": ticket.title,
        "description": getattr(ticket, 'description', ''),
        "status": extract_enum_value(ticket.status),
        "priority": extract_enum_value(ticket.priority),
        "type": extract_enum_value(ticket.type),
        "assignee": ticket.assignee,
        "reporter": getattr(ticket, 'reporter', None),
        "story_points": getattr(ticket, 'story_points', None),
        "labels": getattr(ticket, 'labels', []),
        "created_at": format_timestamp(ticket.created_at),
        "updated_at": format_timestamp(ticket.updated_at),
    }
    
    # Add context information if requested
    if include_context:
        if hasattr(ticket, 'epic_id') and ticket.epic_id:
            details["epic_id"] = ticket.epic_id
        if hasattr(ticket, 'sprint_id') and ticket.sprint_id:
            details["sprint_id"] = ticket.sprint_id
        if hasattr(ticket, 'parent_id') and ticket.parent_id:
            details["parent_id"] = ticket.parent_id
    
    # Add relationship information
    if hasattr(ticket, 'blocked_by'):
        details["blocked_by"] = ticket.blocked_by or []
    if hasattr(ticket, 'blocks'):
        details["blocks"] = ticket.blocks or []
    
    # Add custom fields if present
    if hasattr(ticket, 'custom_fields') and ticket.custom_fields:
        details["custom_fields"] = ticket.custom_fields
    
    return details


def format_ticket_list(tickets: List[Any], format_type: str = "summary", include_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Format a list of tickets consistently.
    
    Args:
        tickets: List of ticket objects to format
        format_type: Type of formatting ("summary" or "details")
        include_fields: Optional list of fields to include for summary format
        
    Returns:
        List of formatted ticket dictionaries
    """
    if format_type == "details":
        return [format_ticket_details(ticket) for ticket in tickets]
    else:
        return [format_ticket_summary(ticket, include_fields) for ticket in tickets]


# ============================================================================
# Timestamp and Date Formatting
# ============================================================================

def format_timestamp(dt: Union[datetime, str, None]) -> Optional[str]:
    """Convert datetime objects to consistent ISO string format.
    
    Args:
        dt: Datetime object, ISO string, or None
        
    Returns:
        ISO formatted string or None
    """
    if dt is None:
        return None
    
    if isinstance(dt, str):
        # Already a string, assume it's properly formatted
        return dt
    
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    
    return str(dt)


def format_timestamps(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Format all datetime fields in a dictionary to ISO strings.
    
    Args:
        obj: Dictionary potentially containing datetime fields
        
    Returns:
        Dictionary with formatted timestamp fields
    """
    formatted = obj.copy()
    
    timestamp_fields = ['created_at', 'updated_at', 'started_at', 'completed_at', 'due_date']
    
    for field in timestamp_fields:
        if field in formatted:
            formatted[field] = format_timestamp(formatted[field])
    
    return formatted


def format_date_range(start_date: Optional[datetime], end_date: Optional[datetime]) -> Dict[str, Optional[str]]:
    """Format date range consistently.
    
    Args:
        start_date: Start date or None
        end_date: End date or None
        
    Returns:
        Dictionary with formatted start and end dates
    """
    return {
        "start_date": format_timestamp(start_date),
        "end_date": format_timestamp(end_date)
    }


# ============================================================================
# Progress Calculation Functions
# ============================================================================

def calculate_epic_progress(epic: Any, tickets: List[Any]) -> Dict[str, Any]:
    """Calculate epic progress with consistent metrics.
    
    Args:
        epic: Epic object 
        tickets: List of tickets associated with the epic
        
    Returns:
        Dictionary with progress metrics
    """
    total_tickets = len(tickets)
    completed_tickets = len([t for t in tickets if getattr(t, 'status', '') == 'done'])
    
    # Calculate story points
    total_story_points = sum(getattr(t, 'story_points', 0) or 0 for t in tickets)
    completed_story_points = sum(
        getattr(t, 'story_points', 0) or 0 
        for t in tickets 
        if getattr(t, 'status', '') == 'done'
    )
    
    # Calculate percentages
    progress_percentage = calculate_completion_percentage(total_tickets, completed_tickets)
    story_point_progress = calculate_completion_percentage(total_story_points, completed_story_points)
    
    return {
        "total_tickets": total_tickets,
        "completed_tickets": completed_tickets,
        "progress_percentage": progress_percentage,
        "total_story_points": total_story_points,
        "completed_story_points": completed_story_points,
        "story_point_progress": story_point_progress,
    }


def calculate_sprint_progress(sprint: Any, tickets: Optional[List[Any]] = None) -> Dict[str, Any]:
    """Calculate sprint progress with consistent metrics.
    
    Args:
        sprint: Sprint object
        tickets: Optional list of tickets. If None, will try to load from sprint.
        
    Returns:
        Dictionary with progress metrics  
    """
    # Try to get tickets from sprint object if not provided
    if tickets is None:
        tickets = getattr(sprint, 'tickets', [])
    
    # Filter tickets that belong to this sprint
    if hasattr(sprint, 'id'):
        sprint_tickets = [t for t in tickets if getattr(t, 'sprint_id', None) == sprint.id]
    else:
        sprint_tickets = tickets
    
    return calculate_epic_progress(sprint, sprint_tickets)  # Same calculation logic


def calculate_completion_percentage(total: int, completed: int) -> float:
    """Calculate completion percentage with consistent rounding.
    
    Args:
        total: Total count
        completed: Completed count
        
    Returns:
        Percentage rounded to 1 decimal place
    """
    if total == 0:
        return 0.0
    
    percentage = (completed / total) * 100
    return round(percentage, 1)


# ============================================================================
# Board Statistics and Status Distribution  
# ============================================================================

def format_board_statistics(tickets: List[Any]) -> Dict[str, Any]:
    """Calculate comprehensive board statistics.
    
    Args:
        tickets: List of all tickets to analyze
        
    Returns:
        Dictionary with board statistics
    """
    # Group by status
    status_counts = format_status_distribution(tickets)
    
    # Calculate totals
    total_tickets = len(tickets)
    completed_tickets = status_counts.get("done", 0)
    in_progress_tickets = status_counts.get("in_progress", 0) + status_counts.get("review", 0)
    
    return {
        "total_tickets": total_tickets,
        "completed_tickets": completed_tickets,
        "in_progress_tickets": in_progress_tickets,
        "status_distribution": status_counts,
        "completion_rate": calculate_completion_percentage(total_tickets, completed_tickets)
    }


def format_status_distribution(tickets: List[Any]) -> Dict[str, int]:
    """Group tickets by status with counts.
    
    Args:
        tickets: List of tickets to group
        
    Returns:
        Dictionary mapping status to count
    """
    distribution = {}
    
    for ticket in tickets:
        status = extract_enum_value(getattr(ticket, 'status', 'unknown'))
        distribution[status] = distribution.get(status, 0) + 1
    
    return distribution


def format_swimlane_data(tickets: List[Any], board_config: Optional[Any] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Organize tickets by swimlanes/statuses for board display.
    
    Args:
        tickets: List of tickets to organize
        board_config: Optional board configuration for swimlane definitions
        
    Returns:
        Dictionary mapping swimlane/status to ticket lists
    """
    swimlanes = {}
    
    # Use standard statuses if no board config provided
    if board_config and hasattr(board_config, 'swimlanes'):
        statuses = [swimlane.id for swimlane in board_config.swimlanes]
    else:
        statuses = ["backlog", "todo", "in_progress", "review", "done"]
    
    # Initialize all swimlanes
    for status in statuses:
        swimlanes[status] = []
    
    # Distribute tickets
    for ticket in tickets:
        status = extract_enum_value(getattr(ticket, 'status', 'todo'))
        if status not in swimlanes:
            swimlanes[status] = []
        swimlanes[status].append(format_ticket_summary(ticket))
    
    return swimlanes


# ============================================================================
# Operation Results and Error Formatting
# ============================================================================

def format_operation_result(success: bool, message: str, data: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
    """Create consistent OperationResult format.
    
    Args:
        success: Whether the operation succeeded
        message: Description of the result
        data: Optional result data
        **kwargs: Additional fields to include
        
    Returns:
        Formatted operation result dictionary
    """
    result = {
        "success": success,
        "message": message,
    }
    
    if data is not None:
        result["data"] = sanitize_for_json(data)
    
    # Add any additional fields
    result.update(kwargs)
    
    return result


def format_bulk_operation_result(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Format results from bulk operations consistently.
    
    Args:
        results: List of individual operation results
        
    Returns:
        Consolidated bulk operation result
    """
    total_operations = len(results)
    successful_operations = sum(1 for r in results if r.get("success", False))
    failed_operations = total_operations - successful_operations
    
    return {
        "success": failed_operations == 0,
        "total_operations": total_operations,
        "successful_operations": successful_operations,
        "failed_operations": failed_operations,
        "results": results,
        "summary": f"{successful_operations}/{total_operations} operations completed successfully"
    }


def format_error_response(error: Union[Exception, str], context: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response format.
    
    Args:
        error: Exception or error message
        context: Optional context description
        
    Returns:
        Formatted error response
    """
    error_message = str(error)
    
    result = {
        "success": False,
        "error": error_message,
    }
    
    if context:
        result["context"] = context
    
    # Add error type if it's an exception
    if isinstance(error, Exception):
        result["error_type"] = type(error).__name__
    
    return result


# ============================================================================
# Data Transformation Utilities
# ============================================================================

def extract_enum_value(obj: Any) -> Any:
    """Safely extract value from enum objects.
    
    Args:
        obj: Any object, potentially an enum
        
    Returns:
        Enum value if it's an enum, otherwise the original object
    """
    if obj is None:
        return None
    
    # Handle enum objects
    if hasattr(obj, 'value'):
        return obj.value
    
    # Handle string representations of enums
    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
        if obj.__class__.__name__.endswith(('Status', 'Priority', 'Type')):
            return str(obj).lower()
    
    return obj


def sanitize_for_json(obj: Any, max_depth: int = 5) -> Any:
    """Prepare objects for JSON serialization by handling complex types.
    
    Args:
        obj: Object to sanitize
        max_depth: Maximum recursion depth
        
    Returns:
        JSON-serializable version of the object
    """
    def _sanitize(item: Any, depth: int = 0) -> Any:
        if depth >= max_depth:
            return "<max_depth_reached>"
        
        if item is None or isinstance(item, (str, int, float, bool)):
            return item
        
        if isinstance(item, (list, tuple)):
            return [_sanitize(i, depth + 1) for i in item]
        
        if isinstance(item, dict):
            return {k: _sanitize(v, depth + 1) for k, v in item.items()}
        
        # Handle datetime objects
        if hasattr(item, 'isoformat'):
            return format_timestamp(item)
        
        # Handle enum objects
        if hasattr(item, 'value'):
            return extract_enum_value(item)
        
        # Handle Pydantic models
        if hasattr(item, 'model_dump'):
            try:
                return _sanitize(item.model_dump(), depth + 1)
            except Exception:
                return str(item)
        
        # Convert other objects to string
        return str(item)
    
    return _sanitize(obj)


def apply_field_selection(data: Union[Dict[str, Any], List[Dict[str, Any]]], fields: Optional[List[str]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Filter data to include only specified fields.
    
    Args:
        data: Dictionary or list of dictionaries to filter
        fields: List of field names to include. If None, returns original data.
        
    Returns:
        Filtered data with only specified fields
    """
    if fields is None:
        return data
    
    def _filter_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in d.items() if k in fields}
    
    if isinstance(data, list):
        return [_filter_dict(item) if isinstance(item, dict) else item for item in data]
    elif isinstance(data, dict):
        return _filter_dict(data)
    else:
        return data


# ============================================================================
# Caching and Performance Utilities
# ============================================================================

@lru_cache(maxsize=128)
def _cached_progress_calculation(epic_id: str, ticket_count: int, completed_count: int, total_points: int, completed_points: int) -> Dict[str, Any]:
    """Cached progress calculation for performance optimization."""
    return {
        "total_tickets": ticket_count,
        "completed_tickets": completed_count,
        "progress_percentage": calculate_completion_percentage(ticket_count, completed_count),
        "total_story_points": total_points,
        "completed_story_points": completed_points,
        "story_point_progress": calculate_completion_percentage(total_points, completed_points),
    }


def clear_format_cache():
    """Clear formatting caches for testing or when data changes significantly."""
    _cached_progress_calculation.cache_clear()
    logger.debug("Response formatter caches cleared")