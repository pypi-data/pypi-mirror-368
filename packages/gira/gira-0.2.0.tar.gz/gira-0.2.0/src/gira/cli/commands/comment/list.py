"""List comments on a ticket command."""

from datetime import datetime
from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.panel import Panel
from rich.text import Text

from gira.utils.field_selection import expand_field_aliases, filter_fields, validate_fields
from gira.utils.mention_utils import format_content_with_mentions
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, is_ticket_archived
from gira.utils.epic_utils import find_epic, is_epic_archived
from gira.utils.comment_attachments import list_comment_attachments

def list_comments(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or Epic ID to show comments for (e.g., GCM-123 or EPIC-001)"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "-l", "--limit",
        help="Limit number of comments shown"
    ),
    reverse: bool = typer.Option(
        False,
        "-r", "--reverse",
        help="Show oldest comments first"
    ),
    output_format: OutputFormat = add_format_option(OutputFormat.TEXT),
    json_flag: bool = typer.Option(False, "--json", help="Output in JSON format (shorthand for --format json)"),
    fields: Optional[str] = typer.Option(
        None,
        "--fields",
        help="Comma-separated list of fields to include in JSON output (e.g., 'id,author,content' or use aliases like 'comment_basics')"
    ),
    filter_json: Optional[str] = typer.Option(
        None,
        "--filter-json",
        help="JSONPath expression to filter JSON output (e.g., '$[?(@.author==\"john@example.com\")].content')"
    ),
    verbose: bool = typer.Option(
        False,
        "-v", "--verbose",
        help="Show detailed information including attachment details"
    ),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List all comments on a ticket or epic.
    
    Examples:
        gira comment list GCM-123
        gira comment list EPIC-001
        gira comment list GCM-123 --limit 5 --reverse
        gira comment list GCM-123 --json
        gira comment list GCM-123 --format json --fields "id,author,content"
        gira comment list GCM-123 --format json --filter-json '$[?(@.author=="john@example.com")]'
        gira comment list GCM-123 --format json --filter-json '$[*].content'
    """
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()
    
    # Handle --json flag as shorthand for --format json
    if json_flag:
        output_format = OutputFormat.JSON

    # Determine if this is a ticket or epic based on ID pattern
    entity_id = entity_id.upper()
    is_epic = entity_id.startswith("EPIC-")
    
    # Find the entity (ticket or epic)
    if is_epic:
        entity, entity_path = find_epic(entity_id, gira_root, include_archived=True)
        entity_type = "epic"
    else:
        entity, entity_path = find_ticket(entity_id, gira_root, include_archived=True)
        entity_type = "ticket"
    
    if not entity:
        console.print(f"[red]Error:[/red] {entity_type.capitalize()} {entity_id} not found")
        raise typer.Exit(1)

    # Check if archived
    if is_epic:
        is_archived = is_epic_archived(entity_path) if entity_path else False
    else:
        is_archived = is_ticket_archived(entity_path) if entity_path else False

    comments = entity.comments or []

    if not comments:
        console.print(f"[yellow]No comments on {entity_type} {entity_id}[/yellow]")
        return

    # Sort comments
    if not reverse:
        comments = list(reversed(comments))  # Newest first by default

    # Apply limit
    if limit:
        comments = comments[:limit]
    
    # Validate filter_json is only used with JSON format
    if filter_json and output_format != OutputFormat.JSON:
        console.print("[red]Error:[/red] --filter-json can only be used with --format json")
        raise typer.Exit(1)

    # Output
    if output_format == OutputFormat.JSON and fields:
        # Apply field selection for JSON output
        comment_data = [comment.model_dump(mode="json") for comment in comments]
        
        # Expand any aliases in the field list
        expanded_fields = expand_field_aliases(fields)
        
        # Validate fields before filtering
        invalid_fields = validate_fields(comment_data, expanded_fields)
        if invalid_fields:
            console.print(f"[yellow]Warning:[/yellow] Unknown fields will be ignored: {', '.join(invalid_fields)}")
        
        # Filter the data to include only requested fields
        comment_data = filter_fields(comment_data, expanded_fields)
        
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(comment_data, output_format, jsonpath_filter=filter_json, **color_kwargs)
    elif output_format in [OutputFormat.TEXT, OutputFormat.TABLE]:
        # Use the existing text display
        # Add archived indicator if needed
        title = f"\n[bold]Comments on {entity_id}[/bold]"
        if is_archived:
            from gira.utils.display import format_archived_indicator
            title += f" {format_archived_indicator(is_archived)}"
        title += f" ({len(entity.comments or [])} total)\n"
        console.print(title)

        # Add note if archived
        if is_archived:
            console.print(f"[dim yellow]Note: This {entity_type} is archived.[/dim yellow]\n")

        for i, comment in enumerate(comments):
            if i > 0:
                console.print()
            _display_comment(comment, i == 0, verbose=verbose, entity_type=entity_type, entity_id=entity_id, gira_root=gira_root)
    else:
        # Use the new output system for other formats
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(comments, output_format, jsonpath_filter=filter_json, **color_kwargs)


def _display_comment(comment, is_first: bool = False, verbose: bool = False, entity_type: str = None, entity_id: str = None, gira_root = None) -> None:
    """Display a single comment."""
    # Handle both Comment objects and dictionaries
    if hasattr(comment, 'created_at'):
        # Comment object
        created_at = comment.created_at
        author = comment.author
        content = comment.content
        comment_id = comment.id
        edited = getattr(comment, 'edited', False)
        attachment_count = getattr(comment, 'attachment_count', 0)
    else:
        # Dictionary
        created_at = datetime.fromisoformat(comment["created_at"])
        author = comment['author']
        content = comment['content']
        comment_id = comment['id']
        edited = comment.get("edited", False)
        attachment_count = comment.get("attachment_count", 0)

    time_str = _format_relative_time(created_at)

    # Build header
    header = f"[cyan]{author}[/cyan] • {time_str}"
    if edited:
        header += " [dim](edited)[/dim]"
    if attachment_count > 0:
        header += f" 📎[dim]({attachment_count})[/dim]"

    # Get project root for @ mention processing
    from gira.utils.project import get_gira_root
    gira_root = get_gira_root()

    # Check if we should render markdown
    from gira.utils.display import render_markdown_content
    from rich.console import Group
    
    markdown_content = render_markdown_content(content)
    
    if markdown_content:
        # When rendering markdown, we need to handle @ mentions separately
        # since the markdown renderer doesn't know about them
        panel_content = Group(
            header,
            "",  # Empty line
            markdown_content
        )
    else:
        # Format content with @ mention highlighting
        formatted_content = format_content_with_mentions(content, gira_root)

        # Build the full panel content
        panel_content = Text()
        panel_content.append(header + "\n\n")
        panel_content.append(formatted_content)

    # Show panel
    console.print(Panel(
        panel_content,
        title=f"[dim]{comment_id[:8]}[/dim]",
        border_style="blue" if is_first else "dim",
        padding=(1, 2)
    ))
    
    # Show attachment details in verbose mode
    if verbose and attachment_count > 0 and entity_type and entity_id and gira_root:
        attachments = list_comment_attachments(entity_type, entity_id, comment_id, gira_root)
        if attachments:
            console.print("\n  [dim]Attachments:[/dim]")
            for att in attachments:
                console.print(f"    📎 {att.file_name} ({att.get_display_size()}) - {att.content_type}")


def _format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time."""
    now = datetime.now(dt.tzinfo)
    delta = now - dt

    if delta.total_seconds() < 60:
        return "just now"
    elif delta.total_seconds() < 3600:
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta.days < 7:
        return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    else:
        return dt.strftime("%Y-%m-%d %H:%M")
