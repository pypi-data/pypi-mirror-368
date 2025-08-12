"""Cache management commands for Gira."""

import typer
from gira.utils.console import console
from rich.table import Table

from gira.utils.cache import (
    clear_cache,
    clear_git_cache,
    clear_blame_cache,
    get_git_cache_stats,
    get_blame_cache_stats,
    invalidate_ticket_cache,
    invalidate_git_cache_for_ticket
)
from gira.utils.metrics_cache import get_metrics_cache, clear_metrics_cache

def clear(
        all: bool = typer.Option(False, "--all", help="Clear all caches including git and blame caches"),
        git: bool = typer.Option(False, "--git", help="Clear only git-related cache"),
        blame: bool = typer.Option(False, "--blame", help="Clear only blame-related cache"),
        tickets: bool = typer.Option(False, "--tickets", help="Clear only ticket-related cache"),
        metrics: bool = typer.Option(False, "--metrics", help="Clear only metrics cache"),
        ticket_id: str = typer.Option(None, "--ticket-id", help="Clear cache for a specific ticket")
):
    """Clear cached data."""
    if not any([all, git, blame, tickets, metrics, ticket_id]):
        console.print(
            "[red]Error:[/red] Please specify what to clear: --all, --git, --blame, --tickets, --metrics, or --ticket-id")
        return

    if all:
        clear_cache()
        clear_git_cache()
        clear_blame_cache()
        clear_metrics_cache()
        console.print("[green]✓[/green] Cleared all caches")
    else:
        if git:
            clear_git_cache()
            console.print("[green]✓[/green] Cleared git cache")

        if blame:
            clear_blame_cache()
            console.print("[green]✓[/green] Cleared blame cache")

        if tickets:
            invalidate_ticket_cache()
            console.print("[green]✓[/green] Cleared ticket cache")
            
        if metrics:
            clear_metrics_cache()
            console.print("[green]✓[/green] Cleared metrics cache")

        if ticket_id:
            invalidate_git_cache_for_ticket(ticket_id)
            console.print(f"[green]✓[/green] Cleared cache for ticket {ticket_id}")


def _create_cache_stats_table(title: str, stats: dict) -> Table:
    """Create a cache statistics table.
    
    Args:
        title: Title for the table
        stats: Dictionary containing cache statistics
        
    Returns:
        Populated Rich Table
    """
    table = Table(title=title, show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Cache Size", f"{stats['size']} / {stats['max_size']}")
    table.add_row("Cache Hits", str(stats['hits']))
    table.add_row("Cache Misses", str(stats['misses']))
    table.add_row("Hit Rate", stats['hit_rate'])
    table.add_row("Total Requests", str(stats['total_requests']))
    
    return table


def status():
    """Show cache statistics."""
    git_stats = get_git_cache_stats()
    blame_stats = get_blame_cache_stats()
    metrics_stats = get_metrics_cache().get_stats()

    # Git Cache Table
    git_table = _create_cache_stats_table("Git Cache Statistics", git_stats)
    console.print(git_table)

    # Blame Cache Table
    console.print()  # Add spacing
    blame_table = _create_cache_stats_table("Blame Cache Statistics", blame_stats)
    console.print(blame_table)
    
    # Metrics Cache Table
    console.print()  # Add spacing
    metrics_table = Table(title="Metrics Cache Statistics", show_header=True)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    
    metrics_table.add_row("Cached Tickets", str(metrics_stats['cached_tickets']))
    metrics_table.add_row("Total Size", f"{metrics_stats['total_size_mb']} MB")
    metrics_table.add_row("Cache Directory", metrics_stats['cache_directory'])
    
    console.print(metrics_table)

    if git_stats['size'] > 0 or blame_stats['size'] > 0 or metrics_stats['cached_tickets'] > 0:
        console.print("\n[dim]Tips:[/dim]")
        if git_stats['size'] > 0:
            console.print("[dim]  • Use 'gira cache clear --git' to clear the git cache[/dim]")
        if blame_stats['size'] > 0:
            console.print("[dim]  • Use 'gira cache clear --blame' to clear the blame cache[/dim]")
        if metrics_stats['cached_tickets'] > 0:
            console.print("[dim]  • Use 'gira cache clear --metrics' to clear the metrics cache[/dim]")
