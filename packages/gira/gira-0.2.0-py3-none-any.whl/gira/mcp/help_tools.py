"""Help and documentation tools for MCP server."""

import json
import logging
from typing import Any, Dict, List, Optional

from gira.mcp.tools import register_tool
from gira.mcp.help_system import (
    help_registry,
    get_command_help,
    list_all_commands,
    HelpFormatter
)
from gira.mcp.enhanced_validation import (
    ParameterBuilder,
    get_available_values,
    create_parameter_example,
    validate_parameter_value
)

logger = logging.getLogger(__name__)


@register_tool(
    name="help",
    description="Get help information for MCP commands",
    schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command name to get help for (omit to list all commands)"
            },
            "format": {
                "type": "string",
                "enum": ["detailed", "brief", "json"],
                "default": "detailed",
                "description": "Format of help output"
            },
            "parameter": {
                "type": "string",
                "description": "Get help for specific parameter (requires command)"
            }
        }
    }
)
def get_help(
    command: Optional[str] = None,
    format: str = "detailed",
    parameter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive help information for MCP commands.
    
    Args:
        command: Command name to get help for
        format: Output format (detailed, brief, json) 
        parameter: Get help for specific parameter
        
    Returns:
        Help information
    """
    if not command:
        # List all commands
        commands = list_all_commands()
        
        if format == "json":
            return {"commands": commands}
        elif format == "brief":
            result = "Available commands:\n"
            for cmd in commands:
                result += f"• {cmd['name']}: {cmd['description']}\n"
            return {"help": result}
        else:
            result = "# Available MCP Commands\n\n"
            for cmd in commands:
                result += f"## {cmd['name']}\n{cmd['description']}\n\n"
            return {"help": result}
    
    # Get help for specific command
    help_text = get_command_help(command, format if format != "json" else "detailed")
    
    if not help_text:
        return {
            "error": f"No help available for command '{command}'",
            "available_commands": [cmd["name"] for cmd in list_all_commands()]
        }
    
    if format == "json":
        cmd_help = help_registry.get_command_help(command)
        if cmd_help:
            return {
                "command": command,
                "description": cmd_help.description,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type_name,
                        "description": p.description,
                        "required": p.required,
                        "default": p.default_value,
                        "enum_values": p.enum_values,
                        "examples": [{"value": ex.value, "description": ex.description} for ex in p.examples],
                        "suggestions": p.suggestions
                    }
                    for p in cmd_help.parameters
                ],
                "usage_examples": cmd_help.usage_examples,
                "related_commands": cmd_help.related_commands
            }
    
    if parameter:
        # Get help for specific parameter
        cmd_help = help_registry.get_command_help(command)
        if cmd_help:
            for param in cmd_help.parameters:
                if param.name == parameter:
                    param_help = HelpFormatter.format_parameter_hint(param, format)
                    return {"parameter_help": param_help}
        
        return {"error": f"Parameter '{parameter}' not found for command '{command}'"}
    
    return {"help": help_text}


@register_tool(
    name="get_parameter_suggestions",
    description="Get suggestions and validation info for command parameters",
    schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command name"
            },
            "parameter": {
                "type": "string", 
                "description": "Parameter name"
            },
            "current_value": {
                "description": "Current parameter value to validate"
            }
        },
        "required": ["command", "parameter"]
    }
)
def get_parameter_suggestions(
    command: str,
    parameter: str,
    current_value: Any = None
) -> Dict[str, Any]:
    """
    Get suggestions and validation information for a parameter.
    
    Args:
        command: Command name
        parameter: Parameter name
        current_value: Current value to validate
        
    Returns:
        Parameter suggestions and validation info
    """
    result = {
        "command": command,
        "parameter": parameter,
        "suggestions": [],
        "available_values": [],
        "validation": {},
        "examples": []
    }
    
    # Get available values for reference parameters
    available_values = get_available_values(command, parameter)
    if available_values:
        result["available_values"] = available_values
    
    # Get parameter info from help system
    cmd_help = help_registry.get_command_help(command)
    if cmd_help:
        for param in cmd_help.parameters:
            if param.name == parameter:
                result["suggestions"] = param.suggestions
                result["examples"] = [
                    {"value": ex.value, "description": ex.description}
                    for ex in param.examples
                ]
                
                if param.enum_values:
                    result["available_values"] = param.enum_values
                
                break
    
    # Validate current value if provided
    if current_value is not None:
        validation_result = validate_parameter_value(command, parameter, current_value)
        result["validation"] = validation_result
    
    return result


@register_tool(
    name="build_parameters",
    description="Interactive parameter builder with validation",
    schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command name to build parameters for"
            },
            "action": {
                "type": "string",
                "enum": ["start", "add", "validate", "complete"],
                "default": "start",
                "description": "Builder action to perform"
            },
            "parameter_name": {
                "type": "string",
                "description": "Parameter name (for 'add' action)"
            },
            "parameter_value": {
                "description": "Parameter value (for 'add' action)"
            },
            "current_params": {
                "type": "object",
                "description": "Current parameters being built"
            }
        },
        "required": ["command"]
    }
)
def build_parameters(
    command: str,
    action: str = "start",
    parameter_name: Optional[str] = None,
    parameter_value: Any = None,
    current_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Interactive parameter builder for commands.
    
    Args:
        command: Command name
        action: Builder action (start, add, validate, complete)
        parameter_name: Parameter name to add
        parameter_value: Parameter value to add
        current_params: Current parameters
        
    Returns:
        Builder state and suggestions
    """
    builder = ParameterBuilder(command)
    
    # Restore current parameters if provided
    if current_params:
        for name, value in current_params.items():
            builder.add_parameter(name, value)
    
    result = {
        "command": command,
        "action": action,
        "parameters": {},
        "suggestions": [],
        "feedback": {},
        "complete": False
    }
    
    if action == "start":
        # Initialize builder and show initial suggestions
        result["suggestions"] = builder.get_suggested_parameters()
        result["parameters"] = builder.built_params.copy()
        
    elif action == "add":
        if not parameter_name:
            result["error"] = "parameter_name is required for 'add' action"
            return result
        
        # Add parameter with validation
        feedback = builder.add_parameter(parameter_name, parameter_value)
        result["feedback"] = feedback
        result["parameters"] = builder.built_params.copy()
        result["suggestions"] = builder.get_suggested_parameters()
        
    elif action == "validate":
        # Validate current parameters
        validation_result = builder.validate_current_params()
        result.update(validation_result)
        
    elif action == "complete":
        # Finalize parameter building
        validation_result = builder.validate_current_params()
        result.update(validation_result)
        
        if validation_result["complete"]:
            result["ready_to_execute"] = True
            result["final_parameters"] = builder.built_params.copy()
        else:
            result["missing_required"] = [
                param["name"] for param in validation_result["suggestions"]
                if param["required"]
            ]
    
    return result


@register_tool(
    name="get_command_examples",
    description="Get usage examples for commands",
    schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command name"
            },
            "scenario": {
                "type": "string",
                "enum": ["basic", "advanced", "minimal", "all"],
                "default": "basic",
                "description": "Type of examples to return"
            }
        },
        "required": ["command"]
    }
)
def get_command_examples(
    command: str,
    scenario: str = "basic"
) -> Dict[str, Any]:
    """
    Get usage examples for a command.
    
    Args:
        command: Command name
        scenario: Type of examples (basic, advanced, minimal, all)
        
    Returns:
        Command usage examples
    """
    result = {
        "command": command,
        "scenario": scenario,
        "examples": []
    }
    
    cmd_help = help_registry.get_command_help(command)
    if not cmd_help:
        result["error"] = f"No help available for command '{command}'"
        return result
    
    if scenario == "all":
        result["examples"] = cmd_help.usage_examples
    else:
        # Create example based on scenario
        example = create_parameter_example(command, scenario)
        if example:
            result["examples"] = [example]
        else:
            result["examples"] = cmd_help.usage_examples[:1] if cmd_help.usage_examples else []
    
    # Add context for each example
    for i, example in enumerate(result["examples"]):
        result["examples"][i] = {
            "parameters": example,
            "description": f"Example {i+1} for {command}",
            "use_case": "General usage"
        }
    
    return result


@register_tool(
    name="validate_command_parameters",
    description="Validate parameters for a command before execution",
    schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command name"
            },
            "parameters": {
                "type": "object",
                "description": "Parameters to validate"
            },
            "include_suggestions": {
                "type": "boolean",
                "default": True,
                "description": "Include helpful suggestions"
            }
        },
        "required": ["command", "parameters"]
    }
)
def validate_command_parameters(
    command: str,
    parameters: Dict[str, Any],
    include_suggestions: bool = True
) -> Dict[str, Any]:
    """
    Validate parameters for a command with detailed feedback.
    
    Args:
        command: Command name
        parameters: Parameters to validate
        include_suggestions: Whether to include suggestions
        
    Returns:
        Validation result with feedback
    """
    result = {
        "command": command,
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "validated_parameters": {}
    }
    
    # This would need to be enhanced to work with actual command schemas
    # For now, provide basic validation feedback
    
    cmd_help = help_registry.get_command_help(command)
    if not cmd_help:
        result["warnings"].append(f"No validation rules available for command '{command}'")
        result["validated_parameters"] = parameters
        return result
    
    # Check required parameters
    required_params = [p for p in cmd_help.parameters if p.required]
    for param in required_params:
        if param.name not in parameters:
            result["valid"] = False
            result["errors"].append(f"Missing required parameter: {param.name}")
    
    # Validate individual parameters
    for param_name, param_value in parameters.items():
        validation = validate_parameter_value(command, param_name, param_value)
        
        if not validation["valid"]:
            result["valid"] = False
            result["errors"].extend(validation["errors"])
        
        result["warnings"].extend(validation["warnings"])
        
        if include_suggestions:
            result["suggestions"].extend(validation["suggestions"])
        
        result["validated_parameters"][param_name] = validation["transformed_value"]
    
    return result


@register_tool(
    name="search_commands",
    description="Search for commands by name or functionality",
    schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "format": {
                "type": "string",
                "enum": ["brief", "detailed"],
                "default": "brief",
                "description": "Output format"
            }
        },
        "required": ["query"]
    }
)
def search_commands(
    query: str,
    format: str = "brief"
) -> Dict[str, Any]:
    """
    Search for commands by name or functionality.
    
    Args:
        query: Search query
        format: Output format
        
    Returns:
        Search results
    """
    matching_commands = help_registry.search_commands(query)
    
    result = {
        "query": query,
        "found": len(matching_commands),
        "commands": []
    }
    
    for cmd_help in matching_commands:
        if format == "detailed":
            result["commands"].append({
                "name": cmd_help.name,
                "description": cmd_help.description,
                "parameters": [p.name for p in cmd_help.parameters],
                "usage_examples": len(cmd_help.usage_examples)
            })
        else:
            result["commands"].append({
                "name": cmd_help.name,
                "description": cmd_help.description
            })
    
    return result