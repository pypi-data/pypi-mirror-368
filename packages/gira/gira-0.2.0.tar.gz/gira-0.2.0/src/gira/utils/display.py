"""Display utilities for Gira using Rich."""

from collections import Counter
from pathlib import Path
from typing import List, Optional

from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from gira.constants import TITLE_MAX_LENGTH, TITLE_TRUNCATE_LENGTH
from gira.models import Ticket
from gira.utils.config import get_global_config
from gira.utils.board_config import get_board_configuration
from gira.utils.console import console
from gira.utils.markdown_custom import LeftAlignedMarkdown
from gira.utils.team_utils import format_assignee_display


def render_markdown_content(content: str, left_align_headings: bool = True) -> Optional[Markdown]:
    """
    Render markdown content if enabled in configuration.

    Args:
        content: The markdown content to render
        left_align_headings: Whether to left-align headings (default: True)

    Returns:
        Markdown object if rendering is enabled, None otherwise
    """
    config = get_global_config()
    # Default to True if no config exists
    render_markdown = True
    if config is not None:
        render_markdown = config.render_markdown

    if render_markdown:
        if left_align_headings:
            return LeftAlignedMarkdown(content)
        else:
            return Markdown(content)
    return None


def format_archived_indicator(is_archived: bool) -> str:
    """
    Format an archived indicator for display.

    Args:
        is_archived: Whether the ticket is archived

    Returns:
        Formatted string with [ARCHIVED] badge if archived, empty string otherwise
    """
    return "[dim red][ARCHIVED][/dim red]" if is_archived else ""


def show_tickets_table(tickets: List[Ticket], project_root: Path = None) -> None:
    """Display tickets in a table format."""
    from gira.utils.project import get_gira_root
    from gira.utils.ticket_utils import find_ticket, is_ticket_archived

    if project_root is None:
        project_root = get_gira_root()

    table = Table(
        title=f"Tickets ({len(tickets)})",
        show_header=True,
        header_style="bold cyan",
    )

    # Add columns
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white", width=30)
    table.add_column("Status", style="yellow")
    table.add_column("Priority", style="magenta", width=10)
    table.add_column("Type", style="blue")
    table.add_column("Assignee", style="green")

    # Add rows
    for ticket in tickets:
        # Check if ticket is archived
        _, ticket_path = find_ticket(ticket.id, project_root, include_archived=True)
        is_archived = is_ticket_archived(ticket_path) if ticket_path else False

        # Truncate title if too long
        title = ticket.title
        if len(title) > TITLE_MAX_LENGTH:
            title = title[:TITLE_TRUNCATE_LENGTH] + "..."

        # Add archived indicator to ID if needed
        id_display = ticket.id
        if is_archived:
            id_display = f"{ticket.id} [dim red][A][/dim red]"

        table.add_row(
            id_display,
            title,
            ticket.status.replace("_", " ").title(),
            ticket.priority.title(),
            ticket.type.title(),
            format_assignee_display(ticket.assignee, project_root) if ticket.assignee else "-"
        )

    console.print(table)


def show_ticket_counts(tickets: List[Ticket]) -> None:
    """Show summary counts of tickets by status."""
    # Count by status
    status_counts = Counter(t.status for t in tickets)

    # Create summary table
    table = Table(title="Ticket Summary", show_header=True, header_style="bold cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Count", style="white", justify="right")

    # Load board config to get valid statuses
    board = get_board_configuration()

    # Add rows for each status from board swimlanes
    for swimlane in board.swimlanes:
        count = status_counts.get(swimlane.id, 0)
        display_status = swimlane.name
        table.add_row(display_status, str(count))

    # Add total row
    table.add_row("─" * 12, "─" * 5, style="dim")
    table.add_row("[bold]Total[/bold]", f"[bold]{len(tickets)}[/bold]")

    console.print(table)


def show_ticket_details(ticket: Ticket, ticket_path: Path, root: Path) -> None:
    """Display ticket details in a formatted panel."""
    import json

    from rich.console import Group

    from gira.utils.ticket_utils import is_ticket_archived

    # Check if ticket is archived
    is_archived = is_ticket_archived(ticket_path)

    # Build content
    content_lines = []

    # Title and ID with archived indicator
    title_line = f"[bold cyan]{ticket.id}[/bold cyan] - [bold]{ticket.title}[/bold]"
    if is_archived:
        title_line += f" {format_archived_indicator(is_archived)}"
    content_lines.append(title_line)
    content_lines.append("")

    # Archive info if archived
    if is_archived:
        # Try to read archive metadata
        try:
            with open(ticket_path) as f:
                data = json.load(f)
                if '_archive_metadata' in data:
                    meta = data['_archive_metadata']
                    content_lines.append(f"[dim red]Archived on {meta.get('archived_at', 'Unknown')}[/dim red]")
                    content_lines.append(f"[dim red]From status: {meta.get('archived_from_status', 'Unknown')}[/dim red]")
                    content_lines.append("")
        except Exception:
            pass

    # Core details
    content_lines.append(f"[yellow]Status:[/yellow] {ticket.status.replace('_', ' ').title()}")
    content_lines.append(f"[yellow]Priority:[/yellow] {ticket.priority.title()}")
    content_lines.append(f"[yellow]Type:[/yellow] {ticket.type.title()}")
    content_lines.append("")

    # People
    content_lines.append(f"[yellow]Reporter:[/yellow] {ticket.reporter}")
    assignee_display = format_assignee_display(ticket.assignee, root) if ticket.assignee else "-"
    content_lines.append(f"[yellow]Assignee:[/yellow] {assignee_display}")
    content_lines.append("")

    # Optional fields
    if ticket.labels:
        content_lines.append(f"[yellow]Labels:[/yellow] {', '.join(ticket.labels)}")

    if ticket.epic_id:
        content_lines.append(f"[yellow]Epic:[/yellow] {ticket.epic_id}")

    if ticket.parent_id:
        content_lines.append(f"[yellow]Parent:[/yellow] {ticket.parent_id}")

    if ticket.story_points is not None:
        content_lines.append(f"[yellow]Story Points:[/yellow] {ticket.story_points}")

    if ticket.blocked_by:
        content_lines.append(f"[yellow]Blocked by:[/yellow] {', '.join(ticket.blocked_by)}")

    if ticket.blocks:
        content_lines.append(f"[yellow]Blocks:[/yellow] {', '.join(ticket.blocks)}")

    # Custom fields
    if hasattr(ticket, 'custom_fields') and ticket.custom_fields:
        content_lines.append("")
        content_lines.append("[yellow]Custom Fields:[/yellow]")

        # Try to load config to get field definitions for better display
        try:
            from gira.models.config import ProjectConfig
            config = ProjectConfig.from_json_file(str(root / ".gira" / "config.json"))

            for field_name, field_value in sorted(ticket.custom_fields.items()):
                field_def = config.custom_fields.get_field_by_name(field_name)
                display_name = field_def.display_name if field_def else field_name

                # Format value based on type
                if isinstance(field_value, bool):
                    display_value = "Yes" if field_value else "No"
                else:
                    display_value = str(field_value)

                content_lines.append(f"  [dim]{display_name}:[/dim] {display_value}")
        except Exception:
            # Fallback to simple display if config can't be loaded
            for field_name, field_value in sorted(ticket.custom_fields.items()):
                # Format boolean values
                if isinstance(field_value, bool):
                    display_value = "Yes" if field_value else "No"
                else:
                    display_value = str(field_value)

                content_lines.append(f"  [dim]{field_name}:[/dim] {display_value}")

    # Timestamps
    content_lines.append("")
    content_lines.append(f"[dim]Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    content_lines.append(f"[dim]Updated: {ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    # File location
    content_lines.append("")
    content_lines.append(f"[dim]Location: {ticket_path.relative_to(root)}[/dim]")

    # Git commits (if available)
    try:
        from gira.utils.config import get_project_config
        from gira.utils.git_utils import get_commits_for_ticket, is_git_repository

        if is_git_repository():
            config = get_project_config(root)
            patterns = config.commit_id_patterns if config else None
            commits = get_commits_for_ticket(ticket.id, limit=5, patterns=patterns)

            if commits:
                content_lines.append("")
                content_lines.append("[yellow]Recent Commits:[/yellow]")
                for commit in commits:
                    content_lines.append(f"  [dim cyan]{commit.short_sha}[/dim cyan] - {commit.subject[:60]}{'...' if len(commit.subject) > 60 else ''}")
                    content_lines.append(f"    [dim]by {commit.author} on {commit.date.strftime('%Y-%m-%d')}[/dim]")
                if len(commits) == 5:
                    content_lines.append(f"  [dim]Use 'gira ticket commits {ticket.id}' to see all commits[/dim]")
    except Exception:
        # Silently ignore any git-related errors
        pass

    # Add note about restoration if archived
    if is_archived:
        content_lines.append("")
        content_lines.append("[dim yellow]Note: This ticket is archived. To restore it, use:[/dim yellow]")
        content_lines.append(f"[dim yellow]  gira archive restore {ticket.id}[/dim yellow]")

    # Check if we have a description and should render markdown
    has_markdown_description = False
    markdown_content = None
    if ticket.description:
        config = get_global_config()
        render_markdown = True
        if config is not None:
            render_markdown = config.render_markdown

        if render_markdown:
            markdown_content = render_markdown_content(ticket.description)
            has_markdown_description = markdown_content is not None

    if has_markdown_description and markdown_content:
        # Add description header to content
        content_lines.append("")
        content_lines.append("[yellow]Description:[/yellow]")

        # Create the basic panel without description
        basic_content = "\n".join(content_lines)

        # Create a group that combines the basic info and markdown
        group_content = Group(
            basic_content,
            markdown_content  # No padding - align with other content
        )

        # Create panel with the group
        panel = Panel(
            group_content,
            title="Ticket Details",
            border_style="cyan",
            padding=(1, 2)
        )
    else:
        # No markdown or plain text mode
        if ticket.description:
            content_lines.append("")
            content_lines.append("[yellow]Description:[/yellow]")
            content_lines.append("")
            content_lines.append(ticket.description)

        # Create panel with plain text
        panel = Panel(
            "\n".join(content_lines),
            title="Ticket Details",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print(panel)
