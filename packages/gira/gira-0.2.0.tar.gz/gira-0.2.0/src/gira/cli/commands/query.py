"""Consolidated query command for searching Gira data using the query language."""

import json
from pathlib import Path
from typing import List, Optional, Union

import typer
from gira.utils.console import console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typer import Argument, Context, Option

from gira.models.comment import Comment
from gira.models.epic import Epic
from gira.models.sprint import Sprint
from gira.models.ticket import Ticket
from gira.models.saved_query import SavedQuery
from gira.query import EntityType, QueryExecutor, QueryParser
from gira.query.parser import QueryParseError
from gira.utils.config import get_default_reporter
from gira.utils.errors import require_project
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
# Color functions are implemented locally in this module
from gira.utils.project import get_gira_root, ensure_gira_project
from gira.utils.saved_queries import resolve_query_string, load_saved_query
from gira.utils.help_formatter import create_example, format_examples_simple

# Create query app for subcommands
query_app = typer.Typer(
    name="query",
    help="Execute queries and manage saved queries",
    add_completion=True,
    rich_markup_mode="markdown"
)

def _format_date(dt) -> str:
    """Format a datetime for display."""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M")
    return "-"


def status_color(status: str) -> str:
    """Return colored status string for tickets."""
    colors = {
        "backlog": "[dim]Backlog[/dim]",
        "todo": "[blue]Todo[/blue]",
        "in_progress": "[yellow]In Progress[/yellow]",
        "review": "[magenta]Review[/magenta]",
        "done": "[green]Done[/green]",
    }
    return colors.get(status.lower(), status)


# Default command that handles direct query execution
@query_app.command("", hidden=True)  # Empty string means this is the default command
def default_query_command(
    query_string: str = typer.Argument(..., help="Query expression to execute or saved query name"),
    entity: str = Option(
        "ticket",
        "--entity", "-e",
        help="Type of entity to search",
    ),
    output_format: OutputFormat = add_format_option(),
    limit: Optional[int] = Option(
        None,
        "--limit", "-l",
        help="Maximum number of results to return",
    ),
    offset: int = Option(
        0,
        "--offset", "-o",
        help="Number of results to skip",
    ),
    sort: Optional[str] = Option(
        None,
        "--sort", "-s",
        help="Sort results by field (e.g., 'created_at:desc' or 'priority:asc')",
    ),
    filter_json: Optional[str] = Option(
        None,
        "--filter-json",
        help="JSONPath expression to filter JSON output (e.g., '$[?(@.priority==\"high\")].id')",
    ),
    no_header: bool = Option(
        False,
        "--no-header",
        help="Don't show table header (useful for scripting)",
    ),
    verbose: bool = Option(
        False,
        "--verbose", "-v",
        help="Show detailed error messages",
    ),
    save: Optional[str] = Option(
        None,
        "--save",
        help="Save query with given name (prompts for description if name provided but no -d)",
    ),
    description: Optional[str] = Option(
        None,
        "--description", "-d",
        help="Description for saved query (used with --save)",
    ),
    force: bool = Option(
        False,
        "--force",
        help="Overwrite existing saved query (used with --save)",
    ),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Execute a query directly - this is the default behavior when no subcommand is specified."""
    execute_query_command(
        query_string=query_string,
        entity=entity,
        output_format=output_format,
        limit=limit,
        offset=offset,
        sort=sort,
        filter_json=filter_json,
        no_header=no_header,
        verbose=verbose,
        save=save,
        description=description,
        force=force,
        color=color,
        no_color=no_color,
    )


# Simple callback for subcommand group
@query_app.callback()
def query_callback():
    """Execute queries and manage saved queries.
    
    Examples:
        gira query "status:in_progress AND priority:high"
        gira query "owner:me()" --entity epic
        gira query "created_at:>days_ago(7)"
        gira query "type:bug" --format ids
        gira query "epic_id:EPIC-001" --format json
        gira query @my-bugs
        gira query high-priority --entity ticket
        gira query "type:bug AND priority:high" --save "critical-bugs" -d "All critical bugs"
        gira query "assignee:me()" --save "my-tickets"
        gira query "type:feature" --format json --filter-json '$[?(@.priority=="high")].id'
        gira query "status:done" --format json --filter-json '$[*]{id: id, title: title}'
        
    Subcommands:
        gira query list    # List saved queries
        gira query show    # Show saved query details
        gira query delete  # Delete saved query
        gira query edit    # Edit saved query
    """
    pass

# Direct query execution command 
@query_app.command(name="exec", help="Execute a query directly")
def execute_query_command(
    query_string: str = Argument(..., help="Query expression to execute or saved query name"),
    entity: str = Option(
        "ticket",
        "--entity", "-e",
        help="Type of entity to search",
    ),
    output_format: OutputFormat = add_format_option(),
    limit: Optional[int] = Option(
        None,
        "--limit", "-l",
        help="Maximum number of results to return",
    ),
    offset: int = Option(
        0,
        "--offset", "-o",
        help="Number of results to skip",
    ),
    sort: Optional[str] = Option(
        None,
        "--sort", "-s",
        help="Sort results by field (e.g., 'created_at:desc' or 'priority:asc')",
    ),
    filter_json: Optional[str] = Option(
        None,
        "--filter-json",
        help="JSONPath expression to filter JSON output (e.g., '$[?(@.priority==\"high\")].id')",
    ),
    no_header: bool = Option(
        False,
        "--no-header",
        help="Don't show table header (useful for scripting)",
    ),
    verbose: bool = Option(
        False,
        "--verbose", "-v",
        help="Show detailed error messages",
    ),
    save: Optional[str] = Option(
        None,
        "--save",
        help="Save query with given name (prompts for description if name provided but no -d)",
    ),
    description: Optional[str] = Option(
        None,
        "--description", "-d",
        help="Description for saved query (used with --save)",
    ),
    force: bool = Option(
        False,
        "--force",
        help="Overwrite existing saved query (used with --save)",
    ),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Execute a query against Gira data.

    QUERY_STRING is the query expression to execute or saved query name.
    
    Examples:
        gira query "status:in_progress AND priority:high"
        gira query "owner:me()" --entity epic
        gira query "created_at:>days_ago(7)"
        gira query "type:bug" --format ids
        gira query "epic_id:EPIC-001" --format json
        gira query @my-bugs
        gira query high-priority --entity ticket
        gira query "type:bug AND priority:high" --save "critical-bugs" -d "All critical bugs"
        gira query "assignee:me()" --save "my-tickets"
        gira query "type:feature" --format json --filter-json '$[?(@.priority=="high")].id'
        gira query "status:done" --format json --filter-json '$[*]{id: id, title: title}'
    """
    # This is now a dedicated command for query execution
    
    project_root = get_gira_root()
    require_project(project_root, output_format)

    try:
        # Handle saving query if --save is specified
        if save:
            # Validate the query syntax before saving
            try:
                parser = QueryParser(query_string, entity_type=entity.lower())
                parser.parse()  # This will raise an error if the query is invalid
            except QueryParseError as e:
                console.print(f"[red]Invalid query syntax:[/red] {e}")
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Error validating query:[/red] {e}")
                raise typer.Exit(1)
            
            # Create saved queries directory if it doesn't exist
            queries_dir = project_root / ".gira" / "saved-queries"
            queries_dir.mkdir(exist_ok=True)
            
            # Check if query with this name already exists
            query_file = queries_dir / f"{save}.json"
            if query_file.exists() and not force:
                console.print(f"[red]Error:[/red] A query named '{save}' already exists. Use --force to overwrite.")
                raise typer.Exit(1)
            
            # Prompt for description if not provided and save wasn't just a flag
            query_description = description
            if not query_description and save != "":
                query_description = typer.prompt("Description (optional)", default="", show_default=False)
                if not query_description:
                    query_description = None
            
            # Create the saved query
            try:
                saved_query = SavedQuery(
                    name=save,
                    query=query_string,
                    description=query_description,
                    entity_type=entity.lower(),
                    author=get_default_reporter()
                )
            except ValueError as e:
                console.print(f"[red]Invalid query name:[/red] {e}")
                raise typer.Exit(1)
            
            # Save to file
            try:
                saved_query.save_to_json_file(str(query_file))
            except Exception as e:
                console.print(f"[red]Error saving query:[/red] {e}")
                raise typer.Exit(1)
            
            # Success message
            console.print(f"[green]✓[/green] Saved query '{save}' to {query_file.relative_to(project_root)}")
            console.print(f"[dim]Use with:[/dim] gira query {save}")
            
            if query_description:
                console.print(f"[dim]Description:[/dim] {query_description}")
        
        # Resolve saved query references (e.g., @my-bugs or my-bugs)
        try:
            resolved_query = resolve_query_string(query_string, entity_type=entity)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        
        # Parse the query
        entity_type = EntityType[entity.upper()]
        parser = QueryParser(resolved_query, entity_type=entity.lower())
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Parsing query...", total=None)
            expression = parser.parse()

        # Load entities
        entities = _load_entities(project_root, entity_type)
        
        
        if not entities:
            console.print(f"No {entity}s found")
            return

        # Execute query
        executor = QueryExecutor(entity_type)
        user_email = get_default_reporter()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"Searching {len(entities)} {entity}s...", total=None)
            results = executor.execute(expression, entities, user_email=user_email)
            

        # Apply sorting
        if sort:
            results = _sort_results(results, sort)

        # Apply pagination
        total_results = len(results)
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]

        # Display results
        if not results:
            console.print(f"No {entity}s match the query")
            return

        # Validate filter_json is only used with JSON format
        if filter_json and output_format != OutputFormat.JSON:
            console.print("[red]Error:[/red] --filter-json can only be used with --format json")
            raise typer.Exit(1)

        if output_format == OutputFormat.JSON:
            color_kwargs = get_color_kwargs(color, no_color)
            print_output(results, output_format, jsonpath_filter=filter_json, **color_kwargs)
        elif output_format == OutputFormat.IDS:
            print_output(results, output_format)
        elif output_format == OutputFormat.TABLE:
            _output_table(results, entity_type, no_header, total_results, offset, limit)
        else:
            # Use the new output system for other formats
            print_output(results, output_format)

    except QueryParseError as e:
        console.print(f"[red]Query Error:[/red] {e}")
        if verbose:
            console.print(f"\nQuery: {query_string}")
            if hasattr(e, 'position'):
                console.print(f"Position: {' ' * e.position}^")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


def _load_entities(
    project_root: Path, entity_type: EntityType
) -> List[Union[Ticket, Epic, Sprint, Comment]]:
    """Load all entities of the specified type."""
    entities = []
    
    
    if entity_type == EntityType.TICKET:
        # Load from all ticket directories  
        seen_ids = set()  # Track loaded IDs to avoid duplicates
        
        # Try to load board configuration to get dynamic swimlanes
        from gira.models.board import Board
        board_config_path = project_root / ".gira" / ".board.json"
        if board_config_path.exists():
            board = Board.from_json_file(str(board_config_path))
            status_dirs = [swimlane.id for swimlane in board.swimlanes]
        else:
            # Fall back to checking what directories actually exist
            board_dir = project_root / ".gira" / "board"
            if board_dir.exists():
                status_dirs = [d.name for d in board_dir.iterdir() if d.is_dir()]
            else:
                # Ultimate fallback to default statuses
                status_dirs = ["todo", "in_progress", "review", "done"]
        
        # Always check backlog separately as it might not be a swimlane
        all_dirs = ["backlog"] + status_dirs if "backlog" not in status_dirs else status_dirs
        
        for status_dir in all_dirs:
            # Check both possible locations - with and without 'board' subdirectory
            board_path = project_root / ".gira" / "board" / status_dir
            direct_path = project_root / ".gira" / status_dir
            
            for dir_path in [board_path, direct_path]:
                if dir_path.exists():
                    for file_path in dir_path.glob("*.json"):
                        try:
                            with open(file_path) as f:
                                data = json.load(f)
                                ticket_id = data.get("id")
                                if ticket_id and ticket_id not in seen_ids:
                                    entities.append(Ticket(**data))
                                    seen_ids.add(ticket_id)
                        except Exception:
                            continue  # Skip invalid files
    
    elif entity_type == EntityType.EPIC:
        epics_dir = project_root / ".gira" / "epics"
        if epics_dir.exists():
            for file_path in epics_dir.glob("*.json"):
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        entities.append(Epic(**data))
                except Exception:
                    continue
    
    elif entity_type == EntityType.SPRINT:
        sprints_dir = project_root / ".gira" / "sprints"
        for subdir in ["active", "completed", "planned"]:
            dir_path = sprints_dir / subdir
            if dir_path.exists():
                for file_path in dir_path.glob("*.json"):
                    try:
                        with open(file_path) as f:
                            data = json.load(f)
                            entities.append(Sprint(**data))
                    except Exception:
                        continue
    
    elif entity_type == EntityType.COMMENT:
        comments_dir = project_root / ".gira" / "comments"
        if comments_dir.exists():
            for ticket_dir in comments_dir.iterdir():
                if ticket_dir.is_dir():
                    for file_path in ticket_dir.glob("*.json"):
                        try:
                            with open(file_path) as f:
                                data = json.load(f)
                                entities.append(Comment(**data))
                        except Exception:
                            continue
    
    return entities


def _sort_results(
    results: List[Union[Ticket, Epic, Sprint, Comment]], sort_spec: str
) -> List[Union[Ticket, Epic, Sprint, Comment]]:
    """Sort results by the specified field and direction."""
    parts = sort_spec.split(":")
    field = parts[0]
    reverse = len(parts) > 1 and parts[1].lower() == "desc"
    
    # Priority order mapping for proper sorting
    priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    
    def get_sort_key(item):
        value = getattr(item, field, "")
        
        # Special handling for priority field
        if field == "priority" and isinstance(value, str):
            return priority_order.get(value.lower(), 0)
        
        # For other fields, use string comparison
        return value
    
    try:
        return sorted(results, key=get_sort_key, reverse=reverse)
    except Exception:
        # If sorting fails, return unsorted
        return results


def _output_json(results: List[Union[Ticket, Epic, Sprint, Comment]]) -> None:
    """Output results as JSON."""
    output = [r.model_dump(mode="json") for r in results]
    console.print_json(data=output)


def _output_ids(results: List[Union[Ticket, Epic, Sprint, Comment]]) -> None:
    """Output just the IDs, one per line."""
    for result in results:
        print(result.id)


def _output_table(
    results: List[Union[Ticket, Epic, Sprint, Comment]],
    entity_type: EntityType,
    no_header: bool,
    total_results: int,
    offset: int,
    limit: Optional[int],
) -> None:
    """Output results as a formatted table."""
    table = Table(show_header=not no_header)
    
    # Define columns based on entity type
    if entity_type == EntityType.TICKET:
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", max_width=40)
        table.add_column("Status", no_wrap=True)
        table.add_column("Priority", no_wrap=True)
        table.add_column("Type", no_wrap=True)
        table.add_column("Assignee", max_width=20)
        
        for ticket in results:
            table.add_row(
                ticket.id,
                ticket.title,
                status_color(ticket.status),
                _priority_color(ticket.priority),
                ticket.type,
                ticket.assignee or "-",
            )
    
    elif entity_type == EntityType.EPIC:
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", max_width=40)
        table.add_column("Status", no_wrap=True)
        table.add_column("Owner", max_width=20)
        table.add_column("Tickets", no_wrap=True)
        table.add_column("Updated", no_wrap=True)
        
        for epic in results:
            table.add_row(
                epic.id,
                epic.title,
                _epic_status_color(epic.status),
                epic.owner or "-",
                str(len(epic.tickets)),
                _format_date(epic.updated_at),
            )
    
    elif entity_type == EntityType.SPRINT:
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", max_width=30)
        table.add_column("Status", no_wrap=True)
        table.add_column("Start", no_wrap=True)
        table.add_column("End", no_wrap=True)
        table.add_column("Goal", max_width=40)
        
        for sprint in results:
            table.add_row(
                sprint.id,
                sprint.name,
                _sprint_status_color(sprint.status),
                str(sprint.start_date) if sprint.start_date else "-",
                str(sprint.end_date) if sprint.end_date else "-",
                sprint.goal or "-",
            )
    
    elif entity_type == EntityType.COMMENT:
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Ticket", no_wrap=True)
        table.add_column("Author", max_width=20)
        table.add_column("Created", no_wrap=True)
        table.add_column("Content", max_width=50)
        
        for comment in results:
            content_preview = comment.content[:50] + "..." if len(comment.content) > 50 else comment.content
            table.add_row(
                comment.id,
                comment.ticket_id,
                comment.author,
                _format_date(comment.created_at),
                content_preview,
            )
    
    console.print(table)
    
    # Show pagination info
    if total_results > len(results):
        shown = len(results)
        if offset > 0:
            console.print(f"\n[dim]Showing results {offset + 1}-{offset + shown} of {total_results}[/dim]")
        else:
            console.print(f"\n[dim]Showing first {shown} of {total_results} results[/dim]")


def _priority_color(priority: str) -> str:
    """Return colored priority string."""
    colors = {
        "critical": "[red]Critical[/red]",
        "high": "[yellow]High[/yellow]",
        "medium": "[blue]Medium[/blue]",
        "low": "[dim]Low[/dim]",
    }
    return colors.get(priority.lower(), priority)


def _epic_status_color(status: str) -> str:
    """Return colored epic status string."""
    colors = {
        "draft": "[dim]Draft[/dim]",
        "active": "[green]Active[/green]",
        "completed": "[blue]Completed[/blue]",
        "abandoned": "[red]Abandoned[/red]",
    }
    return colors.get(status.lower(), status)


def _sprint_status_color(status: str) -> str:
    """Return colored sprint status string."""
    colors = {
        "planned": "[dim]Planned[/dim]",
        "active": "[green]Active[/green]",
        "completed": "[blue]Completed[/blue]",
    }
    return colors.get(status.lower(), status)


# Subcommands for query management

@query_app.command("list")
def list_saved_queries(
    entity: Optional[str] = typer.Option(
        None,
        "--entity",
        "-e",
        help="Filter by entity type (ticket, epic, sprint, comment)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information including descriptions"
    ),
    output_format: OutputFormat = add_format_option(),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List all saved queries.
    
    Examples:
        gira query list
        gira query list --entity epic
        gira query list --verbose
    """
    project_root = get_gira_root()
    if not project_root:
        console.print("[red]❌ Not in a Gira project[/red]")
        raise typer.Exit(1)
    
    queries_dir = project_root / ".gira" / "saved-queries"
    if not queries_dir.exists():
        console.print("[yellow]No saved queries found.[/yellow]")
        console.print("\nCreate your first saved query with:")
        console.print("  [cyan]gira query \"<expression>\" --save <name>[/cyan]")
        return
    
    # Load all saved queries
    queries = []
    for query_file in queries_dir.glob("*.json"):
        try:
            query = SavedQuery.from_json_file(str(query_file))
            if entity is None or query.entity_type == entity:
                queries.append(query)
        except Exception as e:
            console.print(f"[red]Warning: Failed to load {query_file.name}: {e}[/red]")
    
    if not queries:
        if entity:
            console.print(f"[yellow]No saved queries found for entity type '{entity}'.[/yellow]")
        else:
            console.print("[yellow]No saved queries found.[/yellow]")
        return
    
    # Sort by name
    queries.sort(key=lambda q: q.name)
    
    # Handle different output formats
    if output_format == OutputFormat.JSON:
        # Output as JSON for machine processing
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(queries, output_format, **color_kwargs)
    else:
        # Create table for human-readable output
        table = Table(
            title="Saved Queries" if not entity else f"Saved Queries ({entity})",
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Query", style="yellow")
        table.add_column("Entity", style="blue")
        
        if verbose:
            table.add_column("Description", style="white")
            table.add_column("Author", style="magenta")
            table.add_column("Created", style="dim")
        
        # Add rows
        for query in queries:
            row = [
                query.get_display_name(),
                query.query,
                query.entity_type
            ]
            
            if verbose:
                row.extend([
                    query.description or "-",
                    query.author,
                    query.created_at.strftime("%Y-%m-%d %H:%M")
                ])
            
            table.add_row(*row)
        
        console.print(table)
        
        # Show usage hint
        console.print(f"\n[dim]Use saved queries with:[/dim]")
        console.print(f"  [cyan]gira query {queries[0].get_display_name()}[/cyan]")


@query_app.command("show")
def show_saved_query(
    name: str = typer.Argument(..., help="Name of the saved query to show"),
    output_format: OutputFormat = add_format_option(),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Show details of a saved query.
    
    Examples:
        gira query show my-bugs
        gira query show high-priority --format json
    """
    # Load the saved query
    saved_query = load_saved_query(name)
    if not saved_query:
        console.print(f"[red]Error:[/red] Saved query '{name}' not found")
        console.print("\nUse [cyan]gira query list[/cyan] to see available saved queries")
        raise typer.Exit(1)
    
    if output_format == OutputFormat.JSON:
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(saved_query, output_format, **color_kwargs)
    else:
        # Create detailed display
        table = Table(title=f"Saved Query: {saved_query.name}", show_header=False)
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Name", saved_query.name)
        table.add_row("Query", saved_query.query)
        table.add_row("Entity Type", saved_query.entity_type)
        table.add_row("Description", saved_query.description or "-")
        table.add_row("Author", saved_query.author)
        table.add_row("Created", saved_query.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Updated", saved_query.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(table)
        
        # Show usage examples
        console.print(f"\n[dim]Usage examples:[/dim]")
        console.print(f"  [cyan]gira query {saved_query.name}[/cyan]")
        console.print(f"  [cyan]gira query @{saved_query.name}[/cyan]")


@query_app.command("delete")
def delete_saved_query(
    name: str = typer.Argument(..., help="Name of the saved query to delete"),
    force: bool = typer.Option(
        False,
        "--force",
        help="Don't ask for confirmation"
    )
) -> None:
    """Delete a saved query.
    
    Examples:
        gira query delete my-old-query
        gira query delete unused-query --force
    """
    project_root = get_gira_root()
    if not project_root:
        console.print("[red]❌ Not in a Gira project[/red]")
        raise typer.Exit(1)
    
    queries_dir = project_root / ".gira" / "saved-queries"
    query_file = queries_dir / f"{name}.json"
    
    if not query_file.exists():
        console.print(f"[red]Error:[/red] Saved query '{name}' not found")
        console.print("\nUse [cyan]gira query list[/cyan] to see available saved queries")
        raise typer.Exit(1)
    
    # Load query to show what we're deleting
    try:
        saved_query = SavedQuery.from_json_file(str(query_file))
    except Exception as e:
        console.print(f"[red]Error loading query:[/red] {e}")
        raise typer.Exit(1)
    
    # Confirm deletion unless --force
    if not force:
        console.print(f"[yellow]About to delete saved query:[/yellow]")
        console.print(f"  Name: {saved_query.name}")
        console.print(f"  Query: {saved_query.query}")
        console.print(f"  Entity: {saved_query.entity_type}")
        if saved_query.description:
            console.print(f"  Description: {saved_query.description}")
        console.print()
        
        confirm = typer.confirm("Are you sure you want to delete this query?")
        if not confirm:
            console.print("Cancelled")
            return
    
    # Delete the file
    try:
        query_file.unlink()
        console.print(f"[green]✓[/green] Deleted saved query '{name}'")
    except Exception as e:
        console.print(f"[red]Error deleting query:[/red] {e}")
        raise typer.Exit(1)


@query_app.command("edit")
def edit_saved_query(
    name: str = typer.Argument(..., help="Name of the saved query to edit"),
) -> None:
    """Edit a saved query (interactive).
    
    Examples:
        gira query edit my-bugs
        gira query edit high-priority
    """
    project_root = get_gira_root()
    if not project_root:
        console.print("[red]❌ Not in a Gira project[/red]")
        raise typer.Exit(1)
    
    queries_dir = project_root / ".gira" / "saved-queries"
    query_file = queries_dir / f"{name}.json"
    
    if not query_file.exists():
        console.print(f"[red]Error:[/red] Saved query '{name}' not found")
        console.print("\nUse [cyan]gira query list[/cyan] to see available saved queries")
        raise typer.Exit(1)
    
    # Load existing query
    try:
        saved_query = SavedQuery.from_json_file(str(query_file))
    except Exception as e:
        console.print(f"[red]Error loading query:[/red] {e}")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Editing saved query '{name}'[/cyan]")
    console.print()
    
    # Interactive editing
    new_query = typer.prompt("Query", default=saved_query.query)
    new_description = typer.prompt("Description", default=saved_query.description or "", show_default=False)
    new_entity_type = typer.prompt("Entity type", default=saved_query.entity_type)
    
    # Validate the new query syntax
    try:
        parser = QueryParser(new_query, entity_type=new_entity_type.lower())
        parser.parse()
    except QueryParseError as e:
        console.print(f"[red]Invalid query syntax:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error validating query:[/red] {e}")
        raise typer.Exit(1)
    
    # Update the saved query
    saved_query.query = new_query
    saved_query.description = new_description if new_description else None
    saved_query.entity_type = new_entity_type.lower()
    
    # Save the updated query
    try:
        saved_query.save_to_json_file(str(query_file))
        console.print(f"[green]✓[/green] Updated saved query '{name}'")
    except Exception as e:
        console.print(f"[red]Error saving query:[/red] {e}")
        raise typer.Exit(1)