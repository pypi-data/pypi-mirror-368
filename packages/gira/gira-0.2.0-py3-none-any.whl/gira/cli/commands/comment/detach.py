"""Remove attachments from comments."""

from datetime import datetime
from pathlib import Path
from typing import Optional, List

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from gira.utils.comment_attachments import (
    list_comment_attachments,
    find_comment_in_entity,
    remove_comment_attachment,
    update_comment_attachment_count
)
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.epic_utils import find_epic
from gira.storage.utils import format_bytes


def detach(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or Epic ID (e.g., GCM-123 or EPIC-001)"
    ),
    comment_id: str = typer.Argument(
        ...,
        help="Comment ID to remove attachments from"
    ),
    filenames: Optional[List[str]] = typer.Argument(
        None,
        help="Filename(s) to remove (if not specified, use --all)"
    ),
    all_attachments: bool = typer.Option(
        False,
        "--all", "-a",
        help="Remove all attachments from the comment"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt"
    ),
) -> None:
    f"""Remove attachments from a comment.
    
    Note: This only removes the pointer files from the repository.
    The actual files in external storage are not deleted.
    {format_examples_simple([
        create_example("Remove a specific attachment", "gira comment detach GCM-123 20250729-123456 screenshot.png.yml"),
        create_example("Remove multiple attachments", "gira comment detach GCM-123 20250729-123456 file1.yml file2.yml"),
        create_example("Remove all attachments", "gira comment detach GCM-123 20250729-123456 --all"),
        create_example("Skip confirmation", "gira comment detach GCM-123 20250729-123456 --all --force")
    ])}"""
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()
    
    # Validate arguments
    if not filenames and not all_attachments:
        console.print("[red]Error:[/red] Specify filenames or use --all flag")
        raise typer.Exit(1)
    
    if filenames and all_attachments:
        console.print("[red]Error:[/red] Cannot specify both filenames and --all")
        raise typer.Exit(1)
    
    # Determine entity type
    entity_id = entity_id.upper()
    is_epic = entity_id.startswith("EPIC-")
    entity_type = "epic" if is_epic else "ticket"
    
    # Find the entity
    if is_epic:
        entity, entity_path = find_epic(entity_id, gira_root, include_archived=True)
    else:
        entity, entity_path = find_ticket(entity_id, gira_root, include_archived=True)
    
    if not entity:
        console.print(f"[red]Error:[/red] {entity_type.capitalize()} {entity_id} not found")
        raise typer.Exit(1)
    
    # Find the comment
    comment = find_comment_in_entity(entity, comment_id)
    if not comment:
        console.print(f"[red]Error:[/red] Comment {comment_id} not found in {entity_type} {entity_id}")
        raise typer.Exit(1)
    
    # Get current attachments
    attachments = list_comment_attachments(entity_type, entity_id, comment_id, gira_root)
    if not attachments:
        console.print(f"[yellow]No attachments found for comment {comment_id}[/yellow]")
        raise typer.Exit(0)
    
    # Determine which files to remove
    files_to_remove = []
    if all_attachments:
        files_to_remove = [(att.get_pointer_filename(), att) for att in attachments]
    else:
        # Match filenames
        attachment_map = {att.get_pointer_filename(): att for att in attachments}
        for filename in filenames:
            if filename in attachment_map:
                files_to_remove.append((filename, attachment_map[filename]))
            else:
                console.print(f"[yellow]Warning:[/yellow] Attachment not found: {filename}")
    
    if not files_to_remove:
        console.print("[yellow]No matching attachments to remove[/yellow]")
        raise typer.Exit(0)
    
    # Show what will be removed
    table = Table(title="Attachments to Remove")
    table.add_column("Filename", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Uploaded By")
    table.add_column("Uploaded At")
    
    total_size = 0
    for filename, att in files_to_remove:
        table.add_row(
            att.file_name,
            att.get_display_size(),
            att.added_by,
            att.uploaded_at.strftime("%Y-%m-%d %H:%M")
        )
        total_size += att.size
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(files_to_remove)} file(s), {format_bytes(total_size)}[/dim]")
    
    # Confirm removal
    if not force:
        if not Confirm.ask(
            f"Remove {len(files_to_remove)} attachment(s) from comment?",
            default=False
        ):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)
    
    # Remove the attachments
    removed_count = 0
    for filename, _ in files_to_remove:
        if remove_comment_attachment(entity_type, entity_id, comment_id, filename, gira_root):
            removed_count += 1
        else:
            console.print(f"[red]Error:[/red] Failed to remove {filename}")
    
    # Update comment
    if removed_count > 0:
        update_comment_attachment_count(comment, entity_type, entity_id, gira_root)
        
        # Update entity timestamp
        entity.updated_at = datetime.now()
        entity.save_to_json_file(str(entity_path))
        
        # Show success message
        console.print(Panel(
            f"[green]✓[/green] Removed {removed_count} attachment(s) from comment {comment_id}",
            title="Attachments Removed",
            border_style="green"
        ))
        
        # Show remaining attachments
        remaining = len(attachments) - removed_count
        if remaining > 0:
            console.print(f"\n[dim]Comment still has {remaining} attachment(s)[/dim]")
        else:
            console.print("\n[dim]Comment has no more attachments[/dim]")
    else:
        console.print("[red]Error:[/red] No attachments were removed")
        raise typer.Exit(1)