"""Create ticket command for Gira."""

import json
import sys
from typing import List, Optional

import typer
from gira.utils.console import console
from gira.models import ProjectConfig, Ticket
from gira.models.ticket import TicketPriority, TicketType
from gira.utils.config import get_default_reporter
from gira.utils.editor import launch_editor
from gira.utils.epic_utils import add_ticket_to_epic
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, validate_bulk_items, process_bulk_operation
from gira.utils.ticket_creation import (
    determine_initial_status,
    validate_ticket_fields,
    resolve_assignee,
    parse_labels,
    create_ticket_dict
)
from gira.utils.custom_fields import (
    parse_custom_field_value,
    validate_and_merge_custom_fields,
)
from gira.utils.hooks import execute_hook, build_ticket_event_data
from gira.utils.ticket_utils import find_ticket, _would_create_parent_cycle

def create(
    title: Optional[str] = typer.Argument(None, help="Ticket title (required unless using --stdin)"),
    description: str = typer.Option("", "--description", "-d", help="Ticket description (use '-' for stdin, 'editor' to open editor)"),
    description_file: Optional[str] = typer.Option(None, "--description-file", help="Read description from a file"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priority level"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Assignee"),
    ticket_type: str = typer.Option("task", "--type", "-t", help="Ticket type"),
    labels: Optional[str] = typer.Option(None, "--labels", "-l", help="Comma-separated labels"),
    epic: Optional[str] = typer.Option(None, "--epic", "-e", help="Epic ID"),
    parent: Optional[str] = typer.Option(None, "--parent", help="Parent ticket ID for subtasks"),
    story_points: Optional[int] = typer.Option(None, "--story-points", "-sp", help="Story points estimate"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Initial status (e.g., backlog, todo, in_progress)"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket ID"),
    strict: bool = typer.Option(False, "--strict", help="Enforce strict assignee validation (no external assignees)"),
    stdin: bool = typer.Option(False, "--stdin", help="Read JSON array of tickets from stdin for bulk creation"),
    jsonl: bool = typer.Option(False, "--jsonl", help="Read JSONL (JSON Lines) format for streaming large datasets"),
    csv: bool = typer.Option(False, "--csv", help="Read CSV format from stdin for bulk creation"),
    csv_delimiter: str = typer.Option(",", "--csv-delimiter", help="CSV delimiter character (default: comma)"),
    skip_invalid: bool = typer.Option(False, "--skip-invalid", help="Skip invalid rows and continue processing"),
    fail_on_error: bool = typer.Option(True, "--fail-on-error/--no-fail-on-error", help="Exit with error if any row fails (default: true)"),
    custom_field: Optional[List[str]] = typer.Option(None, "--cf", help="Custom field value in format 'name=value' (can be used multiple times)"),
) -> None:
    """Create a new ticket."""
    root = ensure_gira_project()

    # Handle stdin bulk creation
    if stdin:
        return _create_bulk_from_stdin(root, output, quiet, strict, jsonl, status, csv, csv_delimiter, skip_invalid, fail_on_error)
    
    # Check if jsonl or csv is used without stdin
    if jsonl:
        console.print("[red]Error:[/red] --jsonl requires --stdin")
        raise typer.Exit(1)
    
    if csv:
        console.print("[red]Error:[/red] --csv requires --stdin")
        raise typer.Exit(1)

    # Validate title is provided for single ticket creation
    if title is None:
        console.print("[red]Error:[/red] Title is required when not using --stdin")
        raise typer.Exit(1)

    # Check for mutually exclusive description options
    if description and description not in ["", "-", "editor"] and description_file:
        console.print("[red]Error:[/red] Cannot use both --description and --description-file")
        raise typer.Exit(1)

    # Handle description input methods
    if description_file:
        # Read description from file
        from pathlib import Path
        try:
            file_path = Path(description_file)
            if not file_path.exists():
                console.print(f"[red]Error:[/red] File not found: {description_file}")
                raise typer.Exit(1)
            
            # Read the file with UTF-8 encoding, handling different encodings gracefully
            try:
                description = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with latin-1 as fallback
                try:
                    description = file_path.read_text(encoding='latin-1')
                    console.print("[yellow]Warning:[/yellow] File was read with latin-1 encoding")
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to read file: {e}")
                    raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to read description file: {e}")
            raise typer.Exit(1)
    elif description == "editor":
        # Open editor for description
        instructions = (
            "Enter the ticket description below.\n"
            "Lines starting with # will be ignored.\n"
            "Save and exit to create the ticket, or exit without saving to cancel."
        )
        editor_content = launch_editor(
            initial_content="",
            instructions=instructions
        )
        if editor_content is None:
            console.print("[yellow]Cancelled:[/yellow] No description provided")
            raise typer.Exit(1)
        description = editor_content
    elif description == "-":
        # Read from stdin
        description = sys.stdin.read().strip()

    # Load project config to get ticket prefix and validate options
    config_path = root / ".gira" / "config.json"
    config = ProjectConfig.from_json_file(str(config_path))

    # Load state to get next ticket number
    state_path = root / ".gira" / ".state.json"
    with open(state_path) as f:
        state = json.load(f)
    
    # Determine initial status
    initial_status = determine_initial_status(status, config, root)

    # Generate ticket ID
    ticket_id = f"{config.ticket_id_prefix}-{state['next_ticket_number']}"

    # Validate ticket fields
    validation_errors = validate_ticket_fields(ticket_type, priority, initial_status, story_points)
    if validation_errors:
        for error in validation_errors:
            console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(1)

    # Get reporter from git config or gira config
    reporter = get_default_reporter()

    # Parse labels
    label_list = parse_labels(labels)

    # Use ticket type directly (now that model supports feature/subtask)
    model_type = ticket_type.lower()

    # Resolve assignee
    try:
        resolved_assignee, warnings = resolve_assignee(assignee, root, strict)
        for warning in warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Parse custom fields
    custom_fields_dict = {}
    fields_to_save = []  # Track new field definitions to save
    
    # Handle case where custom_field might be OptionInfo object in tests  
    if custom_field and not isinstance(custom_field, (type(None), list)) and hasattr(custom_field, '__class__') and 'OptionInfo' in str(type(custom_field)):
        custom_field = None
    
    if custom_field:
        from gira.utils.interactive_custom_fields import handle_undefined_custom_field, save_field_to_config
        
        for cf in custom_field:
            if '=' not in cf:
                console.print(f"[red]Error:[/red] Invalid custom field format: {cf}")
                console.print("Custom fields must be in format: --cf name=value")
                raise typer.Exit(1)
            
            name, value = cf.split('=', 1)
            name = name.strip()
            value = value.strip()
            
            # Get field definition
            field_def = config.custom_fields.get_field_by_name(name)
            if not field_def:
                # Handle undefined field interactively
                field_def, should_save = handle_undefined_custom_field(
                    name, value, config, "ticket", non_interactive=False
                )
                
                if field_def is None:
                    # User cancelled
                    console.print("[yellow]Creation cancelled[/yellow]")
                    raise typer.Exit(0)
                
                if should_save:
                    fields_to_save.append(field_def)
            
            # Parse the value
            try:
                parsed_value = parse_custom_field_value(field_def, value)
                custom_fields_dict[name] = parsed_value
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)
        
        # Save any new field definitions
        if fields_to_save:
            for field_def in fields_to_save:
                save_field_to_config(field_def, config_path)
                
            # Reload config to include new fields
            config = ProjectConfig.from_json_file(str(config_path))
    
    # For validation, we need to separate defined fields from one-time fields
    defined_fields = {}
    one_time_fields = {}
    
    for name, value in custom_fields_dict.items():
        if config.custom_fields.get_field_by_name(name):
            defined_fields[name] = value
        else:
            # This is a one-time field
            one_time_fields[name] = value
    
    # Validate only the defined fields
    try:
        validated_defined_fields = validate_and_merge_custom_fields(
            config, "ticket", defined_fields
        )
        # Combine validated defined fields with one-time fields
        validated_custom_fields = {**validated_defined_fields, **one_time_fields}
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Validate parent relationship
    validated_parent = None
    if parent:
        normalized_parent = parent.upper()
        
        # Check if the proposed parent exists
        parent_ticket, _ = find_ticket(normalized_parent, root)
        if not parent_ticket:
            console.print(f"[red]Error:[/red] Parent ticket {normalized_parent} not found")
            raise typer.Exit(1)
        
        # Check for circular dependency (though this is a new ticket, 
        # the parent could theoretically have this ticket as an ancestor if there's an existing cycle)
        if _would_create_parent_cycle(ticket_id, normalized_parent, root):
            console.print(f"[red]Error:[/red] Cannot set {normalized_parent} as parent of {ticket_id}: this would create a circular parent-child dependency")
            raise typer.Exit(1)
        
        validated_parent = normalized_parent

    # Create ticket
    try:
        ticket = Ticket(
            id=ticket_id,
            title=title,
            description=description,
            status=initial_status,  # Use determined initial status
            priority=TicketPriority(priority.lower()),
            type=TicketType(model_type),
            reporter=reporter,
            assignee=resolved_assignee,
            labels=label_list,
            epic_id=epic,
            parent_id=validated_parent,
            story_points=story_points,
            custom_fields=validated_custom_fields,
        )

        # Save ticket to appropriate directory based on initial status
        ticket_path = root / ".gira" / "board" / initial_status / f"{ticket_id}.json"
        ticket_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        ticket.save_to_json_file(str(ticket_path))

        # Execute ticket-created hook
        execute_hook("ticket-created", build_ticket_event_data(ticket))
        
        # Execute webhook for ticket creation
        from gira.utils.hooks import execute_webhook_for_ticket_created
        execute_webhook_for_ticket_created(ticket)

        # Sync epic-ticket relationship if epic is specified
        if epic:
            if not add_ticket_to_epic(ticket_id, epic.upper(), root):
                console.print(f"[yellow]Warning:[/yellow] Epic {epic.upper()} not found, but ticket created with epic_id")

        # Update state
        state['next_ticket_number'] += 1
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)

        # Output result
        if quiet:
            console.print(ticket_id)
        elif output == "json":
            console.print_json(ticket.model_dump_json())
        else:
            console.print(f"✅ Created ticket [cyan]{ticket_id}[/cyan]: {title}")
            if description:
                console.print(f"   Description: {description[:50]}{'...' if len(description) > 50 else ''}")
            console.print(f"   Status: [yellow]{initial_status.replace('_', ' ').title()}[/yellow]")
            console.print(f"   Priority: [magenta]{priority.title()}[/magenta]")
            console.print(f"   Type: [blue]{ticket_type.title()}[/blue]")
            if resolved_assignee:
                # Show display name if available
                from gira.utils.team_utils import format_assignee_display
                display_name = format_assignee_display(resolved_assignee, root)
                console.print(f"   Assignee: [green]{display_name}[/green]")
            if labels:
                console.print(f"   Labels: {labels}")
            if validated_custom_fields:
                console.print("   Custom Fields:")
                for name, value in validated_custom_fields.items():
                    field_def = config.custom_fields.get_field_by_name(name)
                    display_name = field_def.display_name if field_def else name
                    console.print(f"     - {display_name}: {value}")

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to create ticket: {e}")
        raise typer.Exit(1) from e


def _create_bulk_from_stdin(root, output: str, quiet: bool, strict: bool, jsonl: bool = False, 
                           default_status: Optional[str] = None, csv_format: bool = False, 
                           csv_delimiter: str = ",", skip_invalid: bool = False, 
                           fail_on_error: bool = True) -> None:
    """Create multiple tickets from stdin input (JSON/JSONL/CSV)."""
    # Check for conflicting format options
    if sum([jsonl, csv_format]) > 1:
        console.print("[red]Error:[/red] Cannot use multiple format options (--jsonl, --csv) together")
        raise typer.Exit(1)
    
    # Read and validate stdin
    stdin_reader = StdinReader()
    
    if not stdin_reader.is_available():
        console.print("[red]Error:[/red] No data available on stdin")
        raise typer.Exit(1)
    
    try:
        if csv_format:
            # Read CSV format
            from gira.utils.csv_utils import CSVReader
            csv_reader = CSVReader(stdin_reader.stream, delimiter=csv_delimiter)
            items = csv_reader.read_csv_dicts()
        elif jsonl:
            # Read JSONL format
            items = list(stdin_reader.read_json_lines())
        else:
            # Read JSON array format
            items = stdin_reader.read_json_array()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    if not items:
        console.print("[yellow]Warning:[/yellow] No items to process")
        return
    
    # Validate bulk items
    required_fields = ["title"]
    optional_fields = [
        "description", "priority", "assignee", "type", "labels", 
        "epic", "parent", "story_points", "status", "custom_fields"
    ]
    
    validation_errors = validate_bulk_items(items, required_fields, optional_fields)
    if validation_errors and not skip_invalid:
        console.print("[red]Validation errors:[/red]")
        for error in validation_errors:
            console.print(f"  - {error}")
        raise typer.Exit(1)
    elif validation_errors and skip_invalid:
        console.print(f"[yellow]Warning:[/yellow] Found {len(validation_errors)} validation errors. Continuing with --skip-invalid...")
    
    # Load project config and state once
    config_path = root / ".gira" / "config.json"
    config = ProjectConfig.from_json_file(str(config_path))
    
    state_path = root / ".gira" / ".state.json"
    with open(state_path) as f:
        state = json.load(f)
    
    # Process bulk creation
    def create_single_ticket(item):
        return _create_single_ticket_from_dict(item, root, config, state, strict, default_status)
    
    result = process_bulk_operation(
        items, 
        create_single_ticket,
        "ticket creation",
        show_progress=not quiet and len(items) > 1
    )
    
    # Save updated state
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    # Output results
    if output == "json":
        console.print_json(json.dumps(result.to_dict(), indent=2))
    elif quiet:
        # Output only successful ticket IDs
        for success in result.successful:
            console.print(success["result"]["id"])
    else:
        result.print_summary("ticket creation")
        
        # Show successful tickets
        if result.successful and len(result.successful) <= 10:
            console.print("\n✅ **Created Tickets:**")
            for success in result.successful:
                ticket_data = success["result"]
                console.print(f"  - [cyan]{ticket_data['id']}[/cyan]: {ticket_data['title']}")
        elif result.successful:
            console.print(f"\n✅ Created {len(result.successful)} tickets")
    
    # Exit with error code if any failures and fail_on_error is True
    if result.failure_count > 0 and fail_on_error:
        raise typer.Exit(1)


def _create_single_ticket_from_dict(item, root, config, state, strict, default_status=None):
    """Create a single ticket from dictionary data."""
    from gira.utils.config import get_default_reporter
    
    # Extract and validate values
    title = item["title"]
    description = item.get("description", "")
    priority = item.get("priority", "medium").lower()
    assignee = item.get("assignee")
    ticket_type = item.get("type", "task").lower()
    labels_str = item.get("labels")
    epic = item.get("epic")
    parent = item.get("parent")
    story_points = item.get("story_points")
    status = item.get("status", default_status)
    
    # Determine initial status
    initial_status = determine_initial_status(status, config, root)
    
    # Validate all fields
    validation_errors = validate_ticket_fields(ticket_type, priority, initial_status, story_points)
    if validation_errors:
        # Join all errors into a single message for bulk operation
        raise ValueError("; ".join(validation_errors))
    
    # Generate ticket ID
    ticket_id = f"{config.ticket_id_prefix}-{state['next_ticket_number']}"
    state['next_ticket_number'] += 1
    
    # Get reporter
    reporter = get_default_reporter()
    
    # Parse labels
    label_list = parse_labels(labels_str)
    
    # Resolve assignee
    resolved_assignee, warnings = resolve_assignee(assignee, root, strict)
    # Note: warnings are not shown in bulk mode to avoid spam
    
    # Handle custom fields
    custom_fields_dict = item.get("custom_fields", {})
    
    # For validation, we need to separate defined fields from one-time fields
    defined_fields = {}
    one_time_fields = {}
    
    for name, value in custom_fields_dict.items():
        if config.custom_fields.get_field_by_name(name):
            defined_fields[name] = value
        else:
            # This is a one-time field
            one_time_fields[name] = value
    
    try:
        validated_defined_fields = validate_and_merge_custom_fields(
            config, "ticket", defined_fields
        )
        # Combine validated defined fields with one-time fields
        validated_custom_fields = {**validated_defined_fields, **one_time_fields}
    except ValueError as e:
        raise ValueError(f"Custom fields error: {e}")
    
    # Validate parent relationship
    validated_parent = None
    if parent:
        normalized_parent = parent.upper()
        
        # Check if the proposed parent exists
        parent_ticket, _ = find_ticket(normalized_parent, root)
        if not parent_ticket:
            raise ValueError(f"Parent ticket {normalized_parent} not found")
        
        # Check for circular dependency
        if _would_create_parent_cycle(ticket_id, normalized_parent, root):
            raise ValueError(f"Cannot set {normalized_parent} as parent of {ticket_id}: this would create a circular parent-child dependency")
        
        validated_parent = normalized_parent
    
    # Create ticket
    ticket = Ticket(
        id=ticket_id,
        title=title,
        description=description,
        status=initial_status,
        priority=TicketPriority(priority),
        type=TicketType(ticket_type),
        reporter=reporter,
        assignee=resolved_assignee,
        labels=label_list,
        epic_id=epic,
        parent_id=validated_parent,
        story_points=story_points,
        custom_fields=validated_custom_fields,
    )
    
    # Save ticket
    ticket_path = root / ".gira" / "board" / initial_status / f"{ticket_id}.json"
    ticket_path.parent.mkdir(parents=True, exist_ok=True)
    ticket.save_to_json_file(str(ticket_path))
    
    # Execute ticket-created hook
    execute_hook("ticket-created", build_ticket_event_data(ticket), silent=True)
    
    # Execute webhook for ticket creation
    from gira.utils.hooks import execute_webhook_for_ticket_created
    execute_webhook_for_ticket_created(ticket)
    
    # Sync epic-ticket relationship if epic is specified
    if epic:
        if not add_ticket_to_epic(ticket_id, epic.upper(), root):
            # Note: We don't fail here, just warn in the result
            pass
    
    return create_ticket_dict(ticket, initial_status)
