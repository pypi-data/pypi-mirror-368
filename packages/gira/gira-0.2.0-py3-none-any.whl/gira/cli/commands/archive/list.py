"""List archived tickets."""

from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.table import Table

from gira.utils.archive import get_archive_stats, list_archived_tickets
from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project

def show_archived_table(archived_tickets, month=None, search=None, limit=None):
    """Display archived tickets in a table format."""
    title = f"Archived Tickets ({len(archived_tickets)})"
    if month:
        title += f" - {month}"
    if search:
        title += f" - matching '{search}'"

    table = Table(title=title)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Type", style="blue")
    table.add_column("Priority")
    table.add_column("Archived From")
    table.add_column("Archive Date", style="dim")
    table.add_column("Month", style="magenta")

    for ticket in archived_tickets:
        priority_style = {
            "critical": "red",
            "high": "yellow",
            "medium": "blue",
            "low": "green"
        }.get(ticket.get("priority", "medium"), "white")

        archived_at = ticket.get("archived_at", "")
        if archived_at:
            # Format the date nicely
            try:
                archived_at = archived_at.split("T")[0]
            except (AttributeError, IndexError):
                pass

        table.add_row(
            ticket["id"],
            ticket["title"],
            ticket.get("type", "task"),
            f"[{priority_style}]{ticket.get('priority', 'medium')}[/{priority_style}]",
            ticket.get("archived_from", "-"),
            archived_at,
            ticket["month"]
        )

    console.print(table)

    if limit and len(archived_tickets) == limit:
        console.print(f"\n[dim]Showing first {limit} tickets[/dim]")


def list_archived(
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Show tickets from specific month (YYYY-MM)"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search in ticket title and description"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of tickets to show"),
    output_format: OutputFormat = add_format_option(),
    stats: bool = typer.Option(False, "--stats", help="Show archive statistics"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression to filter JSON output (e.g., '$[?(@.priority==\"high\")].id')"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List archived tickets with optional filtering.
    
    Examples:
        gira archive list
        gira archive list --month 2025-01
        gira archive list --search "bug fix"
        gira archive list --stats
        gira archive list --format json --filter-json '$[?(@.type=="bug")].id'
        gira archive list --format json --filter-json '$[*].{id: id, title: title, month: month}'
    """
    ensure_gira_project()

    try:
        # Show statistics if requested
        if stats:
            archive_stats = get_archive_stats()

            console.print("\n[bold]Archive Statistics[/bold]")
            console.print(f"Total archived tickets: {archive_stats['total_archived']}")
            console.print(f"Archive months: {archive_stats['months']}")

            if archive_stats['by_month'] and isinstance(archive_stats['by_month'], dict):
                console.print("\nTickets by month:")
                for month, count in sorted(archive_stats['by_month'].items(), reverse=True):
                    console.print(f"  {month}: {count}")
            return

        # Get archived tickets
        archived_tickets = list_archived_tickets(month=month, search=search, limit=limit)

        if not archived_tickets:
            if month:
                console.print(f"[yellow]No archived tickets found for {month}[/yellow]")
            elif search:
                console.print(f"[yellow]No archived tickets matching '{search}'[/yellow]")
            else:
                console.print("[yellow]No archived tickets found[/yellow]")
            return
        
        # Validate filter_json is only used with JSON format
        if filter_json and output_format != OutputFormat.JSON:
            console.print("[red]Error:[/red] --filter-json can only be used with --format json")
            raise typer.Exit(1)

        # Output based on format
        if output_format == OutputFormat.TABLE:
            # Use the existing table display
            show_archived_table(archived_tickets, month, search, limit)
        else:
            # Use the new output system for other formats
            color_kwargs = get_color_kwargs(color, no_color)
            print_output(archived_tickets, output_format, jsonpath_filter=filter_json, **color_kwargs)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
