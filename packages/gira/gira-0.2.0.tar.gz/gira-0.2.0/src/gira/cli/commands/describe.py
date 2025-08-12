"""Describe command for programmatic schema discovery."""

import json
import re
import os
from typing import Optional, Dict, Any, List, Union, get_origin, get_args

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from typer.models import CommandInfo, OptionInfo, ArgumentInfo
from rich.syntax import Syntax
import sys


def should_use_highlighting(no_color: bool, color: bool) -> bool:
    """Determine if syntax highlighting should be used.
    
    By default, returns False (no highlighting) for better compatibility
    with AI agents and programmatic usage. Users must explicitly enable
    highlighting with --color or GIRA_COLOR=1 environment variable.
    """
    # Explicit --no-color always wins
    if no_color:
        return False
    
    # Explicit --color enables highlighting
    if color:
        return True
    
    # Check for explicit environment variable to enable color
    if os.environ.get('GIRA_COLOR', '').lower() in ('1', 'true', 'yes'):
        return True
    
    # Default to no highlighting for safety and AI agent compatibility
    return False


def create_describe_command(app: typer.Typer):
    """Create the describe command with the app reference."""
    
    def describe(
        command: Optional[List[str]] = typer.Argument(None, help="Command path to describe (e.g., 'ticket create')"),
        format: str = typer.Option("json", "--format", "-f", help="Output format: json or markdown"),
        no_color: bool = typer.Option(False, "--no-color", help="Explicitly disable syntax highlighting (default is already no color)"),
        color: bool = typer.Option(False, "--color", help="Enable syntax highlighting (colors the JSON output)"),
        theme: str = typer.Option("monokai", "--theme", help="Syntax highlighting theme (requires --color)"),
        indent: int = typer.Option(2, "--indent", help="JSON indentation spaces"),
        compact: bool = typer.Option(False, "--compact", help="Compact JSON output"),
        render: bool = typer.Option(False, "--render", help="Render markdown with Rich formatting"),
        examples: bool = typer.Option(True, "--examples/--no-examples", help="Include command examples in markdown"),
        full: bool = typer.Option(False, "--full", help="Generate full documentation with all commands"),
    ) -> None:
        f"""Describe Gira commands and their schemas programmatically.
        
        By default, outputs plain JSON for compatibility with AI agents and scripts.
        Use --color to enable syntax highlighting for human readability.
        Use --format markdown for human-readable documentation.
        {format_examples_simple([
            create_example("Show all commands and their structure", "gira describe"),
            create_example("Describe a specific command in JSON format", "gira describe ticket create"),
            create_example("Generate human-readable documentation", "gira describe --format markdown"),
            create_example("Enable syntax highlighting for JSON output", "gira describe --color"),
            create_example("Generate full documentation with all commands", "gira describe --format markdown --full")
        ])}"""
        if command:
            schema = get_command_schema(app, command)
        else:
            schema = get_app_schema(app)
    
        if format.lower() == "json":
            # Generate JSON string
            if compact:
                json_str = json.dumps(schema, ensure_ascii=True, separators=(',', ':'))
            else:
                json_str = json.dumps(schema, indent=indent, ensure_ascii=True)
            
            # Determine if we should use syntax highlighting
            use_highlighting = should_use_highlighting(no_color, color)
            
            if use_highlighting:
                # Use Rich's Syntax highlighting for JSON
                syntax = Syntax(json_str, "json", theme=theme, line_numbers=False)
                console.print(syntax)
            else:
                # Use standard print for plain output
                print(json_str)
        elif format.lower() == "markdown":
            # Generate markdown output
            if command:
                markdown = generate_command_markdown(schema, examples=examples)
            else:
                markdown = generate_app_markdown(schema, full=full, examples=examples)
            
            if render:
                # Use Rich to render markdown
                from rich.markdown import Markdown
                md = Markdown(markdown)
                console.print(md)
            else:
                # Plain output
                print(markdown)
        else:
            console.print(f"[red]Error:[/red] Unsupported format: {format}")
            raise typer.Exit(1)
    
    return describe


def get_app_schema(app: typer.Typer) -> Dict[str, Any]:
    """Get the schema for the main application."""
    schema = {
        "name": "gira",
        "description": "Git-native project management for developers and AI agents",
        "type": "application",
        "commands": [],
        "options": []
    }
    
    # Add project context if in a Gira project
    try:
        from gira.utils.config import load_config
        from gira.utils.project import get_gira_root
        from gira.models import TicketStore, EpicStore, SprintStore
        
        config = load_config()
        gira_root = get_gira_root()
        schema["project_context"] = {
            "project_name": config.get("project_name", "Unknown"),
            "ticket_prefix": config.get("ticket_id_prefix", "PROJ"),
            "workflow": config.get("workflow", "kanban"),
            "config_path": str(gira_root / ".gira" / "config.json")
        }
        
        # Add quick stats
        ticket_store = TicketStore()
        epic_store = EpicStore()
        sprint_store = SprintStore()
        
        schema["project_context"]["stats"] = {
            "total_tickets": len(ticket_store.list_all_tickets()),
            "active_tickets": len([t for t in ticket_store.list_all_tickets() if t.status != "done"]),
            "total_epics": len(epic_store.list_all_epics()),
            "active_sprint": sprint_store.get_active_sprint().name if sprint_store.get_active_sprint() else None
        }
    except Exception:
        # Not in a Gira project, that's OK
        pass
    
    # Get global options from the main app
    if hasattr(app, 'registered_callback') and app.registered_callback:
        callback_func = app.registered_callback.callback
        if callback_func:
            options = extract_options_from_function(callback_func)
            schema["options"] = options
    
    # Get list of available commands and groups
    for command_obj in app.registered_commands:
        cmd_name = command_obj.name or (command_obj.callback.__name__.replace('_', '-') if command_obj.callback and hasattr(command_obj.callback, '__name__') else "unnamed-command")
        schema["commands"].append(get_leaf_command_schema(command_obj, [cmd_name], use_full_path=False))
    
    for group in app.registered_groups:
        # TyperInfo has a typer_instance attribute that holds the actual Typer app
        if hasattr(group, 'typer_instance'):
            group_app = group.typer_instance
        elif hasattr(group, 'app'):
            group_app = group.app
        else:
            # Try to find the app through other means
            group_app = getattr(group, 'typer', None)
        
        if group_app:
            schema["commands"].append(get_command_group_schema(group_app, [group.name]))
    
    return schema


def get_command_schema(app: typer.Typer, command_path: List[str]) -> Dict[str, Any]:
    """Get the schema for a specific command or command group."""
    current_app = app
    current_path_parts = []
    
    for i, cmd_part in enumerate(command_path):
        current_path_parts.append(cmd_part)
        found = False
        
        # Check registered commands (leaf nodes)
        for cmd_obj in current_app.registered_commands:
            cmd_name = cmd_obj.name or (cmd_obj.callback.__name__.replace('_', '-') if cmd_obj.callback and hasattr(cmd_obj.callback, '__name__') else "unnamed-command")
            
            if cmd_name == cmd_part:
                if i == len(command_path) - 1:  # This is the target command
                    return get_leaf_command_schema(cmd_obj, command_path)
                else:
                    # Trying to describe a subcommand of a leaf command
                    return {"error": f"Command '{cmd_name}' has no subcommands.", "path": command_path}
        
        # Check registered groups (intermediate nodes)
        for group in current_app.registered_groups:
            if group.name == cmd_part:
                # TyperInfo has a typer_instance attribute that holds the actual Typer app
                if hasattr(group, 'typer_instance'):
                    current_app = group.typer_instance
                elif hasattr(group, 'app'):
                    current_app = group.app
                else:
                    current_app = getattr(group, 'typer', None)
                
                if current_app:
                    found = True
                break
        
        if not found:
            available_commands = [cmd.name or (cmd.callback.__name__.replace('_', '-') if cmd.callback and hasattr(cmd.callback, '__name__') else 'unnamed-command') for cmd in current_app.registered_commands] + \
                                 [grp.name for grp in current_app.registered_groups]
            return {
                "error": f"Command not found: {' '.join(command_path)}",
                "path": command_path,
                "available_commands": available_commands
            }
    
    # If we're here, we're describing a command group
    return get_command_group_schema(current_app, command_path)


def get_leaf_command_schema(command: CommandInfo, path: List[str], use_full_path: bool = True) -> Dict[str, Any]:
    """Get the schema for a leaf command (not a group)."""
    description = command.help or (command.callback.__doc__.strip().split('\n')[0] if command.callback and command.callback.__doc__ else "")
    
    # Use full path for direct describe, just command name for group listings
    name = " ".join(path) if use_full_path else path[-1]
    
    schema = {
        "name": name,
        "description": description,
        "type": "command",
        "group": get_command_group(path),
        "arguments": [],
        "options": [],
        "command_examples": []
    }
    
    if command.callback:
        arguments = extract_arguments_from_function(command.callback)
        options = extract_options_from_function(command.callback)
        
        schema["arguments"] = arguments
        schema["options"] = options
        
        # Add command examples based on the command type
        schema["command_examples"] = generate_command_examples(path, arguments, options)
    
    return schema


def get_command_group(path: List[str]) -> str:
    """Determine the command group based on the command path."""
    if not path:
        return "Other Commands"
    
    # For subcommands, use the parent command as the group
    if len(path) > 1:
        parent = path[0]
        group_mapping = {
            "ticket": "Ticket Management",
            "epic": "Epic Management", 
            "sprint": "Sprint Management",
            "comment": "Comments",
            "config": "Configuration",
            "completion": "Shell Completion",
            "archive": "Archive Management",
            "team": "Team Management",
            "docs": "Documentation",
            "migrate": "Migration"
        }
        return group_mapping.get(parent, "Other Commands")
    
    # For top-level commands, categorize them
    command = path[0]
    core_commands = {"init", "board", "query", "context", "workflow", "graph", "describe", "sync"}
    
    if command in core_commands:
        return "Core Commands"
    else:
        return "Other Commands"


def get_command_group_schema(group_app: typer.Typer, path: List[str]) -> Dict[str, Any]:
    """Get the schema for a command group."""
    schema = {
        "name": " ".join(path),
        "description": group_app.info.help or "",
        "type": "group",
        "commands": []
    }
    
    # List subcommands and subgroups recursively
    for command_obj in group_app.registered_commands:
        cmd_name = command_obj.name or (command_obj.callback.__name__.replace('_', '-') if command_obj.callback and hasattr(command_obj.callback, '__name__') else "unnamed-command")
        schema["commands"].append(get_leaf_command_schema(command_obj, path + [cmd_name], use_full_path=False))
    
    for group in group_app.registered_groups:
        # TyperInfo has a typer_instance attribute that holds the actual Typer app
        if hasattr(group, 'typer_instance'):
            sub_group_app = group.typer_instance
        elif hasattr(group, 'app'):
            sub_group_app = group.app
        else:
            sub_group_app = getattr(group, 'typer', None)
        
        if sub_group_app:
            schema["commands"].append(get_command_group_schema(sub_group_app, path + [group.name]))
    
    return schema


def extract_arguments_from_function(func) -> List[Dict[str, Any]]:
    """Extract arguments from a function's signature."""
    arguments = []
    
    if hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    
    import inspect
    sig = inspect.signature(func)
    
    for param_name, param in sig.parameters.items():
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and isinstance(param.default, ArgumentInfo):
            arg_info = param.default
            description = arg_info.help or ""
            
            # Get semantic type info
            type_info = get_semantic_type_info(param.annotation, param_name)
            
            argument = {
                "name": param_name,
                "description": description,
                "required": arg_info.default is ...,
            }
            
            # Add all type information
            argument.update(type_info)
            
            if arg_info.default is not ...:
                argument["default"] = arg_info.default
                
            arguments.append(argument)
    
    return arguments


def extract_options_from_function(func) -> List[Dict[str, Any]]:
    """Extract options from a function's signature."""
    options = []
    
    if hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    
    import inspect
    sig = inspect.signature(func)
    
    for param_name, param in sig.parameters.items():
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and isinstance(param.default, OptionInfo):
            opt_info = param.default
            description = opt_info.help or ""
            
            # Get the actual option name from param_decls
            option_name = f"--{param_name.replace('_', '-')}"  # Default fallback
            if opt_info.param_decls:
                # Find the long option name (starts with --)
                long_names = [p for p in opt_info.param_decls if p.startswith('--')]
                if long_names:
                    option_name = long_names[0]
                
                # Find short option names
                short_names = [p for p in opt_info.param_decls if p.startswith('-') and not p.startswith('--')]
            else:
                short_names = []
            
            # Get semantic type info
            type_info = get_semantic_type_info(param.annotation, param_name)
            
            option = {
                "name": option_name,
                "description": description,
                "required": opt_info.default is ...,
            }
            
            # Add all type information
            option.update(type_info)
            
            if short_names:
                option["short_name"] = short_names[0]
            
            if opt_info.default is not None and opt_info.default is not ...:
                option["default"] = opt_info.default
            
            options.append(option)
    
    return options


def get_semantic_type_info(annotation, param_name: str = None) -> Dict[str, Any]:
    """Get semantic type information from a type annotation."""
    base_type = get_type_name(annotation)
    type_info = {"type": base_type}
    
    # Add semantic type based on parameter name patterns
    if param_name:
        semantic_type = infer_semantic_type(param_name, base_type)
        if semantic_type != base_type:
            type_info["semantic_type"] = semantic_type
        
        # Add validation constraints based on semantic type
        constraints = get_type_constraints(semantic_type, param_name)
        if constraints:
            type_info.update(constraints)
    
    # Handle enum types - get the choices
    if hasattr(annotation, '__members__'):
        # noinspection PyTypeChecker
        type_info["choices"] = list(annotation.__members__.keys())
        type_info["semantic_type"] = "enum"
    
    # Handle List types to get inner type
    if hasattr(annotation, '__origin__'):
        origin = get_origin(annotation)
        if origin is list or origin is List:
            args = get_args(annotation)
            if args:
                inner_type_info = get_semantic_type_info(args[0], param_name)
                # noinspection PyTypeChecker
                type_info["items"] = inner_type_info
    
    return type_info


def infer_semantic_type(param_name: str, base_type: str) -> str:
    """Infer semantic type from parameter name."""
    name_lower = param_name.lower()
    
    # Map parameter names to semantic types
    semantic_patterns = {
        "ticket_id": r"ticket.*id|id.*ticket",
        "epic_id": r"epic.*id|id.*epic", 
        "sprint_id": r"sprint.*id|id.*sprint",
        "email": r"email|mail|assignee|reporter|owner",
        "date": r"date|created|updated|start|end|target",
        "file_path": r"file|path|location",
        "glob_pattern": r"glob|pattern.*glob",
        "regex_pattern": r"regex|pattern.*regex|query",
        "url": r"url|link|uri",
        "json": r"json|data",
        "duration": r"duration|days|hours|minutes",
        "status": r"status",
        "priority": r"priority",
        "type": r"^type$",
        "format": r"format|output"
    }
    
    for semantic_type, pattern in semantic_patterns.items():
        if re.search(pattern, name_lower):
            return semantic_type
    
    return base_type


def get_type_constraints(semantic_type: str, param_name: str = None) -> Dict[str, Any]:
    """Get validation constraints for a semantic type."""
    constraints = {}
    
    # Try to dynamically load statuses if we're in a Gira project
    try:
        from gira.utils.board_config import get_valid_statuses
        from gira.utils.project import get_gira_root
        get_gira_root()  # This will raise if not in a project
        dynamic_statuses = get_valid_statuses()
    except (ImportError, FileNotFoundError, Exception):
        # Fall back to default statuses if not in a project or import fails
        dynamic_statuses = ["backlog", "todo", "in_progress", "review", "done"]
    
    constraint_map = {
        "ticket_id": {
            "pattern": r"^[A-Z]{2,4}-\d+$",
            "examples": ["GIRA-123", "GCM-456", "PROJ-1"]
        },
        "epic_id": {
            "pattern": r"^EPIC-\d{3}$",
            "examples": ["EPIC-001", "EPIC-002"]
        },
        "sprint_id": {
            "pattern": r"^SPRINT-\d{3}$",
            "examples": ["SPRINT-001", "SPRINT-002"]
        },
        "email": {
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "examples": ["user@example.com", "john.doe@company.org"]
        },
        "date": {
            "pattern": r"^\d{4}-\d{2}-\d{2}$",
            "format": "YYYY-MM-DD",
            "examples": ["2025-01-20", "2025-12-31"]
        },
        "file_path": {
            "examples": [".gira/config.json", "/path/to/file.txt", "./relative/path.md"]
        },
        "glob_pattern": {
            "examples": ["*.py", "**/*.json", "src/**/*.ts"]
        },
        "regex_pattern": {
            "examples": [".*\\.py$", "^test_.*", "(bug|fix):"]
        },
        "duration": {
            "min_value": 1,
            "max_value": 365,
            "examples": [7, 14, 30]
        },
        "status": {
            "choices": dynamic_statuses,
            "examples": dynamic_statuses[:3] if len(dynamic_statuses) >= 3 else dynamic_statuses
        },
        "priority": {
            "choices": ["low", "medium", "high", "critical"],
            "examples": ["medium", "high"]
        },
        "type": {
            "choices": ["story", "task", "bug", "epic", "feature", "subtask"],
            "examples": ["task", "bug", "feature"]
        },
        "format": {
            "choices": ["text", "json", "table", "csv"],
            "examples": ["json", "table"]
        }
    }
    
    if semantic_type in constraint_map:
        constraints.update(constraint_map[semantic_type])
    
    # Provide context-specific file path examples
    if semantic_type == "file_path" and param_name:
        if "description" in param_name.lower():
            constraints["examples"] = [
                "ticket-description.md",
                "docs/feature-spec.md",
                "/tmp/bug-report.txt"
            ]
        elif "goal" in param_name.lower():
            constraints["examples"] = [
                "sprint-goals.md",
                "objectives/q1-goals.txt",
                "./planning/sprint-15.md"
            ]
        elif "content" in param_name.lower():
            constraints["examples"] = [
                "comment.md",
                "update-notes.txt",
                "./feedback/review-comments.md"
            ]
    
    # Add length constraints for string types
    if semantic_type in ["string", "ticket_id", "epic_id", "sprint_id"]:
        if param_name and "title" in param_name.lower():
            constraints["min_length"] = 3
            constraints["max_length"] = 200
        elif param_name and "description" in param_name.lower():
            constraints["max_length"] = 5000
    
    return constraints


def get_type_name(annotation) -> str:
    """Get a human-readable type name from a type annotation."""
    if annotation == inspect.Parameter.empty:
        return "string"
    
    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        List: "array",
        Dict: "object",
        Optional: "any" # Will be refined by inner type
    }
    
    # Handle Optional and other Union types
    if hasattr(annotation, '__origin__') and annotation.__origin__ is Union:
        # Filter out NoneType from Union args
        non_none_args = [arg for arg in annotation.__args__ if arg is not type(None)]
        if len(non_none_args) == 1:
            return get_type_name(non_none_args[0]) # Unwrap Optional
        else:
            # Handle Union[str, int] etc. - return a generic 'union' or 'any'
            return "union"
    
    # Handle List, Dict, etc. from typing module
    if hasattr(annotation, '__origin__'):
        origin = get_origin(annotation)
        # Check if origin is a type we recognize
        if origin is not None:
            # Check for specific typing constructs we handle
            if origin is list or origin is List:
                return "array"
            elif origin is dict or origin is Dict:
                return "object"
            # For any other origin types, fall through to default
    
    # Handle direct types (e.g., str, int, bool)
    if type(annotation) is type and annotation in type_mapping:
        return type_mapping[annotation]
    
    # Handle enum types (e.g., TicketStatus, TicketType)
    if hasattr(annotation, '__members__'):
        return "enum"
    
    # Handle Typer's specific types (e.g., FileTextWrite)
    if hasattr(annotation, '__name__') and annotation.__name__.startswith('File'):
        return "file"
    
    # Default to string for anything else
    return "string"


def generate_command_examples(path: List[str], arguments: List[Dict[str, Any]], options: List[Dict[str, Any]]) -> List[str]:
    """Generate command examples based on the command path and schema."""
    command_name = "gira " + " ".join(path)
    examples = []
    
    # Map of command patterns to specific examples
    example_patterns = {
        ("ticket", "create"): [
            'gira ticket create "Fix login bug" --priority high --type bug',
            'gira ticket create "Add user authentication" --description "Implement OAuth2" --epic EPIC-001',
            'gira ticket create "Update documentation" --assignee john@example.com --labels "docs,urgent"'
        ],
        ("ticket", "update"): [
            'gira ticket update GCM-123 --status in_progress',
            'gira ticket update PROJ-456 --assignee jane@example.com --priority high',
            'gira ticket update GCM-789 --add-label "backend" --story-points 5'
        ],
        ("ticket", "move"): [
            'gira ticket move GCM-123 in_progress',
            'gira ticket move PROJ-456 review',
            'gira ticket move GCM-789 done'
        ],
        ("ticket", "list"): [
            'gira ticket list --status in_progress',
            'gira ticket list --assignee john@example.com --priority high',
            'gira ticket list --query "login" --format json'
        ],
        ("epic", "create"): [
            'gira epic create "User Authentication System" --description "Implement full auth flow"',
            'gira epic create "Performance Optimization" --owner tech-lead@company.com --target-date 2025-03-01'
        ],
        ("epic", "update"): [
            'gira epic update EPIC-001 --status active',
            'gira epic update EPIC-002 --add-ticket GCM-123 --add-ticket GCM-124'
        ],
        ("sprint", "create"): [
            'gira sprint create "Sprint 23" --goal "Complete authentication features" --duration 14',
            'gira sprint create "Q1 Sprint 1" --start-date 2025-01-15 --duration 21'
        ],
        ("comment", "add"): [
            'gira comment add GCM-123',
            'gira comment add PROJ-456 --message "Fixed the issue with login timeout"'
        ]
    }
    
    # Check if we have specific examples for this command
    # Only check if we have a 2-element path (most common case)
    if len(path) == 2:
        command_tuple = (path[0], path[1])
        if command_tuple in example_patterns:
            return example_patterns[command_tuple]
    
    # Generate generic examples based on arguments and options
    base_example = command_name
    
    # Add required arguments
    required_args = [arg for arg in arguments if arg.get("required", False)]
    for arg in required_args:
        if "examples" in arg and arg["examples"]:
            base_example += f' {arg["examples"][0]}'
        elif arg.get("semantic_type") == "ticket_id":
            base_example += " GCM-123"
        elif arg.get("semantic_type") == "epic_id":
            base_example += " EPIC-001"
        elif arg.get("semantic_type") == "sprint_id":
            base_example += " SPRINT-001"
        else:
            base_example += f' <{arg["name"]}>'
    
    # Create variations with different options
    if not examples:
        examples.append(base_example)
    
    # Add example with common options
    common_options = [opt for opt in options if opt["name"] in ["--priority", "--status", "--format", "--assignee"]]
    if common_options:
        example_with_opts = base_example
        for opt in common_options[:2]:  # Use max 2 options for clarity
            if "examples" in opt and opt["examples"]:
                example_with_opts += f' {opt["name"]} {opt["examples"][0]}'
        examples.append(example_with_opts)
    
    # Add example showing boolean flags
    bool_options = [opt for opt in options if opt.get("type") == "boolean"]
    if bool_options and len(examples) < 3:
        example_with_flags = base_example + f' {bool_options[0]["name"]}'
        examples.append(example_with_flags)
    
    return examples[:3]  # Return max 3 examples


# Import inspect at module level
import inspect


def generate_app_markdown(schema: Dict[str, Any], full: bool = False, examples: bool = True) -> str:
    """Generate markdown documentation for the entire application."""
    lines = []
    
    # Title and description
    lines.append(f"# {schema['name'].upper()} CLI Reference")
    lines.append("")
    lines.append(schema.get('description', ''))
    lines.append("")
    
    # Table of contents
    if full:
        lines.append("## Table of Contents")
        lines.append("")
        lines.append("- [Commands](#commands)")
        for cmd in schema.get('commands', []):
            cmd_name = cmd['name']
            anchor = cmd_name.replace(' ', '-').lower()
            lines.append(f"  - [{cmd_name}](#{anchor})")
        lines.append("- [Global Options](#global-options)")
        lines.append("")
    
    # Commands overview
    lines.append("## Commands")
    lines.append("")
    
    # Group commands by type
    groups = {}
    standalone = []
    
    for cmd in schema.get('commands', []):
        if cmd['type'] == 'group':
            groups[cmd['name']] = cmd
        else:
            standalone.append(cmd)
    
    # Show standalone commands first
    if standalone:
        lines.append("### Core Commands")
        lines.append("")
        for cmd in standalone:
            lines.append(f"- `{cmd['name']}` - {cmd['description']}")
        lines.append("")
    
    # Show command groups
    if groups:
        lines.append("### Command Groups")
        lines.append("")
        for name, group in sorted(groups.items()):
            lines.append(f"#### {name}")
            lines.append(f"{group['description']}")
            lines.append("")
            if 'commands' in group:
                for subcmd in group['commands']:
                    lines.append(f"- `{subcmd['name']}` - {subcmd['description']}")
                lines.append("")
    
    # Detailed command documentation if full
    if full:
        lines.append("## Command Details")
        lines.append("")
        
        # Document each command in detail
        all_commands = standalone + [cmd for group in groups.values() for cmd in group.get('commands', [])]
        for cmd in all_commands:
            if cmd['type'] != 'group':
                lines.extend(generate_command_section(cmd, examples))
                lines.append("")
    
    # Global options
    if schema.get('options'):
        lines.append("## Global Options")
        lines.append("")
        lines.extend(generate_options_table(schema['options']))
        lines.append("")
    
    return '\n'.join(lines)


def generate_command_markdown(schema: Dict[str, Any], examples: bool = True) -> str:
    """Generate markdown documentation for a single command."""
    lines = []
    
    # Handle error schemas
    if 'error' in schema:
        lines.append(f"# Error: {schema['error']}")
        if 'available_commands' in schema:
            lines.append("")
            lines.append("## Available commands:")
            for cmd in schema['available_commands']:
                lines.append(f"- {cmd}")
        return '\n'.join(lines)
    
    # Command header
    lines.append(f"# `{schema['name']}`")
    lines.append("")
    lines.append(schema.get('description', ''))
    lines.append("")
    
    # For groups, show subcommands
    if schema['type'] == 'group':
        lines.append("## Subcommands")
        lines.append("")
        for cmd in schema.get('commands', []):
            lines.append(f"- `{cmd['name']}` - {cmd['description']}")
        lines.append("")
    else:
        # For regular commands, show usage details
        lines.extend(generate_command_section(schema, examples))
    
    return '\n'.join(lines)


def generate_command_section(cmd: Dict[str, Any], examples: bool = True) -> List[str]:
    """Generate detailed documentation section for a command."""
    lines = []
    
    lines.append(f"### `{cmd['name']}`")
    lines.append("")
    lines.append(cmd.get('description', ''))
    lines.append("")
    
    # Usage
    lines.append("**Usage:**")
    lines.append("```bash")
    usage = f"gira {cmd['name']}"
    if cmd.get('options'):
        usage += " [OPTIONS]"
    if cmd.get('arguments'):
        for arg in cmd['arguments']:
            if arg.get('required', False):
                usage += f" {arg['name'].upper()}"
            else:
                usage += f" [{arg['name'].upper()}]"
    lines.append(usage)
    lines.append("```")
    lines.append("")
    
    # Arguments
    if cmd.get('arguments'):
        lines.append("**Arguments:**")
        lines.append("")
        for arg in cmd['arguments']:
            required = " *(required)*" if arg.get('required', False) else ""
            lines.append(f"- `{arg['name'].upper()}`{required} - {arg.get('description', '')}")
            if 'type' in arg:
                lines.append(f"  - Type: `{arg['type']}`")
            if 'default' in arg and arg['default'] is not None:
                lines.append(f"  - Default: `{arg['default']}`")
            if 'examples' in arg:
                lines.append(f"  - Examples: {', '.join(f'`{ex}`' for ex in arg['examples'])}")
        lines.append("")
    
    # Options
    if cmd.get('options'):
        lines.append("**Options:**")
        lines.append("")
        lines.extend(generate_options_table(cmd['options']))
        lines.append("")
    
    # Examples
    if examples and cmd.get('command_examples'):
        lines.append("**Examples:**")
        lines.append("")
        for example in cmd['command_examples']:
            lines.append("```bash")
            lines.append(example)
            lines.append("```")
        lines.append("")
    
    return lines


def generate_options_table(options: List[Dict[str, Any]]) -> List[str]:
    """Generate a markdown table for options."""
    lines = []
    
    # Find the maximum lengths for each column
    max_name = max(len(opt['name']) for opt in options) if options else 0
    max_type = max(len(opt.get('type', 'string')) for opt in options) if options else 0
    
    # Table header
    lines.append("| Option | Type | Description | Default |")
    lines.append("|--------|------|-------------|---------|")
    
    # Table rows
    for opt in options:
        name = opt['name']
        if 'short_name' in opt:
            name += f", {opt['short_name']}"
        
        opt_type = opt.get('type', 'string')
        if opt.get('semantic_type'):
            opt_type = opt['semantic_type']
        
        desc = opt.get('description', '')
        if opt.get('choices'):
            desc += f" (choices: {', '.join(opt['choices'])})"
        
        default = opt.get('default', '')
        if default is None:
            default = ''
        elif isinstance(default, bool):
            default = str(default).lower()
        elif isinstance(default, list):
            default = ', '.join(str(d) for d in default)
        else:
            default = str(default)
        
        lines.append(f"| {name} | {opt_type} | {desc} | {default} |")
    
    return lines