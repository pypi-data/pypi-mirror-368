"""Add comment to ticket command."""

import hashlib
import mimetypes
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from gira.models.comment import Comment
from gira.models.attachment import AttachmentPointer, StorageProvider
from gira.storage import get_storage_backend
from gira.storage.exceptions import StorageError
from gira.utils.config import get_default_reporter
from gira.utils.config_utils import load_config
from gira.utils.credentials import CredentialsManager
from gira.utils.comment_attachments import (
    get_comment_attachments_dir,
    generate_comment_attachment_key,
    update_comment_attachment_count
)
from gira.utils.mention_utils import format_content_with_mentions, get_mentioned_members
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, is_ticket_archived
from gira.utils.epic_utils import find_epic, is_epic_archived
from gira.utils.typer_completion import complete_ticket_or_epic_ids

def _format_bytes(size: int) -> str:
    """Format byte size to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def add(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or Epic ID to add comment to (e.g., GCM-123 or EPIC-001)",
        autocompletion=complete_ticket_or_epic_ids
    ),
    content: Optional[str] = typer.Option(
        None,
        "-c", "--content",
        help="Comment content"
    ),
    content_file: Optional[str] = typer.Option(
        None,
        "--content-file",
        help="Read comment content from a file"
    ),
    editor: bool = typer.Option(
        False,
        "-e", "--editor",
        help="Open editor for comment"
    ),
    attach: Optional[List[str]] = typer.Option(
        None,
        "--attach", "-a",
        help="Attach file(s) to the comment (can be used multiple times)"
    ),
) -> None:
    """Add a comment to a ticket or epic."""
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

    # Check for mutually exclusive content options
    if content and content_file:
        console.print("[red]Error:[/red] Cannot use both --content and --content-file")
        raise typer.Exit(1)
    
    if (content or content_file) and editor:
        console.print("[red]Error:[/red] Cannot use --editor with --content or --content-file")
        raise typer.Exit(1)
    
    # Handle content file input
    if content_file:
        # Read content from file
        try:
            file_path = Path(content_file)
            if not file_path.exists():
                console.print(f"[red]Error:[/red] File not found: {content_file}")
                raise typer.Exit(1)
            
            # Read the file with UTF-8 encoding, handling different encodings gracefully
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with latin-1 as fallback
                try:
                    content = file_path.read_text(encoding='latin-1')
                    console.print("[yellow]Warning:[/yellow] File was read with latin-1 encoding")
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to read file: {e}")
                    raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to read content file: {e}")
            raise typer.Exit(1)
    elif content is None:
        # Get comment content
        if editor:
            # Use editor explicitly requested
            content = _get_content_from_editor()
        elif not sys.stdin.isatty():
            # Read from stdin
            content = sys.stdin.read().strip()
        else:
            # Interactive mode - open editor
            content = _get_content_from_editor()

    if not content:
        console.print("[red]Error:[/red] Comment content cannot be empty")
        raise typer.Exit(1)

    # Get author from git config
    author = get_default_reporter()

    # Create comment
    comment_kwargs = {
        "id": Comment.generate_id(),
        "author": author,
        "content": content,
    }
    
    if is_epic:
        comment_kwargs["epic_id"] = entity.id
    else:
        comment_kwargs["ticket_id"] = entity.id
    
    comment = Comment(**comment_kwargs)

    # Handle attachments if provided
    attachment_pointers = []
    if attach:
        # Load storage configuration
        config = load_config(gira_root)
        
        if not config.get("storage.enabled", False):
            console.print("[red]Error:[/red] Storage is not enabled. Configure storage to use attachments.")
            raise typer.Exit(1)
        
        # Load credentials
        provider = config.get("storage.provider", "s3")
        try:
            provider_enum = StorageProvider.from_string(provider)
            manager = CredentialsManager()
            credentials = manager.load_credentials(provider_enum)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to load credentials: {e}")
            console.print("Run 'gira storage configure' to set up credentials")
            raise typer.Exit(1)
        
        # Get storage backend
        try:
            # Filter out keys that conflict with explicit parameters
            filtered_credentials = {k: v for k, v in credentials.items() if k not in ['bucket', 'region']}
            
            storage = get_storage_backend(
                provider=provider,
                bucket=config.get("storage.bucket"),
                region=config.get("storage.region"),
                project_root=gira_root,
                **filtered_credentials
            )
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to initialize storage: {e}")
            raise typer.Exit(1)
        
        # Process each attachment
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for file_path in attach:
                path = Path(file_path)
                if not path.exists():
                    console.print(f"[red]Error:[/red] File not found: {file_path}")
                    raise typer.Exit(1)
                
                if not path.is_file():
                    console.print(f"[red]Error:[/red] Not a file: {file_path}")
                    raise typer.Exit(1)
                
                task = progress.add_task(f"Uploading {path.name}...", total=None)
                
                try:
                    # Calculate file hash
                    with open(path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    # Get file metadata
                    file_size = path.stat().st_size
                    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
                    
                    # Generate storage key
                    object_key = generate_comment_attachment_key(
                        entity_type,
                        entity_id,
                        comment.id,
                        path.name
                    )
                    
                    # Create attachment pointer
                    pointer = AttachmentPointer(
                        provider=StorageProvider.from_string(config.get("storage.provider", "s3")),
                        bucket=config.get("storage.bucket"),
                        object_key=object_key,
                        file_name=path.name,
                        content_type=content_type,
                        size=file_size,
                        checksum=file_hash,
                        uploaded_at=datetime.now(timezone.utc),
                        added_by=author,
                        note=f"Attached to comment {comment.id}",
                        entity_type=entity_type,
                        entity_id=entity_id
                    )
                    
                    # Upload file to storage
                    storage.upload(str(path), object_key, content_type=content_type)
                    
                    # Save pointer file
                    pointer_dir = get_comment_attachments_dir(
                        entity_type, entity_id, comment.id, gira_root
                    )
                    pointer_dir.mkdir(parents=True, exist_ok=True)
                    pointer_path = pointer_dir / pointer.get_pointer_filename()
                    pointer.save_to_file(pointer_path)
                    
                    attachment_pointers.append(pointer)
                    progress.update(task, completed=True)
                    
                except StorageError as e:
                    console.print(f"[red]Error:[/red] Failed to upload {path.name}: {e}")
                    raise typer.Exit(1)
                except Exception as e:
                    console.print(f"[red]Error:[/red] Unexpected error uploading {path.name}: {e}")
                    raise typer.Exit(1)
    
    # Update comment with attachment info
    if attachment_pointers:
        comment.attachments = [p.get_pointer_filename() for p in attachment_pointers]
        comment.attachment_count = len(attachment_pointers)

    # Add comment to entity
    if not entity.comments:
        entity.comments = []

    entity.comments.append(comment)
    entity.comment_count = len(entity.comments)
    entity.updated_at = datetime.now()

    # Save updated entity
    entity.save_to_json_file(str(entity_path))

    # Check if entity is archived
    if is_epic:
        is_archived = is_epic_archived(entity_path)
    else:
        is_archived = is_ticket_archived(entity_path)

    # Format content with highlighted mentions
    formatted_content = format_content_with_mentions(content, gira_root)

    # Check for mentioned team members
    mentioned_members = get_mentioned_members(content, gira_root)

    # Build success message
    success_text = Text()
    success_text.append("✓ Added comment to ", style="green")
    if is_archived:
        success_text.append("archived ", style="yellow")
    success_text.append(f"{entity_type} ", style="green")
    
    # Normalize the entity ID for display
    if entity_type == "ticket":
        from gira.constants import normalize_ticket_id, get_project_prefix
        try:
            prefix = get_project_prefix()
            display_id = normalize_ticket_id(entity_id, prefix)
        except ValueError:
            display_id = entity_id.upper()
    elif entity_type == "epic":
        from gira.constants import normalize_epic_id
        try:
            display_id = normalize_epic_id(entity_id)
        except ValueError:
            display_id = entity_id.upper()
    else:
        display_id = entity_id
        
    success_text.append(display_id, style="cyan")
    success_text.append("\n\n")
    success_text.append("Author: ", style="dim")
    success_text.append(author + "\n")
    success_text.append("ID: ", style="dim")
    success_text.append(comment.id + "\n")
    success_text.append("Time: ", style="dim")
    success_text.append(comment.created_at.strftime('%Y-%m-%d %H:%M:%S'))

    if mentioned_members:
        success_text.append("\n")
        success_text.append("Mentioned: ", style="dim")
        success_text.append(", ".join(mentioned_members), style="cyan")
    
    if attachment_pointers:
        success_text.append("\n")
        success_text.append("Attachments: ", style="dim")
        success_text.append(f"{len(attachment_pointers)} file(s)", style="cyan")
        total_size = sum(p.size for p in attachment_pointers)
        from gira.storage.utils import format_bytes
        success_text.append(f" ({format_bytes(total_size)})", style="dim")

    # Show success message
    console.print(Panel(
        success_text,
        title="Comment Added",
        border_style="green"
    ))

    # Show preview of the comment with formatted mentions if it contains mentions
    if mentioned_members:
        console.print("\n[dim]Preview:[/dim]")
        preview_panel = Panel(
            formatted_content,
            border_style="dim",
            padding=(1, 2)
        )
        console.print(preview_panel)
    
    # Show attachment details if any
    if attachment_pointers:
        console.print("\n[dim]Attached files:[/dim]")
        for pointer in attachment_pointers:
            console.print(f"  📎 {pointer.file_name} ({pointer.get_display_size()})")


def _get_content_from_editor() -> str:
    """Open editor for comment content."""
    editor = os.environ.get("EDITOR", "vi")

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as tmp:
        tmp.write("# Enter your comment below. Lines starting with # will be ignored.\n")
        tmp.write("# Leave empty to cancel.\n")
        tmp.write("# You can mention team members with @username (e.g., @jdoe)\n\n")
        tmp.flush()
        tmp_path = tmp.name

    try:
        subprocess.run([editor, tmp_path], check=True)

        with open(tmp_path) as f:
            lines = f.readlines()

        # Filter out comment lines and join
        content_lines = [
            line.rstrip() for line in lines
            if not line.strip().startswith('#')
        ]
        content = '\n'.join(content_lines).strip()

        return content
    finally:
        Path(tmp_path).unlink(missing_ok=True)
