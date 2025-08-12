"""Board command for Gira."""

import json
from datetime import datetime
from typing import Optional

import typer
from pydantic import ValidationError
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from gira.models import Board, Swimlane, Ticket
from gira.utils.console import console
from gira.utils.output import OutputFormat, add_format_option, print_output, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.team_utils import format_assignee_display


def board(
    assignee: Optional[str] = typer.Option(
        None, "--assignee", "-a", help="Filter by assignee"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", "-p", help="Filter by priority"
    ),
    ticket_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by ticket type"
    ),
    label: Optional[str] = typer.Option(None, "--label", "-l", help="Filter by label"),
    story_points_eq: Optional[int] = typer.Option(
        None, "--story-points-eq", help="Filter by exact story point value"
    ),
    story_points_gt: Optional[int] = typer.Option(
        None, "--story-points-gt", help="Filter by story points greater than value"
    ),
    story_points_lt: Optional[int] = typer.Option(
        None, "--story-points-lt", help="Filter by story points less than value"
    ),
    created_after: Optional[str] = typer.Option(
        None, "--created-after", help="Filter tickets created after date (YYYY-MM-DD)"
    ),
    created_before: Optional[str] = typer.Option(
        None, "--created-before", help="Filter tickets created before date (YYYY-MM-DD)"
    ),
    updated_after: Optional[str] = typer.Option(
        None, "--updated-after", help="Filter tickets updated after date (YYYY-MM-DD)"
    ),
    updated_before: Optional[str] = typer.Option(
        None, "--updated-before", help="Filter tickets updated before date (YYYY-MM-DD)"
    ),
    due_after: Optional[str] = typer.Option(
        None, "--due-after", help="Filter tickets due after date (YYYY-MM-DD)"
    ),
    due_before: Optional[str] = typer.Option(
        None, "--due-before", help="Filter tickets due before date (YYYY-MM-DD)"
    ),
    due_on: Optional[str] = typer.Option(
        None, "--due-on", help="Filter tickets due on specific date (YYYY-MM-DD)"
    ),
    overdue: bool = typer.Option(
        False, "--overdue", help="Show only tickets past their due date"
    ),
    has_comments: bool = typer.Option(
        False, "--has-comments", help="Show only tickets that have comments"
    ),
    no_comments: bool = typer.Option(
        False, "--no-comments", help="Show only tickets without comments"
    ),
    has_parent: bool = typer.Option(
        False, "--has-parent", help="Show only subtasks that have a parent ticket"
    ),
    no_parent: bool = typer.Option(
        False, "--no-parent", help="Show only tickets that are not subtasks"
    ),
    in_sprint: Optional[str] = typer.Option(
        None, "--in-sprint", help="Filter tickets in a specific sprint"
    ),
    not_in_sprint: Optional[str] = typer.Option(
        None, "--not-in-sprint", help="Filter tickets not in a specific sprint"
    ),
    not_in_epic: Optional[str] = typer.Option(
        None, "--not-in-epic", help="Filter tickets not linked to a specific epic"
    ),
    compact: bool = typer.Option(False, "--compact", "-c", help="Show compact view"),
    fast: bool = typer.Option(
        False, "--fast", help="Use optimized display for large projects"
    ),
    output_format: OutputFormat = add_format_option(OutputFormat.TABLE),
    json_flag: bool = typer.Option(
        False, "--json", help="Output in JSON format (shorthand for --format json)"
    ),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Display the kanban board."""
    root = ensure_gira_project()

    # Handle --json flag as shorthand for --format json
    if json_flag:
        output_format = OutputFormat.JSON

    # Check for automatic archiving
    from gira.utils.auto_archive import check_auto_archive, check_performance_threshold

    check_auto_archive(root, verbose=False)

    # Check performance threshold
    threshold_result = check_performance_threshold(root)
    if threshold_result:
        active_count, threshold = threshold_result
        console.print(
            f"[yellow]⚠️  Performance Warning:[/yellow] You have {active_count} active tickets (threshold: {threshold})"
        )
        console.print(
            "[dim]Consider archiving old tickets with 'gira archive --suggest'[/dim]"
        )
        console.print()

    # Load board configuration or use default
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        board_config = Board.from_json_file(str(board_config_path))
    else:
        # Use default board configuration
        board_config = Board(
            swimlanes=[
                Swimlane(id="todo", name="To Do"),
                Swimlane(id="in_progress", name="In Progress"),
                Swimlane(id="review", name="Review"),
                Swimlane(id="done", name="Done"),
            ],
            transitions={
                "todo": ["in_progress"],
                "in_progress": ["review", "todo"],
                "review": ["done", "in_progress"],
                "done": ["todo"],
            },
        )

    # Use optimized display for large projects
    if fast:
        columns = [swimlane.id for swimlane in board_config.swimlanes]

        # Apply filters if provided
        from gira.utils.board_utils import (
            display_board_optimized_filtered,
        )

        filters = {
            "assignee": assignee,
            "priority": priority,
            "type": ticket_type,
            "label": label,
            "story_points_eq": story_points_eq,
            "story_points_gt": story_points_gt,
            "story_points_lt": story_points_lt,
            "created_after": created_after,
            "created_before": created_before,
            "updated_after": updated_after,
            "updated_before": updated_before,
            "due_after": due_after,
            "due_before": due_before,
            "due_on": due_on,
            "overdue": overdue,
            "has_comments": has_comments,
            "no_comments": no_comments,
            "has_parent": has_parent,
            "no_parent": no_parent,
            "in_sprint": in_sprint,
            "not_in_sprint": not_in_sprint,
            "not_in_epic": not_in_epic,
        }

        display_board_optimized_filtered(
            root,
            columns,
            filters=filters,
            show_assignee=not compact,
            show_labels=not compact,
            max_tickets=10 if compact else 20,
        )
        return

    # Create a table for the board
    table = Table(show_header=False, show_edge=False, padding=(0, 1), expand=True)

    # Add columns for each swimlane
    for _ in board_config.swimlanes:
        table.add_column(width=25)

    # Collect tickets for each swimlane
    swimlane_tickets = {}
    for swimlane in board_config.swimlanes:
        swimlane_tickets[swimlane.id] = []

        # Load tickets from the swimlane directory
        swimlane_dir = root / ".gira" / "board" / swimlane.id
        if swimlane_dir.exists():
            for ticket_file in sorted(swimlane_dir.glob("*.json")):
                try:
                    ticket = Ticket.from_json_file(str(ticket_file))

                    # Apply filters
                    if assignee and ticket.assignee != assignee:
                        continue
                    if priority and ticket.priority != priority.lower():
                        continue
                    if ticket_type and ticket.type != ticket_type.lower():
                        continue
                    if label and label.lower() not in [
                        lbl.lower() for lbl in ticket.labels
                    ]:
                        continue

                    # Apply story point filters
                    if (
                        story_points_eq is not None
                        and ticket.story_points != story_points_eq
                    ):
                        continue
                    if story_points_gt is not None and (
                        ticket.story_points is None
                        or ticket.story_points <= story_points_gt
                    ):
                        continue
                    if story_points_lt is not None and (
                        ticket.story_points is None
                        or ticket.story_points >= story_points_lt
                    ):
                        continue

                    # Apply date filters
                    def parse_date(date_str: str) -> datetime:
                        """Parse date string to datetime object."""
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
                        except ValueError as e:
                            console.print(
                                f"[red]Error:[/red] Invalid date format '{date_str}'. Expected YYYY-MM-DD"
                            )
                            raise typer.Exit(1) from e

                    def normalize_datetime(dt: datetime) -> datetime:
                        """Normalize datetime to naive UTC for comparison."""
                        if dt.tzinfo is not None:
                            return dt.replace(tzinfo=None)
                        return dt

                    if created_after is not None:
                        cutoff_date = parse_date(created_after)
                        if normalize_datetime(ticket.created_at) < cutoff_date:
                            continue

                    if created_before is not None:
                        cutoff_date = parse_date(created_before).replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        if normalize_datetime(ticket.created_at) > cutoff_date:
                            continue

                    if updated_after is not None:
                        cutoff_date = parse_date(updated_after)
                        if normalize_datetime(ticket.updated_at) < cutoff_date:
                            continue

                    if updated_before is not None:
                        cutoff_date = parse_date(updated_before).replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        if normalize_datetime(ticket.updated_at) > cutoff_date:
                            continue

                    # Apply due date filters
                    if due_after is not None:
                        cutoff_date = parse_date(due_after)
                        # Set cutoff to end of day to exclude tickets due on that day
                        cutoff_date = cutoff_date.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        if (
                            ticket.due_date is None
                            or normalize_datetime(ticket.due_date) <= cutoff_date
                        ):
                            continue

                    if due_before is not None:
                        cutoff_date = parse_date(due_before).replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        if (
                            ticket.due_date is None
                            or normalize_datetime(ticket.due_date) > cutoff_date
                        ):
                            continue

                    if due_on is not None:
                        target_date = parse_date(due_on)
                        end_of_day = target_date.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )
                        if ticket.due_date is None or not (
                            target_date
                            <= normalize_datetime(ticket.due_date)
                            <= end_of_day
                        ):
                            continue

                    if overdue:
                        today = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                        if (
                            ticket.due_date is None
                            or normalize_datetime(ticket.due_date) >= today
                        ):
                            continue

                    # Apply relationship and existence filters
                    if has_comments and ticket.comment_count == 0:
                        continue
                    
                    if no_comments and ticket.comment_count > 0:
                        continue
                    
                    if has_parent and ticket.parent_id is None:
                        continue
                    
                    if no_parent and ticket.parent_id is not None:
                        continue
                    
                    if in_sprint is not None and ticket.sprint_id != in_sprint:
                        continue
                    
                    if not_in_sprint is not None and ticket.sprint_id == not_in_sprint:
                        continue
                    
                    if not_in_epic is not None:
                        epic_id = not_in_epic.upper() if not not_in_epic.startswith('EPIC-') else not_in_epic
                        if ticket.epic_id == epic_id:
                            continue

                    swimlane_tickets[swimlane.id].append(ticket)
                except (
                    FileNotFoundError,
                    json.JSONDecodeError,
                    ValidationError,
                    PermissionError,
                ):
                    # Skip tickets that can't be loaded due to file issues or invalid data
                    continue

    # Sort tickets within each swimlane by order
    for swimlane_id in swimlane_tickets:
        swimlane_tickets[swimlane_id].sort(
            key=lambda t: (t.order if t.order > 0 else float("inf"), t.id)
        )

    # Handle JSON output
    if output_format == OutputFormat.JSON:
        # Build JSON structure with swimlanes and their tickets
        board_data = {"swimlanes": []}

        for swimlane in board_config.swimlanes:
            # Convert tickets to dict for JSON serialization
            tickets_data = [
                ticket.model_dump(mode="json")
                for ticket in swimlane_tickets[swimlane.id]
            ]

            swimlane_data = {
                "id": swimlane.id,
                "name": swimlane.name,
                "limit": swimlane.limit,
                "ticket_count": len(swimlane_tickets[swimlane.id]),
                "tickets": tickets_data,
            }
            board_data["swimlanes"].append(swimlane_data)

        color_kwargs = get_color_kwargs(color, no_color)
        print_output(board_data, output_format, **color_kwargs)
        return

    # Create header row with swimlane names and counts
    headers = []
    for swimlane in board_config.swimlanes:
        count = len(swimlane_tickets[swimlane.id])
        header_text = swimlane.name

        if swimlane.limit and swimlane.limit > 0:
            header_text += f" ({count}/{swimlane.limit})"
            # Add warning if at or over limit
            if count >= swimlane.limit:
                header_text += " ⚠️"
        else:
            header_text += f" ({count})"

        headers.append(
            Panel(
                Text(header_text, style="bold cyan", justify="center"),
                expand=True,
                border_style="cyan",
            )
        )

    table.add_row(*headers)

    # Find the maximum number of tickets in any swimlane
    max_tickets = (
        max(len(tickets) for tickets in swimlane_tickets.values())
        if swimlane_tickets
        else 0
    )

    # Add rows for tickets
    if max_tickets == 0:
        # Show empty message
        empty_cells = []
        for _ in board_config.swimlanes:
            empty_cells.append(Text("(empty)", style="dim italic", justify="center"))
        table.add_row(*empty_cells)
    else:
        # Add ticket rows
        for i in range(max_tickets):
            row_cells = []
            for swimlane in board_config.swimlanes:
                tickets = swimlane_tickets[swimlane.id]
                if i < len(tickets):
                    ticket = tickets[i]

                    if compact:
                        # Compact view - just ID and title
                        title_display = (
                            ticket.title
                            if len(ticket.title) <= 30
                            else ticket.title[:30] + "..."
                        )
                        content = f"[bold]{ticket.id}[/bold]\n{title_display}"
                    else:
                        # Full view
                        content_lines = [
                            f"[bold cyan]{ticket.id}[/bold cyan]",
                            ticket.title[:120] + "…"
                            if len(ticket.title) > 120
                            else ticket.title,
                        ]

                        # Priority with color
                        priority_colors = {
                            "low": "green",
                            "medium": "yellow",
                            "high": "red",
                            "critical": "red bold",
                        }
                        priority_style = priority_colors.get(ticket.priority, "white")
                        content_lines.append(
                            f"[{priority_style}]{ticket.priority.title()}[/{priority_style}]"
                        )

                        if ticket.assignee:
                            assignee_display = format_assignee_display(
                                ticket.assignee, root
                            )
                            content_lines.append(f"@ {assignee_display}")

                        content = "\n".join(content_lines)

                    # Create ticket panel
                    ticket_panel = Panel(content, expand=True, border_style="white")
                    row_cells.append(ticket_panel)
                else:
                    row_cells.append("")

            table.add_row(*row_cells)

    # Display the board
    console.print()
    console.print(table)
    console.print()
