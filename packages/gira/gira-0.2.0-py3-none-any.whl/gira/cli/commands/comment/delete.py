"""Delete comment command for Gira."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.prompt import Confirm

from gira.models.comment import Comment
from gira.utils.project import ensure_gira_project

def delete(
    ticket_id: str = typer.Argument(..., help="Ticket ID"),
    comment_id: str = typer.Argument(..., help="Comment ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (json)"),
) -> None:
    """Delete a comment from a ticket.
    
    Comments are permanently deleted and cannot be restored.
    """
    root = ensure_gira_project()
    
    # Find the comment file
    comment_path = root / ".gira" / "comments" / ticket_id / f"{comment_id}.json"
    
    if not comment_path.exists():
        # Check archive
        archive_path = root / ".gira" / "archive" / "comments" / ticket_id / f"{comment_id}.json"
        if archive_path.exists():
            comment_path = archive_path
        else:
            if output == "json":
                console.print_json(data={"error": f"Comment '{comment_id}' not found for ticket '{ticket_id}'"})
            else:
                console.print(f"[red]Error:[/red] Comment '{comment_id}' not found for ticket '{ticket_id}'")
            raise typer.Exit(1)
    
    # Load the comment
    comment = Comment.from_json_file(str(comment_path))
    
    # Show comment details
    if not force and output != "json":
        # Truncate content for display if too long
        content_preview = comment.content
        if len(content_preview) > 200:
            content_preview = content_preview[:200] + "..."
        
        console.print(Panel(
            f"[bold]Comment ID:[/bold] {comment.id}\n"
            f"[bold]Author:[/bold] {comment.author}\n"
            f"[bold]Created:[/bold] {comment.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold]Content:[/bold]\n{content_preview}",
            title="[red]Comment to Delete[/red]",
            border_style="red"
        ))
        
        if not Confirm.ask("\nAre you sure you want to delete this comment?"):
            raise typer.Exit(0)
    
    # Delete the comment
    comment_path.unlink()
    
    # Remove empty comments directory if this was the last comment
    comments_dir = comment_path.parent
    if comments_dir.exists() and not any(comments_dir.iterdir()):
        comments_dir.rmdir()
    
    if output == "json":
        console.print_json(data={
            "success": True,
            "ticket_id": ticket_id,
            "comment_id": comment_id,
            "message": f"Comment {comment_id} has been deleted"
        })
    else:
        console.print(f"✅ Comment '{comment_id}' has been deleted from ticket '{ticket_id}'", style="green")