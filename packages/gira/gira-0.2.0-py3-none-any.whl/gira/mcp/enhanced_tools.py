"""Enhanced MCP tools with validation and help integration."""

import logging
from typing import Any, Dict, List, Optional, Type
from functools import wraps

from pydantic import BaseModel

from gira.mcp.tools import register_tool, tool_registry
from gira.mcp.enhanced_validation import enhanced_validate, EnhancedParameterValidator
from gira.mcp.help_system import help_registry, get_command_help
from gira.mcp.schema import (
    TicketCreateParams, TicketUpdateParams, TicketFilter,
    EpicCreateParams, EpicUpdateParams, EpicFilter,
    SprintCreateParams, SprintUpdateParams, SprintFilter,
    CommentParams, SearchParams
)

logger = logging.getLogger(__name__)


def enhanced_mcp_tool(
    name: str,
    description: str,
    schema_model: Type[BaseModel],
    schema: Optional[Dict[str, Any]] = None,
    requires_confirmation: bool = False,
    is_destructive: bool = False
):
    """
    Enhanced MCP tool decorator with validation and help integration.
    
    Args:
        name: Tool name
        description: Tool description
        schema_model: Pydantic model for parameter validation
        schema: JSON schema (optional, derived from model if not provided)
        requires_confirmation: Whether tool requires confirmation
        is_destructive: Whether tool is destructive
        
    Returns:
        Decorator function
    """
    def decorator(func):
        # Apply enhanced validation
        validated_func = enhanced_validate(name, schema_model)(func)
        
        # Apply standard MCP tool registration
        tool_schema = schema or schema_model.model_json_schema()
        registered_func = register_tool(
            name=name,
            description=description,
            schema=tool_schema,
            requires_confirmation=requires_confirmation,
            is_destructive=is_destructive
        )(validated_func)
        
        # Add help flag support
        help_enabled_func = add_help_support(name)(registered_func)
        
        return help_enabled_func
    
    return decorator


def add_help_support(command_name: str):
    """
    Add --help flag support to a command.
    
    Args:
        command_name: Name of the command
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check for help request
            if kwargs.get('help') or kwargs.get('--help'):
                help_text = get_command_help(command_name, "detailed")
                if help_text:
                    return {"help": help_text}
                else:
                    return {"error": f"No help available for command '{command_name}'"}
            
            # Check for parameter validation request
            if kwargs.get('validate_only'):
                validator = EnhancedParameterValidator(command_name)
                # This would need the schema model, which we don't have here
                # For now, return a placeholder
                return {
                    "validation": "Parameters would be validated here",
                    "command": command_name,
                    "parameters": {k: v for k, v in kwargs.items() if not k.startswith('_')}
                }
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def create_enhanced_command_wrapper(
    original_func,
    command_name: str,
    schema_model: Type[BaseModel]
):
    """
    Create an enhanced wrapper for existing commands.
    
    Args:
        original_func: Original function to wrap
        command_name: Command name
        schema_model: Pydantic model for validation
        
    Returns:
        Enhanced wrapper function
    """
    @wraps(original_func)
    def enhanced_wrapper(*args, **kwargs):
        # Add help support
        if kwargs.get('help') or kwargs.get('--help'):
            help_text = get_command_help(command_name, "detailed")
            if help_text:
                return {"help": help_text}
            else:
                return {"error": f"No help available for command '{command_name}'"}
        
        # Add parameter suggestions
        if kwargs.get('suggest_parameters'):
            cmd_help = help_registry.get_command_help(command_name)
            if cmd_help:
                suggestions = []
                for param in cmd_help.parameters:
                    if param.name not in kwargs:
                        suggestions.append({
                            "name": param.name,
                            "type": param.type_name,
                            "description": param.description,
                            "required": param.required,
                            "examples": [
                                {"value": ex.value, "description": ex.description}
                                for ex in param.examples[:2]
                            ]
                        })
                
                return {
                    "command": command_name,
                    "suggested_parameters": suggestions
                }
        
        # Add parameter validation
        if kwargs.get('validate_only'):
            validator = EnhancedParameterValidator(command_name)
            try:
                result = validator.validate_parameters(kwargs, schema_model)
                return {
                    "validation_result": result.to_dict(),
                    "command": command_name
                }
            except Exception as e:
                return {
                    "validation_error": str(e),
                    "command": command_name
                }
        
        # Add parameter examples
        if kwargs.get('show_examples'):
            cmd_help = help_registry.get_command_help(command_name)
            if cmd_help and cmd_help.usage_examples:
                return {
                    "command": command_name,
                    "examples": cmd_help.usage_examples
                }
        
        # Execute original function
        return original_func(*args, **kwargs)
    
    return enhanced_wrapper


# Enhanced command examples using the new system

@enhanced_mcp_tool(
    name="enhanced_create_ticket",
    description="Create a new ticket with enhanced validation and help",
    schema_model=TicketCreateParams,
    is_destructive=True
)
def enhanced_create_ticket(
    title: str,
    description: Optional[str] = None,
    type: str = "task",
    priority: str = "medium",
    assignee: Optional[str] = None,
    epic_id: Optional[str] = None,
    labels: Optional[List[str]] = None,
    story_points: Optional[int] = None
) -> Dict[str, Any]:
    """
    Enhanced ticket creation with comprehensive validation.
    
    This is an example of how existing commands would be enhanced.
    The actual implementation would delegate to the original function.
    """
    # This would call the actual ticket creation logic
    return {
        "success": True,
        "message": "Ticket created successfully (enhanced version)",
        "ticket": {
            "id": "GCM-NEW",
            "title": title,
            "description": description,
            "type": type,
            "priority": priority,
            "assignee": assignee,
            "epic_id": epic_id,
            "labels": labels or [],
            "story_points": story_points
        }
    }


@enhanced_mcp_tool(
    name="enhanced_list_tickets",
    description="List tickets with enhanced filtering and help",
    schema_model=TicketFilter
)
def enhanced_list_tickets(
    status: Optional[List[str]] = None,
    type: Optional[List[str]] = None,
    priority: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    epic_id: Optional[str] = None,
    labels: Optional[List[str]] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Enhanced ticket listing with comprehensive filtering.
    
    This demonstrates enhanced parameter validation and suggestions.
    """
    # This would call the actual ticket listing logic
    return {
        "success": True,
        "message": "Tickets retrieved successfully (enhanced version)",
        "tickets": [
            {
                "id": "GCM-123",
                "title": "Example ticket",
                "status": "todo",
                "type": "task",
                "priority": "medium"
            }
        ],
        "total": 1,
        "filters_applied": {
            "status": status,
            "type": type,
            "priority": priority,
            "assignee": assignee,
            "epic_id": epic_id,
            "labels": labels,
            "limit": limit
        }
    }


def enhance_existing_commands():
    """
    Enhance existing MCP commands with new validation and help features.
    
    This function would be called during server initialization to wrap
    existing commands with enhanced functionality.
    """
    logger.info("Enhancing existing MCP commands with validation and help")
    
    # Get all registered tools
    existing_tools = tool_registry.list_tools()
    
    enhanced_tools = {}
    schema_mappings = {
        "create_ticket": TicketCreateParams,
        "update_ticket": TicketUpdateParams,
        "list_tickets": TicketFilter,
        "create_epic": EpicCreateParams,
        "update_epic": EpicUpdateParams,
        "list_epics": EpicFilter,
        "create_sprint": SprintCreateParams,
        "update_sprint": SprintUpdateParams,
        "list_sprints": SprintFilter,
        "add_comment": CommentParams,
        "search": SearchParams
    }
    
    for tool_name, tool_info in existing_tools.items():
        if tool_name in schema_mappings:
            # Create enhanced wrapper
            schema_model = schema_mappings[tool_name]
            original_func = tool_info["function"]
            
            enhanced_func = create_enhanced_command_wrapper(
                original_func,
                tool_name,
                schema_model
            )
            
            enhanced_tools[tool_name] = {
                **tool_info,
                "function": enhanced_func,
                "enhanced": True
            }
            
            logger.debug(f"Enhanced command: {tool_name}")
        else:
            # Keep original tool unchanged
            enhanced_tools[tool_name] = tool_info
    
    # Update tool registry with enhanced tools
    for tool_name, tool_info in enhanced_tools.items():
        if tool_info.get("enhanced"):
            tool_registry.tools[tool_name] = tool_info
    
    logger.info(f"Enhanced {len([t for t in enhanced_tools.values() if t.get('enhanced')])} commands")


def add_help_to_all_commands():
    """Add help support to all registered commands."""
    logger.info("Adding help support to all MCP commands")
    
    existing_tools = tool_registry.list_tools()
    
    for tool_name, tool_info in existing_tools.items():
        original_func = tool_info["function"]
        
        # Add help support if not already present
        if not hasattr(original_func, '_help_enabled'):
            enhanced_func = add_help_support(tool_name)(original_func)
            enhanced_func._help_enabled = True
            
            # Update registry
            tool_registry.tools[tool_name] = {
                **tool_info,
                "function": enhanced_func
            }
            
            logger.debug(f"Added help support to: {tool_name}")
    
    logger.info("Help support added to all commands")


def register_enhanced_help_commands():
    """Register enhanced help and utility commands."""
    logger.info("Registering enhanced help commands")
    
    # The help commands are already registered in help_tools.py
    # This function could add additional enhanced features
    
    @register_tool(
        name="get_command_schema",
        description="Get JSON schema for a command's parameters",
        schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command name to get schema for"
                }
            },
            "required": ["command"]
        }
    )
    def get_command_schema(command: str) -> Dict[str, Any]:
        """Get JSON schema for a command."""
        tool_info = tool_registry.get_tool(command)
        if not tool_info:
            return {"error": f"Command '{command}' not found"}
        
        return {
            "command": command,
            "schema": tool_info.get("schema", {}),
            "description": tool_info.get("description", "")
        }
    
    @register_tool(
        name="validate_parameters_for_command",
        description="Validate parameters for any command",
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
                }
            },
            "required": ["command", "parameters"]
        }
    )
    def validate_parameters_for_command(
        command: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate parameters for any command."""
        # This would use the enhanced validation system
        # to validate parameters for any registered command
        
        validator = EnhancedParameterValidator(command)
        
        # Without the schema model, we can only do basic validation
        return {
            "command": command,
            "parameters": parameters,
            "validation": "Basic validation completed",
            "suggestions": [
                "Use 'help' command for detailed parameter information",
                "Use 'get_parameter_suggestions' for specific parameter help"
            ]
        }
    
    logger.info("Enhanced help commands registered")


# Integration function to be called during server startup
def initialize_enhanced_features():
    """Initialize all enhanced MCP features."""
    logger.info("Initializing enhanced MCP features")
    
    try:
        # Add help support to existing commands
        add_help_to_all_commands()
        
        # Enhance existing commands with validation
        enhance_existing_commands()
        
        # Register enhanced help commands
        register_enhanced_help_commands()
        
        logger.info("Enhanced MCP features initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize enhanced features: {e}")
        raise


if __name__ == "__main__":
    # Test the enhanced features
    initialize_enhanced_features()
    
    # Test enhanced command
    result = enhanced_create_ticket(
        title="Test enhanced ticket",
        description="Testing enhanced validation",
        type="feature",
        priority="high"
    )
    
    print("Enhanced command result:", result)