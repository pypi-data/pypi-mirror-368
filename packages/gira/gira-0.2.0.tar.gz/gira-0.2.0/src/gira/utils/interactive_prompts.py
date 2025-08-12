"""Interactive prompt utilities for Gira CLI."""

from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.text import Text

from gira.constants import normalize_ticket_id, get_project_prefix
from gira.models.comment import Comment
from gira.utils.console import console


def prompt_for_entity_id(allow_epic: bool = True) -> str:
    """Prompt user for a ticket or epic ID with number-only support.
    
    Args:
        allow_epic: Whether to allow epic IDs (EPIC-XXX)
        
    Returns:
        Normalized entity ID (e.g., GCM-123 or EPIC-001)
    """
    entity_type = "ticket/epic" if allow_epic else "ticket"
    while True:
        entity_id = Prompt.ask(
            f"Enter {entity_type} ID",
            default=None
        )
        
        if not entity_id:
            console.print("[red]Entity ID is required[/red]")
            continue
            
        # Normalize the ID
        entity_id = entity_id.strip().upper()
        
        # Check if it's an epic
        if entity_id.startswith("EPIC-"):
            if not allow_epic:
                console.print("[red]Epic IDs are not allowed here[/red]")
                continue
            return entity_id
        
        # Try to normalize as ticket ID (handles number-only input)
        try:
            prefix = get_project_prefix()
            normalized_id = normalize_ticket_id(entity_id, prefix)
            return normalized_id
        except Exception as e:
            console.print(f"[red]Invalid ID format: {e}[/red]")
            continue


def display_comments_table(comments: List[Comment], limit: int = 10) -> None:
    """Display a table of comments with truncated content.
    
    Args:
        comments: List of comments to display
        limit: Maximum number of comments to show
    """
    table = Table(title="Comments", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Author", style="green")
    table.add_column("Date", style="yellow")
    table.add_column("Content", style="white")
    table.add_column("Attachments", style="blue", justify="center")
    
    # Sort comments by created_at (newest first) and limit
    sorted_comments = sorted(comments, key=lambda c: c.created_at, reverse=True)[:limit]
    
    for idx, comment in enumerate(sorted_comments, 1):
        # Truncate content to first line, max 50 chars
        content_lines = comment.content.split('\n')
        truncated_content = content_lines[0][:50]
        if len(content_lines) > 1 or len(content_lines[0]) > 50:
            truncated_content += "..."
            
        # Format date
        date_str = comment.created_at.strftime("%Y-%m-%d %H:%M")
        
        # Attachment count
        attachment_count = str(comment.attachment_count) if comment.attachment_count > 0 else "-"
        
        table.add_row(
            str(idx),
            comment.id,
            comment.author,
            date_str,
            truncated_content,
            attachment_count
        )
    
    console.print(table)


def prompt_for_comment_selection(entity, default_latest: bool = True) -> Optional[str]:
    """Prompt user to select a comment from an entity.
    
    Args:
        entity: Ticket or Epic object with comments
        default_latest: Whether to default to the latest comment
        
    Returns:
        Selected comment ID or None if no comments
    """
    comments = entity.comments or []
    
    if not comments:
        console.print("[yellow]No comments found on this entity[/yellow]")
        return None
    
    if len(comments) == 1:
        comment = comments[0]
        console.print(f"\n[green]Using the only comment:[/green] {comment.id} by {comment.author}")
        return comment.id
    
    # Sort comments by created_at (newest first)
    sorted_comments = sorted(comments, key=lambda c: c.created_at, reverse=True)
    
    # Display comments table
    console.print(f"\n[bold]Found {len(comments)} comments:[/bold]")
    display_comments_table(sorted_comments)
    
    # Get default selection
    default_idx = 1 if default_latest else None
    
    # Prompt for selection
    while True:
        choice = IntPrompt.ask(
            "Select comment number",
            default=default_idx,
            choices=[str(i) for i in range(1, min(len(sorted_comments) + 1, 11))]
        )
        
        if 1 <= choice <= len(sorted_comments):
            selected_comment = sorted_comments[choice - 1]
            return selected_comment.id
        else:
            console.print(f"[red]Please select a number between 1 and {len(sorted_comments)}[/red]")


def prompt_for_file_paths() -> List[str]:
    """Prompt user for file paths to attach.
    
    Returns:
        List of validated file paths
    """
    file_paths = []
    
    console.print("\n[bold]Enter file paths to attach[/bold]")
    console.print("[dim]Enter each path and press Enter. Leave empty and press Enter when done.[/dim]")
    
    while True:
        file_path = Prompt.ask("File path", default="")
        
        if not file_path:
            if not file_paths:
                console.print("[red]At least one file is required[/red]")
                continue
            break
            
        # Expand user path
        path = Path(file_path).expanduser()
        
        # Validate path
        if not path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            continue
            
        if not path.is_file():
            console.print(f"[red]Not a file: {file_path}[/red]")
            continue
            
        # Add to list
        file_paths.append(str(path))
        console.print(f"[green]✓[/green] Added: {path.name}")
    
    return file_paths


def prompt_for_confirmation(message: str, default: bool = True) -> bool:
    """Prompt user for yes/no confirmation.
    
    Args:
        message: The confirmation message
        default: Default value if user just presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    return Confirm.ask(message, default=default)