"""Export tickets to Markdown format."""

from io import StringIO
from pathlib import Path
from typing import Optional, List

import typer
from gira.utils.console import console
from gira.models import Ticket
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets

def markdown_export(
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. If not specified, outputs to stdout",
    ),
    include_archived: bool = typer.Option(
        False,
        "--include-archived",
        help="Include archived tickets in the export",
    ),
    fields: Optional[str] = typer.Option(
        None,
        "--fields",
        help="Comma-separated list of fields to include (default: common fields)",
    ),
) -> None:
    """Export project tickets to Markdown format.

    The command exports all active tickets (and optionally archived tickets)
    to a Markdown table. The output can be written to stdout or saved to a file.
    """
    root = ensure_gira_project()

    try:
        tickets = load_all_tickets(root, include_archived=include_archived)

        seen_ids = set()
        unique_tickets: List[Ticket] = []
        for ticket in tickets:
            if ticket.id not in seen_ids:
                seen_ids.add(ticket.id)
                unique_tickets.append(ticket)

        unique_tickets.sort(key=lambda t: t.id)

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
        else:
            field_list = [
                'id', 'title', 'status', 'priority', 'type',
                'assignee', 'reporter', 'story_points',
                'created_at', 'updated_at'
            ]

        buffer = StringIO()

        header_row = '| ' + ' | '.join(field_list) + ' |\n'
        separator_row = '|' + '|'.join([' --- ' for _ in field_list]) + '|\n'
        buffer.write(header_row)
        buffer.write(separator_row)

        for ticket in unique_tickets:
            ticket_dict = ticket.model_dump(mode='json')
            row_values = []
            for field in field_list:
                value = ticket_dict.get(field, '')
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                elif value is None:
                    value = ''
                else:
                    value = str(value).replace('\n', '<br>')
                row_values.append(value)
            buffer.write('| ' + ' | '.join(row_values) + ' |\n')

        md_content = buffer.getvalue()

        if output:
            output.write_text(md_content)
            console.print(f"✅ Exported {len(unique_tickets)} tickets to [cyan]{output}[/cyan]")
        else:
            print(md_content, end='')

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to export tickets: {e}")
        raise typer.Exit(1)
