"""Enhanced parameter validation with hints and examples."""

import json
import logging
from typing import Any, Dict, List, Optional, Type, Union
from functools import wraps

from pydantic import BaseModel, ValidationError as PydanticValidationError

from gira.mcp.validation import ParameterValidationError
from gira.mcp.help_system import (
    help_registry,
    generate_enhanced_error_message,
    get_parameter_suggestions
)
from gira.mcp.errors import ValidationError as EnhancedValidationError, ErrorContext

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of parameter validation with detailed feedback."""
    
    def __init__(self, is_valid: bool, validated_params: Optional[Dict[str, Any]] = None):
        self.is_valid = is_valid
        self.validated_params = validated_params or {}
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
    
    def add_error(
        self,
        parameter: str,
        message: str,
        received_value: Any = None,
        expected_type: str = None,
        suggestions: List[str] = None
    ):
        """Add a validation error with context."""
        self.errors.append({
            "parameter": parameter,
            "message": message,
            "received_value": received_value,
            "expected_type": expected_type,
            "suggestions": suggestions or []
        })
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add a validation warning."""
        self.warnings.append(message)
    
    def add_suggestion(self, message: str):
        """Add a helpful suggestion."""
        self.suggestions.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "validated_params": self.validated_params,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions
        }


class EnhancedParameterValidator:
    """Enhanced parameter validator with hints and suggestions."""
    
    def __init__(self, command_name: str):
        self.command_name = command_name
        self.cmd_help = help_registry.get_command_help(command_name)
    
    def validate_parameters(
        self,
        params: Dict[str, Any],
        schema_model: Type[BaseModel],
        provide_suggestions: bool = True
    ) -> ValidationResult:
        """
        Validate parameters with enhanced error messages and suggestions.
        
        Args:
            params: Parameters to validate
            schema_model: Pydantic model for validation
            provide_suggestions: Whether to include helpful suggestions
            
        Returns:
            ValidationResult with detailed feedback
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Try Pydantic validation first
            validated_model = schema_model(**params)
            result.validated_params = validated_model.model_dump()
            
            # Add suggestions for optional parameters that weren't provided
            if provide_suggestions and self.cmd_help:
                self._add_optional_parameter_suggestions(params, result)
            
        except PydanticValidationError as e:
            result.is_valid = False
            
            # Convert Pydantic errors to enhanced errors
            for error in e.errors():
                param_name = '.'.join(str(loc) for loc in error['loc'])
                error_msg = error['msg']
                received_value = self._extract_received_value(params, error['loc'])
                
                # Generate enhanced error message
                enhanced_msg = self._generate_enhanced_error(
                    param_name, error_msg, received_value
                )
                
                result.add_error(
                    parameter=param_name,
                    message=enhanced_msg,
                    received_value=received_value,
                    expected_type=self._get_expected_type(param_name),
                    suggestions=get_parameter_suggestions(self.command_name, param_name)
                )
        
        except Exception as e:
            logger.exception(f"Unexpected validation error in {self.command_name}")
            result.add_error(
                parameter="unknown",
                message=f"Unexpected validation error: {e}",
                suggestions=["Check parameter format and try again"]
            )
        
        return result
    
    def _extract_received_value(self, params: Dict[str, Any], location: tuple) -> Any:
        """Extract the received value from parameters using error location."""
        try:
            value = params
            for loc in location:
                if isinstance(value, dict) and loc in value:
                    value = value[loc]
                else:
                    return None
            return value
        except Exception:
            return None
    
    def _get_expected_type(self, param_name: str) -> Optional[str]:
        """Get expected type for a parameter."""
        if not self.cmd_help:
            return None
        
        for param in self.cmd_help.parameters:
            if param.name == param_name:
                return param.type_name
        
        return None
    
    def _generate_enhanced_error(
        self,
        param_name: str,
        error_msg: str,
        received_value: Any
    ) -> str:
        """Generate enhanced error message with context."""
        return generate_enhanced_error_message(
            self.command_name,
            param_name,
            received_value,
            error_msg
        )
    
    def _add_optional_parameter_suggestions(
        self,
        params: Dict[str, Any],
        result: ValidationResult
    ):
        """Add suggestions for optional parameters that might be useful."""
        if not self.cmd_help:
            return
        
        for param in self.cmd_help.parameters:
            if not param.required and param.name not in params:
                if param.suggestions:
                    result.add_suggestion(
                        f"Consider using '{param.name}': {param.suggestions[0]}"
                    )


def enhanced_validate(command_name: str, schema_model: Type[BaseModel]):
    """
    Decorator for enhanced parameter validation with hints.
    
    Args:
        command_name: Name of the command for context
        schema_model: Pydantic model for validation
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validator = EnhancedParameterValidator(command_name)
            result = validator.validate_parameters(kwargs, schema_model)
            
            if not result.is_valid:
                # Create comprehensive error message
                error_details = []
                for error in result.errors:
                    error_details.append(error["message"])
                
                raise EnhancedValidationError(
                    message=f"Parameter validation failed for '{command_name}': " + 
                           "; ".join(error_details),
                    field=result.errors[0]["parameter"] if result.errors else None,
                    context=ErrorContext(
                        operation=command_name,
                        parameters=kwargs
                    ),
                    debug_info={
                        "validation_result": result.to_dict()
                    }
                )
            
            # Update kwargs with validated parameters
            kwargs.update(result.validated_params)
            
            # Log warnings and suggestions
            for warning in result.warnings:
                logger.warning(f"{command_name}: {warning}")
            
            for suggestion in result.suggestions:
                logger.info(f"{command_name} suggestion: {suggestion}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class ParameterBuilder:
    """Interactive parameter builder with suggestions."""
    
    def __init__(self, command_name: str):
        self.command_name = command_name
        self.cmd_help = help_registry.get_command_help(command_name)
        self.built_params: Dict[str, Any] = {}
    
    def add_parameter(self, name: str, value: Any) -> Dict[str, Any]:
        """
        Add a parameter with validation and suggestions.
        
        Args:
            name: Parameter name
            value: Parameter value
            
        Returns:
            Dictionary with validation feedback
        """
        feedback = {
            "parameter": name,
            "value": value,
            "accepted": False,
            "suggestions": [],
            "warnings": []
        }
        
        if not self.cmd_help:
            feedback["warnings"].append("No help available for this command")
            self.built_params[name] = value
            feedback["accepted"] = True
            return feedback
        
        # Find parameter info
        param_info = None
        for param in self.cmd_help.parameters:
            if param.name == name:
                param_info = param
                break
        
        if not param_info:
            feedback["warnings"].append(f"Unknown parameter '{name}' for command '{self.command_name}'")
            # Still accept it - might be a valid parameter not in help
            self.built_params[name] = value
            feedback["accepted"] = True
            return feedback
        
        # Validate against enum values
        if param_info.enum_values and str(value).lower() not in [v.lower() for v in param_info.enum_values]:
            feedback["suggestions"].append(f"Valid values: {', '.join(param_info.enum_values)}")
            if self._is_close_match(str(value), param_info.enum_values):
                close_match = self._find_closest_match(str(value), param_info.enum_values)
                feedback["suggestions"].insert(0, f"Did you mean '{close_match}'?")
        
        # Type-specific validation and suggestions
        if param_info.type_name.startswith("List"):
            if not isinstance(value, list) and not isinstance(value, str):
                feedback["suggestions"].append("Provide as array or comma-separated string")
            elif isinstance(value, str) and ',' in value:
                feedback["suggestions"].append(f"Converting comma-separated string to array")
                value = [item.strip() for item in value.split(',')]
        
        # Add general suggestions for this parameter
        if param_info.suggestions:
            feedback["suggestions"].extend(param_info.suggestions[:2])
        
        self.built_params[name] = value
        feedback["accepted"] = True
        feedback["value"] = value  # May have been transformed
        
        return feedback
    
    def get_suggested_parameters(self) -> List[Dict[str, Any]]:
        """Get suggestions for parameters to add next."""
        suggestions = []
        
        if not self.cmd_help:
            return suggestions
        
        for param in self.cmd_help.parameters:
            if param.name not in self.built_params:
                suggestion = {
                    "name": param.name,
                    "type": param.type_name,
                    "required": param.required,
                    "description": param.description,
                    "examples": []
                }
                
                if param.examples:
                    suggestion["examples"] = [
                        {"value": ex.value, "description": ex.description}
                        for ex in param.examples[:3]
                    ]
                
                if param.enum_values:
                    suggestion["valid_values"] = param.enum_values
                
                suggestions.append(suggestion)
        
        # Sort by required first, then alphabetically
        suggestions.sort(key=lambda x: (not x["required"], x["name"]))
        
        return suggestions
    
    def validate_current_params(self) -> Dict[str, Any]:
        """Validate currently built parameters."""
        validator = EnhancedParameterValidator(self.command_name)
        
        # We can't validate without knowing the schema model
        # This would need to be enhanced to work with specific command schemas
        return {
            "parameters": self.built_params.copy(),
            "complete": self._check_required_params(),
            "suggestions": self.get_suggested_parameters()
        }
    
    def _check_required_params(self) -> bool:
        """Check if all required parameters are present."""
        if not self.cmd_help:
            return True
        
        for param in self.cmd_help.parameters:
            if param.required and param.name not in self.built_params:
                return False
        
        return True
    
    def _is_close_match(self, value: str, valid_values: List[str]) -> bool:
        """Check if value is close to any valid value."""
        value_lower = value.lower()
        for valid in valid_values:
            if (abs(len(value_lower) - len(valid)) <= 2 and
                self._string_similarity(value_lower, valid.lower()) > 0.6):
                return True
        return False
    
    def _find_closest_match(self, value: str, valid_values: List[str]) -> str:
        """Find the closest matching valid value."""
        value_lower = value.lower()
        best_match = valid_values[0]
        best_score = 0
        
        for valid in valid_values:
            score = self._string_similarity(value_lower, valid.lower())
            if score > best_score:
                best_score = score
                best_match = valid
        
        return best_match
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (simple implementation)."""
        if not s1 or not s2:
            return 0.0
        
        # Simple character overlap similarity
        s1_chars = set(s1)
        s2_chars = set(s2)
        
        intersection = len(s1_chars.intersection(s2_chars))
        union = len(s1_chars.union(s2_chars))
        
        return intersection / union if union > 0 else 0.0


def get_available_values(command_name: str, parameter_name: str) -> List[str]:
    """
    Get available values for a parameter (e.g., for reference parameters).
    
    Args:
        command_name: Name of the command
        parameter_name: Name of the parameter
        
    Returns:
        List of available values
    """
    # This would integrate with the actual data layer to provide real values
    # For now, return static examples based on parameter type
    
    if 'epic_id' in parameter_name.lower():
        return ["EPIC-001", "EPIC-002", "EPIC-003"]
    elif 'ticket_id' in parameter_name.lower():
        return ["GCM-123", "GCM-124", "GCM-125"]
    elif 'sprint_id' in parameter_name.lower():
        return ["SPRINT-2024-01", "SPRINT-2024-02"]
    elif 'assignee' in parameter_name.lower():
        return ["john.doe@company.com", "jane.smith@company.com"]
    
    return []


def create_parameter_example(command_name: str, scenario: str = "basic") -> Dict[str, Any]:
    """
    Create example parameters for a command.
    
    Args:
        command_name: Name of the command
        scenario: Type of example (basic, advanced, minimal)
        
    Returns:
        Dictionary of example parameters
    """
    cmd_help = help_registry.get_command_help(command_name)
    if not cmd_help or not cmd_help.usage_examples:
        return {}
    
    # Return the first example that matches the scenario
    # For now, just return the first example
    return cmd_help.usage_examples[0] if cmd_help.usage_examples else {}


def validate_parameter_value(
    command_name: str,
    parameter_name: str,
    value: Any
) -> Dict[str, Any]:
    """
    Validate a single parameter value with detailed feedback.
    
    Args:
        command_name: Name of the command
        parameter_name: Name of the parameter
        value: Value to validate
        
    Returns:
        Dictionary with validation result and suggestions
    """
    cmd_help = help_registry.get_command_help(command_name)
    
    result = {
        "valid": True,
        "transformed_value": value,
        "suggestions": [],
        "warnings": [],
        "errors": []
    }
    
    if not cmd_help:
        result["warnings"].append("No validation rules available")
        return result
    
    # Find parameter info
    param_info = None
    for param in cmd_help.parameters:
        if param.name == parameter_name:
            param_info = param
            break
    
    if not param_info:
        result["warnings"].append(f"Unknown parameter '{parameter_name}'")
        return result
    
    # Validate against enum values
    if param_info.enum_values:
        if isinstance(value, str) and value.lower() not in [v.lower() for v in param_info.enum_values]:
            result["valid"] = False
            result["errors"].append(f"Invalid value '{value}'. Valid values: {', '.join(param_info.enum_values)}")
    
    # Add parameter-specific suggestions
    if param_info.suggestions:
        result["suggestions"].extend(param_info.suggestions)
    
    return result