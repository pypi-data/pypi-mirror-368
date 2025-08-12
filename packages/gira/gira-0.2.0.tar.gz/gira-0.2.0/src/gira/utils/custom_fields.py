"""Utilities for custom fields integration."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import click
import typer
from rich.table import Table

from gira.models.config import ProjectConfig
from gira.models.custom_fields import CustomFieldDefinition, CustomFieldType
from gira.utils.console import console
from gira.utils.project import ensure_gira_project


def parse_custom_field_value(field_def: CustomFieldDefinition, value: str) -> Any:
    """Parse a string value into the appropriate type for a custom field."""
    if field_def.type == CustomFieldType.STRING:
        return value
    elif field_def.type == CustomFieldType.INTEGER:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid integer value for field '{field_def.name}': {value}")
    elif field_def.type == CustomFieldType.BOOLEAN:
        lower_value = value.lower()
        if lower_value in ("true", "yes", "1", "on"):
            return True
        elif lower_value in ("false", "no", "0", "off"):
            return False
        else:
            raise ValueError(
                f"Invalid boolean value for field '{field_def.name}': {value}. "
                "Use: true/false, yes/no, 1/0, on/off"
            )
    elif field_def.type == CustomFieldType.DATE:
        # Validate ISO date format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError(
                f"Invalid date format for field '{field_def.name}': {value}. "
                "Use ISO format: YYYY-MM-DD"
            )
        # Validate it's a real date
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date for field '{field_def.name}': {value}")
        return value
    elif field_def.type == CustomFieldType.ENUM:
        if value not in field_def.options:
            raise ValueError(
                f"Invalid value for field '{field_def.name}': {value}. "
                f"Must be one of: {', '.join(field_def.options)}"
            )
        return value
    else:
        return value


def extract_custom_fields_from_kwargs(
    config: ProjectConfig,
    entity_type: str,
    kwargs: Dict[str, Any],
    allow_undefined: bool = False
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extract custom field values from kwargs based on config.
    
    Args:
        config: Project configuration
        entity_type: Type of entity (ticket or epic)
        kwargs: Keyword arguments to extract from
        allow_undefined: If True, allow undefined fields
    
    Returns:
        Tuple of (custom_field_values, remaining_kwargs)
    """
    custom_fields = {}
    remaining_kwargs = {}

    # Get applicable custom fields
    applicable_fields = config.custom_fields.get_fields_for_entity(entity_type)

    # Build a mapping of CLI option names to field definitions
    field_map = {}
    for field in applicable_fields:
        cli_option = field.get_cli_option_name()
        field_map[cli_option.replace("-", "_")] = field

    # Extract custom field values
    for key, value in kwargs.items():
        if key in field_map and value is not None:
            field_def = field_map[key]
            try:
                parsed_value = parse_custom_field_value(field_def, value)
                custom_fields[field_def.name] = parsed_value
            except ValueError as e:
                raise typer.BadParameter(str(e))
        else:
            remaining_kwargs[key] = value

    # Validate all required fields are present
    for field in applicable_fields:
        if field.required and field.name not in custom_fields:
            if field.default_value is not None:
                custom_fields[field.name] = field.default_value
            else:
                raise typer.BadParameter(
                    f"Required custom field '{field.display_name}' (--{field.get_cli_option_name()}) is missing"
                )

    return custom_fields, remaining_kwargs


def add_custom_field_options_to_command(command: click.Command, entity_type: str) -> None:
    """
    Dynamically add custom field options to a Click/Typer command.
    
    This function modifies the command in-place to add options for all
    custom fields defined in the project configuration.
    """
    try:
        project_root = ensure_gira_project()
        config = ProjectConfig.load_from_path(project_root)
    except Exception:
        # If we can't load config (not in a Gira project), skip adding options
        return

    # Get applicable custom fields
    applicable_fields = config.custom_fields.get_fields_for_entity(entity_type)

    # Add an option for each custom field
    for field in applicable_fields:
        option_name = f"--{field.get_cli_option_name()}"
        param_name = field.get_cli_option_name().replace("-", "_")

        # Create the option
        option = click.Option(
            [option_name],
            param_name,
            help=field.get_cli_help_text(),
            required=False,  # We handle required validation separately
            default=None,    # We apply defaults during validation
        )

        # Add to command params
        command.params.append(option)


def display_custom_fields(
    custom_fields: Dict[str, Any],
    field_definitions: List[CustomFieldDefinition],
    title: str = "Custom Fields"
) -> None:
    """Display custom fields in a formatted table."""
    if not custom_fields:
        return

    table = Table(title=title, show_header=True)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    # Create a map of field names to definitions for display names
    field_map = {f.name: f for f in field_definitions}

    for name, value in sorted(custom_fields.items()):
        field_def = field_map.get(name)
        display_name = field_def.display_name if field_def else name

        # Format value based on type
        if isinstance(value, bool):
            display_value = "Yes" if value else "No"
        elif isinstance(value, list):
            display_value = ", ".join(str(v) for v in value)
        else:
            display_value = str(value)

        table.add_row(display_name, display_value)

    console.print(table)


def validate_and_merge_custom_fields(
    config: ProjectConfig,
    entity_type: str,
    provided_fields: Dict[str, Any],
    existing_fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate and merge custom fields with existing values.
    
    Args:
        config: Project configuration
        entity_type: Type of entity (ticket or epic)
        provided_fields: New field values to set
        existing_fields: Existing custom field values (for updates)
    
    Returns:
        Merged and validated custom field values
    """
    # Start with existing fields or empty dict
    merged = (existing_fields or {}).copy()

    # Update with provided fields
    merged.update(provided_fields)

    # Validate all fields
    validated = config.custom_fields.validate_custom_fields(merged, entity_type)

    return validated


def format_custom_field_for_display(
    field_name: str,
    field_value: Any,
    field_def: Optional[CustomFieldDefinition] = None
) -> str:
    """Format a custom field value for display."""
    if field_value is None:
        return "Not set"

    if isinstance(field_value, bool):
        return "Yes" if field_value else "No"
    elif isinstance(field_value, list):
        return ", ".join(str(v) for v in field_value)
    else:
        return str(field_value)
