"""Parameter validation utilities for MCP server operations."""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import ValidationError as PydanticValidationError

from gira.mcp.tools import ValidationError

logger = logging.getLogger(__name__)


class ParameterValidationError(ValidationError):
    """Enhanced validation error with parameter context."""
    
    def __init__(self, message: str, field: str, value: Any, expected_type: str):
        self.field = field
        self.value = value
        self.expected_type = expected_type
        super().__init__(message, field)


def coerce_array_parameter(value: Any, field_name: str, allow_empty: bool = True) -> List[str]:
    """
    Coerce various input types to a list of strings.
    
    Args:
        value: Input value to coerce
        field_name: Name of the parameter field for error messages
        allow_empty: Whether to allow empty lists
        
    Returns:
        List of strings
        
    Raises:
        ParameterValidationError: If coercion fails
    """
    if value is None:
        return []
    
    # Already a list
    if isinstance(value, list):
        # Convert all elements to strings
        try:
            result = [str(item) for item in value]
            if not allow_empty and len(result) == 0:
                raise ParameterValidationError(
                    f"Parameter '{field_name}' cannot be empty",
                    field_name, value, "non-empty list"
                )
            return result
        except Exception as e:
            raise ParameterValidationError(
                f"Failed to convert array elements to strings in '{field_name}': {e}. "
                f"Received: {value}. Example: [\"item1\", \"item2\"]",
                field_name, value, "list of strings"
            )
    
    # Single string - could be JSON array, comma-separated, or single item
    if isinstance(value, str):
        # First try to parse as JSON array (for Claude Desktop compatibility)
        if value.strip().startswith('[') and value.strip().endswith(']'):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    # Successfully parsed JSON array - convert elements to strings
                    result = [str(item) for item in parsed]
                    if not allow_empty and len(result) == 0:
                        raise ParameterValidationError(
                            f"Parameter '{field_name}' cannot be empty",
                            field_name, value, "non-empty list"
                        )
                    return result
            except json.JSONDecodeError:
                # Not valid JSON, fall through to other parsing methods
                pass
        
        # Try comma-separated values
        if ',' in value:
            # Split by comma and clean up whitespace
            result = [item.strip() for item in value.split(',') if item.strip()]
        else:
            # Single item
            result = [value.strip()] if value.strip() else []
        
        if not allow_empty and len(result) == 0:
            raise ParameterValidationError(
                f"Parameter '{field_name}' cannot be empty",
                field_name, value, "non-empty list"
            )
        return result
    
    # Check for unsupported types that shouldn't be coerced to arrays
    if isinstance(value, (dict, set, tuple)):
        raise ParameterValidationError(
            f"Cannot convert '{field_name}' to array: {type(value).__name__} is not supported. "
            f"Received {type(value).__name__}: {value}. "
            f"Expected array like [\"item1\", \"item2\"] or comma-separated string \"item1,item2\"",
            field_name, value, "list of strings"
        )
    
    # Try to convert single values to string
    try:
        result = [str(value)]
        return result
    except Exception as e:
        raise ParameterValidationError(
            f"Cannot convert '{field_name}' to array: {e}. "
            f"Received {type(value).__name__}: {value}. "
            f"Expected array like [\"item1\", \"item2\"] or comma-separated string \"item1,item2\"",
            field_name, value, "list of strings"
        )


def coerce_integer_parameter(value: Any, field_name: str, min_value: Optional[int] = None, 
                           max_value: Optional[int] = None) -> int:
    """
    Coerce various input types to an integer.
    
    Args:
        value: Input value to coerce
        field_name: Name of the parameter field for error messages
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        
    Returns:
        Integer value
        
    Raises:
        ParameterValidationError: If coercion fails or value is out of range
    """
    if value is None:
        raise ParameterValidationError(
            f"Parameter '{field_name}' cannot be None",
            field_name, value, "integer"
        )
    
    # Already an integer
    if isinstance(value, int):
        result = value
    # String that might represent an integer
    elif isinstance(value, str):
        try:
            result = int(value.strip())
        except ValueError:
            raise ParameterValidationError(
                f"Parameter '{field_name}' must be a valid integer, got '{value}'",
                field_name, value, "integer"
            )
    # Float - try to convert if it's a whole number
    elif isinstance(value, float):
        if value.is_integer():
            result = int(value)
        else:
            raise ParameterValidationError(
                f"Parameter '{field_name}' must be a whole number, got {value}",
                field_name, value, "integer"
            )
    else:
        raise ParameterValidationError(
            f"Parameter '{field_name}' must be an integer, got {type(value).__name__}",
            field_name, value, "integer"
        )
    
    # Check range constraints
    if min_value is not None and result < min_value:
        raise ParameterValidationError(
            f"Parameter '{field_name}' must be at least {min_value}, got {result}",
            field_name, value, f"integer >= {min_value}"
        )
    
    if max_value is not None and result > max_value:
        raise ParameterValidationError(
            f"Parameter '{field_name}' must be at most {max_value}, got {result}",
            field_name, value, f"integer <= {max_value}"
        )
    
    return result


def coerce_boolean_parameter(value: Any, field_name: str) -> bool:
    """
    Coerce various input types to a boolean.
    
    Args:
        value: Input value to coerce
        field_name: Name of the parameter field for error messages
        
    Returns:
        Boolean value
        
    Raises:
        ParameterValidationError: If coercion fails
    """
    if value is None:
        return False
    
    # Already a boolean
    if isinstance(value, bool):
        return value
    
    # String representations
    if isinstance(value, str):
        lower_value = value.lower().strip()
        if lower_value in ('true', '1', 'yes', 'on'):
            return True
        elif lower_value in ('false', '0', 'no', 'off', ''):
            return False
        else:
            raise ParameterValidationError(
                f"Parameter '{field_name}' must be a boolean value, got '{value}'",
                field_name, value, "boolean"
            )
    
    # Numeric representations
    if isinstance(value, (int, float)):
        return bool(value)
    
    raise ParameterValidationError(
        f"Parameter '{field_name}' must be a boolean, got {type(value).__name__}",
        field_name, value, "boolean"
    )


def validate_enum_parameter(value: Any, field_name: str, allowed_values: List[str], 
                          case_sensitive: bool = False) -> str:
    """
    Validate that a parameter value is in a list of allowed values.
    
    Args:
        value: Input value to validate
        field_name: Name of the parameter field for error messages
        allowed_values: List of allowed string values
        case_sensitive: Whether to perform case-sensitive comparison
        
    Returns:
        Validated string value
        
    Raises:
        ParameterValidationError: If value is not in allowed values
    """
    if value is None:
        raise ParameterValidationError(
            f"Parameter '{field_name}' cannot be None",
            field_name, value, f"one of: {allowed_values}"
        )
    
    # Convert to string
    str_value = str(value).strip()
    
    # Check against allowed values
    if case_sensitive:
        if str_value in allowed_values:
            return str_value
    else:
        # Case-insensitive comparison
        lower_allowed = [v.lower() for v in allowed_values]
        lower_value = str_value.lower()
        if lower_value in lower_allowed:
            # Return the original casing from allowed_values
            index = lower_allowed.index(lower_value)
            return allowed_values[index]
    
    raise ParameterValidationError(
        f"Parameter '{field_name}' must be one of {allowed_values}, got '{str_value}'",
        field_name, value, f"one of: {allowed_values}"
    )


def validate_parameters(params: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and coerce parameters according to a JSON schema.
    
    Args:
        params: Dictionary of parameter values
        schema: JSON schema definition
        
    Returns:
        Dictionary of validated and coerced parameters
        
    Raises:
        ParameterValidationError: If validation fails
    """
    validated = {}
    properties = schema.get('properties', {})
    required_fields = set(schema.get('required', []))
    
    # Check for required fields
    for field_name in required_fields:
        if field_name not in params or params[field_name] is None:
            raise ParameterValidationError(
                f"Required parameter '{field_name}' is missing",
                field_name, None, "required"
            )
    
    # Validate and coerce each parameter
    for field_name, field_schema in properties.items():
        if field_name not in params:
            continue
            
        value = params[field_name]
        
        # Handle None values properly - they should be preserved for optional fields
        # but validated through the schema to ensure null is allowed
        try:
            validated[field_name] = _coerce_by_schema(value, field_name, field_schema)
        except ParameterValidationError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error validating parameter '{field_name}'")
            raise ParameterValidationError(
                f"Failed to validate parameter '{field_name}': {e}",
                field_name, value, "valid value"
            )
    
    return validated


def _coerce_by_schema(value: Any, field_name: str, field_schema: Dict[str, Any]) -> Any:
    """
    Coerce a value according to its JSON schema definition.
    
    Args:
        value: Value to coerce
        field_name: Field name for error messages
        field_schema: JSON schema for the field
        
    Returns:
        Coerced value
        
    Raises:
        ParameterValidationError: If coercion fails
    """
    field_type = field_schema.get('type')
    
    # Handle anyOf schemas (common for Optional[List[T]] fields)
    if field_type is None and 'anyOf' in field_schema:
        return _coerce_any_of_schema(value, field_name, field_schema)
    
    if field_type == 'string':
        return str(value) if value is not None else None
    
    elif field_type == 'integer':
        min_val = field_schema.get('minimum')
        max_val = field_schema.get('maximum')
        return coerce_integer_parameter(value, field_name, min_val, max_val)
    
    elif field_type == 'boolean':
        return coerce_boolean_parameter(value, field_name)
    
    elif field_type == 'array':
        return _coerce_array_schema(value, field_name, field_schema)
    
    elif field_type == 'object':
        if not isinstance(value, dict):
            raise ParameterValidationError(
                f"Parameter '{field_name}' must be an object",
                field_name, value, "object"
            )
        return value
    
    else:
        # Unknown type or no type specified - return as-is
        logger.warning(f"Unknown field type '{field_type}' for parameter '{field_name}'")
        return value


def _coerce_any_of_schema(value: Any, field_name: str, field_schema: Dict[str, Any]) -> Any:
    """
    Handle anyOf schema validation (commonly used for Optional[List[T]] fields).
    
    Args:
        value: Value to coerce
        field_name: Field name for error messages
        field_schema: JSON schema with anyOf definition
        
    Returns:
        Coerced value
        
    Raises:
        ParameterValidationError: If coercion fails
    """
    any_of_schemas = field_schema.get('anyOf', [])
    
    if value is None:
        # Check if null is explicitly allowed
        for schema in any_of_schemas:
            if schema.get('type') == 'null':
                return None
        
        # If default is provided and None is the value, use default
        if 'default' in field_schema:
            return field_schema['default']
        
        # If None not allowed, raise error
        raise ParameterValidationError(
            f"Parameter '{field_name}' cannot be null",
            field_name, value, "non-null value"
        )
    
    # Try each schema in anyOf until one works
    last_error = None
    
    for schema in any_of_schemas:
        # Skip null schemas when value is not None
        if schema.get('type') == 'null' and value is not None:
            continue
            
        try:
            return _coerce_by_schema(value, field_name, schema)
        except ParameterValidationError as e:
            last_error = e
            continue
        except Exception as e:
            # Convert unexpected errors to ParameterValidationError
            last_error = ParameterValidationError(
                f"Failed to validate '{field_name}': {e}",
                field_name, value, "valid value"
            )
            continue
    
    # If no schema worked, raise the last error with enhanced message
    if last_error:
        # Enhance error message for array types
        array_schemas = [s for s in any_of_schemas if s.get('type') == 'array']
        if array_schemas:
            raise ParameterValidationError(
                f"Parameter '{field_name}' must be an array of strings or null. "
                f"Received {type(value).__name__}: {value}. "
                f"Example: [\"item1\", \"item2\"] or null",
                field_name, value, "array of strings or null"
            )
        else:
            raise last_error
    
    raise ParameterValidationError(
        f"Parameter '{field_name}' does not match any of the expected types",
        field_name, value, "valid type"
    )


def _coerce_array_schema(value: Any, field_name: str, field_schema: Dict[str, Any]) -> Any:
    """
    Handle array schema validation with enhanced error messages.
    
    Args:
        value: Value to coerce
        field_name: Field name for error messages
        field_schema: Array schema definition
        
    Returns:
        Coerced array value
        
    Raises:
        ParameterValidationError: If coercion fails
    """
    items_schema = field_schema.get('items', {})
    if items_schema.get('type') == 'string':
        # For string arrays, only accept strings, arrays, or None
        # Reject numeric types to prevent unexpected conversions
        if isinstance(value, (int, float, bool)) and not isinstance(value, str):
            raise ParameterValidationError(
                f"Parameter '{field_name}' must be an array of strings. "
                f"Received {type(value).__name__}: {value}. "
                f"Example: [\"item1\", \"item2\"] or \"item1,item2\"",
                field_name, value, "array of strings"
            )
        
        min_items = field_schema.get('minItems', 0)
        return coerce_array_parameter(value, field_name, allow_empty=(min_items == 0))
    else:
        # For non-string arrays, just ensure it's a list
        if not isinstance(value, list):
            raise ParameterValidationError(
                f"Parameter '{field_name}' must be an array. "
                f"Received {type(value).__name__}: {value}. "
                f"Example: [\"item1\", \"item2\"]",
                field_name, value, "array"
            )
        return value


def create_validation_decorator(schema: Dict[str, Any]):
    """
    Create a decorator that validates function parameters against a schema.
    
    Args:
        schema: JSON schema to validate against
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                validated_kwargs = validate_parameters(kwargs, schema)
                # Update kwargs with validated values
                kwargs.update(validated_kwargs)
                return func(*args, **kwargs)
            except ParameterValidationError:
                raise
            except Exception as e:
                logger.exception(f"Validation error in {func.__name__}")
                raise ValidationError(f"Parameter validation failed: {e}")
        
        return wrapper
    return decorator


def get_helpful_error_message(error: ParameterValidationError) -> str:
    """
    Generate a helpful error message for parameter validation failures.
    
    Args:
        error: The validation error
        
    Returns:
        Formatted error message
    """
    base_msg = f"Parameter validation failed for '{error.field}'"
    
    if hasattr(error, 'expected_type'):
        base_msg += f" - expected {error.expected_type}, got {type(error.value).__name__}"
        
        if error.expected_type.startswith('one of:'):
            base_msg += f"\nAvailable options: {error.expected_type[7:]}"
        elif 'array' in error.expected_type.lower():
            base_msg += f"\nTip: Arrays can be provided as ['item1', 'item2'] or as comma-separated strings 'item1,item2'"
        elif 'integer' in error.expected_type.lower():
            base_msg += f"\nTip: Integers can be provided as numbers (123) or numeric strings ('123')"
    
    return base_msg