"""Update ticket command for Gira."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import typer
from rich.prompt import Confirm
from rich.table import Table
from gira.utils.console import console
from gira.constants import (
    VALID_PRIORITIES,
    VALID_TYPES,
    normalize_status,
)
from gira.models.ticket import TicketPriority, TicketType
from gira.utils.board_config import get_board_configuration
from gira.utils.editor import launch_editor
from gira.utils.epic_utils import sync_epic_ticket_relationship
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, validate_bulk_items, process_bulk_operation
from gira.utils.team_utils import find_assignee
from gira.utils.ticket_utils import find_ticket, get_ticket_path, _would_create_parent_cycle
from gira.utils.custom_fields import (
    parse_custom_field_value,
    validate_and_merge_custom_fields,
)
from gira.utils.hooks import execute_hook, build_ticket_event_data
from gira.utils.help_formatter import create_example, format_examples_simple
from gira.utils.typer_completion import complete_ticket_ids, complete_status_values, complete_priority_values, complete_type_values, complete_epic_ids, complete_sprint_ids

def update(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to update (supports patterns like 'GCM-1*', ranges like 'GCM-1..10', use '-' to read IDs from stdin, or omit for --stdin JSON)", autocompletion=complete_ticket_ids),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description (use '-' for stdin, 'editor' to open editor)"),
    description_file: Optional[str] = typer.Option(None, "--description-file", help="Read description from a file"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status", autocompletion=complete_status_values),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="New priority", autocompletion=complete_priority_values),
    ticket_type: Optional[str] = typer.Option(None, "--type", help="New ticket type", autocompletion=complete_type_values),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="New assignee (use 'none' to clear)"),
    add_labels: Optional[str] = typer.Option(None, "--add-labels", help="Labels to add (comma-separated)"),
    remove_labels: Optional[str] = typer.Option(None, "--remove-labels", help="Labels to remove (comma-separated)"),
    epic: Optional[str] = typer.Option(None, "--epic", "-e", help="New epic ID (use 'none' to clear)", autocompletion=complete_epic_ids),
    parent: Optional[str] = typer.Option(None, "--parent", help="New parent ID (use 'none' to clear)", autocompletion=complete_ticket_ids),
    sprint: Optional[str] = typer.Option(None, "--sprint", help="Sprint ID to assign ticket to (use 'current' for active sprint, 'none' to clear)", autocompletion=complete_sprint_ids),
    story_points: Optional[int] = typer.Option(None, "--story-points", "-sp", help="New story points estimate (use 0 to clear)"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket ID"),
    strict: bool = typer.Option(False, "--strict", help="Enforce strict assignee validation (no external assignees)"),
    stdin: bool = typer.Option(False, "--stdin", help="Read JSON array of ticket updates from stdin"),
    jsonl: bool = typer.Option(False, "--jsonl", help="Read JSONL (JSON Lines) format for streaming large datasets"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without saving them"),
    force: bool = typer.Option(False, "--force", "-f", help="Legacy option (confirmation removed for AI-friendliness)"),
    custom_field: Optional[List[str]] = typer.Option(None, "--cf", help="Update custom field value in format 'name=value' (can be used multiple times)"),
    remove_custom_field: Optional[List[str]] = typer.Option(None, "--remove-cf", help="Remove custom field by name (can be used multiple times)"),
) -> None:
    """Update one or more tickets.
    
    Supports updating single tickets, multiple tickets, or tickets matching patterns.
    
    Pattern Support:
        - Wildcards: GCM-1* matches GCM-10, GCM-11, etc.
        - Ranges: GCM-1..10 matches GCM-1 through GCM-10
        - Multiple IDs: GCM-1 GCM-2 GCM-3
    
    Multiple Ticket Mode:
        - AI-friendly: No confirmation required by default
        - Shows preview for 5+ tickets or when using --dry-run
        - Some options incompatible: --description-file, 'editor' description, stdin description
    
    Examples:
        gira ticket update GCM-123 --status done --priority high
        gira ticket update GCM-1 GCM-2 GCM-3 --assignee alice --priority medium
        gira ticket update "GCM-1*" --add-labels "urgent" --sprint SPRINT-2025-07-30
        gira ticket update "GCM-1..10" --status "in progress" --assignee bob
        gira ticket update GCM-1 GCM-2 --status done
        gira ticket update "GCM-1*" --priority high --dry-run
        echo "GCM-1\\nGCM-2" | gira ticket update - --status done
        gira ticket update --stdin < updates.json
    """
    root = ensure_gira_project()
    
    # Handle bulk operations
    if stdin:
        if ticket_ids is not None:
            console.print("[red]Error:[/red] Cannot specify ticket IDs when using --stdin")
            raise typer.Exit(1)
        
        _update_bulk_from_stdin(
            root, title, description, status, priority, ticket_type,
            assignee, add_labels, remove_labels, epic, parent, sprint, story_points,
            output, quiet, strict, jsonl
        )
        return
    
    # Handle ticket ID collection and expansion
    all_ticket_ids = []
    
    # Check if we should read ticket IDs from stdin
    if ticket_ids and len(ticket_ids) == 1 and ticket_ids[0] == "-":
        # Explicitly requested stdin with "-"
        return _update_bulk_tickets_from_stdin(
            root, title, description, status, priority, ticket_type,
            assignee, add_labels, remove_labels, epic, parent, sprint, story_points,
            output, quiet, strict
        )
    
    # Expand ticket ID patterns
    if ticket_ids:
        for ticket_id_pattern in ticket_ids:
            expanded = _expand_ticket_pattern(root, ticket_id_pattern)
            all_ticket_ids.extend(expanded)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ticket_ids = []
    for ticket_id in all_ticket_ids:
        if ticket_id not in seen:
            seen.add(ticket_id)
            unique_ticket_ids.append(ticket_id)
    all_ticket_ids = unique_ticket_ids
    
    # Validate we have tickets to update
    if not all_ticket_ids:
        console.print("[red]Error:[/red] No ticket IDs specified (or use --stdin for bulk updates)")
        raise typer.Exit(1)

    # Single ticket path for backward compatibility  
    if len(all_ticket_ids) == 1:
        ticket_id = all_ticket_ids[0]
    
        # Find the ticket
        ticket, ticket_path = find_ticket(ticket_id, root)

        # Handle not found
        if not ticket:
            console.print(f"[red]Error:[/red] Ticket {ticket_id.upper()} not found")
            raise typer.Exit(1)

        # Check if any changes requested
        has_changes = any([
            title is not None,
            description is not None,
            description_file is not None,
            status is not None,
            priority is not None,
            ticket_type is not None,
            assignee is not None,
            add_labels is not None,
            remove_labels is not None,
            epic is not None,
            parent is not None,
            sprint is not None,
            story_points is not None,
            custom_field is not None,
            remove_custom_field is not None
        ])

        if not has_changes:
            if not quiet:
                console.print("No changes to update")
            raise typer.Exit(0)
            
        # Continue with single ticket logic here
    else:
        # Multiple tickets - show preview and get confirmation if not forced
        return _update_multiple_tickets(
            all_ticket_ids, root, title, description, description_file, status, priority, ticket_type,
            assignee, add_labels, remove_labels, epic, parent, sprint, story_points,
            output, quiet, dry_run, force, strict, custom_field, remove_custom_field
        )

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
            "Update the ticket description below.\n"
            "Lines starting with # will be ignored.\n"
            "Save and exit to update, or exit without saving to cancel."
        )
        editor_content = launch_editor(
            initial_content=ticket.description or "",
            instructions=instructions
        )
        if editor_content is None:
            console.print("[yellow]Cancelled:[/yellow] Description not updated")
            description = None  # Don't update
        else:
            description = editor_content
    elif description == "-":
        # Read from stdin
        description = sys.stdin.read().strip()

    # Validate and apply updates
    original_status = ticket.status
    original_epic_id = ticket.epic_id

    # Update fields
    if title is not None:
        ticket.title = title

    if description is not None:
        ticket.description = description

    if status is not None:
        board = get_board_configuration()
        normalized_status = normalize_status(status)
        if not board.is_valid_status(normalized_status):
            valid_statuses = board.get_valid_statuses()
            console.print(f"[red]Error:[/red] Invalid status '{status}'")
            console.print(f"Valid statuses are: {', '.join(valid_statuses)}")
            raise typer.Exit(1)
        ticket.status = normalized_status

    if priority is not None:
        if priority.lower() not in VALID_PRIORITIES:
            console.print(f"[red]Error:[/red] Invalid priority '{priority}'")
            console.print(f"Valid priorities are: {', '.join(VALID_PRIORITIES)}")
            raise typer.Exit(1)
        ticket.priority = TicketPriority(priority.lower())

    if ticket_type is not None:
        if ticket_type.lower() not in VALID_TYPES:
            console.print(f"[red]Error:[/red] Invalid ticket type '{ticket_type}'")
            console.print(f"Valid types are: {', '.join(VALID_TYPES)}")
            raise typer.Exit(1)
        ticket.type = TicketType(ticket_type.lower())

    if assignee is not None:
        if assignee.lower() == "none":
            ticket.assignee = None
        else:
            # Resolve assignee using team.json
            resolved_email, team = find_assignee(assignee, root)
            if resolved_email:
                # Check if this is a known team member or external assignee
                is_team_member = team and team.find_member(assignee) is not None
                if not is_team_member:
                    console.print(f"[yellow]Warning:[/yellow] Unknown assignee '{assignee}'")
                    # Check strict mode or team setting
                    if strict or (team and not team.allow_external_assignees):
                        if strict:
                            console.print("[red]Error:[/red] Unknown assignee not allowed in strict mode. Use 'gira team add' to add team members.")
                        else:
                            console.print("[red]Error:[/red] External assignees not allowed. Use 'gira team add' to add team members.")
                        raise typer.Exit(1)
                ticket.assignee = resolved_email
            else:
                console.print(f"[yellow]Warning:[/yellow] Unknown assignee '{assignee}'")
                console.print("[red]Error:[/red] External assignees not allowed. Use 'gira team add' to add team members.")
                raise typer.Exit(1)

    if add_labels is not None:
        new_labels = [lbl.strip() for lbl in add_labels.split(",") if lbl.strip()]
        for label in new_labels:
            if label.lower() not in [lbl.lower() for lbl in ticket.labels]:
                ticket.labels.append(label.lower())

    if remove_labels is not None:
        labels_to_remove = [lbl.strip().lower() for lbl in remove_labels.split(",") if lbl.strip()]
        ticket.labels = [lbl for lbl in ticket.labels if lbl.lower() not in labels_to_remove]

    if epic is not None:
        if epic.lower() == "none":
            ticket.epic_id = None
        else:
            ticket.epic_id = epic.upper()

    if parent is not None:
        if parent.lower() == "none":
            ticket.parent_id = None
        else:
            normalized_parent = parent.upper()
            
            # Check if the proposed parent exists
            parent_ticket, _ = find_ticket(normalized_parent, root)
            if not parent_ticket:
                console.print(f"[red]Error:[/red] Parent ticket {normalized_parent} not found")
                raise typer.Exit(1)
            
            # Check for circular dependency
            if _would_create_parent_cycle(ticket.id, normalized_parent, root):
                console.print(f"[red]Error:[/red] Cannot set {normalized_parent} as parent of {ticket.id}: this would create a circular parent-child dependency")
                raise typer.Exit(1)
            
            ticket.parent_id = normalized_parent

    if sprint is not None:
        if sprint.lower() == "none":
            ticket.sprint_id = None
        elif sprint.lower() in ["current", "active"]:
            # Get the active sprint
            state_file = root / ".gira" / ".state.json"
            if not state_file.exists():
                console.print("[red]Error:[/red] No active sprint found")
                raise typer.Exit(1)
            
            with open(state_file) as f:
                state = json.load(f)
            
            active_sprint_id = state.get("active_sprint")
            if not active_sprint_id:
                console.print("[red]Error:[/red] No active sprint found")
                raise typer.Exit(1)
            
            # Verify the sprint exists (check in subdirectories)
            sprint_dirs = ["active", "planned", "completed"]
            sprint_file = None
            for subdir in sprint_dirs:
                potential_file = root / ".gira" / "sprints" / subdir / f"{active_sprint_id}.json"
                if potential_file.exists():
                    sprint_file = potential_file
                    break
            
            if not sprint_file:
                console.print(f"[red]Error:[/red] Active sprint {active_sprint_id} not found")
                raise typer.Exit(1)
            
            ticket.sprint_id = active_sprint_id
        else:
            # Direct sprint ID
            sprint_id = sprint.upper() if not sprint.startswith('SPRINT-') else sprint
            # Verify the sprint exists (check in subdirectories)
            sprint_dirs = ["active", "planned", "completed"]
            sprint_file = None
            for subdir in sprint_dirs:
                potential_file = root / ".gira" / "sprints" / subdir / f"{sprint_id}.json"
                if potential_file.exists():
                    sprint_file = potential_file
                    break
            
            if not sprint_file:
                console.print(f"[red]Error:[/red] Sprint {sprint_id} not found")
                raise typer.Exit(1)
            ticket.sprint_id = sprint_id

    if story_points is not None:
        if story_points == 0:
            ticket.story_points = None
        else:
            if not (0 <= story_points <= 100):
                console.print("[red]Error:[/red] Story points must be between 0 and 100")
                raise typer.Exit(1)
            ticket.story_points = story_points

    # Load project config for custom fields
    from gira.models.config import ProjectConfig
    config_path = root / ".gira" / "config.json"
    config = ProjectConfig.from_json_file(str(config_path))
    
    # Handle custom fields
    custom_field_changes = {}
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
                    console.print("[yellow]Update cancelled[/yellow]")
                    raise typer.Exit(0)
                
                if should_save:
                    fields_to_save.append(field_def)
            
            # Parse the value
            try:
                parsed_value = parse_custom_field_value(field_def, value)
                custom_field_changes[name] = parsed_value
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)
        
        # Save any new field definitions
        if fields_to_save:
            for field_def in fields_to_save:
                save_field_to_config(field_def, config_path)
                
            # Reload config to include new fields
            config = ProjectConfig.from_json_file(str(config_path))
    
    # Handle custom field removals
    custom_fields_to_remove = []
    
    # Handle case where remove_custom_field might be OptionInfo object in tests
    if remove_custom_field and not isinstance(remove_custom_field, (type(None), list)) and hasattr(remove_custom_field, '__class__') and 'OptionInfo' in str(type(remove_custom_field)):
        remove_custom_field = None
    
    if remove_custom_field:
        for name in remove_custom_field:
            name = name.strip()
            if name in ticket.custom_fields:
                custom_fields_to_remove.append(name)
            else:
                console.print(f"[yellow]Warning:[/yellow] Custom field '{name}' not found on ticket")
    
    # Apply custom field changes
    if custom_field_changes or custom_fields_to_remove:
        # Start with existing custom fields
        new_custom_fields = ticket.custom_fields.copy()
        
        # Remove fields
        for name in custom_fields_to_remove:
            new_custom_fields.pop(name, None)
        
        # Update/add fields
        new_custom_fields.update(custom_field_changes)
        
        # For validation, we need to separate defined fields from one-time fields
        defined_fields = {}
        one_time_fields = {}
        
        for name, value in new_custom_fields.items():
            if config.custom_fields.get_field_by_name(name):
                defined_fields[name] = value
            else:
                # This is a one-time field or a field from before it was defined
                one_time_fields[name] = value
        
        # Validate only the defined fields
        try:
            validated_defined_fields = validate_and_merge_custom_fields(
                config, "ticket", defined_fields
            )
            # Combine validated defined fields with one-time fields
            ticket.custom_fields = {**validated_defined_fields, **one_time_fields}
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Update timestamp
    ticket.updated_at = datetime.now(timezone.utc)

    # If dry-run, show what would be changed but don't save
    if dry_run:
        console.print("[yellow]DRY RUN:[/yellow] The following changes would be made:")
        console.print(f"\nTicket: [cyan]{ticket.id}[/cyan]")
        
        # Show changes
        changes = []
        if title is not None:
            changes.append(f"  • Title: {title}")
        if description is not None:
            desc_preview = description[:50] + "..." if len(description) > 50 else description
            changes.append(f"  • Description: {desc_preview}")
        if status is not None:
            changes.append(f"  • Status: {original_status} → {ticket.status}")
        if priority is not None:
            changes.append(f"  • Priority: {priority}")
        if ticket_type is not None:
            changes.append(f"  • Type: {ticket_type}")
        if assignee is not None:
            if assignee.lower() == "none":
                changes.append(f"  • Assignee: [cleared]")
            else:
                changes.append(f"  • Assignee: {ticket.assignee}")
        if add_labels is not None:
            changes.append(f"  • Add labels: {', '.join(ticket.labels[-len(add_labels.split(',')):])}") 
        if remove_labels is not None:
            changes.append(f"  • Remove labels: {remove_labels}")
        if epic is not None:
            if epic.lower() == "none":
                changes.append(f"  • Epic: [cleared]")
            else:
                changes.append(f"  • Epic: {ticket.epic_id}")
        if parent is not None:
            if parent.lower() == "none":
                changes.append(f"  • Parent: [cleared]")
            else:
                changes.append(f"  • Parent: {ticket.parent_id}")
        if sprint is not None:
            if sprint.lower() == "none":
                changes.append(f"  • Sprint: [cleared]")
            else:
                changes.append(f"  • Sprint: {ticket.sprint_id}")
        if story_points is not None:
            if story_points == 0:
                changes.append(f"  • Story points: [cleared]")
            else:
                changes.append(f"  • Story points: {story_points}")
        if custom_field_changes:
            for name, value in custom_field_changes.items():
                field_def = config.custom_fields.get_field_by_name(name)
                display_name = field_def.display_name if field_def else name
                changes.append(f"  • Custom field '{display_name}': {value}")
        if custom_fields_to_remove:
            for name in custom_fields_to_remove:
                field_def = config.custom_fields.get_field_by_name(name)
                display_name = field_def.display_name if field_def else name
                changes.append(f"  • Remove custom field: {display_name}")
        
        for change in changes:
            console.print(change)
        
        if status is not None and ticket.status != original_status:
            new_path = get_ticket_path(ticket.id, ticket.status, root)
            console.print(f"\n[dim]File would be moved from:[/dim]")
            console.print(f"  {ticket_path.relative_to(root)}")
            console.print(f"[dim]To:[/dim]")
            console.print(f"  {new_path.relative_to(root)}")
        
        console.print("\n[dim]No changes were made (dry run)[/dim]")
        return

    # Sync epic-ticket relationship if epic was changed
    if epic is not None:
        sync_epic_ticket_relationship(
            ticket_id,
            original_epic_id,
            ticket.epic_id,
            root
        )

    # Handle status change (move file if needed)
    if status is not None and ticket.status != original_status:
        # Get new path based on status
        new_path = get_ticket_path(ticket.id, ticket.status, root)

        # Save to new location
        ticket.save_to_json_file(str(new_path))

        # Remove old file
        if ticket_path != new_path:
            ticket_path.unlink()
    else:
        # Save in place
        ticket.save_to_json_file(str(ticket_path))

    # Output result
    if quiet:
        console.print(ticket.id)
    elif output == "json":
        print(json.dumps(ticket.model_dump(mode='json'), default=str, indent=2))
    else:
        console.print(f"✅ Updated ticket [cyan]{ticket.id}[/cyan]")


def _update_multiple_tickets(
    ticket_ids: List[str], root: Path, title: Optional[str], description: Optional[str], 
    description_file: Optional[str], status: Optional[str], priority: Optional[str], 
    ticket_type: Optional[str], assignee: Optional[str], add_labels: Optional[str], 
    remove_labels: Optional[str], epic: Optional[str], parent: Optional[str], 
    sprint: Optional[str], story_points: Optional[int], output: str, quiet: bool, 
    dry_run: bool, force: bool, strict: bool, custom_field: Optional[List[str]], 
    remove_custom_field: Optional[List[str]]
) -> None:
    """Update multiple tickets with confirmation and preview."""
    
    # Check if any changes requested
    has_changes = any([
        title is not None,
        description is not None,
        status is not None,
        priority is not None,
        ticket_type is not None,
        assignee is not None,
        add_labels is not None,
        remove_labels is not None,
        epic is not None,
        parent is not None,
        sprint is not None,
        story_points is not None,
        custom_field is not None,
        remove_custom_field is not None
    ])

    if not has_changes:
        if not quiet:
            console.print("No changes to update")
        raise typer.Exit(0)
    
    # Validate that tickets exist and collect them
    valid_tickets = []
    missing_tickets = []
    
    for ticket_id in ticket_ids:
        ticket, ticket_path = find_ticket(ticket_id, root)
        if ticket:
            valid_tickets.append((ticket, ticket_path))
        else:
            missing_tickets.append(ticket_id)
    
    if missing_tickets:
        console.print(f"[red]Error:[/red] {len(missing_tickets)} ticket(s) not found:")
        for ticket_id in missing_tickets[:5]:  # Show first 5
            console.print(f"  - {ticket_id}")
        if len(missing_tickets) > 5:
            console.print(f"  ... and {len(missing_tickets) - 5} more")
        raise typer.Exit(1)
    
    # Check for description conflicts that can't be used in bulk mode
    if description == "editor":
        console.print("[red]Error:[/red] Cannot use 'editor' for description in multiple ticket mode")
        raise typer.Exit(1)
    
    if description == "-":
        console.print("[red]Error:[/red] Cannot use stdin for description in multiple ticket mode")
        raise typer.Exit(1)
    
    if description_file:
        console.print("[red]Error:[/red] Cannot use --description-file in multiple ticket mode")
        raise typer.Exit(1)
    
    # Show preview if requested or if many tickets (AI-friendly: no confirmation by default)
    if not quiet and (len(valid_tickets) >= 5 or dry_run):
        _show_update_preview(valid_tickets, title, description, status, priority, ticket_type,
                            assignee, add_labels, remove_labels, epic, parent, sprint, 
                            story_points, custom_field, remove_custom_field)
    
    # Apply updates to all tickets
    if dry_run:
        _show_dry_run_preview_multiple(valid_tickets, title, description, status, priority, 
                                      ticket_type, assignee, add_labels, remove_labels, 
                                      epic, parent, sprint, story_points, custom_field, 
                                      remove_custom_field)
        return
    
    # Process all tickets
    successful_updates = []
    failed_updates = []
    
    for ticket, ticket_path in valid_tickets:
        try:
            # Apply updates using existing helper function
            _apply_ticket_updates(
                ticket, ticket_path, root, strict,
                title=title,
                description=description,
                status=status,
                priority=priority,
                ticket_type=ticket_type,
                assignee=assignee,
                add_labels=add_labels,
                remove_labels=remove_labels,
                epic=epic,
                parent=parent,
                sprint=sprint,
                story_points=story_points
            )
            successful_updates.append(ticket.id)
        except Exception as e:
            failed_updates.append((ticket.id, str(e)))
    
    # Output results
    if output == "json":
        result = {
            "summary": {
                "total": len(ticket_ids),
                "successful": len(successful_updates),
                "failed": len(failed_updates)
            },
            "successful": successful_updates,
            "failed": [{"id": tid, "error": error} for tid, error in failed_updates]
        }
        console.print_json(json.dumps(result, indent=2))
    elif quiet:
        # Output only successful ticket IDs
        for ticket_id in successful_updates:
            console.print(ticket_id)
    else:
        # Show summary
        console.print(f"\n✅ Successfully updated {len(successful_updates)} ticket(s)")
        if failed_updates:
            console.print(f"❌ Failed to update {len(failed_updates)} ticket(s)")
            for ticket_id, error in failed_updates[:3]:  # Show first 3 failures
                console.print(f"  - [red]{ticket_id}[/red]: {error}")
            if len(failed_updates) > 3:
                console.print(f"  ... and {len(failed_updates) - 3} more failures")
    
    # Exit with error code if any failures
    if failed_updates and len(failed_updates) == len(ticket_ids):
        raise typer.Exit(1)


def _show_update_preview(tickets, title, description, status, priority, ticket_type,
                        assignee, add_labels, remove_labels, epic, parent, sprint, 
                        story_points, custom_field, remove_custom_field):
    """Show preview of tickets to be updated and what changes will be made."""
    console.print(f"\n[yellow]About to update {len(tickets)} ticket(s):[/yellow]")
    
    # Show tickets in a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ticket ID", width=12)
    table.add_column("Title", width=40)
    table.add_column("Current Status", width=15)
    
    preview_count = min(10, len(tickets))
    for i, (ticket, _) in enumerate(tickets[:preview_count]):
        table.add_row(
            f"[cyan]{ticket.id}[/cyan]",
            ticket.title[:37] + "..." if len(ticket.title) > 40 else ticket.title,
            ticket.status
        )
    
    if len(tickets) > preview_count:
        table.add_row("...", f"and {len(tickets) - preview_count} more", "...")
    
    console.print(table)
    
    # Show changes that will be applied
    console.print("\n[yellow]Changes to apply:[/yellow]")
    changes = []
    if title is not None:
        changes.append(f"  • Title: {title}")
    if description is not None:
        desc_preview = description[:50] + "..." if len(description) > 50 else description
        changes.append(f"  • Description: {desc_preview}")
    if status is not None:
        changes.append(f"  • Status: → {status}")
    if priority is not None:
        changes.append(f"  • Priority: → {priority}")
    if ticket_type is not None:
        changes.append(f"  • Type: → {ticket_type}")
    if assignee is not None:
        if assignee.lower() == "none":
            changes.append(f"  • Assignee: [cleared]")
        else:
            changes.append(f"  • Assignee: → {assignee}")
    if add_labels is not None:
        changes.append(f"  • Add labels: {add_labels}")
    if remove_labels is not None:
        changes.append(f"  • Remove labels: {remove_labels}")
    if epic is not None:
        if epic.lower() == "none":
            changes.append(f"  • Epic: [cleared]")
        else:
            changes.append(f"  • Epic: → {epic}")
    if parent is not None:
        if parent.lower() == "none":
            changes.append(f"  • Parent: [cleared]")
        else:
            changes.append(f"  • Parent: → {parent}")
    if sprint is not None:
        if sprint.lower() == "none":
            changes.append(f"  • Sprint: [cleared]")
        else:
            changes.append(f"  • Sprint: → {sprint}")
    if story_points is not None:
        if story_points == 0:
            changes.append(f"  • Story points: [cleared]")
        else:
            changes.append(f"  • Story points: → {story_points}")
    if custom_field:
        for cf in custom_field:
            if '=' in cf:
                name, value = cf.split('=', 1)
                changes.append(f"  • Custom field '{name}': → {value}")
    if remove_custom_field:
        for name in remove_custom_field:
            changes.append(f"  • Remove custom field: {name}")
    
    for change in changes:
        console.print(change)


def _show_dry_run_preview_multiple(tickets, title, description, status, priority, ticket_type,
                                  assignee, add_labels, remove_labels, epic, parent, sprint, 
                                  story_points, custom_field, remove_custom_field):
    """Show dry run preview for multiple tickets."""
    console.print("[yellow]DRY RUN:[/yellow] The following changes would be made:")
    
    _show_update_preview(tickets, title, description, status, priority, ticket_type,
                        assignee, add_labels, remove_labels, epic, parent, sprint, 
                        story_points, custom_field, remove_custom_field)
    
    console.print("\n[dim]No changes were made (dry run)[/dim]")


def _update_bulk_from_stdin(
    root, title, description, status, priority, ticket_type,
    assignee, add_labels, remove_labels, epic, parent, sprint, story_points,
    output, quiet, strict, jsonl
):
    """Handle bulk update operations from stdin."""
    reader = StdinReader()
    
    # Check if stdin has data
    if not reader.is_available():
        console.print("[red]Error:[/red] No data provided on stdin")
        raise typer.Exit(1)
    
    # Read items based on format
    try:
        if jsonl:
            # Process JSONL streaming
            items = list(reader.read_json_lines())
        else:
            # Process JSON array
            items = reader.read_json_array()
    except ValueError as e:
        console.print(f"[red]Error parsing input:[/red] {e}")
        raise typer.Exit(1)
    
    if not items:
        console.print("[yellow]Warning:[/yellow] No items to process")
        return
    
    # Validate bulk items
    required_fields = ["id"]  # Only ID is required for updates
    optional_fields = [
        "title", "description", "status", "priority", "type",
        "assignee", "add_labels", "remove_labels", "epic",
        "parent", "sprint", "story_points"
    ]
    
    validation_errors = validate_bulk_items(items, required_fields, optional_fields)
    if validation_errors:
        console.print("[red]Validation errors:[/red]")
        for error in validation_errors:
            console.print(f"  - {error}")
        raise typer.Exit(1)
    
    # Create update function that applies CLI overrides
    def update_single_ticket(item):
        ticket_id = item["id"]
        
        # Find the ticket
        ticket, ticket_path = find_ticket(ticket_id, root)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id.upper()} not found")
        
        # Apply updates from item, with CLI options taking precedence
        update_data = {
            "title": title or item.get("title"),
            "description": description or item.get("description"),
            "status": status or item.get("status"),
            "priority": priority or item.get("priority"),
            "ticket_type": ticket_type or item.get("type"),
            "assignee": assignee or item.get("assignee"),
            "add_labels": add_labels or item.get("add_labels"),
            "remove_labels": remove_labels or item.get("remove_labels"),
            "epic": epic or item.get("epic"),
            "parent": parent or item.get("parent"),
            "sprint": sprint or item.get("sprint"),
            "story_points": story_points if story_points is not None else item.get("story_points")
        }
        
        # Apply the updates
        _apply_ticket_updates(
            ticket, ticket_path, root, strict, **update_data
        )
        
        return {
            "id": ticket.id,
            "title": ticket.title,
            "status": ticket.status
        }
    
    # Process bulk operation
    result = process_bulk_operation(
        items,
        update_single_ticket,
        "ticket update",
        show_progress=not quiet and len(items) > 1
    )
    
    # Output results
    if output == "json":
        console.print_json(json.dumps(result.to_dict(), indent=2))
    elif quiet:
        # Output only successful ticket IDs
        for success in result.successful:
            console.print(success["result"]["id"])
    else:
        result.print_summary("ticket update")
        
        # Show successful updates
        if result.successful and len(result.successful) <= 10:
            console.print("\n✅ **Updated Tickets:**")
            for success in result.successful:
                ticket_data = success["result"]
                console.print(f"  - [cyan]{ticket_data['id']}[/cyan]: {ticket_data['status']}")
        elif result.successful:
            console.print(f"\n✅ Updated {len(result.successful)} tickets")
    
    # Exit with error code if any failures
    if result.failure_count > 0:
        raise typer.Exit(1)


def _apply_ticket_updates(
    ticket, ticket_path, root, strict,
    title=None, description=None, status=None, priority=None,
    ticket_type=None, assignee=None, add_labels=None, remove_labels=None,
    epic=None, parent=None, sprint=None, story_points=None
):
    """Apply updates to a ticket and save it."""
    original_status = ticket.status
    original_epic_id = ticket.epic_id
    
    # Update fields
    if title is not None:
        ticket.title = title
    
    if description is not None:
        ticket.description = description
    
    if status is not None:
        board = get_board_configuration()
        normalized_status = normalize_status(status)
        if not board.is_valid_status(normalized_status):
            valid_statuses = board.get_valid_statuses()
            raise ValueError(f"Invalid status '{status}'. Valid statuses: {', '.join(valid_statuses)}")
        ticket.status = normalized_status
    
    if priority is not None:
        if priority.lower() not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'")
        ticket.priority = TicketPriority(priority.lower())
    
    if ticket_type is not None:
        if ticket_type.lower() not in VALID_TYPES:
            raise ValueError(f"Invalid ticket type '{ticket_type}'")
        ticket.type = TicketType(ticket_type.lower())
    
    if assignee is not None:
        if assignee.lower() == "none":
            ticket.assignee = None
        else:
            # Resolve assignee using team.json
            resolved_email, team = find_assignee(assignee, root)
            if resolved_email:
                # Check if this is a known team member or external assignee
                is_team_member = team and team.find_member(assignee) is not None
                if not is_team_member:
                    # Check strict mode or team setting
                    if strict or (team and not team.allow_external_assignees):
                        raise ValueError(f"Unknown assignee '{assignee}' not allowed")
                ticket.assignee = resolved_email
            else:
                raise ValueError(f"External assignees not allowed")
    
    if add_labels is not None:
        new_labels = [lbl.strip() for lbl in add_labels.split(",") if lbl.strip()]
        for label in new_labels:
            if label.lower() not in [lbl.lower() for lbl in ticket.labels]:
                ticket.labels.append(label.lower())
    
    if remove_labels is not None:
        labels_to_remove = [lbl.strip().lower() for lbl in remove_labels.split(",") if lbl.strip()]
        ticket.labels = [lbl for lbl in ticket.labels if lbl.lower() not in labels_to_remove]
    
    if epic is not None:
        if epic.lower() == "none":
            ticket.epic_id = None
        else:
            ticket.epic_id = epic.upper()
    
    if parent is not None:
        if parent.lower() == "none":
            ticket.parent_id = None
        else:
            normalized_parent = parent.upper()
            
            # Check if the proposed parent exists
            parent_ticket, _ = find_ticket(normalized_parent, root)
            if not parent_ticket:
                raise ValueError(f"Parent ticket {normalized_parent} not found")
            
            # Check for circular dependency
            if _would_create_parent_cycle(ticket.id, normalized_parent, root):
                raise ValueError(f"Cannot set {normalized_parent} as parent of {ticket.id}: this would create a circular parent-child dependency")
            
            ticket.parent_id = normalized_parent
    
    if sprint is not None:
        if sprint.lower() == "none":
            ticket.sprint_id = None
        elif sprint.lower() in ["current", "active"]:
            # Get the active sprint
            state_file = root / ".gira" / ".state.json"
            if not state_file.exists():
                raise ValueError("No active sprint found")
            
            with open(state_file) as f:
                state = json.load(f)
            
            active_sprint_id = state.get("active_sprint")
            if not active_sprint_id:
                raise ValueError("No active sprint found")
            
            # Verify the sprint exists (check in subdirectories)
            sprint_dirs = ["active", "planned", "completed"]
            sprint_file = None
            for subdir in sprint_dirs:
                potential_file = root / ".gira" / "sprints" / subdir / f"{active_sprint_id}.json"
                if potential_file.exists():
                    sprint_file = potential_file
                    break
            
            if not sprint_file:
                raise ValueError(f"Active sprint {active_sprint_id} not found")
            
            ticket.sprint_id = active_sprint_id
        else:
            # Direct sprint ID
            sprint_id = sprint.upper() if not sprint.startswith('SPRINT-') else sprint
            # Verify the sprint exists (check in subdirectories)
            sprint_dirs = ["active", "planned", "completed"]
            sprint_file = None
            for subdir in sprint_dirs:
                potential_file = root / ".gira" / "sprints" / subdir / f"{sprint_id}.json"
                if potential_file.exists():
                    sprint_file = potential_file
                    break
            
            if not sprint_file:
                raise ValueError(f"Sprint {sprint_id} not found")
            ticket.sprint_id = sprint_id
    
    if story_points is not None:
        if story_points == 0:
            ticket.story_points = None
        else:
            if not (0 <= story_points <= 100):
                raise ValueError("Story points must be between 0 and 100")
            ticket.story_points = story_points
    
    # Update timestamp
    ticket.updated_at = datetime.now(timezone.utc)
    
    # Sync epic-ticket relationship if epic was changed
    if epic is not None:
        sync_epic_ticket_relationship(
            ticket.id,
            original_epic_id,
            ticket.epic_id,
            root
        )
    
    # Handle status change (move file if needed)
    if status is not None and ticket.status != original_status:
        # Get new path based on status
        new_path = get_ticket_path(ticket.id, ticket.status, root)
        
        # Save to new location
        ticket.save_to_json_file(str(new_path))
        
        # Execute ticket-updated hook (and ticket-moved if status changed)
        execute_hook("ticket-updated", build_ticket_event_data(ticket), silent=True)
        from gira.utils.hooks import build_ticket_move_event_data
        execute_hook("ticket-moved", build_ticket_move_event_data(ticket, original_status, ticket.status), silent=True)
        
        # Remove old file
        if ticket_path != new_path:
            ticket_path.unlink()
    else:
        # Save in place
        ticket.save_to_json_file(str(ticket_path))
        
        # Execute ticket-updated hook
        execute_hook("ticket-updated", build_ticket_event_data(ticket), silent=True)



def _update_bulk_tickets_from_stdin(root, title, description, status, priority, ticket_type,
                                    assignee, add_labels, remove_labels, epic, parent, sprint, story_points,
                                    output, quiet, strict):
    """Apply the same updates to multiple tickets from stdin (one ticket ID per line)."""
    # Read ticket IDs from stdin using StdinReader
    stdin_reader = StdinReader()
    ticket_ids = stdin_reader.read_lines()
    
    if not ticket_ids:
        console.print("[yellow]Warning:[/yellow] No ticket IDs provided on stdin")
        return
    
    # Check if any changes requested
    has_changes = any([
        title is not None,
        description is not None,
        status is not None,
        priority is not None,
        ticket_type is not None,
        assignee is not None,
        add_labels is not None,
        remove_labels is not None,
        epic is not None,
        parent is not None,
        sprint is not None,
        story_points is not None,
    ])
    
    if not has_changes:
        console.print("[yellow]Warning:[/yellow] No updates specified")
        return
    
    # Convert to format expected by process_bulk_operation
    items = [{"id": ticket_id} for ticket_id in ticket_ids]
    
    # Process bulk update
    def update_single_ticket(item):
        ticket_id = item["id"]
        return _update_single_ticket_by_id(
            ticket_id, root, title, description, status, priority, ticket_type,
            assignee, add_labels, remove_labels, epic, parent, sprint, story_points, strict
        )
    
    result = process_bulk_operation(
        items,
        update_single_ticket,
        "ticket update",
        show_progress=not quiet and len(items) > 1 and output != "json"
    )
    
    # Output results
    if output == "json":
        console.print_json(json.dumps(result.to_dict(), indent=2))
    elif quiet:
        # Output only successfully updated ticket IDs
        for success in result.successful:
            console.print(success["result"]["id"])
    else:
        result.print_summary("ticket update")
        
        # Show successful updates
        if result.successful and len(result.successful) <= 10:
            console.print("\n✅ **Updated Tickets:**")
            for success in result.successful:
                ticket_data = success["result"]
                changes_str = ", ".join(ticket_data.get("changes", []))
                console.print(f"  - [cyan]{ticket_data['id']}[/cyan]: {changes_str}")
        elif result.successful:
            console.print(f"\n✅ Updated {len(result.successful)} tickets")
    
    # Exit with error code if any failures
    if result.failure_count > 0:
        raise typer.Exit(1)


def _update_single_ticket_by_id(ticket_id, root, title, description, status, priority, ticket_type,
                                 assignee, add_labels, remove_labels, epic, parent, sprint, story_points, strict):
    """Update a single ticket by ID and return result data."""
    # Find the ticket
    ticket, ticket_path = find_ticket(ticket_id, root)
    
    if not ticket:
        raise ValueError(f"Ticket {ticket_id} not found")
    
    original_status = ticket.status
    changes = []
    
    # Apply updates
    if title is not None:
        ticket.title = title
        changes.append("title")
    
    if description is not None:
        if description == "editor":
            # Can't use editor in bulk mode
            raise ValueError("Cannot use editor for description in bulk update mode")
        elif description == "-":
            raise ValueError("Cannot use stdin for description in bulk update mode")
        else:
            ticket.description = description
            changes.append("description")
    
    if status is not None:
        board = get_board_configuration()
        normalized_status = normalize_status(status)
        if not board.is_valid_status(normalized_status):
            valid_statuses = board.get_valid_statuses()
            raise ValueError(f"Invalid status '{status}'. Valid statuses: {', '.join(valid_statuses)}")
        ticket.status = normalized_status
        changes.append("status")
    
    if priority is not None:
        if priority.lower() not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Valid priorities: {', '.join(VALID_PRIORITIES)}")
        ticket.priority = TicketPriority(priority.lower())
        changes.append("priority")
    
    if ticket_type is not None:
        if ticket_type.lower() not in VALID_TYPES:
            raise ValueError(f"Invalid ticket type '{ticket_type}'. Valid types: {', '.join(VALID_TYPES)}")
        ticket.type = TicketType(ticket_type.lower())
        changes.append("type")
    
    if assignee is not None:
        if assignee.lower() == "none":
            ticket.assignee = None
            changes.append("assignee (cleared)")
        else:
            resolved_email, team = find_assignee(assignee, root)
            if resolved_email:
                is_team_member = team and team.find_member(assignee) is not None
                if not is_team_member:
                    if strict or (team and not team.allow_external_assignees):
                        raise ValueError(f"Unknown assignee '{assignee}' not allowed")
                ticket.assignee = resolved_email
                changes.append("assignee")
            else:
                raise ValueError(f"Unknown assignee '{assignee}' not allowed")
    
    if add_labels is not None:
        new_labels = [lbl.strip() for lbl in add_labels.split(",") if lbl.strip()]
        for label in new_labels:
            if label not in ticket.labels:
                ticket.labels.append(label)
        if new_labels:
            changes.append(f"added labels: {', '.join(new_labels)}")
    
    if remove_labels is not None:
        labels_to_remove = [lbl.strip() for lbl in remove_labels.split(",") if lbl.strip()]
        ticket.labels = [lbl for lbl in ticket.labels if lbl not in labels_to_remove]
        if labels_to_remove:
            changes.append(f"removed labels: {', '.join(labels_to_remove)}")
    
    if epic is not None:
        if epic.lower() == "none":
            ticket.epic_id = None
            changes.append("epic (cleared)")
        else:
            ticket.epic_id = epic.upper()
            changes.append("epic")
    
    if parent is not None:
        if parent.lower() == "none":
            ticket.parent_id = None
            changes.append("parent (cleared)")
        else:
            normalized_parent = parent.upper()
            
            # Check if the proposed parent exists
            parent_ticket, _ = find_ticket(normalized_parent, root)
            if not parent_ticket:
                raise ValueError(f"Parent ticket {normalized_parent} not found")
            
            # Check for circular dependency
            if _would_create_parent_cycle(ticket.id, normalized_parent, root):
                raise ValueError(f"Cannot set {normalized_parent} as parent of {ticket.id}: this would create a circular parent-child dependency")
            
            ticket.parent_id = normalized_parent
            changes.append("parent")
    
    if sprint is not None:
        if sprint.lower() == "none":
            ticket.sprint_id = None
            changes.append("sprint (cleared)")
        elif sprint.lower() in ["current", "active"]:
            # Get the active sprint
            state_file = root / ".gira" / ".state.json"
            if not state_file.exists():
                raise ValueError("No active sprint found")
            
            with open(state_file) as f:
                state = json.load(f)
            
            active_sprint_id = state.get("active_sprint")
            if not active_sprint_id:
                raise ValueError("No active sprint found")
            
            # Verify the sprint exists (check in subdirectories)
            sprint_dirs = ["active", "planned", "completed"]
            sprint_file = None
            for subdir in sprint_dirs:
                potential_file = root / ".gira" / "sprints" / subdir / f"{active_sprint_id}.json"
                if potential_file.exists():
                    sprint_file = potential_file
                    break
            
            if not sprint_file:
                raise ValueError(f"Active sprint {active_sprint_id} not found")
            
            ticket.sprint_id = active_sprint_id
            changes.append("sprint")
        else:
            # Direct sprint ID
            sprint_id = sprint.upper() if not sprint.startswith('SPRINT-') else sprint
            # Verify the sprint exists (check in subdirectories)
            sprint_dirs = ["active", "planned", "completed"]
            sprint_file = None
            for subdir in sprint_dirs:
                potential_file = root / ".gira" / "sprints" / subdir / f"{sprint_id}.json"
                if potential_file.exists():
                    sprint_file = potential_file
                    break
            
            if not sprint_file:
                raise ValueError(f"Sprint {sprint_id} not found")
            ticket.sprint_id = sprint_id
            changes.append("sprint")
    
    if story_points is not None:
        if story_points == 0:
            ticket.story_points = None
            changes.append("story_points (cleared)")
        else:
            if not (0 <= story_points <= 100):
                raise ValueError("Story points must be between 0 and 100")
            ticket.story_points = story_points
            changes.append("story_points")
    
    # Update timestamp
    ticket.updated_at = datetime.now(timezone.utc)
    
    # Handle status change (move file if needed)
    if status is not None and ticket.status != original_status:
        # Get new path based on status
        new_path = get_ticket_path(ticket.id, ticket.status, root)
        
        # Save to new location
        ticket.save_to_json_file(str(new_path))
        
        # Execute ticket-updated hook (and ticket-moved if status changed)
        execute_hook("ticket-updated", build_ticket_event_data(ticket), silent=True)
        from gira.utils.hooks import build_ticket_move_event_data
        execute_hook("ticket-moved", build_ticket_move_event_data(ticket, original_status, ticket.status), silent=True)
        
        # Remove old file
        if ticket_path != new_path:
            ticket_path.unlink()
    else:
        # Save in place
        ticket.save_to_json_file(str(ticket_path))
        
        # Execute ticket-updated hook
        execute_hook("ticket-updated", build_ticket_event_data(ticket), silent=True)
    
    # Sync epic-ticket relationship if epic was changed
    if epic is not None:
        sync_epic_ticket_relationship(ticket.id, ticket.epic_id, root)
    
    return {
        "id": ticket.id,
        "title": ticket.title,
        "changes": changes
    }


def _expand_ticket_pattern(root: Path, pattern: str) -> List[str]:
    """Expand ticket pattern to list of ticket IDs.
    
    Supports:
    - Wildcards: TEST-1* matches TEST-10, TEST-11, etc.
    - Ranges: 801..807, TEST-1..10, GCM-801..GCM-807
    - Single IDs: TEST-1 returns [TEST-1]
    """
    tickets = []
    
    # Check for range pattern
    if ".." in pattern:
        try:
            # Split on .. to get start and end parts
            start_part, end_part = pattern.split("..", 1)
            
            # Handle different range formats:
            # 1. "801..807" - just numbers
            # 2. "GCM-801..807" - prefix with start number, end number only  
            # 3. "GCM-801..GCM-807" - full ticket IDs
            
            if "-" not in start_part and "-" not in end_part:
                # Format: "801..807" - need to get project prefix
                from gira.mcp.tools import get_project_ticket_prefix
                prefix = get_project_ticket_prefix()
                try:
                    start = int(start_part)
                    end = int(end_part)
                    for i in range(start, end + 1):
                        ticket_id = f"{prefix}-{i}"
                        if _ticket_exists(root, ticket_id):
                            tickets.append(ticket_id)
                except ValueError:
                    # Not valid numbers, treat as literal
                    if _ticket_exists(root, pattern):
                        tickets.append(pattern)
                        
            elif "-" in start_part and "-" not in end_part:
                # Format: "GCM-801..807" - prefix with start number, end number only
                prefix, start_str = start_part.rsplit("-", 1)
                try:
                    start = int(start_str)
                    end = int(end_part)
                    for i in range(start, end + 1):
                        ticket_id = f"{prefix}-{i}"
                        if _ticket_exists(root, ticket_id):
                            tickets.append(ticket_id)
                except ValueError:
                    # Not valid range, treat as literal
                    if _ticket_exists(root, pattern):
                        tickets.append(pattern)
                        
            elif "-" in start_part and "-" in end_part:
                # Format: "GCM-801..GCM-807" - full ticket IDs
                start_prefix, start_str = start_part.rsplit("-", 1)
                end_prefix, end_str = end_part.rsplit("-", 1)
                
                # Prefixes must match
                if start_prefix != end_prefix:
                    if _ticket_exists(root, pattern):
                        tickets.append(pattern)
                else:
                    try:
                        start = int(start_str)
                        end = int(end_str)
                        for i in range(start, end + 1):
                            ticket_id = f"{start_prefix}-{i}"
                            if _ticket_exists(root, ticket_id):
                                tickets.append(ticket_id)
                    except ValueError:
                        # Not valid range, treat as literal
                        if _ticket_exists(root, pattern):
                            tickets.append(pattern)
                            
        except ValueError:
            # Split failed or other error, treat as literal
            if _ticket_exists(root, pattern):
                tickets.append(pattern)
    
    # Check for wildcard pattern
    elif "*" in pattern:
        # Convert wildcard to regex
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")
        
        # Get swimlane IDs dynamically
        swimlane_ids = _get_swimlane_ids(root)
        
        # Search all ticket locations
        locations = [f"board/{swimlane}" for swimlane in swimlane_ids] + ["archive/tickets"]
        for location in locations:
            ticket_dir = root / ".gira" / location
            if ticket_dir.exists():
                for ticket_file in ticket_dir.glob("*.json"):
                    ticket_id = ticket_file.stem
                    if regex.match(ticket_id):
                        tickets.append(ticket_id)
    
    # Regular ticket ID
    else:
        if _ticket_exists(root, pattern):
            tickets.append(pattern)
    
    return tickets


def _get_swimlane_ids(root: Path) -> List[str]:
    """Get swimlane IDs from board configuration and actual directories."""
    swimlane_ids = set()
    
    # Get configured swimlanes from board config
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        board = get_board_configuration()
        swimlane_ids.update(swimlane.id for swimlane in board.swimlanes)
    
    # Also include any actual directories that exist in board/
    board_dir = root / ".gira" / "board"
    if board_dir.exists():
        for item in board_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                swimlane_ids.add(item.name)
    
    return list(swimlane_ids)


def _ticket_exists(root: Path, ticket_id: str) -> bool:
    """Check if a ticket exists in any location."""
    # Use find_ticket which properly handles all ticket locations
    from gira.utils.ticket_utils import find_ticket
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    return ticket is not None
