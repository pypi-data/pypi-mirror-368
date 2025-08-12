"""Utilities for field selection in JSON output."""

from typing import Any, Dict, List, Optional, Union


def filter_fields(data: Union[Dict[str, Any], List[Dict[str, Any]]],
                 fields: Optional[str]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Filter data to include only specified fields.
    
    Args:
        data: The data to filter (dict or list of dicts)
        fields: Comma-separated list of fields to include (supports nested fields with dot notation)
        
    Returns:
        Filtered data containing only the specified fields
        
    Examples:
        >>> data = {"id": "TEST-1", "title": "Test", "epic": {"id": "EPIC-1", "name": "Epic"}}
        >>> filter_fields(data, "id,title")
        {"id": "TEST-1", "title": "Test"}
        >>> filter_fields(data, "id,epic.name")
        {"id": "TEST-1", "epic": {"name": "Epic"}}
    """
    if not fields:
        return data

    field_list = [f.strip() for f in fields.split(",")]

    if isinstance(data, list):
        return [filter_single_item(item, field_list) for item in data]
    else:
        return filter_single_item(data, field_list)


def filter_single_item(item: Dict[str, Any], field_list: List[str]) -> Dict[str, Any]:
    """Filter a single dictionary item to include only specified fields."""
    result = {}

    for field in field_list:
        if "." in field:
            # Handle nested fields
            parts = field.split(".", 1)
            parent_field = parts[0]
            child_field = parts[1]

            if parent_field in item and item[parent_field] is not None:
                if parent_field not in result:
                    result[parent_field] = {}

                if isinstance(item[parent_field], dict):
                    # Single nested object
                    nested_result = filter_single_item(item[parent_field], [child_field])
                    if nested_result:
                        if isinstance(result.get(parent_field), dict):
                            result[parent_field].update(nested_result)
                        else:
                            result[parent_field] = nested_result
                elif isinstance(item[parent_field], list):
                    # List of objects
                    if parent_field not in result or not isinstance(result[parent_field], list):
                        result[parent_field] = []
                    for nested_item in item[parent_field]:
                        if isinstance(nested_item, dict):
                            nested_result = filter_single_item(nested_item, [child_field])
                            if nested_result:
                                result[parent_field].append(nested_result)
        else:
            # Top-level field
            if field in item:
                result[field] = item[field]

    return result


def get_common_field_aliases() -> Dict[str, str]:
    """Get common field aliases for user convenience.
    
    Returns:
        Dictionary mapping aliases to actual field paths
    """
    return {
        # Ticket aliases
        "basics": "id,title,status,priority,type",
        "assignments": "assignee,reporter",
        "relationships": "epic_id,sprint_id,parent_id,blocked_by,blocks",
        "metadata": "created_at,updated_at,labels,story_points",
        "all_ids": "id,uuid,epic_id,sprint_id,parent_id",

        # Epic aliases
        "epic_basics": "id,title,status,owner",
        "epic_progress": "tickets,created_at,updated_at,target_date",

        # Sprint aliases
        "sprint_basics": "id,name,status,goal",
        "sprint_dates": "start_date,end_date,created_at,updated_at",
        "sprint_metrics": "tickets,velocity",

        # Comment aliases
        "comment_basics": "id,author,content,created_at",

        # Common patterns
        "ids": "id,uuid",
        "timestamps": "created_at,updated_at",
        "status_priority": "status,priority",
    }


def expand_field_aliases(fields: str) -> str:
    """Expand field aliases to their actual field names.
    
    Args:
        fields: Comma-separated list of fields that may include aliases
        
    Returns:
        Expanded field list with aliases replaced
        
    Example:
        >>> expand_field_aliases("basics,epic.title")
        "id,title,status,priority,type,epic.title"
    """
    if not fields:
        return fields

    aliases = get_common_field_aliases()
    field_list = [f.strip() for f in fields.split(",")]
    expanded_fields = []

    for field in field_list:
        if field in aliases:
            # Expand alias
            expanded_fields.extend(aliases[field].split(","))
        else:
            # Keep original field
            expanded_fields.append(field)

    # Remove duplicates while preserving order
    seen = set()
    unique_fields = []
    for field in expanded_fields:
        if field not in seen:
            seen.add(field)
            unique_fields.append(field)

    return ",".join(unique_fields)


def validate_fields(data: Union[Dict[str, Any], List[Dict[str, Any]]],
                   fields: str) -> List[str]:
    """Validate that requested fields exist in the data.
    
    Args:
        data: The data to validate against
        fields: Comma-separated list of fields to validate
        
    Returns:
        List of invalid field names (empty if all valid)
    """
    if not fields or not data:
        return []

    # Get sample item to check fields against
    if isinstance(data, list):
        if not data:
            return []
        sample = data[0]
    else:
        sample = data

    field_list = [f.strip() for f in fields.split(",")]
    invalid_fields = []

    for field in field_list:
        if not is_valid_field_path(sample, field):
            invalid_fields.append(field)

    return invalid_fields


def is_valid_field_path(data: Dict[str, Any], field_path: str) -> bool:
    """Check if a field path is valid in the given data structure.
    
    Args:
        data: The data to check against
        field_path: The field path to validate (e.g., "epic.title")
        
    Returns:
        True if the field path exists, False otherwise
    """
    parts = field_path.split(".")
    current = data

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and current:
            # For lists, check if the field exists in the first item
            if isinstance(current[0], dict) and part in current[0]:
                current = current[0][part]
            else:
                return False
        else:
            return False

    return True
