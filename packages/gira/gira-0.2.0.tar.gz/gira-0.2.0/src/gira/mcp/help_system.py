"""Help system and parameter hints for Gira MCP server commands."""

import json
import logging
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from gira.mcp.schema import (
    TicketStatus, TicketType, Priority,
    TicketCreateParams, TicketUpdateParams, TicketFilter,
    EpicCreateParams, EpicUpdateParams, EpicFilter,
    SprintCreateParams, SprintUpdateParams, SprintFilter,
    CommentParams, SearchParams
)
from gira.mcp.tools import tool_registry

logger = logging.getLogger(__name__)


@dataclass
class ParameterExample:
    """Example usage for a parameter."""
    value: Any
    description: str
    context: Optional[str] = None


@dataclass
class ParameterHint:
    """Comprehensive parameter hint information."""
    name: str
    type_name: str
    description: str
    required: bool = False
    default_value: Any = None
    enum_values: Optional[List[str]] = None
    examples: List[ParameterExample] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    related_parameters: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)


@dataclass
class CommandHelp:
    """Complete help information for a command."""
    name: str
    description: str
    parameters: List[ParameterHint]
    usage_examples: List[Dict[str, Any]] = field(default_factory=list)
    common_workflows: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    troubleshooting: List[Dict[str, str]] = field(default_factory=list)


class HelpFormatter:
    """Formats help information for different output formats."""
    
    @staticmethod
    def format_parameter_hint(param: ParameterHint, format_type: str = "detailed") -> str:
        """Format a parameter hint for display."""
        if format_type == "brief":
            return f"{param.name} ({param.type_name}): {param.description}"
        
        lines = [
            f"**{param.name}** ({param.type_name})",
            f"  {param.description}"
        ]
        
        if param.required:
            lines.append("  ✅ Required")
        else:
            lines.append(f"  ⚪ Optional (default: {param.default_value})")
        
        if param.enum_values:
            lines.append(f"  📋 Valid values: {', '.join(param.enum_values)}")
        
        if param.examples:
            lines.append("  💡 Examples:")
            for example in param.examples[:3]:  # Show up to 3 examples
                lines.append(f"    • {example.value} - {example.description}")
        
        if param.validation_rules:
            lines.append("  📏 Rules:")
            for rule in param.validation_rules:
                lines.append(f"    • {rule}")
        
        if param.suggestions:
            lines.append("  💭 Tips:")
            for suggestion in param.suggestions:
                lines.append(f"    • {suggestion}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_command_help(cmd_help: CommandHelp, format_type: str = "detailed") -> str:
        """Format complete command help."""
        if format_type == "brief":
            return f"{cmd_help.name}: {cmd_help.description}"
        
        lines = [
            f"# {cmd_help.name}",
            "",
            cmd_help.description,
            "",
            "## Parameters",
            ""
        ]
        
        for param in cmd_help.parameters:
            lines.append(HelpFormatter.format_parameter_hint(param, "detailed"))
            lines.append("")
        
        if cmd_help.usage_examples:
            lines.extend([
                "## Usage Examples",
                ""
            ])
            for i, example in enumerate(cmd_help.usage_examples, 1):
                lines.append(f"### Example {i}")
                lines.append(f"```json")
                lines.append(json.dumps(example, indent=2))
                lines.append("```")
                lines.append("")
        
        if cmd_help.common_workflows:
            lines.extend([
                "## Common Workflows",
                ""
            ])
            for workflow in cmd_help.common_workflows:
                lines.append(f"• {workflow}")
            lines.append("")
        
        if cmd_help.related_commands:
            lines.extend([
                "## Related Commands",
                ""
            ])
            for related in cmd_help.related_commands:
                lines.append(f"• {related}")
            lines.append("")
        
        if cmd_help.troubleshooting:
            lines.extend([
                "## Troubleshooting",
                ""
            ])
            for issue in cmd_help.troubleshooting:
                lines.append(f"**{issue['problem']}**")
                lines.append(f"Solution: {issue['solution']}")
                lines.append("")
        
        return "\n".join(lines)


class ParameterHintGenerator:
    """Generates parameter hints from Pydantic models and JSON schemas."""
    
    @staticmethod
    def from_pydantic_model(model: Type[BaseModel]) -> List[ParameterHint]:
        """Generate parameter hints from a Pydantic model."""
        hints = []
        
        for field_name, field_info in model.model_fields.items():
            hint = ParameterHintGenerator._create_hint_from_field(
                field_name, field_info, model
            )
            hints.append(hint)
        
        return hints
    
    @staticmethod
    def _create_hint_from_field(
        field_name: str, 
        field_info: FieldInfo, 
        model: Type[BaseModel]
    ) -> ParameterHint:
        """Create a parameter hint from a Pydantic field."""
        # Get field annotation
        field_annotation = model.model_fields[field_name].annotation
        type_name = ParameterHintGenerator._get_type_name(field_annotation)
        
        # Extract basic information
        hint = ParameterHint(
            name=field_name,
            type_name=type_name,
            description=field_info.description or f"Parameter: {field_name}",
            required=field_info.is_required(),
            default_value=field_info.default if field_info.default is not None else None
        )
        
        # Add enum values if applicable
        if hasattr(field_annotation, '__origin__') and field_annotation.__origin__ is Union:
            # Handle Optional[Enum] or Union[Enum, List[Enum]]
            enum_type = None
            for arg in field_annotation.__args__:
                if isinstance(arg, type) and issubclass(arg, Enum):
                    enum_type = arg
                    break
            
            if enum_type:
                hint.enum_values = [e.value for e in enum_type]
        elif isinstance(field_annotation, type) and issubclass(field_annotation, Enum):
            hint.enum_values = [e.value for e in field_annotation]
        
        # Add validation rules from field constraints
        if hasattr(field_info, 'constraints'):
            constraints = field_info.constraints
            if constraints.get('min_length'):
                hint.validation_rules.append(f"Minimum length: {constraints['min_length']}")
            if constraints.get('max_length'):
                hint.validation_rules.append(f"Maximum length: {constraints['max_length']}")
            if constraints.get('ge'):
                hint.validation_rules.append(f"Must be >= {constraints['ge']}")
            if constraints.get('le'):
                hint.validation_rules.append(f"Must be <= {constraints['le']}")
        
        # Add field-specific examples and suggestions
        ParameterHintGenerator._add_field_specific_info(hint)
        
        return hint
    
    @staticmethod
    def _get_type_name(annotation: Any) -> str:
        """Get human-readable type name from annotation."""
        if hasattr(annotation, '__origin__'):
            origin = annotation.__origin__
            if origin is Union:
                # Handle Optional[T] and Union types
                args = [arg for arg in annotation.__args__ if arg != type(None)]
                if len(args) == 1:
                    return f"Optional[{ParameterHintGenerator._get_type_name(args[0])}]"
                else:
                    type_names = [ParameterHintGenerator._get_type_name(arg) for arg in args]
                    return f"Union[{', '.join(type_names)}]"
            elif origin is list:
                inner_type = ParameterHintGenerator._get_type_name(annotation.__args__[0])
                return f"List[{inner_type}]"
        
        if hasattr(annotation, '__name__'):
            return annotation.__name__
        
        return str(annotation)
    
    @staticmethod
    def _add_field_specific_info(hint: ParameterHint):
        """Add field-specific examples and suggestions."""
        field_name = hint.name.lower()
        
        # Ticket ID patterns
        if 'ticket_id' in field_name:
            hint.examples = [
                ParameterExample("GCM-123", "Full ticket ID with prefix"),
                ParameterExample("123", "Ticket number (will be expanded to GCM-123)"),
                ParameterExample("TASK-456", "Custom ticket type with ID")
            ]
            hint.suggestions = [
                "You can use just the number (e.g., '123') for GCM tickets",
                "Always include the prefix for non-GCM tickets"
            ]
            hint.validation_rules.append("Must not be empty")
        
        # Epic ID patterns
        elif 'epic_id' in field_name:
            hint.examples = [
                ParameterExample("EPIC-001", "Standard epic ID format"),
                ParameterExample("001", "Epic number (will be expanded to EPIC-001)")
            ]
            hint.suggestions = [
                "Epic IDs are zero-padded to 3 digits",
                "Use 'gira epic list' to see available epics"
            ]
        
        # Status fields
        elif 'status' in field_name:
            if hint.enum_values:
                hint.examples = [
                    ParameterExample(hint.enum_values[0], f"Set status to {hint.enum_values[0]}"),
                    ParameterExample(hint.enum_values[-1], f"Set status to {hint.enum_values[-1]}")
                ]
            hint.suggestions = ["Status values are case-insensitive"]
        
        # Title fields
        elif 'title' in field_name:
            hint.examples = [
                ParameterExample("Implement user authentication", "Feature title"),
                ParameterExample("Fix login bug with empty passwords", "Bug fix title"),
                ParameterExample("Update API documentation", "Documentation task")
            ]
            hint.suggestions = [
                "Keep titles concise but descriptive",
                "Use imperative mood (e.g., 'Fix bug' not 'Fixed bug')"
            ]
        
        # Description fields
        elif 'description' in field_name:
            hint.examples = [
                ParameterExample(
                    "Add JWT-based authentication system with login/logout endpoints",
                    "Detailed feature description"
                ),
                ParameterExample(
                    "Login form accepts empty passwords and logs users in incorrectly",
                    "Bug description with reproduction details"
                )
            ]
            hint.suggestions = [
                "Markdown formatting is supported",
                "Include acceptance criteria for features",
                "Add reproduction steps for bugs"
            ]
        
        # Labels fields
        elif 'labels' in field_name:
            hint.examples = [
                ParameterExample(["bug-fix", "critical"], "Multiple labels as array"),
                ParameterExample("frontend,ui", "Comma-separated string"),
                ParameterExample(["feature"], "Single label in array")
            ]
            hint.suggestions = [
                "Labels can be provided as arrays or comma-separated strings",
                "Use lowercase with hyphens for consistency",
                "Common labels: bug-fix, feature, documentation, refactoring"
            ]
        
        # Priority fields
        elif 'priority' in field_name:
            if hint.enum_values:
                hint.examples = [
                    ParameterExample("high", "High priority item"),
                    ParameterExample("medium", "Standard priority (default)"),
                    ParameterExample("critical", "Urgent issue requiring immediate attention")
                ]
        
        # Email/assignee fields
        elif 'assignee' in field_name or 'email' in field_name:
            hint.examples = [
                ParameterExample("john.doe@company.com", "Assign to team member"),
                ParameterExample("", "Unassign (empty string)")
            ]
            hint.suggestions = [
                "Use empty string to unassign",
                "Email must be valid format"
            ]
        
        # Limit fields
        elif 'limit' in field_name:
            hint.examples = [
                ParameterExample(10, "Return 10 results (default)"),
                ParameterExample(50, "Return up to 50 results"),
                ParameterExample(1, "Return only 1 result")
            ]
            hint.suggestions = [
                "Use smaller limits for better performance",
                "Maximum limit varies by command"
            ]
        
        # Query fields
        elif 'query' in field_name:
            hint.examples = [
                ParameterExample("authentication", "Search for tickets containing 'authentication'"),
                ParameterExample("bug login", "Search for tickets with 'bug' and 'login'"),
                ParameterExample("\"exact phrase\"", "Search for exact phrase")
            ]
            hint.suggestions = [
                "Use quotes for exact phrase matching",
                "Multiple words are AND-ed together",
                "Search includes title and description"
            ]


class CommandHelpRegistry:
    """Registry for command help information."""
    
    def __init__(self):
        self.command_help: Dict[str, CommandHelp] = {}
        self._populate_built_in_help()
    
    def register_command_help(self, help_info: CommandHelp):
        """Register help information for a command."""
        self.command_help[help_info.name] = help_info
        logger.debug(f"Registered help for command: {help_info.name}")
    
    def get_command_help(self, command_name: str) -> Optional[CommandHelp]:
        """Get help information for a command."""
        return self.command_help.get(command_name)
    
    def list_commands(self) -> List[str]:
        """Get list of all available commands."""
        return list(self.command_help.keys())
    
    def search_commands(self, query: str) -> List[CommandHelp]:
        """Search for commands by name or description."""
        query_lower = query.lower()
        results = []
        
        for cmd_help in self.command_help.values():
            if (query_lower in cmd_help.name.lower() or
                query_lower in cmd_help.description.lower()):
                results.append(cmd_help)
        
        return results
    
    def _populate_built_in_help(self):
        """Populate help for built-in commands."""
        # Ticket commands
        self._register_ticket_commands()
        self._register_epic_commands()
        self._register_sprint_commands()
        self._register_board_commands()
        self._register_utility_commands()
    
    def _register_ticket_commands(self):
        """Register help for ticket management commands."""
        # get_ticket
        self.register_command_help(CommandHelp(
            name="get_ticket",
            description="Retrieve detailed information about a specific ticket",
            parameters=ParameterHintGenerator.from_pydantic_model(TicketFilter),
            usage_examples=[
                {"ticket_id": "GCM-123"},
                {"ticket_id": "123"}
            ],
            related_commands=["list_tickets", "update_ticket", "create_ticket"],
            troubleshooting=[
                {
                    "problem": "Ticket not found",
                    "solution": "Check the ticket ID format. Use 'list_tickets' to see available tickets."
                }
            ]
        ))
        
        # create_ticket
        create_params = ParameterHintGenerator.from_pydantic_model(TicketCreateParams)
        self.register_command_help(CommandHelp(
            name="create_ticket",
            description="Create a new ticket in the project",
            parameters=create_params,
            usage_examples=[
                {
                    "title": "Implement user authentication",
                    "description": "Add JWT-based authentication with login/logout endpoints",
                    "type": "feature",
                    "priority": "high",
                    "labels": ["backend", "security"]
                },
                {
                    "title": "Fix login form validation",
                    "description": "Login form accepts empty passwords",
                    "type": "bug",
                    "priority": "critical",
                    "assignee": "developer@company.com"
                }
            ],
            common_workflows=[
                "Create feature ticket → assign to developer → add to epic",
                "Create bug ticket → set high priority → assign immediately",
                "Create documentation ticket → add to sprint"
            ],
            related_commands=["update_ticket", "list_tickets", "add_comment"]
        ))
        
        # list_tickets
        filter_params = ParameterHintGenerator.from_pydantic_model(TicketFilter)
        self.register_command_help(CommandHelp(
            name="list_tickets",
            description="List tickets with optional filtering",
            parameters=filter_params,
            usage_examples=[
                {"status": "todo", "limit": 10},
                {"assignee": "john@company.com", "type": "bug"},
                {"priority": ["high", "critical"], "status": "in_progress"},
                {"labels": ["frontend"], "limit": 20}
            ],
            common_workflows=[
                "List all open tickets: status=['todo', 'in_progress']",
                "Find my assigned tickets: assignee='your-email@company.com'",
                "Check high-priority work: priority=['high', 'critical']"
            ],
            related_commands=["get_ticket", "update_ticket", "search"]
        ))
    
    def _register_epic_commands(self):
        """Register help for epic management commands."""
        # create_epic
        epic_params = ParameterHintGenerator.from_pydantic_model(EpicCreateParams)
        self.register_command_help(CommandHelp(
            name="create_epic",
            description="Create a new epic to group related tickets",
            parameters=epic_params,
            usage_examples=[
                {
                    "title": "User Authentication System",
                    "description": "Complete authentication and authorization system",
                    "labels": ["security", "backend"],
                    "status": "active"
                }
            ],
            common_workflows=[
                "Create epic → add tickets → track progress",
                "Plan feature set → create epic → break down into tickets"
            ],
            related_commands=["list_epics", "add_tickets_to_epic", "get_epic"]
        ))
    
    def _register_sprint_commands(self):
        """Register help for sprint management commands."""
        # create_sprint
        sprint_params = ParameterHintGenerator.from_pydantic_model(SprintCreateParams)
        self.register_command_help(CommandHelp(
            name="create_sprint",
            description="Create a new sprint for organizing work",
            parameters=sprint_params,
            usage_examples=[
                {
                    "name": "Sprint 1 - Authentication",
                    "goal": "Implement core authentication features",
                    "duration_days": 14,
                    "start_date": "2024-01-15"
                }
            ],
            common_workflows=[
                "Create sprint → add tickets → start sprint → track progress",
                "Plan iteration → create sprint → assign team capacity"
            ],
            related_commands=["list_sprints", "add_tickets_to_sprint", "update_sprint"]
        ))
    
    def _register_board_commands(self):
        """Register help for board visualization commands."""
        self.register_command_help(CommandHelp(
            name="get_board",
            description="Get board view of all tickets organized by status",
            parameters=[],
            usage_examples=[{}],
            common_workflows=[
                "Daily standup: check board for status updates",
                "Sprint planning: review backlog and move tickets"
            ],
            related_commands=["list_tickets", "update_ticket", "get_board_stats"]
        ))
    
    def _register_utility_commands(self):
        """Register help for utility commands."""
        # search
        search_params = ParameterHintGenerator.from_pydantic_model(SearchParams)
        self.register_command_help(CommandHelp(
            name="search",
            description="Search across tickets, epics, and other entities",
            parameters=search_params,
            usage_examples=[
                {"query": "authentication", "entity_type": "ticket", "limit": 10},
                {"query": "bug login", "limit": 5},
                {"query": "performance optimization", "entity_type": "epic"}
            ],
            common_workflows=[
                "Find related work: search for keywords",
                "Locate specific items: search by title or description",
                "Research features: search across all entity types"
            ],
            related_commands=["list_tickets", "list_epics", "get_ticket"]
        ))


# Global help registry
help_registry = CommandHelpRegistry()


def get_command_help(command_name: str, format_type: str = "detailed") -> Optional[str]:
    """Get formatted help for a command."""
    cmd_help = help_registry.get_command_help(command_name)
    if not cmd_help:
        return None
    
    return HelpFormatter.format_command_help(cmd_help, format_type)


def get_parameter_suggestions(command_name: str, parameter_name: str) -> List[str]:
    """Get suggestions for a specific parameter."""
    cmd_help = help_registry.get_command_help(command_name)
    if not cmd_help:
        return []
    
    for param in cmd_help.parameters:
        if param.name == parameter_name:
            suggestions = param.suggestions.copy()
            
            if param.enum_values:
                suggestions.append(f"Valid values: {', '.join(param.enum_values)}")
            
            if param.examples:
                suggestions.append("Example values:")
                for example in param.examples[:3]:
                    suggestions.append(f"  • {example.value}")
            
            return suggestions
    
    return []


def generate_enhanced_error_message(
    command_name: str,
    parameter_name: str,
    received_value: Any,
    error_message: str
) -> str:
    """Generate an enhanced error message with hints and examples."""
    base_msg = f"Error in '{command_name}': {error_message}"
    
    # Get parameter hints
    cmd_help = help_registry.get_command_help(command_name)
    if not cmd_help:
        return base_msg
    
    param_hint = None
    for param in cmd_help.parameters:
        if param.name == parameter_name:
            param_hint = param
            break
    
    if not param_hint:
        return base_msg
    
    # Build enhanced message
    lines = [
        base_msg,
        "",
        f"Parameter: {parameter_name}",
        f"Expected: {param_hint.type_name}",
        f"Received: {type(received_value).__name__} = {received_value}",
        ""
    ]
    
    if param_hint.enum_values:
        lines.extend([
            "Valid values:",
            f"  {', '.join(param_hint.enum_values)}",
            ""
        ])
    
    if param_hint.examples:
        lines.extend([
            "Examples:",
        ])
        for example in param_hint.examples[:2]:
            lines.append(f"  • {example.value} - {example.description}")
        lines.append("")
    
    if param_hint.suggestions:
        lines.extend([
            "Tips:",
        ])
        for suggestion in param_hint.suggestions[:2]:
            lines.append(f"  • {suggestion}")
    
    return "\n".join(lines)


def list_all_commands() -> List[Dict[str, str]]:
    """List all available commands with brief descriptions."""
    commands = []
    for cmd_name in help_registry.list_commands():
        cmd_help = help_registry.get_command_help(cmd_name)
        if cmd_help:
            commands.append({
                "name": cmd_name,
                "description": cmd_help.description
            })
    
    return sorted(commands, key=lambda x: x["name"])