"""JSONPath filtering utilities for Gira CLI output."""

import json
from typing import Any

from jsonpath_ng import parse as jsonpath_parse
from jsonpath_ng.ext import parse as jsonpath_ext_parse


def apply_jsonpath_filter(data: Any, jsonpath_expr: str) -> Any:
    """Apply a JSONPath expression to filter data.
    
    Args:
        data: The data to filter (dict, list, or any JSON-serializable object)
        jsonpath_expr: The JSONPath expression to apply
        
    Returns:
        The filtered data based on the JSONPath expression
        
    Raises:
        ValueError: If the JSONPath expression is invalid
    """
    # Convert data to dict if it's a Pydantic model
    if hasattr(data, 'model_dump'):
        data = data.model_dump(mode='json')
    elif isinstance(data, list) and data and hasattr(data[0], 'model_dump'):
        # Convert list of Pydantic models
        data = [item.model_dump(mode='json') for item in data]

    # Try to parse with extended parser first (supports filter expressions)
    try:
        if '?' in jsonpath_expr:
            # Use extended parser for filter expressions
            parsed_expr = jsonpath_ext_parse(jsonpath_expr)
        else:
            # Use standard parser for simple expressions
            parsed_expr = jsonpath_parse(jsonpath_expr)
    except Exception as e:
        raise ValueError(f"Invalid JSONPath expression: {e}")

    # Find all matches
    matches = parsed_expr.find(data)

    # Extract values from matches
    if not matches:
        return None

    # Check if we're extracting a field from filtered array results
    # This happens when we have array filtering followed by field extraction
    # e.g., $[?(@.priority=="high")].id
    is_field_extraction_from_array = (
        jsonpath_expr.startswith('$[') and
        '].' in jsonpath_expr and
        '?' in jsonpath_expr
    )

    if len(matches) == 1 and not is_field_extraction_from_array:
        return matches[0].value
    else:
        return [match.value for match in matches]


def format_filtered_output(data: Any, jsonpath_expr: str, pretty: bool = True) -> str:
    """Format filtered data as JSON string.
    
    Args:
        data: The data to filter
        jsonpath_expr: The JSONPath expression to apply
        pretty: Whether to pretty-print the JSON
        
    Returns:
        JSON string representation of the filtered data
    """
    filtered_data = apply_jsonpath_filter(data, jsonpath_expr)

    if pretty:
        return json.dumps(filtered_data, indent=2, default=str)
    else:
        return json.dumps(filtered_data, separators=(',', ':'), default=str)
