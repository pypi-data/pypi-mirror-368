"""List epics command for Gira."""

from pathlib import Path
from typing import List, Optional

import typer
from gira.utils.console import console
from rich.table import Table

from gira.models import Epic
from gira.query import EntityType, QueryExecutor, QueryParser
from gira.query.parser import QueryParseError
from gira.utils.config import get_default_reporter
from gira.utils.field_selection import expand_field_aliases, filter_fields, validate_fields
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.search import search_and_rank
from gira.utils.advanced_search import SearchMode, advanced_search_and_rank

def load_all_epics(root: Path) -> List[Epic]:
    """Load all epics from the project."""
    epics_dir = root / ".gira" / "epics"
    epics = []

    if epics_dir.exists():
        for epic_file in epics_dir.glob("EPIC-*.json"):
            try:
                epic = Epic.from_json_file(str(epic_file))
                epics.append(epic)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Failed to load {epic_file.name}: {e}")

    return epics


def show_epic_counts(epics: List[Epic]) -> None:
    """Show summary counts of epics."""
    status_counts = {}
    owner_counts = {}

    for epic in epics:
        # Count by status
        status = epic.status
        status_counts[status] = status_counts.get(status, 0) + 1

        # Count by owner
        owner = epic.owner
        owner_counts[owner] = owner_counts.get(owner, 0) + 1

    # Display counts
    console.print("\n[bold]Epic Summary[/bold]")
    console.print(f"Total epics: {len(epics)}")

    if status_counts:
        console.print("\n[bold]By Status:[/bold]")
        for status, count in sorted(status_counts.items()):
            console.print(f"  {status.title()}: {count}")

    if owner_counts:
        console.print("\n[bold]By Owner:[/bold]")
        for owner, count in sorted(owner_counts.items()):
            console.print(f"  {owner}: {count}")


def show_epics_table(epics: List[Epic]) -> None:
    """Display epics in a table format."""
    table = Table(show_header=True, header_style="bold magenta")

    # Add columns
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Owner", style="green")
    table.add_column("Target Date", style="blue")
    table.add_column("Tickets", style="magenta", justify="right")

    # Add rows
    for epic in epics:
        status_style = {
            "draft": "yellow",
            "active": "green",
            "completed": "blue"
        }.get(epic.status, "white")

        table.add_row(
            epic.id,
            epic.title[:50] + ("..." if len(epic.title) > 50 else ""),
            f"[{status_style}]{epic.status.title()}[/{status_style}]",
            epic.owner,
            str(epic.target_date) if epic.target_date else "-",
            str(epic.ticket_count())
        )

    console.print(table)


def list_epics(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query expression (e.g., 'status:active AND owner:me()')"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (draft, active, completed)"),
    owner: Optional[str] = typer.Option(None, "--owner", "-o", help="Filter by owner email"),
    search: Optional[str] = typer.Option(None, "--search", help="Search text in epic fields (default: title and description)"),
    search_in: Optional[list[str]] = typer.Option(None, "--search-in", help="Specify fields to search: title, description, id, status, owner, all (can be used multiple times)"),
    exact_match: bool = typer.Option(False, "--exact-match", help="Perform exact string match instead of fuzzy match"),
    regex_search: bool = typer.Option(False, "--regex-search", help="Treat search pattern as a regular expression"),
    case_sensitive_search: bool = typer.Option(False, "--case-sensitive-search", help="Make search case-sensitive"),
    output_format: OutputFormat = add_format_option(),
    counts: bool = typer.Option(False, "--counts", help="Show summary counts"),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated list of fields to include in JSON output (e.g., 'id,title,status' or use aliases like 'epic_basics')"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression to filter JSON output (e.g., '$[?(@.status==\"active\")].id')"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List epics with optional filters.
    
    Examples:
        # Using query language (recommended)
        gira epic list --query "status:active AND owner:me()"
        gira epic list --query "title:~'*frontend*'"
        gira epic list --query "created_at:>days_ago(30)"
        
        # Using legacy filters (still supported)
        gira epic list --status active --owner john@example.com
        
        # Using field selection with JSON output
        gira epic list --format json --fields "id,title,status"
        gira epic list --format json --fields "epic_basics,tickets"
        
        # Using JSONPath filtering (requires --format json)
        gira epic list --format json --filter-json '$[?(@.status=="active")].id'
        gira epic list --format json --filter-json '$[?(@.ticket_count>5)]'
        gira epic list --format json --filter-json '$[*].{id: id, title: title}'
        
        # Using field-specific text search
        gira epic list --search "frontend" --search-in title
        gira epic list --search "john" --search-in owner
        gira epic list --search "014" --search-in id
        gira epic list --search "api" --search-in title --search-in description
        gira epic list --search "active" --search-in status
    """
    root = ensure_gira_project()

    # Load all epics
    epics = load_all_epics(root)
    
    # Apply query if provided
    if query:
        try:
            parser = QueryParser(query, entity_type="epic")
            expression = parser.parse()
            
            if expression:
                executor = QueryExecutor(EntityType.EPIC)
                user_email = get_default_reporter()
                epics = executor.execute(expression, epics, user_email=user_email)
        except QueryParseError as e:
            console.print(f"[red]Query Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error executing query:[/red] {e}")
            raise typer.Exit(1)

    # Apply legacy filters (only if query is not provided)
    if not query:
        if status:
            status_lower = status.lower()
            epics = [e for e in epics if e.status == status_lower]

        if owner:
            epics = [e for e in epics if e.owner == owner]

        if search is not None:
            # Build search fields based on search_in parameter
            all_search_fields = {
                "title": lambda e: e.title,
                "description": lambda e: e.description,
                "owner": lambda e: e.owner if e.owner else '',
                "status": lambda e: e.status,
                "id": lambda e: e.id,
            }
            
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
                    epics, search, search_fields, 
                    search_mode=search_mode,
                    case_sensitive=case_sensitive_search,
                    min_score=0.4
                )
            else:
                # Use regular fuzzy search for backward compatibility
                search_results = search_and_rank(
                    epics, search, search_fields, min_score=0.4
                )
            
            epics = [item for item, score in search_results]
    elif any([status, owner, search]):
        console.print("[yellow]Warning:[/yellow] Legacy filter options are ignored when using --query")

    # Sort epics by ID
    epics.sort(key=lambda e: int(e.id.split("-")[1]))

    # Show counts if requested
    if counts:
        show_epic_counts(epics)
        return

    # Handle no epics
    if not epics:
        console.print("No epics found")
        return

    # Validate filter_json is only used with JSON format
    if filter_json and output_format != OutputFormat.JSON:
        console.print("[red]Error:[/red] --filter-json can only be used with --format json")
        raise typer.Exit(1)

    # Output results
    if output_format == OutputFormat.JSON and fields:
        # Apply field selection for JSON output
        epic_data = [e.model_dump(mode='json') for e in epics]
        
        # Expand any aliases in the field list
        expanded_fields = expand_field_aliases(fields)
        
        # Validate fields before filtering
        invalid_fields = validate_fields(epic_data, expanded_fields)
        if invalid_fields:
            console.print(f"[yellow]Warning:[/yellow] Unknown fields will be ignored: {', '.join(invalid_fields)}")
        
        # Filter the data to include only requested fields
        epic_data = filter_fields(epic_data, expanded_fields)
        
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(epic_data, output_format, jsonpath_filter=filter_json, **color_kwargs)
    elif output_format == OutputFormat.TABLE:
        # Use the existing table display
        show_epics_table(epics)
    else:
        # Use the new output system for other formats
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(epics, output_format, jsonpath_filter=filter_json, **color_kwargs)
