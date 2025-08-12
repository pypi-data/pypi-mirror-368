"""List sprints command."""

from datetime import date, datetime
from typing import Optional, List

import typer
from gira.utils.console import console
from rich.table import Table

from gira.models.sprint import Sprint, SprintStatus
from gira.query import EntityType, QueryExecutor, QueryParser
from gira.query.parser import QueryParseError
from gira.utils.config import get_default_reporter
from gira.utils.field_selection import expand_field_aliases, filter_fields, validate_fields
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.search import search_and_rank
from gira.utils.advanced_search import SearchMode, advanced_search_and_rank

def show_sprints_table(sprints):
    """Display sprints in a table format."""
    table = Table(title="Sprints")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Status", style="dim")
    table.add_column("Start", style="dim")
    table.add_column("End", style="dim")
    table.add_column("Days", style="dim", justify="right")
    table.add_column("Tickets", style="dim", justify="right")

    today = date.today()

    for sprint in sprints:
        # Calculate days
        if sprint.status == SprintStatus.ACTIVE:
            days_left = (sprint.end_date - today).days + 1
            days_str = f"{days_left} left" if days_left > 0 else "Overdue"
            days_style = "green" if days_left > 3 else "yellow" if days_left > 0 else "red"
        else:
            duration = (sprint.end_date - sprint.start_date).days + 1
            days_str = f"{duration} days"
            days_style = "dim"

        # Status color
        status_colors = {
            SprintStatus.PLANNED: "yellow",
            SprintStatus.ACTIVE: "green",
            SprintStatus.COMPLETED: "blue",
            "planned": "yellow",
            "active": "green",
            "completed": "blue"
        }
        # Handle both enum and string status values
        status_value = sprint.status.value if hasattr(sprint.status, 'value') else sprint.status
        status_style = status_colors.get(sprint.status, "dim")

        table.add_row(
            sprint.id,
            sprint.name,
            f"[{status_style}]{status_value}[/{status_style}]",
            sprint.start_date.isoformat(),
            sprint.end_date.isoformat(),
            f"[{days_style}]{days_str}[/{days_style}]",
            str(len(sprint.tickets))
        )

    console.print(table)


def list_sprints(
    query: Optional[str] = typer.Option(
        None,
        "--query", "-q",
        help="Query expression (e.g., 'status:active AND name:~\"*sprint*\"')"
    ),
    status: Optional[List[str]] = typer.Option(
        None,
        "--status",
        help="Filter by sprint status (planned, active, completed)"
    ),
    after: Optional[str] = typer.Option(
        None,
        "--after",
        help="Show sprints that start after this date (YYYY-MM-DD)"
    ),
    before: Optional[str] = typer.Option(
        None,
        "--before",
        help="Show sprints that end before this date (YYYY-MM-DD)"
    ),
    between: Optional[str] = typer.Option(
        None,
        "--between",
        help="Show sprints within date range (YYYY-MM-DD,YYYY-MM-DD)"
    ),
    min_tickets: Optional[int] = typer.Option(
        None,
        "--min-tickets",
        help="Show sprints with at least this many tickets"
    ),
    active: bool = typer.Option(
        False,
        "--active",
        help="Show only active sprints (deprecated: use --status active)"
    ),
    completed: bool = typer.Option(
        False,
        "--completed",
        help="Show only completed sprints (deprecated: use --status completed)"
    ),
    search: Optional[str] = typer.Option(
        None,
        "--search",
        help="Search text in sprint fields (default: name and goal)"
    ),
    search_in: Optional[list[str]] = typer.Option(
        None,
        "--search-in",
        help="Specify fields to search: name, goal, id, status, all (can be used multiple times)"
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
    output_format: OutputFormat = add_format_option(),
    json_flag: bool = typer.Option(False, "--json", help="Output in JSON format (shorthand for --format json)"),
    fields: Optional[str] = typer.Option(
        None,
        "--fields",
        help="Comma-separated list of fields to include in JSON output (e.g., 'id,name,status' or use aliases like 'sprint_basics')"
    ),
    filter_json: Optional[str] = typer.Option(
        None,
        "--filter-json",
        help="JSONPath expression to filter JSON output (e.g., '$[?(@.status==\"active\")].id')"
    ),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List all sprints.
    
    Examples:
        # Using query language (recommended)
        gira sprint list --query "status:active"
        gira sprint list --query "name:~'*MVP*' AND start_date:>days_ago(30)"
        gira sprint list --query "end_date:<today"
        
        # Using filter options
        gira sprint list --status active
        gira sprint list --status completed --status planned
        gira sprint list --after 2025-07-01
        gira sprint list --before 2025-08-01
        gira sprint list --between 2025-06-01,2025-07-31
        gira sprint list --min-tickets 5
        gira sprint list --status completed --after 2025-07-01
        
        # Using legacy filters (deprecated)
        gira sprint list --active
        gira sprint list --completed
        
        # Export as JSON
        gira sprint list --json
        
        # Using field selection with JSON output
        gira sprint list --format json --fields "id,name,status"
        gira sprint list --format json --fields "sprint_basics,tickets"
        
        # Using JSONPath filtering (requires --format json)
        gira sprint list --format json --filter-json '$[?(@.status=="active")].id'
        gira sprint list --format json --filter-json '$[*].{id: id, name: name}'
        
        # Using field-specific text search
        gira sprint list --search "MVP" --search-in name
        gira sprint list --search "release" --search-in goal
        gira sprint list --search "active" --search-in status
        gira sprint list --search "SPRINT-1" --search-in id
        gira sprint list --search "backend" --search-in name --search-in goal
    """
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()
    
    # Handle --json flag as shorthand for --format json
    if json_flag:
        output_format = OutputFormat.JSON

    # Load sprints
    sprints = []
    
    # Check if we need to load all sprints (when using filters or query)
    load_all = query or status or after or before or between or min_tickets is not None

    # Load active sprints
    if not completed or load_all:
        active_dir = gira_root / ".gira" / "sprints" / "active"
        if active_dir.exists():
            for sprint_file in active_dir.glob("*.json"):
                try:
                    sprint = Sprint.model_validate_json(sprint_file.read_text())
                    sprints.append(sprint)
                except Exception:
                    console.print(f"[yellow]Warning:[/yellow] Skipping invalid sprint file: {sprint_file.name}")

    # Load completed sprints
    if not active or load_all:
        completed_dir = gira_root / ".gira" / "sprints" / "completed"
        if completed_dir.exists():
            for sprint_file in completed_dir.glob("*.json"):
                try:
                    sprint = Sprint.model_validate_json(sprint_file.read_text())
                    sprints.append(sprint)
                except Exception:
                    console.print(f"[yellow]Warning:[/yellow] Skipping invalid sprint file: {sprint_file.name}")
    
    # Load planned sprints
    if load_all:
        planned_dir = gira_root / ".gira" / "sprints" / "planned"
        if planned_dir.exists():
            for sprint_file in planned_dir.glob("*.json"):
                try:
                    sprint = Sprint.model_validate_json(sprint_file.read_text())
                    sprints.append(sprint)
                except Exception:
                    console.print(f"[yellow]Warning:[/yellow] Skipping invalid sprint file: {sprint_file.name}")
    
    # Apply query if provided
    if query:
        try:
            parser = QueryParser(query, entity_type="sprint")
            expression = parser.parse()
            
            if expression:
                executor = QueryExecutor(EntityType.SPRINT)
                user_email = get_default_reporter()
                sprints = executor.execute(expression, sprints, user_email=user_email)
        except QueryParseError as e:
            console.print(f"[red]Query Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error executing query:[/red] {e}")
            raise typer.Exit(1)

    # Apply new filter options (only if query is not provided)
    if not query:
        # Apply status filter
        if status:
            # Normalize status values to lowercase
            status_filters = [s.lower() for s in status]
            sprints = [
                s for s in sprints 
                if (s.status.value if hasattr(s.status, 'value') else str(s.status)).lower() in status_filters
            ]
        
        # Apply date filters
        if after:
            try:
                after_date = datetime.strptime(after, "%Y-%m-%d").date()
                sprints = [s for s in sprints if s.start_date >= after_date]
            except ValueError:
                console.print(f"[red]Error:[/red] Invalid date format for --after: {after}. Use YYYY-MM-DD")
                raise typer.Exit(1)
        
        if before:
            try:
                before_date = datetime.strptime(before, "%Y-%m-%d").date()
                sprints = [s for s in sprints if s.end_date <= before_date]
            except ValueError:
                console.print(f"[red]Error:[/red] Invalid date format for --before: {before}. Use YYYY-MM-DD")
                raise typer.Exit(1)
        
        if between:
            try:
                dates = between.split(",")
                if len(dates) != 2:
                    raise ValueError("Expected two dates separated by comma")
                start_date = datetime.strptime(dates[0].strip(), "%Y-%m-%d").date()
                end_date = datetime.strptime(dates[1].strip(), "%Y-%m-%d").date()
                sprints = [
                    s for s in sprints 
                    if s.start_date >= start_date and s.end_date <= end_date
                ]
            except ValueError as e:
                console.print(f"[red]Error:[/red] Invalid date format for --between: {between}. Use YYYY-MM-DD,YYYY-MM-DD")
                raise typer.Exit(1)
        
        # Apply min-tickets filter
        if min_tickets is not None:
            sprints = [s for s in sprints if len(s.tickets) >= min_tickets]

    # Apply legacy filters (only if query is not provided)
    if not query:
        # Apply search filter
        if search is not None:
            # Build search fields based on search_in parameter
            all_search_fields = {
                "name": lambda s: s.name,
                "goal": lambda s: s.goal if s.goal else '',
                "id": lambda s: s.id,
                "status": lambda s: s.status.value if hasattr(s.status, 'value') else str(s.status),
            }
            
            # Determine which fields to search
            if search_in is None or "all" in search_in:
                # Default: search in name and goal only
                search_fields = [
                    all_search_fields["name"],
                    all_search_fields["goal"],
                ]
            else:
                # Use specified fields
                search_fields = []
                for field in search_in:
                    field_lower = field.lower()
                    if field_lower in all_search_fields:
                        search_fields.append(all_search_fields[field_lower])
                    else:
                        console.print(
                            f"[yellow]Warning:[/yellow] Unknown search field '{field}'. "
                            f"Valid fields: {', '.join(sorted(all_search_fields.keys()))}, all"
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
                    sprints, search, search_fields, 
                    search_mode=search_mode,
                    case_sensitive=case_sensitive_search,
                    min_score=0.4
                )
            else:
                # Use regular fuzzy search for backward compatibility
                search_results = search_and_rank(
                    sprints, search, search_fields, min_score=0.4
                )
            
            sprints = [item for item, score in search_results]
    elif any([active, completed, search, status, after, before, between, min_tickets is not None]):
        console.print("[yellow]Warning:[/yellow] Legacy filter options are ignored when using --query")

    if not sprints:
        console.print("[yellow]No sprints found[/yellow]")
        return

    # Sort by start date
    sprints.sort(key=lambda s: s.start_date, reverse=True)
    
    # Validate filter_json is only used with JSON format
    if filter_json and output_format != OutputFormat.JSON:
        console.print("[red]Error:[/red] --filter-json can only be used with --format json")
        raise typer.Exit(1)

    # Output results
    if output_format == OutputFormat.JSON and fields:
        # Apply field selection for JSON output
        sprint_data = [sprint.model_dump(mode='json') for sprint in sprints]
        
        # Expand any aliases in the field list
        expanded_fields = expand_field_aliases(fields)
        
        # Validate fields before filtering
        invalid_fields = validate_fields(sprint_data, expanded_fields)
        if invalid_fields:
            console.print(f"[yellow]Warning:[/yellow] Unknown fields will be ignored: {', '.join(invalid_fields)}")
        
        # Filter the data to include only requested fields
        sprint_data = filter_fields(sprint_data, expanded_fields)
        
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(sprint_data, output_format, jsonpath_filter=filter_json, **color_kwargs)
    elif output_format == OutputFormat.TABLE:
        # Use the existing table display
        show_sprints_table(sprints)
    else:
        # Use the new output system for other formats
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(sprints, output_format, jsonpath_filter=filter_json, **color_kwargs)
