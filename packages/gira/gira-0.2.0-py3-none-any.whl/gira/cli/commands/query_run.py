"""Run saved queries command."""

from typing import Optional

import typer
from gira.utils.console import console
from gira.cli.commands.query import execute_query_command
from gira.utils.output import OutputFormat, add_format_option
from gira.utils.saved_queries import load_saved_query
from gira.utils.help_formatter import create_example, format_examples_simple

def query_run(
    name: str = typer.Argument(
        ...,
        help="Name of the saved query to run (with or without @ prefix)"
    ),
    output_format: OutputFormat = add_format_option(),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Maximum number of results to return",
    ),
    offset: int = typer.Option(
        0,
        "--offset", "-o",
        help="Number of results to skip",
    ),
    sort: Optional[str] = typer.Option(
        None,
        "--sort", "-s",
        help="Sort results by field (e.g., 'created_at:desc' or 'priority:asc')",
    ),
    filter_json: Optional[str] = typer.Option(
        None,
        "--filter-json",
        help="JSONPath expression to filter JSON output",
    ),
    no_header: bool = typer.Option(
        False,
        "--no-header",
        help="Don't show table header (useful for scripting)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed error messages",
    ),
) -> None:
    f"""Run a saved query by name.
    
    This is an explicit way to execute saved queries. You can also use
    saved queries directly with 'gira query @name' or 'gira ticket list --query @name'.
    {format_examples_simple([
        create_example(
            "Run a saved query by name",
            "gira query-run my-bugs"
        ),
        create_example(
            "Run saved query with JSON output",
            "gira query-run high-priority --format json"
        ),
        create_example(
            "Run saved query with result limit",
            "gira query-run active-epics --limit 10"
        )
    ])}
    """
    # Load the saved query
    saved_query = load_saved_query(name)
    if not saved_query:
        console.print(f"[red]Error:[/red] Saved query '{name}' not found")
        console.print("\nUse [cyan]gira query-list[/cyan] to see available saved queries")
        raise typer.Exit(1)
    
    # Show what query is being executed
    console.print(f"[dim]Running saved query '{saved_query.name}': {saved_query.query}[/dim]")
    if saved_query.description:
        console.print(f"[dim]Description: {saved_query.description}[/dim]")
    console.print()
    
    # Execute the query using the existing query command
    execute_query_command(
        query_string=saved_query.query,
        entity=saved_query.entity_type,
        output_format=output_format,
        limit=limit,
        offset=offset,
        sort=sort,
        filter_json=filter_json,
        no_header=no_header,
        verbose=verbose,
        save=None,
        description=None,
        force=False,
        color=True,
        no_color=False
    )