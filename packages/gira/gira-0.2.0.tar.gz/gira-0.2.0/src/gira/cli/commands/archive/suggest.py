"""Suggest tickets to archive based on various criteria."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.table import Table

from gira.utils.archive import archive_ticket
from gira.utils.auto_archive import suggest_archivable_tickets
from gira.utils.config_utils import load_config
from gira.utils.project import ensure_gira_project

def suggest(
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute the suggestions (archive the tickets)"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category: old_done, completed_epics, completed_sprints, stale_backlog"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of suggestions per category"),
) -> None:
    """Suggest tickets to archive based on various criteria."""
    root = ensure_gira_project()
    
    # Load config to get suggestion days
    config = load_config(root)
    done_days = config.get("archive.suggest_done_after_days", 30)
    stale_days = config.get("archive.suggest_stale_after_days", 90)
    
    # Get suggestions
    suggestions = suggest_archivable_tickets(root)
    
    # Filter by category if specified
    if category:
        if category not in suggestions:
            console.print(f"[red]Invalid category:[/red] {category}")
            console.print("Available categories: old_done, completed_epics, completed_sprints, stale_backlog")
            raise typer.Exit(1)
        suggestions = {category: suggestions[category]}
    
    # Display suggestions
    total_count = sum(len(items) for items in suggestions.values())
    
    if total_count == 0:
        console.print("[green]✓[/green] No tickets need archiving at this time!")
        return
    
    console.print(f"\n[bold]Found {total_count} tickets that could be archived:[/bold]\n")
    
    for category_name, items in suggestions.items():
        if not items:
            continue
            
        # Limit items
        display_items = items[:limit]
        hidden_count = len(items) - len(display_items)
        
        # Create table for this category
        table = Table(
            title=get_category_title(category_name, done_days, stale_days),
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Status", style="yellow")
        table.add_column("Reason", style="dim")
        
        for item in display_items:
            ticket = item["ticket"]
            table.add_row(
                ticket.id,
                ticket.title[:50] + "..." if len(ticket.title) > 50 else ticket.title,
                ticket.status,
                item["reason"]
            )
        
        if hidden_count > 0:
            table.add_row(
                "...",
                f"[dim]({hidden_count} more tickets)[/dim]",
                "",
                ""
            )
        
        console.print(table)
        console.print()
    
    # Execute if requested
    if execute:
        if not typer.confirm(f"\nArchive {total_count} tickets?"):
            raise typer.Exit(0)
        
        archived_count = 0
        for items in suggestions.values():
            for item in items:
                try:
                    archive_ticket(item["ticket"])
                    archived_count += 1
                except Exception as e:
                    console.print(f"[red]Failed to archive {item['ticket'].id}:[/red] {e}")
        
        console.print(f"\n[green]✓[/green] Archived {archived_count} tickets")
    else:
        console.print(Panel(
            "[yellow]To archive these tickets, run:[/yellow]\n"
            "gira archive suggest --execute",
            title="Next Step",
            border_style="yellow"
        ))


def get_category_title(category: str, done_days: int, stale_days: int) -> str:
    """Get a human-readable title for a category."""
    titles = {
        "old_done": f"Old Done Tickets ({done_days}+ days)",
        "completed_epics": "Tickets from Completed Epics",
        "completed_sprints": "Tickets from Completed Sprints",
        "stale_backlog": f"Stale Backlog Tickets ({stale_days}+ days)"
    }
    return titles.get(category, category.replace("_", " ").title())