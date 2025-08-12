"""Save query command for Gira."""

from pathlib import Path
from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from gira.models.saved_query import SavedQuery
from gira.query import QueryParser
from gira.query.parser import QueryParseError
from gira.utils.config import get_default_reporter
from gira.utils.project import ensure_gira_project

def query_save(
    name: str = typer.Argument(..., help="Name for the saved query"),
    query_string: str = typer.Argument(..., help="Query expression to save"),
    description: Optional[str] = typer.Option(
        None,
        "--description", "-d",
        help="Description of what the query returns"
    ),
    entity_type: str = typer.Option(
        "ticket",
        "--entity", "-e",
        help="Entity type the query targets"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Overwrite existing query with the same name"
    ),
) -> None:
    """Save a query expression for later reuse.
    
    Examples:
        gira query-save high-bugs "type:bug AND priority:high"
        gira query-save my-tasks "assignee:me() AND status:todo" -d "My open tasks"
        gira query-save active-epics "status:active" --entity epic
        gira query-save my-tasks "assignee:me() AND status:in_progress" --force
    """
    root = ensure_gira_project()
    
    # Validate the query syntax before saving
    try:
        parser = QueryParser(query_string, entity_type=entity_type.lower())
        parser.parse()  # This will raise an error if the query is invalid
    except QueryParseError as e:
        console.print(f"[red]Invalid query syntax:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error validating query:[/red] {e}")
        raise typer.Exit(1)
    
    # Create saved queries directory if it doesn't exist
    queries_dir = root / ".gira" / "saved-queries"
    queries_dir.mkdir(exist_ok=True)
    
    # Check if query with this name already exists
    query_file = queries_dir / f"{name}.json"
    if query_file.exists() and not force:
        console.print(f"[red]Error:[/red] A query named '{name}' already exists. Use --force to overwrite.")
        raise typer.Exit(1)
    
    # Create the saved query
    try:
        saved_query = SavedQuery(
            name=name,
            query=query_string,
            description=description,
            entity_type=entity_type.lower(),
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
    console.print(f"[green]✓[/green] Saved query '{name}' to {query_file.relative_to(root)}")
    console.print(f"[dim]Use with:[/dim] gira query @{name}")
    console.print(f"[dim]      or:[/dim] gira ticket list --query @{name}")
    
    if description:
        console.print(f"[dim]Description:[/dim] {description}")