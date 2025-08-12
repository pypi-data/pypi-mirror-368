"""Export tickets to CSV format."""

import csv
from io import StringIO
from pathlib import Path
from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets

def csv_export(
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
    fields: Optional[str] = typer.Option(
        None,
        "--fields",
        help="Comma-separated list of fields to include (default: common fields)"
    ),
    delimiter: str = typer.Option(
        ",",
        "--delimiter",
        help="Field delimiter character (default: comma)"
    ),
    quote_all: bool = typer.Option(
        False,
        "--quote-all",
        help="Quote all fields, not just those containing special characters"
    ),
) -> None:
    """Export project tickets to CSV format.
    
    This command exports all active tickets (and optionally archived tickets)
    to a CSV file. The output is suitable for importing into spreadsheet
    applications like Excel or Google Sheets.
    
    Examples:
        # Export all tickets to stdout
        gira export csv
        
        # Export to a file
        gira export csv --output tickets.csv
        
        # Include archived tickets
        gira export csv --include-archived -o all-tickets.csv
        
        # Export specific fields only
        gira export csv --fields id,title,status,priority,assignee
        
        # Use semicolon as delimiter (for some European locales)
        gira export csv --delimiter ";" -o tickets.csv
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
        
        # Sort by ID for consistent output
        unique_tickets.sort(key=lambda t: t.id)
        
        # Determine fields to export
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            # Default fields for CSV export
            field_list = [
                'id', 'title', 'status', 'priority', 'type', 
                'assignee', 'reporter', 'story_points', 
                'created_at', 'updated_at'
            ]
        
        # Create CSV output
        csv_buffer = StringIO()
        
        # Set up CSV writer with appropriate quoting
        quoting = csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL
        writer = csv.DictWriter(
            csv_buffer, 
            fieldnames=field_list,
            delimiter=delimiter,
            quoting=quoting
        )
        
        # Write header
        writer.writeheader()
        
        # Write ticket data
        for ticket in unique_tickets:
            ticket_dict = ticket.model_dump(mode='json')
            
            # Extract only requested fields
            row_data = {}
            for field in field_list:
                value = ticket_dict.get(field, '')
                
                # Format certain fields for CSV
                if field in ['labels', 'blocked_by', 'blocks', 'children', 'subtasks']:
                    # Convert lists to comma-separated strings
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                elif field in ['created_at', 'updated_at', 'due_date']:
                    # Keep datetime as string
                    if value:
                        value = str(value)
                elif value is None:
                    value = ''
                
                row_data[field] = value
            
            writer.writerow(row_data)
        
        # Get CSV content
        csv_content = csv_buffer.getvalue()
        
        # Write output
        if output:
            # Write to file
            output.write_text(csv_content)
            console.print(f"✅ Exported {len(unique_tickets)} tickets to [cyan]{output}[/cyan]")
        else:
            # Write to stdout
            print(csv_content, end='')
            
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to export tickets: {e}")
        raise typer.Exit(1)