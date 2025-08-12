"""Interactive custom field definition utilities."""

import json
from pathlib import Path
from typing import Optional, Tuple

from rich.prompt import Confirm, IntPrompt, Prompt

from gira.models.config import ProjectConfig
from gira.models.custom_fields import (
    CustomFieldAppliesTo,
    CustomFieldDefinition,
    CustomFieldType,
)
from gira.utils.console import console


def prompt_for_field_type() -> CustomFieldType:
    """Prompt user to select a field type."""
    console.print("\nField type for this custom field:")
    console.print("  1. string (text)")
    console.print("  2. integer (number)")
    console.print("  3. boolean (true/false)")
    console.print("  4. date (YYYY-MM-DD)")
    console.print("  5. enum (predefined options)")

    choice = IntPrompt.ask("Choice", default=1, choices=["1", "2", "3", "4", "5"])

    type_map = {
        1: CustomFieldType.STRING,
        2: CustomFieldType.INTEGER,
        3: CustomFieldType.BOOLEAN,
        4: CustomFieldType.DATE,
        5: CustomFieldType.ENUM,
    }

    return type_map[choice]


def prompt_for_field_definition(
    field_name: str,
    field_value: str,
    entity_type: str = "ticket"
) -> Optional[CustomFieldDefinition]:
    """
    Interactively prompt user to define a custom field.
    
    Returns:
        CustomFieldDefinition if user chooses to define it, None if cancelled
    """
    console.print(f"\n[yellow]Custom field '{field_name}' is not defined.[/yellow]")
    console.print("Would you like to:")
    console.print("  1. Define it now (recommended)")
    console.print("  2. Use it as a one-time string field")
    console.print("  3. Cancel")

    choice = IntPrompt.ask("Choice", default=1, choices=["1", "2", "3"])

    if choice == 3:
        # Cancel
        return None
    elif choice == 2:
        # One-time use - return a minimal definition that won't be saved
        return CustomFieldDefinition(
            name=field_name,
            display_name=field_name.replace("_", " ").title(),
            type=CustomFieldType.STRING,
            applies_to=CustomFieldAppliesTo.ALL,
            required=False,
            description="One-time custom field (not saved to config)"
        )

    # Choice 1: Define the field
    field_type = prompt_for_field_type()

    # Get display name
    default_display = field_name.replace("_", " ").title()
    display_name = Prompt.ask("Display name", default=default_display)

    # Get description
    description = Prompt.ask("Description (optional)", default="")
    if not description:
        description = None

    # Get required status
    required = Confirm.ask("Should this field be required?", default=False)

    # Type-specific configuration
    default_value = None
    options = None
    min_value = None
    max_value = None
    validation_pattern = None

    if field_type == CustomFieldType.BOOLEAN:
        # For boolean, try to parse the current value as default
        if field_value.lower() in ("true", "yes", "1", "on"):
            default_bool = True
        elif field_value.lower() in ("false", "no", "0", "off"):
            default_bool = False
        else:
            default_bool = False

        if Confirm.ask("Default value", default=default_bool):
            default_value = True
        else:
            default_value = False

    elif field_type == CustomFieldType.INTEGER:
        # Get min/max values
        if Confirm.ask("Set minimum value?", default=False):
            min_value = IntPrompt.ask("Minimum value")

        if Confirm.ask("Set maximum value?", default=False):
            max_value = IntPrompt.ask("Maximum value")

        # Get default
        if Confirm.ask("Set default value?", default=False):
            default_value = IntPrompt.ask("Default value")

    elif field_type == CustomFieldType.STRING:
        # Get validation pattern
        if Confirm.ask("Add validation pattern (regex)?", default=False):
            validation_pattern = Prompt.ask("Validation pattern")

        # Get default
        if Confirm.ask("Set default value?", default=False):
            default_value = Prompt.ask("Default value")

    elif field_type == CustomFieldType.ENUM:
        # Get options
        console.print("Enter enum options (comma-separated):")
        options_str = Prompt.ask("Options")
        options = [opt.strip() for opt in options_str.split(",") if opt.strip()]

        if not options:
            console.print("[red]Error: Enum fields must have at least one option[/red]")
            return None

        # Get default
        console.print(f"Available options: {', '.join(options)}")
        default_choice = Prompt.ask("Default value (optional)", default="")
        if default_choice and default_choice in options:
            default_value = default_choice

    elif field_type == CustomFieldType.DATE:
        # Get default
        if Confirm.ask("Set default value?", default=False):
            default_value = Prompt.ask("Default value (YYYY-MM-DD)")

    # Determine applies_to
    applies_to = CustomFieldAppliesTo.ALL
    if entity_type == "ticket":
        if Confirm.ask("Should this field apply to tickets only?", default=True):
            applies_to = CustomFieldAppliesTo.TICKET
    elif entity_type == "epic":
        if Confirm.ask("Should this field apply to epics only?", default=True):
            applies_to = CustomFieldAppliesTo.EPIC

    # Create the field definition
    field_def = CustomFieldDefinition(
        name=field_name,
        display_name=display_name,
        type=field_type,
        applies_to=applies_to,
        required=required,
        default_value=default_value,
        options=options,
        description=description,
        validation_pattern=validation_pattern,
        min_value=min_value,
        max_value=max_value,
    )

    return field_def


def save_field_to_config(field_def: CustomFieldDefinition, config_path: Path) -> None:
    """Save a field definition to the project config."""
    # Load current config
    config = ProjectConfig.from_json_file(str(config_path))

    # Check if field already exists
    existing = config.custom_fields.get_field_by_name(field_def.name)
    if existing:
        console.print(f"[yellow]Warning: Field '{field_def.name}' already exists, skipping[/yellow]")
        return

    # Add the new field
    config.custom_fields.fields.append(field_def)

    # Save back to file
    with open(config_path, 'w') as f:
        json.dump(config.model_dump(mode='json'), f, indent=2, default=str)

    console.print(f"[green]✓ Added '{field_def.name}' to custom fields configuration[/green]")


def handle_undefined_custom_field(
    field_name: str,
    field_value: str,
    config: ProjectConfig,
    entity_type: str = "ticket",
    non_interactive: bool = False
) -> Tuple[Optional[CustomFieldDefinition], bool]:
    """
    Handle an undefined custom field.
    
    Args:
        field_name: Name of the undefined field
        field_value: Value provided for the field
        config: Current project configuration
        entity_type: Type of entity (ticket or epic)
        non_interactive: If True, skip interactive prompts
    
    Returns:
        Tuple of (field_definition, should_save_to_config)
        Returns (None, False) if cancelled
    """
    if non_interactive:
        # In non-interactive mode, treat as one-time string field
        console.print(
            f"[yellow]Warning: '{field_name}' is not a defined custom field. "
            f"Using as one-time string field.[/yellow]"
        )
        field_def = CustomFieldDefinition(
            name=field_name,
            display_name=field_name.replace("_", " ").title(),
            type=CustomFieldType.STRING,
            applies_to=CustomFieldAppliesTo.ALL,
            required=False,
        )
        return field_def, False

    # Interactive mode
    field_def = prompt_for_field_definition(field_name, field_value, entity_type)

    if field_def is None:
        # User cancelled
        return None, False

    # Check if this is a one-time field (has specific description)
    if field_def.description == "One-time custom field (not saved to config)":
        return field_def, False

    # Save to config
    return field_def, True
