"""Edit ticket command - alias for update."""

from typing import List, Optional
import typer

from gira.cli.commands.ticket.update import update as update_ticket


def edit(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to edit (supports patterns like 'GCM-1*', ranges like 'GCM-1..10', use '-' to read IDs from stdin, or omit for --stdin JSON)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description (use '-' for stdin, 'editor' to open editor)"),
    description_file: Optional[str] = typer.Option(None, "--description-file", help="Read description from a file"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="New priority"),
    ticket_type: Optional[str] = typer.Option(None, "--type", help="New ticket type"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="New assignee (use 'none' to clear)"),
    add_labels: Optional[str] = typer.Option(None, "--add-labels", help="Labels to add (comma-separated)"),
    remove_labels: Optional[str] = typer.Option(None, "--remove-labels", help="Labels to remove (comma-separated)"),
    epic: Optional[str] = typer.Option(None, "--epic", "-e", help="New epic ID (use 'none' to clear)"),
    parent: Optional[str] = typer.Option(None, "--parent", help="New parent ID (use 'none' to clear)"),
    sprint: Optional[str] = typer.Option(None, "--sprint", help="Sprint ID to assign ticket to (use 'current' for active sprint, 'none' to clear)"),
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
    """Edit a ticket (alias for update).
    
    This is a more intuitive alias for the 'update' command. It supports updating
    single tickets, multiple tickets, or tickets matching patterns.
    
    Pattern Support:
        - Wildcards: GCM-1* matches GCM-10, GCM-11, etc.
        - Ranges: GCM-1..10 matches GCM-1 through GCM-10
        - Multiple IDs: GCM-1 GCM-2 GCM-3
    
    Multiple Ticket Mode:
        - AI-friendly: No confirmation required by default
        - Shows preview for 5+ tickets or when using --dry-run
        - Some options incompatible: --description-file, 'editor' description, stdin description
    
    Examples:
        # Edit single ticket
        gira ticket edit GCM-123 --status done --priority high
        
        # Edit multiple tickets by ID
        gira ticket edit GCM-1 GCM-2 GCM-3 --assignee alice --priority medium
        
        # Edit ticket description with editor
        gira ticket edit GCM-123 --description editor
        
        # Edit tickets from stdin
        echo "GCM-1 GCM-2 GCM-3" | gira ticket edit - --status "in progress"
    """
    # Simply call the update function with the same parameters
    update_ticket(
        ticket_ids=ticket_ids,
        title=title,
        description=description,
        description_file=description_file,
        status=status,
        priority=priority,
        ticket_type=ticket_type,
        assignee=assignee,
        add_labels=add_labels,
        remove_labels=remove_labels,
        epic=epic,
        parent=parent,
        sprint=sprint,
        story_points=story_points,
        output=output,
        quiet=quiet,
        strict=strict,
        stdin=stdin,
        jsonl=jsonl,
        dry_run=dry_run,
        force=force,
        custom_field=custom_field,
        remove_custom_field=remove_custom_field,
    )