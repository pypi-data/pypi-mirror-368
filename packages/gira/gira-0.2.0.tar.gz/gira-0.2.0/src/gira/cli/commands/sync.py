"""Sync command for detecting and resolving conflicts."""

import typer
from gira.utils.console import console
from gira.utils.conflict_resolution import sync_project
from gira.utils.project import ensure_gira_project

def sync(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be changed without making changes"),
) -> None:
    """Detect and resolve ticket ID conflicts from merge operations."""
    root = ensure_gira_project()
    
    console.print("🔄 Syncing Gira project...", style="bold cyan")
    console.print()
    
    # Sync conflicts
    sync_project(root, dry_run=dry_run)
    
    if not dry_run:
        console.print()
        console.print("✅ Sync completed successfully!", style="bold green")
    else:
        console.print()
        console.print("ℹ️  Run without --dry-run to apply changes", style="dim")