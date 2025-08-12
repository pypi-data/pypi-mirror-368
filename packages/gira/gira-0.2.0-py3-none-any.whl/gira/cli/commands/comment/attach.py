"""Add attachments to existing comments."""

import hashlib
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from gira.models.attachment import AttachmentPointer, StorageProvider
from gira.storage import get_storage_backend
from gira.storage.exceptions import StorageError
from gira.utils.config import get_default_reporter
from gira.utils.config_utils import load_config
from gira.utils.credentials import CredentialsManager
from gira.utils.comment_attachments import (
    get_comment_attachments_dir,
    generate_comment_attachment_key,
    find_comment_in_entity,
    update_comment_attachment_count,
    list_comment_attachments
)
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.epic_utils import find_epic
from gira.storage.utils import format_bytes
from gira.constants import normalize_ticket_id, get_project_prefix
from gira.utils.interactive_prompts import (
    prompt_for_entity_id,
    prompt_for_comment_selection,
    prompt_for_file_paths
)


def attach(
    entity_id: Optional[str] = typer.Argument(
        None,
        help="Ticket or Epic ID (e.g., GCM-123, 123, or EPIC-001)"
    ),
    comment_id: Optional[str] = typer.Argument(
        None,
        help="Comment ID to attach files to"
    ),
    file_paths: Optional[List[str]] = typer.Argument(
        None,
        help="Path(s) to file(s) to attach"
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive", "-i",
        help="Run in interactive mode"
    ),
    note: Optional[str] = typer.Option(
        None,
        "--note", "-n",
        help="Optional note for the attachments"
    ),
    user: Optional[str] = typer.Option(
        None,
        "--user", "-u",
        help="User adding the attachment (defaults to git user)"
    ),
) -> None:
    """Attach files to an existing comment.
    
    Examples:
    - Attach a single file: gira comment attach GCM-123 20250729-123456 screenshot.png
    - Attach multiple files: gira comment attach GCM-123 20250729-123456 error.log debug.log
    - Attach with a note: gira comment attach GCM-123 20250729-123456 logs.zip --note "Debug logs"
    - Interactive mode: gira comment attach
    - Force interactive mode: gira comment attach --interactive
    - Using number-only ID: gira comment attach 123 20250729-123456 file.pdf
    """
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()
    
    # Check if we should run in interactive mode
    if interactive or (entity_id is None and comment_id is None and file_paths is None):
        # Interactive mode
        console.print("[bold]Interactive mode:[/bold] Let's attach files to a comment\n")
        
        # Prompt for entity ID
        if not entity_id:
            entity_id = prompt_for_entity_id(allow_epic=True)
        
        # Normalize entity ID (support number-only input)
        if not entity_id.startswith("EPIC-"):
            try:
                prefix = get_project_prefix()
                entity_id = normalize_ticket_id(entity_id, prefix)
            except:
                pass  # Keep as-is if normalization fails
        
        entity_id = entity_id.upper()
        is_epic = entity_id.startswith("EPIC-")
        entity_type = "epic" if is_epic else "ticket"
        
        # Find the entity first to get comments
        if is_epic:
            entity, entity_path = find_epic(entity_id, gira_root, include_archived=True)
        else:
            entity, entity_path = find_ticket(entity_id, gira_root, include_archived=True)
        
        if not entity:
            console.print(f"[red]Error:[/red] {entity_type.capitalize()} {entity_id} not found")
            raise typer.Exit(1)
        
        # Prompt for comment selection if not provided
        if not comment_id:
            comment_id = prompt_for_comment_selection(entity, default_latest=True)
            if not comment_id:
                console.print("[red]No comments available to attach files to[/red]")
                raise typer.Exit(1)
        
        # Prompt for file paths if not provided
        if not file_paths:
            file_paths = prompt_for_file_paths()
            if not file_paths:
                console.print("[red]No files specified[/red]")
                raise typer.Exit(1)
    else:
        # Non-interactive mode - validate required arguments
        if not entity_id or not comment_id or not file_paths:
            console.print("[red]Error:[/red] All arguments are required in non-interactive mode")
            console.print("Use 'gira comment attach --interactive' for interactive mode")
            raise typer.Exit(1)
        
        # Normalize entity ID (support number-only input)
        entity_id = entity_id.upper()
        if not entity_id.startswith("EPIC-"):
            try:
                prefix = get_project_prefix()
                entity_id = normalize_ticket_id(entity_id, prefix)
            except:
                pass  # Keep as-is if normalization fails
        
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
    
    # Get user
    if not user:
        user = get_default_reporter()
    
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
    
    # Process each file
    uploaded_files = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for file_path in file_paths:
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
                    comment_id,
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
                    added_by=user,
                    note=note or f"Attached to comment {comment_id}",
                    entity_type=entity_type,
                    entity_id=entity_id
                )
                
                # Upload file to storage
                storage.upload(str(path), object_key, content_type=content_type)
                
                # Save pointer file
                pointer_dir = get_comment_attachments_dir(
                    entity_type, entity_id, comment_id, gira_root
                )
                pointer_dir.mkdir(parents=True, exist_ok=True)
                pointer_path = pointer_dir / pointer.get_pointer_filename()
                pointer.save_to_file(pointer_path)
                
                uploaded_files.append(pointer)
                progress.update(task, completed=True)
                
            except StorageError as e:
                console.print(f"[red]Error:[/red] Failed to upload {path.name}: {e}")
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Error:[/red] Unexpected error uploading {path.name}: {e}")
                raise typer.Exit(1)
    
    # Update comment attachment count and list
    update_comment_attachment_count(comment, entity_type, entity_id, gira_root)
    
    # Update entity timestamp
    entity.updated_at = datetime.now()
    entity.save_to_json_file(str(entity_path))
    
    # Show success message
    console.print(Panel(
        f"[green]✓[/green] Attached {len(uploaded_files)} file(s) to comment {comment_id}",
        title="Attachments Added",
        border_style="green"
    ))
    
    # Display attachment details
    if uploaded_files:
        table = Table(title="Attached Files")
        table.add_column("Filename", style="cyan")
        table.add_column("Size", justify="right")
        table.add_column("Type")
        
        total_size = 0
        for pointer in uploaded_files:
            table.add_row(
                pointer.file_name,
                pointer.get_display_size(),
                pointer.content_type
            )
            total_size += pointer.size
        
        console.print(table)
        console.print(f"\n[dim]Total size: {format_bytes(total_size)}[/dim]")
    
    # Show updated comment attachment count
    all_attachments = list_comment_attachments(entity_type, entity_id, comment_id, gira_root)
    console.print(f"\n[dim]Comment now has {len(all_attachments)} attachment(s)[/dim]")


from typing import Optional