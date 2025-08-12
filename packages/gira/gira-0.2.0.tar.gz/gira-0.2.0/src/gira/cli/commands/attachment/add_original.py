"""Add attachment command for Gira."""

import hashlib
import mimetypes
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import typer
import urllib3
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

from gira.models.attachment import AttachmentPointer, StorageProvider
from gira.models.ticket import Ticket
from gira.models.epic import Epic
from gira.storage import get_storage_backend
from gira.storage.exceptions import StorageError
from gira.utils.config_utils import load_config
from gira.utils.credentials import CredentialsManager
from gira.utils.git_ops import commit_changes
from gira.utils.project import ensure_gira_project
from gira.utils.storage import get_file_info

def add(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or epic ID to attach file to (e.g., PROJ-123 or EPIC-001)",
    ),
    file_paths: List[str] = typer.Argument(
        ...,
        help="Path(s) to file(s) or directory to attach",
    ),
    note: Optional[str] = typer.Option(
        None,
        "--note", "-n",
        help="Optional description or note for the attachments",
    ),
    entity_type: Optional[str] = typer.Option(
        None,
        "--type", "-t",
        help="Entity type: ticket or epic (auto-detected if not specified)",
    ),
    commit: bool = typer.Option(
        True,
        "--commit/--no-commit",
        help="Automatically commit the attachment pointers",
    ),
    user: Optional[str] = typer.Option(
        None,
        "--user", "-u",
        help="User adding the attachment (defaults to git user)",
    ),
    include: Optional[str] = typer.Option(
        None,
        "--include", "-i",
        help="Include only files matching pattern (e.g., '*.pdf')",
    ),
    exclude: Optional[str] = typer.Option(
        None,
        "--exclude", "-e",
        help="Exclude files matching pattern (e.g., '*.tmp')",
    ),
) -> None:
    """Add attachment(s) to a ticket or epic.
    
    This command uploads files to the configured storage backend and creates
    pointer files in the repository. The actual file content is stored
    externally, while only small metadata files are committed to Git.
    
    Supports multiple files and directory uploads.
    
    Examples:
        gira attachment add PROJ-123 screenshot.png
        gira attachment add PROJ-123 doc1.pdf doc2.xlsx image.png
        gira attachment add PROJ-123 ./screenshots/
        gira attachment add PROJ-123 ./docs/ --include "*.pdf"
        gira attachment add PROJ-123 ./output/ --exclude "*.tmp"
    """
    # Ensure we're in a Gira project
    root = ensure_gira_project()
    
    # Collect all files to upload
    files_to_upload = []
    for file_path in file_paths:
        path_obj = Path(file_path).resolve()
        
        if not path_obj.exists():
            console.print(f"[red]Error:[/red] Path not found: {file_path}")
            raise typer.Exit(1)
        
        if path_obj.is_file():
            # Single file
            files_to_upload.append(path_obj)
        elif path_obj.is_dir():
            # Directory - collect all files
            files_in_dir = _collect_files_from_directory(path_obj, include, exclude)
            if not files_in_dir:
                console.print(f"[yellow]Warning:[/yellow] No files found in directory: {file_path}")
            files_to_upload.extend(files_in_dir)
        else:
            console.print(f"[red]Error:[/red] Not a file or directory: {file_path}")
            raise typer.Exit(1)
    
    if not files_to_upload:
        console.print("[red]Error:[/red] No files to upload")
        raise typer.Exit(1)
    
    # Auto-detect entity type if not specified
    if not entity_type:
        if entity_id.startswith("EPIC-"):
            entity_type = "epic"
        else:
            entity_type = "ticket"
    
    # Validate entity type
    if entity_type not in ["ticket", "epic"]:
        console.print(f"[red]Error:[/red] Invalid entity type: {entity_type}")
        console.print("Must be 'ticket' or 'epic'")
        raise typer.Exit(1)
    
    # Load and validate entity
    try:
        if entity_type == "ticket":
            entity_dir = root / ".gira" / "board"
            entity = None
            
            # Search for ticket across all statuses
            for status_dir in entity_dir.iterdir():
                if status_dir.is_dir():
                    ticket_file = status_dir / f"{entity_id}.json"
                    if ticket_file.exists():
                        entity = Ticket.from_json_file(ticket_file)
                        break
            
            if not entity:
                console.print(f"[red]Error:[/red] Ticket not found: {entity_id}")
                raise typer.Exit(1)
        else:
            epic_file = root / ".gira" / "epics" / f"{entity_id}.json"
            if not epic_file.exists():
                console.print(f"[red]Error:[/red] Epic not found: {entity_id}")
                raise typer.Exit(1)
            entity = Epic.from_json_file(epic_file)
    except Exception as e:
        console.print(f"[red]Error loading {entity_type}:[/red] {e}")
        raise typer.Exit(1)
    
    # Load storage configuration
    config = load_config(root)
    if not config.get("storage.enabled", False):
        console.print("[red]Error:[/red] Storage is not enabled in this project")
        console.print("Run 'gira storage configure' to set up storage")
        raise typer.Exit(1)
    
    provider = config.get("storage.provider")
    bucket = config.get("storage.bucket")
    region = config.get("storage.region")
    base_path = config.get("storage.base_path")
    
    if not provider or not bucket:
        console.print("[red]Error:[/red] Storage provider or bucket not configured")
        console.print("Run 'gira storage configure' to complete setup")
        raise typer.Exit(1)
    
    # Load credentials
    try:
        provider_enum = StorageProvider(provider)
        manager = CredentialsManager()
        credentials = manager.load_credentials(provider_enum)
    except Exception as e:
        console.print(f"[red]Error loading credentials:[/red] {e}")
        console.print("Run 'gira storage configure' to set up credentials")
        raise typer.Exit(1)
    
    # Get file information
    file_info = get_file_info(file_path_obj)
    
    # Determine user
    if not user:
        # Try to get from git config
        try:
            import subprocess
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                cwd=root,
            )
            if result.returncode == 0:
                user = result.stdout.strip()
            else:
                user = os.environ.get("USER", "unknown")
        except Exception:
            user = os.environ.get("USER", "unknown")
    
    # Generate object key
    object_key = AttachmentPointer.generate_object_key(
        entity_type=entity_type,
        entity_id=entity_id,
        filename=file_path_obj.name,
        base_path=base_path,
    )
    
    # Create attachment pointer
    pointer = AttachmentPointer(
        provider=provider_enum,
        bucket=bucket,
        object_key=object_key,
        file_name=file_path_obj.name,
        content_type=file_info["content_type"],
        size=file_info["size"],
        checksum=file_info["checksum"],
        uploaded_at=datetime.utcnow(),
        added_by=user,
        note=note,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    
    # Show upload information
    console.print(Panel.fit(
        f"[bold]Uploading Attachment[/bold]\n\n"
        f"File: {file_path_obj.name}\n"
        f"Size: {pointer.get_display_size()}\n"
        f"Type: {pointer.content_type}\n"
        f"To: {entity_type.capitalize()} {entity_id}",
        border_style="cyan"
    ))
    
    # Initialize storage backend
    try:
        # Disable SSL warnings for R2
        if provider == "r2":
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Filter out keys that conflict with explicit parameters
        filtered_credentials = {k: v for k, v in credentials.items() if k not in ['bucket', 'region']}
        backend = get_storage_backend(
            provider=provider,
            bucket=bucket,
            region=region,
            **filtered_credentials
        )
    except Exception as e:
        console.print(f"[red]Error initializing storage:[/red] {e}")
        raise typer.Exit(1)
    
    # Upload file with progress
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Uploading {file_path_obj.name}...",
                total=file_info["size"]
            )
            
            # Define progress callback
            def update_progress(upload_progress) -> None:
                # Handle both int and UploadProgress object
                if hasattr(upload_progress, 'bytes_uploaded'):
                    # It's an UploadProgress object
                    progress.update(task, completed=upload_progress.bytes_uploaded)
                else:
                    # It's an int (bytes count)
                    progress.update(task, completed=upload_progress)
            
            # Upload file
            storage_object = backend.upload(
                file_path_obj,
                object_key,
                content_type=pointer.content_type,
                progress_callback=update_progress,
            )
            
            progress.update(task, completed=file_info["size"])
            
        console.print("[green]✓ Upload completed successfully![/green]")
        
    except StorageError as e:
        console.print(f"[red]Upload failed:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error during upload:[/red] {e}")
        raise typer.Exit(1)
    
    # Save pointer file
    pointer_dir = root / ".gira" / "attachments" / entity_id
    pointer_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique pointer filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    pointer_filename = f"{timestamp}_{file_path_obj.stem}.yml"
    pointer_path = pointer_dir / pointer_filename
    
    try:
        pointer.save_to_file(pointer_path)
        console.print(f"[green]✓ Created pointer file:[/green] {pointer_path.relative_to(root)}")
    except Exception as e:
        console.print(f"[red]Error saving pointer file:[/red] {e}")
        # Try to clean up uploaded file
        try:
            backend.delete(object_key)
        except Exception:
            pass
        raise typer.Exit(1)
    
    # Update entity attachment count
    try:
        entity.attachment_count = getattr(entity, "attachment_count", 0) + 1
        entity.updated_at = datetime.utcnow()
        
        if entity_type == "ticket":
            # Find the ticket file again to save
            for status_dir in entity_dir.iterdir():
                if status_dir.is_dir():
                    ticket_file = status_dir / f"{entity_id}.json"
                    if ticket_file.exists():
                        entity.save_to_json_file(ticket_file)
                        break
        else:
            entity.save_to_json_file(epic_file)
            
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Failed to update {entity_type} attachment count: {e}")
    
    # Commit changes if requested
    if commit:
        try:
            # Stage both pointer file and entity file
            files_to_commit = [pointer_path.relative_to(root)]
            
            if entity_type == "ticket":
                for status_dir in entity_dir.iterdir():
                    if status_dir.is_dir():
                        ticket_file = status_dir / f"{entity_id}.json"
                        if ticket_file.exists():
                            files_to_commit.append(ticket_file.relative_to(root))
                            break
            else:
                files_to_commit.append(epic_file.relative_to(root))
            
            # Create commit message
            commit_msg = f"feat(attachments): add {file_path_obj.name} to {entity_id}\n\n"
            commit_msg += f"- File: {file_path_obj.name}\n"
            commit_msg += f"- Size: {pointer.get_display_size()}\n"
            commit_msg += f"- Type: {pointer.content_type}\n"
            if note:
                commit_msg += f"- Note: {note}\n"
            commit_msg += f"\nGira: {entity_id}"
            
            commit_changes(root, files_to_commit, commit_msg)
            console.print("[green]✓ Changes committed to repository[/green]")
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to commit changes: {e}")
            console.print("You can commit manually with: git add -A && git commit")
    
    # Success summary
    console.print("\n[green]✓ Attachment added successfully![/green]")
    console.print(f"\nAttachment details:")
    console.print(f"  • File: {pointer.file_name}")
    console.print(f"  • Size: {pointer.get_display_size()}")
    console.print(f"  • Provider: {pointer.provider if isinstance(pointer.provider, str) else pointer.provider.value}")
    console.print(f"  • Location: {pointer.bucket}/{pointer.object_key}")
    
    if note:
        console.print(f"  • Note: {note}")
    
    console.print(f"\nTo list attachments: [cyan]gira attachment list {entity_id}[/cyan]")
    console.print(f"To download: [cyan]gira attachment open {entity_id} {pointer.file_name}[/cyan]")