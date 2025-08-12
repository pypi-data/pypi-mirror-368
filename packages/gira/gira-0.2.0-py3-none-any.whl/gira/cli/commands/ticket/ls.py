"""List tickets command alias - short form of list."""

from typing import Optional
import typer

from gira.cli.commands.ticket.list import list_tickets as list_tickets_command
from gira.utils.output import OutputFormat, add_format_option, add_color_option, add_no_color_option


def ls(
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
    """List tickets (alias for list).
    
    This is a shorter Unix-style alias for the 'list' command.
    
    Examples:
        # List all tickets
        gira ticket ls
        
        # List with filters
        gira ticket ls --status todo --priority high
        gira ticket ls --assignee me --type bug
        
        # Using query language
        gira ticket ls --query "status:todo AND priority:high"
        
        # List IDs only
        gira ticket ls --ids-only
    """
    # Simply call the list function with the same parameters
    list_tickets_command(
        query=query,
        status=status,
        assignee=assignee,
        ticket_type=ticket_type,
        priority=priority,
        label=label,
        parent=parent,
        blocked=blocked,
        story_points_eq=story_points_eq,
        story_points_gt=story_points_gt,
        story_points_lt=story_points_lt,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
        due_after=due_after,
        due_before=due_before,
        due_on=due_on,
        overdue=overdue,
        has_comments=has_comments,
        no_comments=no_comments,
        has_parent=has_parent,
        no_parent=no_parent,
        in_sprint=in_sprint,
        not_in_sprint=not_in_sprint,
        not_in_epic=not_in_epic,
        epic=epic,
        no_epic=no_epic,
        search=search,
        search_in=search_in,
        exact_match=exact_match,
        regex_search=regex_search,
        case_sensitive_search=case_sensitive_search,
        sort=sort,
        output_format=output_format,
        ids_only=ids_only,
        counts=counts,
        include_archived=include_archived,
        fields=fields,
        filter_json=filter_json,
        color=color,
        no_color=no_color,
    )