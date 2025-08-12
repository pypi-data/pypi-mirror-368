"""Delete sprint command for Gira."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.prompt import Confirm

from gira.models.sprint import Sprint
from gira.utils.git_ops import should_use_git, move_with_git_fallback, remove_with_git_fallback
from gira.utils.project import ensure_gira_project

def delete(
    sprint_id: str = typer.Argument(..., help="Sprint ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    permanent: bool = typer.Option(False, "--permanent", "-p", help="Permanently delete instead of archiving"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (json)"),
    git: Optional[bool] = typer.Option(None, "--git/--no-git", help="Stage the archive/delete using 'git mv' or 'git rm'"),
) -> None:
    """Delete or archive a sprint.
    
    By default, sprints are archived (moved to .gira/archive/) and can be restored later.
    Use --permanent to permanently delete the sprint.
    
    Note: Tickets associated with the sprint are NOT deleted, only the sprint itself.
    
    Git Integration:
        By default, archive/delete operations are automatically staged with 'git mv' or 'git rm' if .gira is tracked.
        Control this behavior with:
        - --git / --no-git flags
        - GIRA_AUTO_GIT_MV environment variable
        - git.auto_stage_archives or git.auto_stage_deletes in config.json
    """
    root = ensure_gira_project()
    
    # Determine whether to use git operations
    use_git = should_use_git(root, git, "archive" if not permanent else "delete")
    
    # Find the sprint file - check in subdirectories
    current_path = None
    sprint_dirs = [
        root / ".gira" / "sprints" / "active",
        root / ".gira" / "sprints" / "completed",
        root / ".gira" / "sprints" / "planned",
        root / ".gira" / "archive" / "sprints"
    ]
    
    for sprint_dir in sprint_dirs:
        potential_path = sprint_dir / f"{sprint_id}.json"
        if potential_path.exists():
            current_path = potential_path
            break
    
    if not current_path:
        if output == "json":
            console.print_json(data={"error": f"Sprint '{sprint_id}' not found"})
        else:
            console.print(f"[red]Error:[/red] Sprint '{sprint_id}' not found")
        raise typer.Exit(1)
    
    # Load the sprint
    sprint = Sprint.from_json_file(str(current_path))
    
    # Show sprint details and what will be affected
    if not force and output != "json":
        console.print(Panel(
            f"[bold]{sprint.id}[/bold] - {sprint.name}\n"
            f"Status: {sprint.status}\n"
            f"Goal: {sprint.goal or 'None'}\n"
            f"Start Date: {sprint.start_date or 'Not set'}\n"
            f"End Date: {sprint.end_date or 'Not set'}\n"
            f"Tickets: {len(sprint.tickets)} ticket(s)",
            title="[red]Sprint to Delete[/red]",
            border_style="red"
        ))
        
        if sprint.status == "active":
            console.print(f"\n[yellow]Warning:[/yellow] This sprint is currently active!")
        
        if sprint.tickets:
            console.print(f"\n[yellow]Note:[/yellow] The {len(sprint.tickets)} ticket(s) in this sprint will NOT be deleted.")
        
        action = "permanently delete" if permanent else "archive"
        if not Confirm.ask(f"\nAre you sure you want to {action} this sprint?"):
            raise typer.Exit(0)
    
    # Delete or archive the sprint
    if permanent:
        # Delete sprint file
        remove_with_git_fallback(current_path, root, use_git)
        action_msg = "permanently deleted"
    else:
        # Archive the sprint
        archive_dir = root / ".gira" / "archive" / "sprints"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Move sprint to archive
        archive_path = archive_dir / f"{sprint_id}.json"
        move_with_git_fallback(current_path, archive_path, root, use_git)
        action_msg = "archived"
    
    if output == "json":
        console.print_json(data={
            "success": True,
            "sprint_id": sprint_id,
            "action": "deleted" if permanent else "archived",
            "tickets_count": len(sprint.tickets),
            "message": f"Sprint {sprint_id} has been {action_msg}"
        })
    else:
        console.print(f"✅ Sprint '{sprint_id}' has been {action_msg}", style="green")
        if sprint.tickets:
            console.print(f"   {len(sprint.tickets)} ticket(s) remain unaffected")