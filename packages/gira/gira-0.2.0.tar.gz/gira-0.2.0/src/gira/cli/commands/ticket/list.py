"""List tickets command for Gira."""

from datetime import datetime
from typing import Optional

import typer

from gira.query import EntityType, QueryExecutor, QueryParser
from gira.query.parser import QueryParseError
from gira.utils.advanced_search import SearchMode, advanced_search_and_rank
from gira.utils.config import get_default_reporter
from gira.utils.console import console
from gira.utils.display import show_ticket_counts, show_tickets_table
from gira.utils.field_selection import (
    expand_field_aliases,
    filter_fields,
    validate_fields,
)
from gira.utils.output import (
    OutputFormat,
    add_color_option,
    add_format_option,
    add_no_color_option,
    get_color_kwargs,
    print_output,
)
from gira.utils.project import ensure_gira_project
from gira.utils.saved_queries import resolve_query_string
from gira.utils.search import search_and_rank
from gira.utils.ticket_utils import load_all_tickets


def list_tickets(
    query: Optional[str] = typer.Option(
        None,
        "--query",
        "-q",
        help="Query expression (e.g., 'status:todo AND priority:high')",
    ),
    status: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status"
    ),
    assignee: Optional[str] = typer.Option(
        None, "--assignee", "-a", help="Filter by assignee"
    ),
    ticket_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by type"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", "-p", help="Filter by priority"
    ),
    label: Optional[str] = typer.Option(
        None, "--label", "--labels", "-l", help="Filter by label"
    ),
    parent: Optional[str] = typer.Option(
        None, "--parent", help="Filter by parent ticket ID (show subtasks)"
    ),
    blocked: bool = typer.Option(
        False, "--blocked", help="Show only tickets blocked by unresolved dependencies"
    ),
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
    epic: Optional[str] = typer.Option(
        None, "--epic", help="Filter tickets by epic ID (comma-separated for multiple epics)"
    ),
    no_epic: bool = typer.Option(
        False, "--no-epic", help="Show only tickets without epic assignment (alias for --not-in-epic without value)"
    ),
    search: Optional[str] = typer.Option(
        None, "--search", help="Search text in ticket fields (default: title and description)"
    ),
    search_in: Optional[list[str]] = typer.Option(
        None, "--search-in", help="Specify fields to search: title, description, id, status, type, priority, assignee, reporter, labels, all (can be used multiple times)"
    ),
    exact_match: bool = typer.Option(
        False, "--exact-match", help="Perform exact string match instead of fuzzy match"
    ),
    regex_search: bool = typer.Option(
        False, "--regex-search", help="Treat search pattern as a regular expression"
    ),
    case_sensitive_search: bool = typer.Option(
        False, "--case-sensitive-search", help="Make search case-sensitive"
    ),
    sort: str = typer.Option(
        "id", "--sort", help="Sort by: id, priority, created, updated, title, order"
    ),
    output_format: OutputFormat = add_format_option(),
    ids_only: bool = typer.Option(False, "--ids-only", help="Show only ticket IDs"),
    counts: bool = typer.Option(False, "--counts", help="Show summary counts"),
    include_archived: bool = typer.Option(
        False, "--include-archived", help="Include archived tickets in results"
    ),
    fields: Optional[str] = typer.Option(
        None,
        "--fields",
        help="Comma-separated list of fields to include in JSON output (e.g., 'id,title,status' or use aliases like 'basics')",
    ),
    filter_json: Optional[str] = typer.Option(
        None,
        "--filter-json",
        help="JSONPath expression to filter JSON output (e.g., '$[?(@.priority==\"high\")].id')",
    ),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List tickets with optional filters.

    Examples:
        # Using query language (recommended)
        gira ticket list --query "status:todo AND priority:high"
        gira ticket list --query "assignee:me() AND type:bug"
        gira ticket list --query "labels:contains('frontend')"

        # Using saved queries
        gira ticket list --query @my-bugs
        gira ticket list --query @high-priority

        # Using legacy filters (still supported)
        gira ticket list --status todo --priority high
        gira ticket list --assignee john@example.com --type bug

        # Using story point filters
        gira ticket list --story-points-eq 5
        gira ticket list --story-points-gt 3 --story-points-lt 8
        gira ticket list --status todo --story-points-gt 5

        # Using date filters
        gira ticket list --created-after 2025-01-01
        gira ticket list --updated-after 2025-01-15 --updated-before 2025-01-31
        gira ticket list --created-before 2024-12-31 --status done

        # Using due date filters
        gira ticket list --due-before 2025-02-01
        gira ticket list --due-on 2025-01-31
        gira ticket list --overdue
        gira ticket list --due-after 2025-01-15 --due-before 2025-02-15

        # Using relationship and existence filters
        gira ticket list --has-comments
        gira ticket list --no-comments --status todo
        gira ticket list --has-parent
        gira ticket list --no-parent --type task
        gira ticket list --in-sprint SPRINT-1
        gira ticket list --not-in-sprint SPRINT-1 --status todo
        gira ticket list --not-in-epic EPIC-001

        # Using epic filters
        gira ticket list --epic EPIC-001
        gira ticket list --epic EPIC-001,EPIC-002
        gira ticket list --epic EPIC-001 --status "in progress"
        gira ticket list --no-epic

        # Using field selection with JSON output
        gira ticket list --format json --fields "id,title,status"
        gira ticket list --format json --fields "basics,assignee"
        gira ticket list --format json --fields "id,epic.title,sprint.name"

        # Using JSONPath filtering (requires --format json)
        gira ticket list --format json --filter-json '$[?(@.priority=="high")].id'
        gira ticket list --format json --filter-json '$[?(@.type=="bug" && @.status=="todo")]'
        gira ticket list --format json --filter-json '$[*].{id: id, title: title}'

        # Using field-specific text search
        gira ticket list --search "login" --search-in title
        gira ticket list --search "bug" --search-in title --search-in description
        gira ticket list --search "john" --search-in assignee --search-in reporter
        gira ticket list --search "frontend" --search-in labels
        gira ticket list --search "GCM" --search-in id
        gira ticket list --search "urgent" --search-in all

        # Using advanced text search modifiers
        gira ticket list --search "Login Bug" --exact-match
        gira ticket list --search "GCM-[0-9]+" --regex-search
        gira ticket list --search "TODO" --case-sensitive-search
        gira ticket list --search "bug.*fix" --regex-search --search-in title
        gira ticket list --search "High Priority" --exact-match --case-sensitive-search
    """
    root = ensure_gira_project()

    # Check for automatic archiving
    from gira.utils.auto_archive import check_auto_archive

    check_auto_archive(root, verbose=False)

    # Collect all tickets - pass root to ensure test isolation
    tickets = load_all_tickets(root, include_archived=include_archived)

    # Apply query if provided
    if query:
        try:
            # Resolve saved query references (e.g., @my-bugs)
            resolved_query = resolve_query_string(query, entity_type="ticket")

            parser = QueryParser(resolved_query, entity_type="ticket")
            expression = parser.parse()

            if expression:
                executor = QueryExecutor(EntityType.TICKET)
                user_email = get_default_reporter()
                tickets = executor.execute(expression, tickets, user_email=user_email)
        except ValueError as e:
            # Saved query not found
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e
        except QueryParseError as e:
            console.print(f"[red]Query Error:[/red] {e}")
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(f"[red]Error executing query:[/red] {e}")
            raise typer.Exit(1) from e

    # Apply legacy filters (only if query is not provided)
    if not query:
        if status:
            tickets = [t for t in tickets if t.status == status.lower()]

        if assignee:
            tickets = [t for t in tickets if t.assignee == assignee]

        if ticket_type:
            tickets = [t for t in tickets if t.type == ticket_type.lower()]

        if priority:
            tickets = [t for t in tickets if t.priority == priority.lower()]

        if label:
            tickets = [
                t for t in tickets if label.lower() in [lbl.lower() for lbl in t.labels]
            ]

        if parent:
            # Filter to show only subtasks of the specified parent ticket
            parent_id = parent.upper()
            tickets = [t for t in tickets if t.parent_id == parent_id]

        if blocked:
            # Filter to show only tickets that are blocked by unresolved dependencies
            # Create a lookup map for all tickets by ID for efficient status checking
            ticket_map = {
                t.id: t
                for t in load_all_tickets(root, include_archived=include_archived)
            }

            def is_ticket_blocked(ticket):
                """Check if ticket is blocked by any unresolved dependencies."""
                if not ticket.blocked_by:
                    return False

                # Check if any dependency is not in 'done' status
                for dep_id in ticket.blocked_by:
                    dep_ticket = ticket_map.get(dep_id)
                    if dep_ticket and dep_ticket.status != "done" or not dep_ticket:
                        return True

                return False

            tickets = [t for t in tickets if is_ticket_blocked(t)]

        # Apply story point filters
        if story_points_eq is not None:
            tickets = [t for t in tickets if t.story_points == story_points_eq]

        if story_points_gt is not None:
            tickets = [
                t
                for t in tickets
                if t.story_points is not None and t.story_points > story_points_gt
            ]

        if story_points_lt is not None:
            tickets = [
                t
                for t in tickets
                if t.story_points is not None and t.story_points < story_points_lt
            ]

        # Apply date filters
        def parse_date(date_str: str) -> datetime:
            """Parse date string to datetime object."""
            try:
                # Parse YYYY-MM-DD format and set to start of day (timezone-naive)
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
                # Convert to UTC and remove timezone info
                return dt.replace(tzinfo=None)
            return dt

        if created_after is not None:
            cutoff_date = parse_date(created_after)
            tickets = [
                t for t in tickets if normalize_datetime(t.created_at) >= cutoff_date
            ]

        if created_before is not None:
            cutoff_date = parse_date(created_before)
            # Add one day to include the entire day
            cutoff_date = cutoff_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            tickets = [
                t for t in tickets if normalize_datetime(t.created_at) <= cutoff_date
            ]

        if updated_after is not None:
            cutoff_date = parse_date(updated_after)
            tickets = [
                t for t in tickets if normalize_datetime(t.updated_at) >= cutoff_date
            ]

        if updated_before is not None:
            cutoff_date = parse_date(updated_before)
            # Add one day to include the entire day
            cutoff_date = cutoff_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            tickets = [
                t for t in tickets if normalize_datetime(t.updated_at) <= cutoff_date
            ]

        # Apply due date filters
        if due_after is not None:
            cutoff_date = parse_date(due_after)
            # Set cutoff to end of day to exclude tickets due on that day
            cutoff_date = cutoff_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            # Only include tickets with due dates that are strictly after the cutoff
            tickets = [
                t
                for t in tickets
                if t.due_date is not None
                and normalize_datetime(t.due_date) > cutoff_date
            ]

        if due_before is not None:
            cutoff_date = parse_date(due_before)
            # Include the entire day
            cutoff_date = cutoff_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            # Only include tickets with due dates that are before the cutoff
            tickets = [
                t
                for t in tickets
                if t.due_date is not None
                and normalize_datetime(t.due_date) <= cutoff_date
            ]

        if due_on is not None:
            target_date = parse_date(due_on)
            end_of_day = target_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            # Only include tickets due on the specific date
            tickets = [
                t
                for t in tickets
                if t.due_date is not None
                and target_date <= normalize_datetime(t.due_date) <= end_of_day
            ]

        if overdue:
            # Get current date (start of today)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # Only include tickets with due dates in the past
            tickets = [
                t
                for t in tickets
                if t.due_date is not None and normalize_datetime(t.due_date) < today
            ]

        # Apply relationship and existence filters
        if has_comments:
            tickets = [t for t in tickets if t.comment_count > 0]

        if no_comments:
            tickets = [t for t in tickets if t.comment_count == 0]

        if has_parent:
            tickets = [t for t in tickets if t.parent_id is not None]

        if no_parent:
            tickets = [t for t in tickets if t.parent_id is None]

        if in_sprint is not None:
            tickets = [t for t in tickets if t.sprint_id == in_sprint]

        if not_in_sprint is not None:
            tickets = [t for t in tickets if t.sprint_id != not_in_sprint]

        if not_in_epic is not None:
            epic_id = not_in_epic.upper() if not not_in_epic.startswith('EPIC-') else not_in_epic
            tickets = [t for t in tickets if t.epic_id != epic_id]

        if no_epic:
            # Show only tickets without epic assignment
            tickets = [t for t in tickets if t.epic_id is None]

        if epic is not None:
            # Filter tickets by epic ID(s)
            epic_ids = [e.strip() for e in epic.split(',')]
            # Normalize epic IDs to uppercase if they don't start with EPIC-
            epic_ids = [e.upper() if not e.startswith('EPIC-') else e for e in epic_ids]
            tickets = [t for t in tickets if t.epic_id in epic_ids]

        if search is not None:
            # Build search fields based on search_in parameter
            all_search_fields = {
                "title": lambda t: t.title,
                "description": lambda t: t.description,
                "labels": lambda t: " ".join(t.labels) if t.labels else "",
                "assignee": lambda t: t.assignee if t.assignee else "",
                "type": lambda t: t.type,
                "priority": lambda t: t.priority,
                "status": lambda t: t.status,
                "id": lambda t: t.id,
                "reporter": lambda t: t.reporter if t.reporter else "",
            }

            # Note: comments field requires loading comments separately
            # which is not implemented in the current architecture

            # Determine which fields to search
            if search_in is None or "all" in search_in:
                # Default: search in title and description only
                search_fields = [
                    all_search_fields["title"],
                    all_search_fields["description"],
                ]
            else:
                # Use specified fields
                search_fields = []
                for field in search_in:
                    field_lower = field.lower()
                    if field_lower in all_search_fields:
                        search_fields.append(all_search_fields[field_lower])
                    elif field_lower == "comments":
                        console.print(
                            "[yellow]Warning:[/yellow] Searching in comments is not yet implemented"
                        )
                    else:
                        console.print(
                            f"[yellow]Warning:[/yellow] Unknown search field '{field}'. "
                            f"Valid fields: {', '.join(sorted(all_search_fields.keys()))}, comments, all"
                        )

                if not search_fields:
                    console.print(
                        "[red]Error:[/red] No valid search fields specified"
                    )
                    raise typer.Exit(1)

            # Check for conflicting search modes
            if exact_match and regex_search:
                console.print(
                    "[red]Error:[/red] Cannot use both --exact-match and --regex-search"
                )
                raise typer.Exit(1)

            # Determine search mode
            if exact_match:
                search_mode = SearchMode.EXACT
            elif regex_search:
                search_mode = SearchMode.REGEX
            else:
                search_mode = SearchMode.FUZZY

            # Use advanced search if any modifiers are specified
            if exact_match or regex_search or case_sensitive_search:
                search_results = advanced_search_and_rank(
                    tickets, search, search_fields,
                    search_mode=search_mode,
                    case_sensitive=case_sensitive_search,
                    min_score=0.4
                )
            else:
                # Use regular fuzzy search for backward compatibility
                search_results = search_and_rank(
                    tickets, search, search_fields, min_score=0.4
                )

            tickets = [item for item, score in search_results]
    elif any(
        [
            status,
            assignee,
            ticket_type,
            priority,
            label,
            parent,
            blocked,
            story_points_eq,
            story_points_gt,
            story_points_lt,
            created_after,
            created_before,
            updated_after,
            updated_before,
            due_after,
            due_before,
            due_on,
            overdue,
            has_comments,
            no_comments,
            has_parent,
            no_parent,
            in_sprint,
            not_in_sprint,
            not_in_epic,
            epic,
            no_epic,
            search,
        ]
    ):
        console.print(
            "[yellow]Warning:[/yellow] Legacy filter options are ignored when using --query"
        )

    # Sort tickets (unless already sorted by query)
    if not query or sort != "id":
        if sort == "priority":
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            tickets.sort(key=lambda t: (priority_order.get(t.priority, 4), t.id))
        elif sort == "created":
            tickets.sort(key=lambda t: (t.created_at, t.id))
        elif sort == "updated":
            tickets.sort(key=lambda t: (t.updated_at, t.id))
        elif sort == "title":
            tickets.sort(key=lambda t: (t.title.lower(), t.id))
        elif sort == "order":
            # Group by status first, then sort by order within each status
            tickets.sort(
                key=lambda t: (
                    t.status,
                    t.order if hasattr(t, "order") and t.order > 0 else float("inf"),
                    t.id,
                )
            )
        else:  # default to id
            tickets.sort(key=lambda t: t.id)

    # Show counts if requested
    if counts:
        show_ticket_counts(tickets)
        return

    # Handle no tickets
    if not tickets:
        console.print("No tickets found")
        return

    # Validate filter_json is only used with JSON format
    if filter_json and output_format != OutputFormat.JSON:
        console.print(
            "[red]Error:[/red] --filter-json can only be used with --format json"
        )
        raise typer.Exit(1)

    # Output results
    color_kwargs = get_color_kwargs(color, no_color)

    if ids_only:
        # Use IDS format
        print_output(tickets, OutputFormat.IDS, **color_kwargs)
    elif output_format == OutputFormat.JSON and fields:
        # Apply field selection for JSON output
        ticket_data = [t.model_dump(mode="json") for t in tickets]

        # Expand any aliases in the field list
        expanded_fields = expand_field_aliases(fields)

        # Validate fields before filtering
        invalid_fields = validate_fields(ticket_data, expanded_fields)
        if invalid_fields:
            console.print(
                f"[yellow]Warning:[/yellow] Unknown fields will be ignored: {', '.join(invalid_fields)}"
            )

        # Filter the data to include only requested fields
        ticket_data = filter_fields(ticket_data, expanded_fields)

        print_output(ticket_data, output_format, jsonpath_filter=filter_json, **color_kwargs)
    elif output_format == OutputFormat.TABLE:
        # Use the existing table display
        show_tickets_table(tickets, root)
    else:
        # Use the new output system for other formats
        print_output(tickets, output_format, jsonpath_filter=filter_json, **color_kwargs)
