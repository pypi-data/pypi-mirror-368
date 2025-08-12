"""Delete comment command for inline comments."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.prompt import Confirm

from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, is_ticket_archived
from gira.utils.epic_utils import find_epic, is_epic_archived

def delete(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or Epic ID (e.g., GCM-123 or EPIC-001)"
    ),
    comment_id: str = typer.Argument(
        ...,
        help="Comment ID to delete"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt"
    ),
) -> None:
    """Delete a comment from a ticket or epic.
    
    Comments are permanently deleted and cannot be restored.
    """
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()
    
    # Determine if this is a ticket or epic based on ID pattern
    entity_id = entity_id.upper()
    is_epic = entity_id.startswith("EPIC-")
    
    # Find the entity (ticket or epic)
    if is_epic:
        entity, entity_path = find_epic(entity_id, gira_root, include_archived=True)
        entity_type = "epic"
    else:
        entity, entity_path = find_ticket(entity_id, gira_root, include_archived=True)
        entity_type = "ticket"
    
    if not entity:
        console.print(f"[red]Error:[/red] {entity_type.capitalize()} {entity_id} not found")
        raise typer.Exit(1)
    
    # Find the comment
    if not entity.comments:
        console.print(f"[red]Error:[/red] No comments found on {entity_type} {entity_id}")
        raise typer.Exit(1)
    
    comment_to_delete = None
    comment_index = None
    
    for i, comment in enumerate(entity.comments):
        if comment.id == comment_id or comment.id.startswith(comment_id):
            comment_to_delete = comment
            comment_index = i
            break
    
    if comment_to_delete is None:
        console.print(f"[red]Error:[/red] Comment '{comment_id}' not found on {entity_type} {entity_id}")
        raise typer.Exit(1)
    
    # Check if entity is archived
    if is_epic:
        is_archived = is_epic_archived(entity_path)
    else:
        is_archived = is_ticket_archived(entity_path)
    
    # Show comment details and confirm
    if not force:
        # Truncate content for display if too long
        content_preview = comment_to_delete.content
        if len(content_preview) > 200:
            content_preview = content_preview[:200] + "..."
        
        console.print(Panel(
            f"[bold]Comment ID:[/bold] {comment_to_delete.id}\n"
            f"[bold]Author:[/bold] {comment_to_delete.author}\n"
            f"[bold]Created:[/bold] {comment_to_delete.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold]Content:[/bold]\n{content_preview}",
            title=f"[red]Comment to Delete from {entity_type.title()} {entity_id}[/red]",
            border_style="red"
        ))
        
        if is_archived:
            console.print(f"\n[yellow]Note: This {entity_type} is archived.[/yellow]")
        
        if not Confirm.ask(f"\nAre you sure you want to delete this comment from {entity_type} {entity_id}?"):
            raise typer.Exit(0)
    
    # Delete the comment
    entity.comments.pop(comment_index)
    entity.comment_count = len(entity.comments)
    
    # Save the updated entity
    from datetime import datetime
    entity.updated_at = datetime.now()
    entity.save_to_json_file(str(entity_path))
    
    console.print(f"✅ Comment '{comment_to_delete.id}' has been deleted from {entity_type} '{entity_id}'", style="green")