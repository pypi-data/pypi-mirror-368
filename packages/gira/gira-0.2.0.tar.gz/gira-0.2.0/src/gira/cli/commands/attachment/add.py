"""Add attachment command for Gira with multiple file support."""

import hashlib
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
import fnmatch

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
    TaskID,
)
from rich.table import Table

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
from gira.constants import normalize_ticket_id, get_project_prefix

def add(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or epic ID to attach file to (e.g., PROJ-123, 123, or EPIC-001)",
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
        gira attachment add 123 document.pdf
    """
    # Ensure we're in a Gira project
    root = ensure_gira_project()
    
    # Normalize entity ID (support number-only input)
    entity_id = entity_id.upper()
    if not entity_id.startswith("EPIC-"):
        try:
            prefix = get_project_prefix()
            entity_id = normalize_ticket_id(entity_id, prefix)
        except:
            pass  # Keep as-is if normalization fails
    
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
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in files_to_upload:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    files_to_upload = unique_files
    
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
    
    if not provider:
        console.print("[red]Error:[/red] Storage provider not configured")
        console.print("Run 'gira storage configure' to complete setup")
        raise typer.Exit(1)
    
    # Git LFS doesn't require bucket configuration
    if provider != "git-lfs" and not bucket:
        console.print("[red]Error:[/red] Storage bucket not configured")
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
    
    # Initialize storage backend
    try:
        # Disable SSL warnings for R2
        if provider == "r2":
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Filter out keys that conflict with explicit parameters
        filtered_credentials = {k: v for k, v in credentials.items() if k not in ['bucket', 'region']}
        
        # Git LFS has different parameters
        if provider == "git-lfs":
            backend = get_storage_backend(
                provider=provider,
                project_root=root,
                **filtered_credentials
            )
        else:
            backend = get_storage_backend(
                provider=provider,
                bucket=bucket,
                region=region,
                **filtered_credentials
            )
    except Exception as e:
        console.print(f"[red]Error initializing storage:[/red] {e}")
        raise typer.Exit(1)
    
    # Show upload information
    total_size = sum(f.stat().st_size for f in files_to_upload)
    console.print(Panel.fit(
        f"[bold]Uploading {len(files_to_upload)} Attachment(s)[/bold]\n\n"
        f"Total Size: {_format_bytes(total_size)}\n"
        f"To: {entity_type.capitalize()} {entity_id}",
        border_style="cyan"
    ))
    
    # Process uploads
    uploaded_pointers = []
    failed_uploads = []
    pointer_files = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        # Create overall progress task
        overall_task = progress.add_task(
            f"Uploading {len(files_to_upload)} file(s)...",
            total=total_size
        )
        
        overall_bytes_uploaded = 0
        
        for file_path in files_to_upload:
            try:
                # Get file information
                file_info = get_file_info(file_path)
                
                # Generate object key
                if provider == "git-lfs":
                    # For Git LFS, simpler key format without base_path
                    object_key = f"{entity_id}/{file_path.name}"
                else:
                    object_key = AttachmentPointer.generate_object_key(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        filename=file_path.name,
                        base_path=base_path,
                    )
                
                # Create attachment pointer  
                # For Git LFS, bucket is not required
                pointer_data = {
                    "provider": provider_enum,
                    "object_key": object_key,
                    "file_name": file_path.name,
                    "content_type": file_info["content_type"],
                    "size": file_info["size"],
                    "checksum": file_info["checksum"],
                    "uploaded_at": datetime.now(timezone.utc),
                    "added_by": user,
                    "note": note,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                }
                
                # Only add bucket for non-Git LFS providers
                if provider != "git-lfs":
                    pointer_data["bucket"] = bucket
                
                pointer = AttachmentPointer(**pointer_data)
                
                # Create file-specific task
                file_task = progress.add_task(
                    f"  {file_path.name}",
                    total=file_info["size"]
                )
                
                # Upload with progress callback
                def update_progress(upload_progress):
                    # Handle both int and UploadProgress object
                    if hasattr(upload_progress, 'bytes_uploaded'):
                        bytes_uploaded = upload_progress.bytes_uploaded
                    else:
                        bytes_uploaded = upload_progress
                    
                    progress.update(file_task, completed=bytes_uploaded)
                    # Update overall progress
                    new_overall = overall_bytes_uploaded + bytes_uploaded
                    progress.update(overall_task, completed=new_overall)
                
                # Upload file
                storage_object = backend.upload(
                    file_path,
                    object_key,
                    content_type=pointer.content_type,
                    progress_callback=update_progress if file_info["size"] > 1024 * 1024 else None,
                )
                
                # Mark file task as complete
                progress.update(file_task, completed=file_info["size"])
                overall_bytes_uploaded += file_info["size"]
                progress.update(overall_task, completed=overall_bytes_uploaded)
                
                # For Git LFS, we don't save pointer files - the actual files are in the repo
                if provider != "git-lfs":
                    # Save pointer file for cloud storage
                    pointer_dir = root / ".gira" / "attachments" / entity_id
                    pointer_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Generate unique pointer filename
                    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                    pointer_filename = f"{timestamp}_{file_path.stem}.yml"
                    pointer_path = pointer_dir / pointer_filename
                    
                    pointer.save_to_file(pointer_path)
                    pointer_files.append(pointer_path.relative_to(root))
                else:
                    # For Git LFS, the file itself is tracked
                    lfs_file_path = root / ".gira" / "attachments" / entity_id / file_path.name
                    pointer_files.append(lfs_file_path.relative_to(root))
                
                uploaded_pointers.append(pointer)
                
                # Remove file task
                progress.remove_task(file_task)
                
            except Exception as e:
                console.print(f"[red]✗[/red] Failed to upload {file_path.name}: {e}")
                failed_uploads.append((file_path, str(e)))
                # Still update overall progress
                overall_bytes_uploaded += file_path.stat().st_size
                progress.update(overall_task, completed=overall_bytes_uploaded)
                if 'file_task' in locals():
                    progress.remove_task(file_task)
    
    # Show results
    if uploaded_pointers:
        console.print(f"\n[green]✓ Successfully uploaded {len(uploaded_pointers)} file(s)[/green]")
        
        # Update entity attachment count
        try:
            entity.attachment_count = getattr(entity, "attachment_count", 0) + len(uploaded_pointers)
            entity.updated_at = datetime.now(timezone.utc)
            
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
    
    if failed_uploads:
        console.print(f"\n[red]✗ Failed to upload {len(failed_uploads)} file(s):[/red]")
        for file_path, error in failed_uploads:
            console.print(f"  [red]✗[/red] {file_path.name}: {error}")
    
    # Commit changes if requested and we have successful uploads
    if commit and uploaded_pointers:
        try:
            # Stage all pointer files and entity file
            files_to_commit = list(pointer_files)
            
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
            if len(uploaded_pointers) == 1:
                commit_msg = f"feat(attachments): add {uploaded_pointers[0].file_name} to {entity_id}\n\n"
                commit_msg += f"- File: {uploaded_pointers[0].file_name}\n"
                commit_msg += f"- Size: {uploaded_pointers[0].get_display_size()}\n"
                commit_msg += f"- Type: {uploaded_pointers[0].content_type}\n"
            else:
                commit_msg = f"feat(attachments): add {len(uploaded_pointers)} files to {entity_id}\n\n"
                commit_msg += "Files added:\n"
                for p in uploaded_pointers:
                    commit_msg += f"- {p.file_name} ({p.get_display_size()})\n"
            
            if note:
                commit_msg += f"\nNote: {note}\n"
            commit_msg += f"\nGira: {entity_id}"
            
            commit_changes(root, files_to_commit, commit_msg)
            console.print("[green]✓ Changes committed to repository[/green]")
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to commit changes: {e}")
            console.print("You can commit manually with: git add -A && git commit")
    
    # Success summary
    if uploaded_pointers:
        console.print(f"\n[green]Summary:[/green]")
        console.print(f"  • Uploaded: {len(uploaded_pointers)} file(s)")
        console.print(f"  • Total size: {_format_bytes(sum(p.size for p in uploaded_pointers))}")
        console.print(f"  • Entity: {entity_type.capitalize()} {entity_id}")
        
        console.print(f"\nTo list attachments: [cyan]gira attachment list {entity_id}[/cyan]")
        console.print(f"To download: [cyan]gira attachment download {entity_id} <filename>[/cyan]")


def _collect_files_from_directory(directory: Path, include: Optional[str], exclude: Optional[str]) -> List[Path]:
    """Collect files from a directory based on include/exclude patterns."""
    files = []
    
    for item in directory.rglob("*"):
        if not item.is_file():
            continue
        
        # Skip hidden files and directories
        if any(part.startswith('.') for part in item.parts):
            continue
        
        # Apply include pattern
        if include and not fnmatch.fnmatch(item.name, include):
            continue
        
        # Apply exclude pattern
        if exclude and fnmatch.fnmatch(item.name, exclude):
            continue
        
        files.append(item)
    
    return sorted(files)


def _format_bytes(size: int) -> str:
    """Format bytes as human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            if unit == 'B':
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"