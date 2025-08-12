"""Show ticket command for Gira."""

from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.display import show_ticket_details
from gira.utils.errors import require_ticket
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.typer_completion import complete_ticket_ids

def show(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show", autocompletion=complete_ticket_ids),
    output_format: OutputFormat = add_format_option(OutputFormat.TEXT),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON (shorthand for --format json)"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression to filter JSON output (e.g., '$.title')"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Show details of a specific ticket.
    
    Examples:
        # Show ticket details
        gira ticket show GCM-123
        
        # Export as JSON
        gira ticket show GCM-123 --format json
        gira ticket show GCM-123 --json
        
        # Export as JSON with JSONPath filtering
        gira ticket show GCM-123 --json --filter-json '$.title'
        gira ticket show GCM-123 --format json --filter-json '$.comments[*].content'
    """
    root = ensure_gira_project()

    # Handle --json flag as shorthand for --format json
    if json_output:
        output_format = OutputFormat.JSON

    # Find the ticket (including archived)
    ticket, ticket_path = find_ticket(ticket_id, root, include_archived=True)

    # Handle not found using standardized error handling
    require_ticket(ticket_id.upper(), ticket, output_format)
    
    # Validate filter_json is only used with JSON format
    if filter_json and output_format != OutputFormat.JSON:
        console.print("[red]Error:[/red] --filter-json can only be used with --format json or --json")
        raise typer.Exit(1)

    # Output in requested format
    if output_format in [OutputFormat.TEXT, OutputFormat.TABLE]:
        # Use the existing detailed display
        show_ticket_details(ticket, ticket_path, root)
    else:
        # Use the new output system for other formats
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(ticket, output_format, jsonpath_filter=filter_json, **color_kwargs)
