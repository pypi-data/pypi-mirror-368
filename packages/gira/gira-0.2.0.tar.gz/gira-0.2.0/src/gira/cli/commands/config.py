"""Configuration management commands for Gira."""

import json
from typing import Any, Optional

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.table import Table

from gira.utils.board_config import get_valid_statuses
from gira.utils.config_utils import load_config, save_config, DEFAULT_CONFIG
from gira.utils.project import ensure_gira_project

# Configuration key descriptions
CONFIG_DESCRIPTIONS = {
    "user.name": "Default name for tickets and commits",
    "user.email": "Default email for tickets and commits",
    "ticket.default_type": "Default type for new tickets (feature/bug/task/docs)",
    "ticket.default_priority": "Default priority for new tickets (low/medium/high)",
    "ticket.default_status": "Default status for new tickets",
    "sprint.duration_days": "Default sprint duration in days",
    "board.columns": "Board column names and order",
    "display.truncate_title": "Maximum title length in list views",
    "display.date_format": "Date format for display",
    "render_markdown": "Render Markdown in descriptions (true/false)",
    "archive.auto_archive_after_days": "Automatically archive done tickets after N days (None to disable)",
    "archive.performance_threshold": "Warn when active tickets exceed this count",
    "archive.suggest_done_after_days": "Suggest archiving done tickets after N days",
    "archive.suggest_stale_after_days": "Suggest archiving stale backlog tickets after N days",
    "git.auto_stage_moves": "Automatically stage file moves with 'git mv' (true/false)",
    "git.auto_stage_archives": "Automatically stage archives with 'git mv' (true/false)",
    "git.auto_stage_deletes": "Automatically stage deletions with 'git rm' (true/false)",
    "storage.enabled": "Enable attachment storage (true/false)",
    "storage.provider": "Storage provider (s3/gcs/azure/r2/b2)",
    "storage.bucket": "Storage bucket/container name",
    "storage.region": "Storage region (e.g., us-east-1)",
    "storage.base_path": "Base path in bucket for all attachments",
    "storage.max_file_size_mb": "Maximum file size in megabytes (1-5000)",
    "storage.credential_source": "Where to load credentials from (environment/file/prompt)",
    "storage.retention_days": "Default retention period in days (1-3650 or none)",
    "project.name": "Project display name",
    "project.ticket_prefix": "Ticket ID prefix (2-5 uppercase letters, triggers rename wizard if changed)",
    "skip_confirmations": "Skip all confirmation prompts (true/false)",
}


def validate_config_value(key: str, value: str) -> tuple[bool, Any, Optional[str]]:
    """Validate a configuration value based on its key.
    
    Returns: (is_valid, parsed_value, error_message)
    """
    # Type validation based on key
    if key == "sprint.duration_days":
        try:
            parsed = int(value)
            if parsed <= 0:
                return False, None, "Sprint duration must be positive"
            return True, parsed, None
        except ValueError:
            return False, None, "Sprint duration must be a number"

    elif key == "display.truncate_title":
        try:
            parsed = int(value)
            if parsed < 10:
                return False, None, "Title truncation must be at least 10"
            return True, parsed, None
        except ValueError:
            return False, None, "Title truncation must be a number"

    elif key == "ticket.default_type":
        valid_types = ["feature", "bug", "task", "docs"]
        if value.lower() not in valid_types:
            return False, None, f"Invalid type. Must be one of: {', '.join(valid_types)}"
        return True, value.lower(), None

    elif key == "ticket.default_priority":
        valid_priorities = ["low", "medium", "high"]
        if value.lower() not in valid_priorities:
            return False, None, f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        return True, value.lower(), None

    elif key == "ticket.default_status":
        valid_statuses = get_valid_statuses()
        if value.lower() not in valid_statuses:
            return False, None, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        return True, value.lower(), None

    elif key == "board.columns":
        # Accept comma-separated list
        columns = [col.strip() for col in value.split(",")]
        if len(columns) < 2:
            return False, None, "Board must have at least 2 columns"
        return True, columns, None
    
    elif key == "archive.auto_archive_after_days":
        if value.lower() == "none" or value == "":
            return True, None, None
        try:
            parsed = int(value)
            if parsed <= 0:
                return False, None, "Archive days must be positive"
            if parsed > 365:
                return False, None, "Archive days must be less than 365"
            return True, parsed, None
        except ValueError:
            return False, None, "Archive days must be a number or 'none'"
    
    elif key == "archive.performance_threshold":
        try:
            parsed = int(value)
            if parsed <= 0:
                return False, None, "Performance threshold must be positive"
            return True, parsed, None
        except ValueError:
            return False, None, "Performance threshold must be a number"
    
    elif key in ["archive.suggest_done_after_days", "archive.suggest_stale_after_days"]:
        try:
            parsed = int(value)
            if parsed <= 0:
                return False, None, "Days must be positive"
            return True, parsed, None
        except ValueError:
            return False, None, "Days must be a number"
            
    elif key == "render_markdown":
        if value.lower() in ["true", "false", "yes", "no", "1", "0"]:
            return True, value.lower() in ["true", "yes", "1"], None
        return False, None, "Must be true or false"
    
    elif key.startswith("git.auto_stage_"):
        # All git.auto_stage_* options are boolean
        if value.lower() in ["true", "false", "yes", "no", "1", "0"]:
            return True, value.lower() in ["true", "yes", "1"], None
        return False, None, "Must be true or false"
    
    elif key == "storage.enabled":
        if value.lower() in ["true", "false", "yes", "no", "1", "0"]:
            return True, value.lower() in ["true", "yes", "1"], None
        return False, None, "Must be true or false"
    
    elif key == "skip_confirmations":
        if value.lower() in ["true", "false", "yes", "no", "1", "0"]:
            return True, value.lower() in ["true", "yes", "1"], None
        return False, None, "Must be true or false"
    
    elif key == "storage.provider":
        if value.lower() == "none" or value == "":
            return True, None, None
        valid_providers = ["s3", "gcs", "azure", "r2", "b2"]
        if value.lower() not in valid_providers:
            return False, None, f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        return True, value.lower(), None
    
    elif key == "storage.bucket":
        if value == "none" or value == "":
            return True, None, None
        # Basic bucket name validation
        if len(value) < 3 or len(value) > 63:
            return False, None, "Bucket name must be between 3 and 63 characters"
        import re
        if not re.match(r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$", value):
            return False, None, "Bucket name must start and end with lowercase letter or number"
        return True, value, None
    
    elif key == "storage.region":
        if value == "none" or value == "":
            return True, None, None
        # Basic region validation (AWS-style)
        import re
        if not re.match(r"^[a-z]{2}-[a-z]+-\d+$", value):
            return False, None, "Region should be in format like us-east-1, eu-west-2"
        return True, value, None
    
    elif key == "storage.base_path":
        if value == "none" or value == "":
            return True, None, None
        # Sanitize path
        value = value.strip("/")
        import re
        if not re.match(r"^[a-zA-Z0-9/_.-]*$", value):
            return False, None, "Base path can only contain letters, numbers, /, _, ., and -"
        return True, value, None
    
    elif key == "storage.max_file_size_mb":
        try:
            parsed = int(value)
            if parsed < 1 or parsed > 5000:
                return False, None, "Max file size must be between 1 and 5000 MB"
            return True, parsed, None
        except ValueError:
            return False, None, "Max file size must be a number"
    
    elif key == "storage.credential_source":
        valid_sources = ["environment", "file", "prompt"]
        if value.lower() not in valid_sources:
            return False, None, f"Invalid source. Must be one of: {', '.join(valid_sources)}"
        return True, value.lower(), None
    
    elif key == "storage.retention_days":
        if value.lower() == "none" or value == "":
            return True, None, None
        try:
            parsed = int(value)
            if parsed < 1 or parsed > 3650:
                return False, None, "Retention days must be between 1 and 3650"
            return True, parsed, None
        except ValueError:
            return False, None, "Retention days must be a number or 'none'"
    
    elif key == "project.name":
        # Validate project name
        if not value.strip():
            return False, None, "Project name cannot be empty"
        if len(value) > 100:
            return False, None, "Project name must be 100 characters or less"
        return True, value.strip(), None
    
    elif key == "project.ticket_prefix":
        # Validate ticket prefix format
        import re
        if not re.match(r'^[A-Z]{2,5}$', value):
            return False, None, "Ticket prefix must be 2-5 uppercase letters (e.g., GCM, PROJ, NEW)"
        # This will trigger the rename wizard in the set command
        return True, value, None

    # For string values, just return as-is
    return True, value, None


def config_set(
    key: str = typer.Argument(..., help="Configuration key (e.g., user.name)"),
    value: str = typer.Argument(..., help="Configuration value"),
    global_config: bool = typer.Option(False, "--global", "-g", help="Set in global config (not implemented)"),
) -> None:
    """Set a configuration value."""
    root = ensure_gira_project()

    # Check if key is known
    if key not in DEFAULT_CONFIG:
        console.print(f"[yellow]Warning:[/yellow] Unknown configuration key: {key}")
        console.print("Known keys:")
        for k in sorted(DEFAULT_CONFIG.keys()):
            console.print(f"  • {k}")

        # Ask for confirmation
        if not typer.confirm("Do you want to set this custom key anyway?"):
            raise typer.Exit(0)

    # Validate value if it's a known key
    if key in DEFAULT_CONFIG:
        is_valid, parsed_value, error_msg = validate_config_value(key, value)
        if not is_valid:
            console.print(f"[red]Error:[/red] {error_msg}")
            raise typer.Exit(1)
        value = parsed_value

    # Load current config
    config = load_config(root)
    
    # Special handling for ticket prefix changes
    if key == "project.ticket_prefix":
        # Load the full project config to get the current prefix
        from gira.models.config import ProjectConfig
        config_path = root / ".gira" / "config.json"
        if config_path.exists():
            project_config = ProjectConfig.from_json_file(str(config_path))
            current_prefix = project_config.ticket_id_prefix
            
            if current_prefix != value:
                # Trigger the rename wizard
                console.print(f"[yellow]Warning:[/yellow] Changing ticket prefix from '{current_prefix}' to '{value}'")
                console.print("This will trigger a rename wizard to update all existing tickets and references.")
                
                if not typer.confirm("Do you want to proceed with the rename wizard?"):
                    console.print("[red]Aborted:[/red] Ticket prefix change cancelled")
                    raise typer.Exit(0)
                
                # Import and run the rename wizard
                from gira.utils.prefix_rename import run_rename_wizard
                success = run_rename_wizard(root, current_prefix, value)
                
                if success:
                    console.print(f"[green]✓[/green] Successfully renamed ticket prefix from '{current_prefix}' to '{value}'")
                else:
                    console.print("[red]Error:[/red] Failed to rename ticket prefix")
                    raise typer.Exit(1)
                
                return  # Exit early since rename wizard handles everything
    
    # For all other config values, set normally
    elif key == "project.name":
        # Update the project name in the main config.json
        from gira.models.config import ProjectConfig
        config_path = root / ".gira" / "config.json"
        if config_path.exists():
            project_config = ProjectConfig.from_json_file(str(config_path))
            project_config.name = value
            project_config.save_to_json_file(str(config_path))
            console.print(f"[green]✓[/green] Set project name = {value}")
            return

    # Set the value
    config[key] = value

    # Save config
    save_config(root, config)

    console.print(f"[green]✓[/green] Set {key} = {value}")


def config_get(
    key: Optional[str] = typer.Argument(None, help="Configuration key to get (show all if not specified)"),
    list_keys: bool = typer.Option(False, "--list", "-l", help="List all configuration keys"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON (shorthand for --format json)"),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated list of fields to include in JSON output (for filtering config keys)"),
) -> None:
    f"""Get configuration values.
    {format_examples_simple([
        create_example("Get all configuration values", "gira config get"),
        create_example("Get a specific configuration value", "gira config get user.email"),
        create_example("Export as JSON", "gira config get --format json"),
        create_example("Get specific config value as JSON", "gira config get user.email --json"),
        create_example("Filter specific fields in JSON output", "gira config get --json --fields user.name,user.email")
    ])}"""
    root = ensure_gira_project()
    config = load_config(root)
    
    # Handle --json flag as shorthand for --format json
    if json_output:
        output_format = "json"

    if list_keys:
        # List all available keys with descriptions
        table = Table(title="Available Configuration Keys", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Default", style="dim")

        for k in sorted(DEFAULT_CONFIG.keys()):
            default_val = DEFAULT_CONFIG[k]
            if isinstance(default_val, list):
                default_val = ", ".join(str(v) for v in default_val)
            table.add_row(k, CONFIG_DESCRIPTIONS.get(k, ""), str(default_val))

        console.print(table)
        return

    if key:
        # Get specific key
        if key in config:
            value = config[key]
            if output_format == "json":
                # Output as JSON
                print(json.dumps(value, indent=2, default=str))
            else:
                # Output as text
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                console.print(f"{key} = {value}")
        else:
            if output_format == "json":
                # Return default value in JSON format if key not set
                if key in DEFAULT_CONFIG:
                    print(json.dumps(DEFAULT_CONFIG[key], indent=2, default=str))
                else:
                    print("null")
            else:
                console.print(f"[yellow]Configuration key not set:[/yellow] {key}")
                if key in DEFAULT_CONFIG:
                    default = DEFAULT_CONFIG[key]
                    if isinstance(default, list):
                        default = ", ".join(str(v) for v in default)
                    console.print(f"[dim]Default value: {default}[/dim]")
                raise typer.Exit(1)
    else:
        # Show all configuration
        if output_format == "json":
            # Merge with defaults to show all keys
            all_config = DEFAULT_CONFIG.copy()
            all_config.update(config)
            
            # Apply field selection if specified
            if fields:
                # For config, fields is actually a filter on config keys
                field_list = [f.strip() for f in fields.split(",")]
                filtered_config = {k: v for k, v in all_config.items() if k in field_list}
                all_config = filtered_config
            
            print(json.dumps(all_config, indent=2, default=str))
        else:
            table = Table(title="Current Configuration", show_header=True, header_style="bold cyan")
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")

            # Merge with defaults to show all keys
            all_keys = set(DEFAULT_CONFIG.keys()) | set(config.keys())

            for k in sorted(all_keys):
                value = config.get(k, DEFAULT_CONFIG.get(k, ""))
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)

                # Highlight non-default values
                if k in config and k in DEFAULT_CONFIG and config[k] != DEFAULT_CONFIG[k]:
                    table.add_row(k, f"[bold]{value}[/bold]")
                else:
                    table.add_row(k, str(value))

            console.print(table)


def config_reset(
    key: Optional[str] = typer.Argument(None, help="Configuration key to reset (reset all if not specified)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
) -> None:
    """Reset configuration to default values."""
    root = ensure_gira_project()

    if key:
        # Reset specific key
        if key not in DEFAULT_CONFIG:
            console.print(f"[red]Error:[/red] Unknown configuration key: {key}")
            raise typer.Exit(1)

        if not force and not typer.confirm(f"Reset {key} to default value?"):
            raise typer.Exit(0)

        config = load_config(root)
        if key in config:
            config[key] = DEFAULT_CONFIG[key]
            save_config(root, config)
            console.print(f"[green]✓[/green] Reset {key} to default value")
        else:
            console.print(f"[yellow]Key {key} is already at default value[/yellow]")
    else:
        # Reset all configuration
        if not force and not typer.confirm("Reset all configuration to default values?"):
            raise typer.Exit(0)

        save_config(root, DEFAULT_CONFIG.copy())
        console.print("[green]✓[/green] Reset all configuration to default values")


def config_rename_prefix(
    new_prefix: str = typer.Argument(..., help="New ticket ID prefix (2-5 uppercase letters)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompts"),
) -> None:
    """Rename the ticket ID prefix for the entire project.
    
    This command will:
    - Analyze the impact of the rename
    - Create a backup of all data (only if .gira is not git-tracked)
    - Rename all ticket and epic IDs
    - Update all references and relationships
    - Update configuration and prefix history
    - Preserve git commit history (old IDs will still work)
    
    Note: If .gira is tracked by git, no backup is created since you can
    use git to revert changes if needed.
    
    Examples:
        # Rename from GCM to NEW
        gira config rename-prefix NEW
        
        # Skip confirmation prompts
        gira config rename-prefix PROJ --force
    """
    root = ensure_gira_project()
    
    # Validate the new prefix
    import re
    if not re.match(r'^[A-Z]{2,5}$', new_prefix):
        console.print("[red]Error:[/red] Ticket prefix must be 2-5 uppercase letters (e.g., GCM, PROJ, NEW)")
        raise typer.Exit(1)
    
    # Get current prefix
    from gira.models.config import ProjectConfig
    config_path = root / ".gira" / "config.json"
    if not config_path.exists():
        console.print("[red]Error:[/red] Project configuration not found")
        raise typer.Exit(1)
    
    project_config = ProjectConfig.from_json_file(str(config_path))
    current_prefix = project_config.ticket_id_prefix
    
    if current_prefix == new_prefix:
        console.print(f"[yellow]The ticket prefix is already '{new_prefix}'[/yellow]")
        raise typer.Exit(0)
    
    # Run the rename wizard
    from gira.utils.prefix_rename import run_rename_wizard
    
    if force:
        # For force mode, we need to modify the wizard behavior
        # For now, just warn the user
        console.print(f"[yellow]Warning:[/yellow] Force mode will skip all confirmations")
    
    success = run_rename_wizard(root, current_prefix, new_prefix)
    
    if not success:
        raise typer.Exit(1)
