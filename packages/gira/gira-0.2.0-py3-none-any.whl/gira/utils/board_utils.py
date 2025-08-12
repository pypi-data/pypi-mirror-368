"""Board display utilities with performance optimizations."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from rich.box import ROUNDED
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from gira.models import Ticket
from gira.utils.cache import cached
from gira.utils.console import console
from gira.utils.team_utils import format_assignee_display


@cached(ttl=30)  # Cache for 30 seconds
def load_board_tickets_optimized(root: Path) -> Dict[str, List[Ticket]]:
    """
    Load all board tickets in parallel for better performance.

    Args:
        root: Project root path

    Returns:
        Dictionary mapping status to list of tickets
    """
    board_dir = root / ".gira" / "board"
    tickets_by_status = {}

    if not board_dir.exists():
        return tickets_by_status

    # Use ThreadPoolExecutor for parallel file loading
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all file loading tasks
        future_to_status = {}
        for status_dir in board_dir.iterdir():
            if status_dir.is_dir():
                status = status_dir.name
                tickets_by_status[status] = []

                for ticket_file in status_dir.glob("*.json"):
                    future = executor.submit(Ticket.from_json_file, str(ticket_file))
                    future_to_status[future] = status

        # Collect results
        for future in as_completed(future_to_status):
            status = future_to_status[future]
            try:
                ticket = future.result()
                tickets_by_status[status].append(ticket)
            except Exception:
                # Skip invalid tickets
                pass

    # Sort tickets within each status by order, then by ID
    for status, tickets in tickets_by_status.items():
        tickets.sort(
            key=lambda t: (
                t.order if hasattr(t, "order") and t.order > 0 else float("inf"),
                t.id,
            )
        )

    return tickets_by_status


def display_board_optimized(
    root: Path,
    columns: List[str],
    show_assignee: bool = False,
    show_labels: bool = False,
    max_tickets: int = 10,
) -> None:
    """
    Display board using optimized ticket loading.

    Args:
        root: Project root path
        columns: List of status columns to display
        show_assignee: Whether to show assignee
        show_labels: Whether to show labels
        max_tickets: Maximum tickets per column
    """
    # Load all tickets at once
    tickets_by_status = load_board_tickets_optimized(root)

    # Calculate total tickets
    total_tickets = sum(len(tickets) for tickets in tickets_by_status.values())

    # Build columns
    board_columns = []

    # Define column styles
    column_styles = {
        "todo": {"border": "yellow", "title": "📋 To Do"},
        "in_progress": {"border": "cyan", "title": "🚀 In Progress"},
        "review": {"border": "magenta", "title": "👀 Review"},
        "done": {"border": "green", "title": "✅ Done"},
    }

    for status in columns:
        tickets = tickets_by_status.get(status, [])

        # Get column style
        style = column_styles.get(
            status, {"border": "white", "title": status.replace("_", " ").title()}
        )

        # Create table for this column
        table = Table(
            show_header=False,
            padding=(0, 1),
            box=None,
            expand=True,
        )

        # Add tickets to table
        displayed = 0
        for ticket in tickets[:max_tickets]:
            # Create ticket card
            ticket_lines = []

            # Header with ID and priority
            priority_colors = {
                "critical": "bold red",
                "high": "bold yellow",
                "medium": "yellow",
                "low": "green",
            }
            priority_style = priority_colors.get(ticket.priority, "white")

            # Type emoji
            type_emoji = {
                "bug": "🐛",
                "feature": "✨",
                "task": "📝",
                "story": "📖",
                "subtask": "📌",
            }.get(ticket.type, "🎯")

            # Build header line
            header = Text()
            header.append(f"{type_emoji} ", style="default")
            header.append(ticket.id, style="bold cyan")
            if ticket.priority in ["critical", "high"]:
                header.append(" ● ", style=priority_style)
                header.append(ticket.priority.upper(), style=priority_style)

            ticket_lines.append(header)

            # Title (truncate if needed)
            title = ticket.title
            if len(title) > 50:
                title = title[:47] + "..."
            ticket_lines.append(Text(title, style="white"))

            # Assignee
            if show_assignee and ticket.assignee:
                assignee_name = format_assignee_display(ticket.assignee, root)
                ticket_lines.append(Text(f"@ {assignee_name}", style="dim cyan"))

            # Labels
            if show_labels and ticket.labels:
                label_line = Text()
                for i, label in enumerate(ticket.labels[:3]):
                    if i > 0:
                        label_line.append(" ", style="default")
                    label_line.append(f"#{label}", style="dim magenta")
                if len(ticket.labels) > 3:
                    label_line.append(f" +{len(ticket.labels) - 3}", style="dim")
                ticket_lines.append(label_line)

            # Story points
            if ticket.story_points:
                ticket_lines.append(
                    Text(f"⚡ {ticket.story_points} pts", style="dim blue")
                )

            # Blocked indicator
            if ticket.blocked_by:
                ticket_lines.append(Text("🚫 Blocked", style="bold red"))

            # Add ticket to table with spacing
            for line in ticket_lines:
                table.add_row(line)

            displayed += 1

            # Add separator between tickets (except last)
            if displayed < min(len(tickets), max_tickets):
                table.add_row("")  # Empty row for spacing

        # Show overflow indicator
        if len(tickets) > max_tickets:
            overflow_text = Text()
            overflow_text.append(
                f"↓ {len(tickets) - max_tickets} more", style="dim italic"
            )
            table.add_row("")  # Spacing
            table.add_row(overflow_text)

        # Add empty message if no tickets
        if not tickets:
            empty_text = Text("∅ No tickets", style="dim italic")
            table.add_row(empty_text)

        # Create title with count
        title_text = f"{style['title']} [{len(tickets)}]"

        # Wrap in panel
        panel = Panel(
            table,
            title=title_text,
            border_style=style["border"],
            box=ROUNDED,
            expand=True,
            padding=(1, 2),
        )
        board_columns.append(panel)

    # Print board header
    console.print()
    console.print(
        f"[bold]📊 Kanban Board[/bold] • {total_tickets} tickets total",
        justify="center",
    )
    console.print()

    # Display columns
    console.print(Columns(board_columns, equal=True, expand=True))
    console.print()


def display_board_optimized_filtered(
    root: Path,
    columns: List[str],
    filters: Dict[str, Any],
    show_assignee: bool = False,
    show_labels: bool = False,
    max_tickets: int = 10,
) -> None:
    """
    Display board with filters applied.

    Args:
        root: Project root path
        columns: List of status columns to display
        filters: Dictionary of filters to apply
        show_assignee: Whether to show assignee
        show_labels: Whether to show labels
        max_tickets: Maximum tickets per column
    """
    # Load all tickets at once
    tickets_by_status = load_board_tickets_optimized(root)

    # Apply filters
    filtered_by_status = {}
    for status, tickets in tickets_by_status.items():
        filtered = tickets

        # Apply assignee filter
        if filters.get("assignee"):
            filtered = [t for t in filtered if t.assignee == filters["assignee"]]

        # Apply priority filter
        if filters.get("priority"):
            filtered = [
                t for t in filtered if t.priority == filters["priority"].lower()
            ]

        # Apply type filter
        if filters.get("type"):
            filtered = [t for t in filtered if t.type == filters["type"].lower()]

        # Apply label filter
        if filters.get("label"):
            label_lower = filters["label"].lower()
            filtered = [
                t for t in filtered if label_lower in [lbl.lower() for lbl in t.labels]
            ]

        # Apply story point filters
        if filters.get("story_points_eq") is not None:
            filtered = [
                t for t in filtered if t.story_points == filters["story_points_eq"]
            ]

        if filters.get("story_points_gt") is not None:
            filtered = [
                t
                for t in filtered
                if t.story_points is not None
                and t.story_points > filters["story_points_gt"]
            ]

        if filters.get("story_points_lt") is not None:
            filtered = [
                t
                for t in filtered
                if t.story_points is not None
                and t.story_points < filters["story_points_lt"]
            ]

        # Apply date filters
        def parse_date(date_str: str):
            """Parse date string to datetime object."""
            from datetime import datetime

            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)

        def normalize_datetime(dt):
            """Normalize datetime to naive UTC for comparison."""
            if hasattr(dt, "tzinfo") and dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt

        if filters.get("created_after"):
            cutoff_date = parse_date(filters["created_after"])
            filtered = [
                t for t in filtered if normalize_datetime(t.created_at) >= cutoff_date
            ]

        if filters.get("created_before"):
            cutoff_date = parse_date(filters["created_before"]).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            filtered = [
                t for t in filtered if normalize_datetime(t.created_at) <= cutoff_date
            ]

        if filters.get("updated_after"):
            cutoff_date = parse_date(filters["updated_after"])
            filtered = [
                t for t in filtered if normalize_datetime(t.updated_at) >= cutoff_date
            ]

        if filters.get("updated_before"):
            cutoff_date = parse_date(filters["updated_before"]).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            filtered = [
                t for t in filtered if normalize_datetime(t.updated_at) <= cutoff_date
            ]

        # Apply due date filters
        if filters.get("due_after"):
            cutoff_date = parse_date(filters["due_after"])
            # Set cutoff to end of day to exclude tickets due on that day
            cutoff_date = cutoff_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            filtered = [
                t
                for t in filtered
                if hasattr(t, "due_date")
                and t.due_date is not None
                and normalize_datetime(t.due_date) > cutoff_date
            ]

        if filters.get("due_before"):
            cutoff_date = parse_date(filters["due_before"]).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            filtered = [
                t
                for t in filtered
                if hasattr(t, "due_date")
                and t.due_date is not None
                and normalize_datetime(t.due_date) <= cutoff_date
            ]

        if filters.get("due_on"):
            target_date = parse_date(filters["due_on"])
            end_of_day = target_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            filtered = [
                t
                for t in filtered
                if hasattr(t, "due_date")
                and t.due_date is not None
                and target_date <= normalize_datetime(t.due_date) <= end_of_day
            ]

        if filters.get("overdue"):
            from datetime import datetime

            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            filtered = [
                t
                for t in filtered
                if hasattr(t, "due_date")
                and t.due_date is not None
                and normalize_datetime(t.due_date) < today
            ]

        # Apply relationship and existence filters
        if filters.get("has_comments"):
            filtered = [t for t in filtered if hasattr(t, 'comment_count') and t.comment_count > 0]

        if filters.get("no_comments"):
            filtered = [t for t in filtered if hasattr(t, 'comment_count') and t.comment_count == 0]

        if filters.get("has_parent"):
            filtered = [t for t in filtered if hasattr(t, 'parent_id') and t.parent_id is not None]

        if filters.get("no_parent"):
            filtered = [t for t in filtered if not hasattr(t, 'parent_id') or t.parent_id is None]

        if filters.get("in_sprint"):
            sprint_id = filters["in_sprint"]
            filtered = [t for t in filtered if hasattr(t, 'sprint_id') and t.sprint_id == sprint_id]

        if filters.get("not_in_sprint"):
            sprint_id = filters["not_in_sprint"]
            filtered = [t for t in filtered if not hasattr(t, 'sprint_id') or t.sprint_id != sprint_id]

        if filters.get("not_in_epic"):
            epic_id = filters["not_in_epic"]
            epic_id = epic_id.upper() if not epic_id.startswith('EPIC-') else epic_id
            filtered = [t for t in filtered if not hasattr(t, 'epic_id') or t.epic_id != epic_id]

        filtered_by_status[status] = filtered

    # Calculate totals
    total_tickets = sum(len(tickets) for tickets in filtered_by_status.values())
    original_total = sum(len(tickets) for tickets in tickets_by_status.values())

    # Build columns
    board_columns = []

    # Define column styles
    column_styles = {
        "todo": {"border": "yellow", "title": "📋 To Do"},
        "in_progress": {"border": "cyan", "title": "🚀 In Progress"},
        "review": {"border": "magenta", "title": "👀 Review"},
        "done": {"border": "green", "title": "✅ Done"},
    }

    for status in columns:
        tickets = filtered_by_status.get(status, [])

        # Get column style
        style = column_styles.get(
            status, {"border": "white", "title": status.replace("_", " ").title()}
        )

        # Create table for this column
        table = Table(
            show_header=False,
            padding=(0, 1),
            box=None,
            expand=True,
        )

        # Add tickets to table
        displayed = 0
        for ticket in tickets[:max_tickets]:
            # Create ticket card
            ticket_lines = []

            # Header with ID and priority
            priority_colors = {
                "critical": "bold red",
                "high": "bold yellow",
                "medium": "yellow",
                "low": "green",
            }
            priority_style = priority_colors.get(ticket.priority, "white")

            # Type emoji
            type_emoji = {
                "bug": "🐛",
                "feature": "✨",
                "task": "📝",
                "story": "📖",
                "subtask": "📌",
            }.get(ticket.type, "🎯")

            # Build header line
            header = Text()
            header.append(f"{type_emoji} ", style="default")
            header.append(ticket.id, style="bold cyan")
            if ticket.priority in ["critical", "high"]:
                header.append(" ● ", style=priority_style)
                header.append(ticket.priority.upper(), style=priority_style)

            ticket_lines.append(header)

            # Title (truncate if needed)
            title = ticket.title
            if len(title) > 50:
                title = title[:47] + "..."
            ticket_lines.append(Text(title, style="white"))

            # Assignee
            if show_assignee and ticket.assignee:
                assignee_name = format_assignee_display(ticket.assignee, root)
                ticket_lines.append(Text(f"@ {assignee_name}", style="dim cyan"))

            # Labels
            if show_labels and ticket.labels:
                label_line = Text()
                for i, label in enumerate(ticket.labels[:3]):
                    if i > 0:
                        label_line.append(" ", style="default")
                    label_line.append(f"#{label}", style="dim magenta")
                if len(ticket.labels) > 3:
                    label_line.append(f" +{len(ticket.labels) - 3}", style="dim")
                ticket_lines.append(label_line)

            # Story points
            if ticket.story_points:
                ticket_lines.append(
                    Text(f"⚡ {ticket.story_points} pts", style="dim blue")
                )

            # Blocked indicator
            if ticket.blocked_by:
                ticket_lines.append(Text("🚫 Blocked", style="bold red"))

            # Add ticket to table with spacing
            for line in ticket_lines:
                table.add_row(line)

            displayed += 1

            # Add separator between tickets (except last)
            if displayed < min(len(tickets), max_tickets):
                table.add_row("")  # Empty row for spacing

        # Show overflow indicator
        if len(tickets) > max_tickets:
            overflow_text = Text()
            overflow_text.append(
                f"↓ {len(tickets) - max_tickets} more", style="dim italic"
            )
            table.add_row("")  # Spacing
            table.add_row(overflow_text)

        # Add empty message if no tickets
        if not tickets:
            empty_text = Text("∅ No tickets", style="dim italic")
            table.add_row(empty_text)

        # Create title with count
        title_text = f"{style['title']} [{len(tickets)}]"

        # Wrap in panel
        panel = Panel(
            table,
            title=title_text,
            border_style=style["border"],
            box=ROUNDED,
            expand=True,
            padding=(1, 2),
        )
        board_columns.append(panel)

    # Print board header
    console.print()
    header_text = f"[bold]📊 Kanban Board[/bold] • {total_tickets} tickets"
    if total_tickets < original_total:
        header_text += f" (filtered from {original_total})"

    # Show active filters
    active_filters = []
    if filters.get("assignee"):
        active_filters.append(f"@ {filters['assignee']}")
    if filters.get("priority"):
        active_filters.append(f"🎯 {filters['priority']}")
    if filters.get("type"):
        active_filters.append(f"📝 {filters['type']}")
    if filters.get("label"):
        active_filters.append(f"🏷️  {filters['label']}")

    if active_filters:
        header_text += f"\n[dim]Filters: {' • '.join(active_filters)}[/dim]"

    console.print(header_text, justify="center")
    console.print()

    # Display columns
    console.print(Columns(board_columns, equal=True, expand=True))
    console.print()
