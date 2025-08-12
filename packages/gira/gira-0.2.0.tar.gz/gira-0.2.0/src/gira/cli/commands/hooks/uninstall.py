"""Uninstall Git hooks for Gira integration."""

from typing import List, Optional

import typer
from gira.utils.console import console
from rich.prompt import Confirm

from gira.utils.git_utils import is_git_repository
from gira.utils.project import ensure_gira_project

def uninstall(
    hooks: Optional[List[str]] = typer.Option(
        None,
        "--hook",
        "-h",
        help="Specific hooks to uninstall (can be used multiple times). If not specified, uninstalls all Gira hooks."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Remove hooks without prompting"),
) -> None:
    """Uninstall Git hooks for Gira integration.
    
    This command removes Git hooks installed by Gira and optionally restores backups.
    
    Examples:
        # Uninstall all Gira hooks
        gira hooks uninstall
        
        # Uninstall specific hooks
        gira hooks uninstall --hook commit-msg
        
        # Force removal without prompts
        gira hooks uninstall --force
    """
    root = ensure_gira_project()
    
    # Check if we're in a git repository
    if not is_git_repository():
        console.print("[red]Error:[/red] Not in a Git repository.")
        raise typer.Exit(1)
    
    # Available hooks
    available_hooks = ["commit-msg", "prepare-commit-msg"]
    
    # Determine which hooks to uninstall
    if hooks:
        # Validate requested hooks
        invalid_hooks = [h for h in hooks if h not in available_hooks]
        if invalid_hooks:
            console.print(f"[red]Error:[/red] Unknown hooks: {', '.join(invalid_hooks)}")
            console.print(f"Available hooks: {', '.join(available_hooks)}")
            raise typer.Exit(1)
        hooks_to_uninstall = hooks
    else:
        hooks_to_uninstall = available_hooks
    
    # Git hooks directory
    git_dir = root / ".git"
    hooks_dir = git_dir / "hooks"
    
    if not hooks_dir.exists():
        console.print("[yellow]No hooks directory found[/yellow]")
        raise typer.Exit(0)
    
    removed_count = 0
    restored_count = 0
    
    for hook_name in hooks_to_uninstall:
        hook_path = hooks_dir / hook_name
        backup_path = hook_path.with_suffix(f"{hook_path.suffix}.backup")
        
        if not hook_path.exists():
            continue
        
        # Check if this is a Gira hook by looking for our marker
        try:
            content = hook_path.read_text()
            if "Gira" not in content:
                console.print(f"[yellow]Skipped:[/yellow] {hook_name} (not a Gira hook)")
                continue
        except Exception:
            continue
        
        # Confirm removal
        if not force:
            if not Confirm.ask(f"Remove '{hook_name}' hook?", default=True):
                console.print(f"[yellow]Skipped:[/yellow] {hook_name}")
                continue
        
        # Remove the hook
        hook_path.unlink()
        removed_count += 1
        
        # Restore backup if it exists
        if backup_path.exists():
            backup_path.rename(hook_path)
            console.print(f"[green]✓[/green] Removed {hook_name} hook and restored backup")
            restored_count += 1
        else:
            console.print(f"[green]✓[/green] Removed {hook_name} hook")
    
    if removed_count > 0:
        console.print(f"\n[green]Successfully removed {removed_count} hook(s)[/green]")
        if restored_count > 0:
            console.print(f"[green]Restored {restored_count} backup(s)[/green]")
    else:
        console.print("[yellow]No Gira hooks found to remove[/yellow]")