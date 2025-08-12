"""List saved queries command."""

from pathlib import Path
from typing import Optional

import typer
from gira.utils.console import console
from rich.table import Table

from gira.models.saved_query import SavedQuery
from gira.utils.project import get_gira_root
from gira.utils.output import OutputFormat, print_output, add_format_option

def query_list(
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
    output_format: OutputFormat = add_format_option()
) -> None:
    """List all saved queries.
    
    Examples:
        gira query-list
        gira query-list --entity epic
        gira query-list --verbose
    """
    project_root = get_gira_root()
    if not project_root:
        console.print("[red]❌ Not in a Gira project[/red]")
        raise typer.Exit(1)
    
    queries_dir = project_root / ".gira" / "saved-queries"
    if not queries_dir.exists():
        console.print("[yellow]No saved queries found.[/yellow]")
        console.print("\nCreate your first saved query with:")
        console.print("  [cyan]gira query-save <name> <query>[/cyan]")
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
        print_output(queries, output_format)
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
        console.print(f"  [cyan]gira ticket list --query {queries[0].get_display_name()}[/cyan]")