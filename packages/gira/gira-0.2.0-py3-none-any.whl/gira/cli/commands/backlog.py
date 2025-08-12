"""Backlog command for Gira - specialized view for backlog tickets."""

from typing import Optional, List
import typer
from gira.utils.console import console
from gira.utils.output import OutputFormat, add_format_option, add_color_option, add_no_color_option, get_color_kwargs, print_output
from gira.utils.project import ensure_gira_project
from gira.query import EntityType, QueryExecutor, QueryParser
from gira.utils.config import get_default_reporter
from gira.utils.ticket_utils import load_all_tickets
from gira.utils.display import show_tickets_table, show_ticket_counts
from gira.utils.field_selection import expand_field_aliases, filter_fields, validate_fields


def backlog(
    assignee: Optional[str] = typer.Option(
        None, "--assignee", "-a", help="Filter by assignee"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", "-p", help="Filter by priority (critical, high, medium, low)"
    ),
    ticket_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by type (bug, feature, task, etc.)"
    ),
    label: Optional[str] = typer.Option(
        None, "--label", "-l", help="Filter by label"
    ),
    epic: Optional[str] = typer.Option(
        None, "--epic", help="Filter by epic ID (comma-separated for multiple)"
    ),
    no_epic: bool = typer.Option(
        False, "--no-epic", help="Show only tickets without epic assignment"
    ),
    search: Optional[str] = typer.Option(
        None, "--search", help="Search text in ticket title and description"
    ),
    sort: str = typer.Option(
        "priority", "--sort", help="Sort by: priority (default), created, updated, title, id"
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", help="Limit number of results shown"
    ),
    format: OutputFormat = add_format_option(),
    fields: Optional[str] = typer.Option(
        None,
        "--fields",
        help="Comma-separated list of fields to include in JSON output"
    ),
    counts: bool = typer.Option(
        False, "--counts", help="Show summary counts by priority"
    ),
    ready: bool = typer.Option(
        False, "--ready", help="Show only ready tickets (no blockers, assigned)"
    ),
    unassigned: bool = typer.Option(
        False, "--unassigned", help="Show only unassigned tickets"
    ),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Show tickets in the backlog with enhanced filtering and display options.
    
    This command provides a specialized view of backlog tickets with commonly used
    filters and display options optimized for backlog management.
    
    Examples:
        # Show all backlog tickets sorted by priority
        gira backlog
        
        # Show high priority backlog tickets
        gira backlog --priority high
        
        # Show unassigned backlog tickets
        gira backlog --unassigned
        
        # Show ready tickets (assigned and not blocked)
        gira backlog --ready
        
        # Show backlog for specific epic
        gira backlog --epic EPIC-001
        
        # Show backlog tickets without epic assignment
        gira backlog --no-epic
        
        # Search backlog for specific text
        gira backlog --search "login bug"
        
        # Show backlog with custom sorting
        gira backlog --sort created
        
        # Show backlog counts by priority
        gira backlog --counts
        
        # Limit results
        gira backlog --limit 10
        
        # Export backlog as JSON with specific fields
        gira backlog --format json --fields "id,title,priority,assignee"
    """
    # Ensure we're in a Gira project
    root = ensure_gira_project()
    
    # Build the query for backlog tickets
    query_parts = ["status:backlog"]
    
    # Add ready filter if requested
    if ready:
        # Ready means assigned and not blocked
        if not assignee:  # Don't override explicit assignee filter
            query_parts.append("assignee:!null")
        query_parts.append("NOT blocked_by:*")
    
    # Add unassigned filter if requested
    if unassigned:
        if assignee:
            console.print("[yellow]Warning:[/yellow] --unassigned conflicts with --assignee filter")
        else:
            query_parts.append("assignee:null")
    
    # Construct the final query
    query = " AND ".join(query_parts)
    
    
    # Load all tickets
    tickets = load_all_tickets(root, include_archived=False)
    
    # Execute the query
    parser = QueryParser(query, entity_type="ticket")
    expression = parser.parse()
    
    if expression:
        executor = QueryExecutor(EntityType.TICKET)
        user_email = get_default_reporter()
        tickets = executor.execute(expression, tickets, user_email=user_email)
    
    # Apply any additional filters if provided
    if assignee:
        tickets = [t for t in tickets if t.assignee == assignee]
    if priority:
        tickets = [t for t in tickets if t.priority == priority.lower()]
    if ticket_type:
        tickets = [t for t in tickets if t.type == ticket_type.lower()]
    if label:
        tickets = [t for t in tickets if label.lower() in [lbl.lower() for lbl in t.labels]]
    if epic:
        epic_ids = [e.strip() for e in epic.split(',')]
        epic_ids = [e.upper() if not e.startswith('EPIC-') else e for e in epic_ids]
        tickets = [t for t in tickets if t.epic_id in epic_ids]
    if no_epic:
        tickets = [t for t in tickets if t.epic_id is None]
    
    # Apply search if provided
    if search:
        from gira.utils.search import search_and_rank
        search_fields = [
            lambda t: t.title,
            lambda t: t.description,
        ]
        search_results = search_and_rank(tickets, search, search_fields, min_score=0.4)
        tickets = [item for item, score in search_results]
    
    # Sort tickets
    if sort == "priority":
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        tickets.sort(key=lambda t: (priority_order.get(t.priority, 4), t.id))
    elif sort == "created":
        tickets.sort(key=lambda t: (t.created_at, t.id))
    elif sort == "updated":
        tickets.sort(key=lambda t: (t.updated_at, t.id))
    elif sort == "title":
        tickets.sort(key=lambda t: (t.title.lower(), t.id))
    else:  # default to id
        tickets.sort(key=lambda t: t.id)
    
    # Apply limit if specified
    if limit:
        tickets = tickets[:limit]
    
    # If counts requested, show summary
    if counts:
        show_ticket_counts(tickets)
        return
    
    # Handle no tickets
    if not tickets:
        console.print("[yellow]No backlog tickets found[/yellow]")
        return
    
    # Display header for non-JSON output
    if format == OutputFormat.TABLE:
        console.print("\n[bold cyan]Backlog Tickets[/bold cyan]")
        if ready:
            console.print("[dim]Showing tickets that are ready to work on (assigned and not blocked)[/dim]")
        elif unassigned:
            console.print("[dim]Showing unassigned tickets[/dim]")
        console.print()
    
    # Output results
    color_kwargs = get_color_kwargs(color, no_color)
    
    if format == OutputFormat.JSON and fields:
        # Apply field selection for JSON output
        ticket_data = [t.model_dump(mode="json") for t in tickets]
        
        # Expand any aliases in the field list
        expanded_fields = expand_field_aliases(fields)
        
        # Validate fields before filtering
        invalid_fields = validate_fields(ticket_data, expanded_fields)
        if invalid_fields:
            console.print(f"[yellow]Warning:[/yellow] Unknown fields will be ignored: {', '.join(invalid_fields)}")
        
        # Filter the data to include only requested fields
        ticket_data = filter_fields(ticket_data, expanded_fields)
        
        print_output(ticket_data, format, **color_kwargs)
    elif format == OutputFormat.TABLE:
        # Use the existing table display
        show_tickets_table(tickets, root)
    else:
        # Use the output system for other formats
        print_output(tickets, format, **color_kwargs)