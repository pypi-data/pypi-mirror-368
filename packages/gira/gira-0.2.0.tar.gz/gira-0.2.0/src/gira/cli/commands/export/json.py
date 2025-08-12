"""Export tickets to JSON format."""

import json
from pathlib import Path
from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets

def json_export(
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file path. If not specified, outputs to stdout"
    ),
    include_archived: bool = typer.Option(
        False,
        "--include-archived",
        help="Include archived tickets in the export"
    ),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        help="Pretty-print JSON output with indentation"
    ),
    fields: Optional[str] = typer.Option(
        None,
        "--fields",
        help="Comma-separated list of fields to include (default: all fields)"
    ),
) -> None:
    """Export project tickets to JSON format.
    
    This command exports all active tickets (and optionally archived tickets)
    to a JSON file or stdout. The output is a JSON array containing ticket objects.
    
    Examples:
        # Export all tickets to stdout
        gira export json
        
        # Export to a file
        gira export json --output tickets.json
        
        # Include archived tickets
        gira export json --include-archived -o all-tickets.json
        
        # Pretty-print the output
        gira export json --pretty
        
        # Export only specific fields
        gira export json --fields id,title,status,priority
    """
    root = ensure_gira_project()
    
    try:
        # Get all tickets
        tickets = load_all_tickets(root, include_archived=include_archived)
        
        # Deduplicate tickets by ID (in case of hybrid storage duplicates)
        seen_ids = set()
        unique_tickets = []
        for ticket in tickets:
            if ticket.id not in seen_ids:
                seen_ids.add(ticket.id)
                unique_tickets.append(ticket)
        
        # Convert tickets to dictionaries
        ticket_dicts = []
        for ticket in unique_tickets:
            ticket_dict = ticket.model_dump(mode='json')
            
            # Filter fields if specified
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                ticket_dict = {k: v for k, v in ticket_dict.items() if k in field_list}
            
            ticket_dicts.append(ticket_dict)
        
        # Sort by ID for consistent output
        ticket_dicts.sort(key=lambda t: t.get('id', ''))
        
        # Prepare JSON output
        indent = 2 if pretty else None
        json_output = json.dumps(ticket_dicts, indent=indent, default=str)
        
        # Write output
        if output:
            # Write to file
            output.write_text(json_output + '\n')
            console.print(f"✅ Exported {len(unique_tickets)} tickets to [cyan]{output}[/cyan]")
        else:
            # Write to stdout
            print(json_output)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to export tickets: {e}")
        raise typer.Exit(1)