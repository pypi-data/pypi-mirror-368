"""Show status of Git hooks for Gira integration."""

import typer
from gira.utils.console import console
from rich.table import Table

from gira.utils.git_utils import is_git_repository
from gira.utils.project import ensure_gira_project

def status() -> None:
    """Show the status of Git hooks for Gira integration.
    
    This command displays which Git hooks are installed and whether they are
    Gira-managed hooks.
    
    Example:
        gira hooks status
    """
    root = ensure_gira_project()
    
    # Check if we're in a git repository
    if not is_git_repository():
        console.print("[red]Error:[/red] Not in a Git repository.")
        raise typer.Exit(1)
    
    # Git hooks directory
    git_dir = root / ".git"
    hooks_dir = git_dir / "hooks"
    
    # Available Gira hooks
    gira_hooks = ["commit-msg", "prepare-commit-msg"]
    
    # Create status table
    table = Table(
        title="Git Hooks Status",
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Hook", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Type")
    table.add_column("Backup", style="dim")
    
    for hook_name in gira_hooks:
        hook_path = hooks_dir / hook_name
        backup_path = hook_path.with_suffix(f"{hook_path.suffix}.backup")
        
        if hook_path.exists():
            # Check if it's a Gira hook
            try:
                content = hook_path.read_text()
                is_gira = "Gira" in content
                hook_type = "Gira" if is_gira else "Custom"
                status = "✓ Installed"
                style = "green" if is_gira else "yellow"
            except Exception:
                hook_type = "Unknown"
                status = "? Error reading"
                style = "red"
                
            backup_status = "Yes" if backup_path.exists() else "No"
        else:
            hook_type = "-"
            status = "Not installed"
            style = "dim"
            backup_status = "Yes" if backup_path.exists() else "-"
        
        table.add_row(
            hook_name,
            status,
            hook_type,
            backup_status,
            style=style
        )
    
    console.print(table)
    
    # Show additional information
    console.print("\n[dim]Gira hooks validate commit messages and can add ticket ID templates.[/dim]")
    console.print("[dim]Use 'gira hooks install' to install hooks.[/dim]")
    console.print("[dim]Use 'gira hooks uninstall' to remove hooks.[/dim]")