"""Enhanced ticket create command with custom fields support."""

import json
import sys
from typing import Any, Dict, Optional

import click
import typer
from click import Context
from gira.utils.console import console
from gira.models import ProjectConfig, Ticket
from gira.models.ticket import TicketPriority, TicketType
from gira.utils.config import get_default_reporter
from gira.utils.custom_fields import (
    extract_custom_fields_from_kwargs,
    validate_and_merge_custom_fields,
)
from gira.utils.editor import launch_editor
from gira.utils.epic_utils import add_ticket_to_epic
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, validate_bulk_items, process_bulk_operation
from gira.utils.ticket_creation import (
    determine_initial_status,
    validate_ticket_fields,
    resolve_assignee,
    parse_labels,
    create_ticket_dict,
)

@click.command()
@click.argument("title", required=False)
@click.option("--description", "-d", default="", help="Ticket description (use '-' for stdin, 'editor' to open editor)")
@click.option("--description-file", help="Read description from a file")
@click.option("--priority", "-p", default="medium", help="Priority level")
@click.option("--assignee", "-a", help="Assignee")
@click.option("--type", "-t", "ticket_type", default="task", help="Ticket type")
@click.option("--labels", "-l", help="Comma-separated labels")
@click.option("--epic", "-e", help="Epic ID")
@click.option("--parent", help="Parent ticket ID for subtasks")
@click.option("--story-points", "-sp", type=int, help="Story points estimate")
@click.option("--status", "-s", help="Initial status (e.g., backlog, todo, in_progress)")
@click.option("--output", "-o", default="text", help="Output format: text, json")
@click.option("--quiet", "-q", is_flag=True, help="Only output ticket ID")
@click.option("--strict", is_flag=True, help="Enforce strict assignee validation (no external assignees)")
@click.option("--stdin", is_flag=True, help="Read JSON array of tickets from stdin for bulk creation")
@click.option("--jsonl", is_flag=True, help="Read JSONL (JSON Lines) format for streaming large datasets")
@click.option("--csv", is_flag=True, help="Read CSV format from stdin for bulk creation")
@click.option("--csv-delimiter", default=",", help="CSV delimiter character (default: comma)")
@click.option("--skip-invalid", is_flag=True, help="Skip invalid rows and continue processing")
@click.option("--fail-on-error/--no-fail-on-error", default=True, help="Exit with error if any row fails (default: true)")
@click.pass_context
def create_with_custom_fields(ctx: Context, **kwargs: Any) -> None:
    """Create a new ticket with custom fields support."""
    # Extract standard arguments
    title = kwargs.pop("title")
    description = kwargs.pop("description")
    description_file = kwargs.pop("description_file")
    priority = kwargs.pop("priority")
    assignee = kwargs.pop("assignee")
    ticket_type = kwargs.pop("ticket_type")
    labels = kwargs.pop("labels")
    epic = kwargs.pop("epic")
    parent = kwargs.pop("parent")
    story_points = kwargs.pop("story_points")
    status = kwargs.pop("status")
    output = kwargs.pop("output")
    quiet = kwargs.pop("quiet")
    strict = kwargs.pop("strict")
    stdin = kwargs.pop("stdin")
    jsonl = kwargs.pop("jsonl")
    csv = kwargs.pop("csv")
    csv_delimiter = kwargs.pop("csv_delimiter")
    skip_invalid = kwargs.pop("skip_invalid")
    fail_on_error = kwargs.pop("fail_on_error")
    
    # Get project config
    project_root = ensure_gira_project()
    config = ProjectConfig.load_from_path(project_root)
    
    # Extract custom fields from remaining kwargs
    custom_fields, unknown_kwargs = extract_custom_fields_from_kwargs(
        config, "ticket", kwargs
    )
    
    # If there are unknown kwargs, they might be from the dynamic options
    # that weren't properly registered, so we should check them
    for key, value in unknown_kwargs.items():
        if key.startswith("cf_") and value is not None:
            # This is a custom field that wasn't extracted properly
            field_name = key[3:].replace("_", "-")
            custom_fields[field_name] = value
    
    # Handle bulk creation
    if stdin or jsonl or csv:
        reader = StdinReader(
            stdin=stdin,
            jsonl=jsonl,
            csv=csv,
            csv_delimiter=csv_delimiter,
            skip_invalid=skip_invalid,
            fail_on_error=fail_on_error
        )
        
        items = reader.read()
        
        # For CSV, validate headers
        if csv and reader.headers:
            # Map CSV headers to field names
            custom_field_mappings = {}
            for field in config.custom_fields.fields:
                csv_header = f"cf_{field.name}"
                if csv_header in reader.headers:
                    custom_field_mappings[csv_header] = field.name
        
        # Process bulk items
        def process_item(item: Dict[str, Any]) -> Ticket:
            # Extract custom fields from item
            item_custom_fields = {}
            if csv and reader.headers:
                # Handle CSV custom fields
                for csv_header, field_name in custom_field_mappings.items():
                    if csv_header in item and item[csv_header]:
                        item_custom_fields[field_name] = item.pop(csv_header)
            else:
                # Handle JSON custom fields
                item_custom_fields = item.pop("custom_fields", {})
            
            # Validate custom fields
            validated_custom_fields = validate_and_merge_custom_fields(
                config, "ticket", item_custom_fields
            )
            
            # Create ticket with custom fields
            ticket_data = create_ticket_dict(
                config=config,
                title=item.get("title"),
                description=item.get("description", ""),
                ticket_type=item.get("type", "task"),
                priority=item.get("priority", "medium"),
                labels=parse_labels(item.get("labels")),
                assignee=resolve_assignee(item.get("assignee"), strict),
                reporter=item.get("reporter", get_default_reporter()),
                epic_id=item.get("epic"),
                parent_id=item.get("parent"),
                story_points=item.get("story_points"),
                status=determine_initial_status(config, item.get("status"))
            )
            
            # Add custom fields
            ticket_data["custom_fields"] = validated_custom_fields
            
            return Ticket(**ticket_data)
        
        results = process_bulk_operation(
            items=items,
            process_func=process_item,
            output_format=output,
            quiet=quiet,
            operation_name="ticket creation"
        )
        
        if output == "json":
            console.print_json(json.dumps(results, indent=2))
        
        return
    
    # Single ticket creation
    if not title:
        console.print("[red]Error: Title is required (provide as argument or use --stdin)[/red]")
        raise typer.Exit(1)
    
    # Handle description input
    if description == "-":
        description = sys.stdin.read().strip()
    elif description == "editor":
        description = launch_editor("", suffix=".md") or ""
    elif description_file:
        try:
            with open(description_file, "r") as f:
                description = f.read().strip()
        except Exception as e:
            console.print(f"[red]Error reading description file: {e}[/red]")
            raise typer.Exit(1)
    
    # Validate ticket fields
    try:
        validate_ticket_fields(
            config=config,
            ticket_type=ticket_type,
            priority=priority,
            status=status
        )
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    
    # Validate custom fields
    try:
        validated_custom_fields = validate_and_merge_custom_fields(
            config, "ticket", custom_fields
        )
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    
    # Create ticket
    ticket_data = create_ticket_dict(
        config=config,
        title=title,
        description=description,
        ticket_type=ticket_type,
        priority=priority,
        labels=parse_labels(labels),
        assignee=resolve_assignee(assignee, strict),
        reporter=get_default_reporter(),
        epic_id=epic,
        parent_id=parent,
        story_points=story_points,
        status=determine_initial_status(config, status)
    )
    
    # Add custom fields
    ticket_data["custom_fields"] = validated_custom_fields
    
    # Create and save ticket
    ticket = Ticket(**ticket_data)
    ticket.save()
    
    # Add to epic if specified
    if epic:
        add_ticket_to_epic(ticket.id, epic)
    
    # Output
    if quiet:
        console.print(ticket.id)
    elif output == "json":
        console.print_json(ticket.model_dump_json(indent=2))
    else:
        console.print(f"[green]✅ Created ticket {ticket.id}: {ticket.title}[/green]")
        if validated_custom_fields:
            console.print("\nCustom Fields:")
            for name, value in validated_custom_fields.items():
                field_def = config.custom_fields.get_field_by_name(name)
                display_name = field_def.display_name if field_def else name
                console.print(f"  {display_name}: {value}")


def create_dynamic_command() -> click.Command:
    """Create a dynamic command with custom field options."""
    # Create base command
    cmd = create_with_custom_fields
    
    # Try to load config and add custom field options
    try:
        project_root = ensure_gira_project()
        config = ProjectConfig.load_from_path(project_root)
        
        # Get applicable custom fields for tickets
        applicable_fields = config.custom_fields.get_fields_for_entity("ticket")
        
        # Add an option for each custom field
        for field in applicable_fields:
            option_name = f"--{field.get_cli_option_name()}"
            param_name = field.get_cli_option_name().replace("-", "_")
            
            # Create the option
            option = click.Option(
                [option_name],
                param_name,
                help=field.get_cli_help_text(),
                required=False,
                default=None,
            )
            
            # Add to command params
            cmd.params.append(option)
    
    except Exception:
        # If we can't load config, just return the base command
        pass
    
    return cmd