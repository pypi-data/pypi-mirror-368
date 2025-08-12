"""Open attachments using the system default application."""

import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

import typer
import urllib3
from rich import print
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from gira.models.attachment import AttachmentPointer, EntityType
from gira.storage import get_storage_backend
from gira.storage.config import StorageConfig
from gira.storage.exceptions import StorageError, StorageNotFoundError
from gira.storage.utils import verify_checksum
from gira.utils.errors import GiraError
from gira.utils.project import ensure_gira_project


def open_attachment(
    entity_id: str = typer.Argument(..., help="Entity ID (e.g., GCM-123 or EPIC-001)"),
    attachment_ids: List[str] = typer.Argument(..., help="Attachment ID(s) to open"),
    entity_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Entity type (ticket or epic)"
    ),
    download_only: bool = typer.Option(
        False, "--download-only", "-d", help="Download without opening"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for downloads"
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Skip cache and download fresh copy"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing files"
    ),
) -> None:
    f"""Open attachments using the system default application.
    
    Downloads attachments from storage and opens them with the appropriate
    application. Files are cached locally to avoid repeated downloads.
    {format_examples_simple([
        create_example("Open a single attachment", "gira attachment open GCM-123 20250727120000-abc123"),
        create_example("Open multiple attachments", "gira attachment open GCM-123 attach1 attach2 attach3"),
        create_example("Download without opening", "gira attachment open GCM-123 attach1 --download-only -o ~/Downloads"),
        create_example("Force fresh download (skip cache)", "gira attachment open GCM-123 attach1 --no-cache")
    ])}"""
    try:
        # Ensure we're in a Gira project
        root = ensure_gira_project()
        
        # Determine entity type
        if entity_type:
            entity_type_enum = EntityType(entity_type.lower())
        else:
            entity_type_enum = _infer_entity_type(entity_id)
        
        # Get cache directory
        cache_dir = _get_cache_directory()
        
        # Process each attachment
        opened_files = []
        for attachment_id in attachment_ids:
            try:
                file_path = _process_attachment(
                    root=root,
                    entity_id=entity_id,
                    entity_type=entity_type_enum,
                    attachment_id=attachment_id,
                    cache_dir=cache_dir,
                    output_dir=output_dir,
                    no_cache=no_cache,
                    force=force,
                )
                
                if file_path:
                    opened_files.append(file_path)
                    
                    if not download_only:
                        _open_file(file_path)
                        print(f"[green]✓[/green] Opened: {file_path.name}")
                    else:
                        print(f"[green]✓[/green] Downloaded: {file_path}")
                        
            except StorageNotFoundError:
                print(f"[red]✗[/red] Attachment not found: {attachment_id}")
            except Exception as e:
                print(f"[red]✗[/red] Error processing {attachment_id}: {e}")
        
        if not opened_files:
            raise GiraError("No attachments were successfully processed")
            
        # Summary
        if download_only:
            print(f"\n[green]Downloaded {len(opened_files)} file(s)[/green]")
        else:
            print(f"\n[green]Opened {len(opened_files)} file(s)[/green]")
            
    except Exception as e:
        raise GiraError(f"Failed to open attachments: {e}")


def _load_attachment_pointer(root: Path, entity_id: str, attachment_id: str) -> AttachmentPointer:
    """Load attachment pointer from filesystem."""
    attachments_dir = root / ".gira" / "attachments" / entity_id
    
    if not attachments_dir.exists():
        raise StorageNotFoundError(f"No attachments directory for {entity_id}")
    
    # Find the attachment file by ID (checking all yml files)
    for pointer_file in attachments_dir.glob("*.yml"):
        try:
            candidate_pointer = AttachmentPointer.from_yaml(pointer_file.read_text())
            # Check if the filename matches the attachment_id
            file_stem = Path(candidate_pointer.file_name).stem
            if attachment_id in [file_stem, candidate_pointer.file_name, pointer_file.stem]:
                return candidate_pointer
        except Exception:
            continue
    
    raise StorageNotFoundError(f"Attachment not found: {attachment_id}")


def _process_attachment(
    root: Path,
    entity_id: str,
    entity_type: EntityType,
    attachment_id: str,
    cache_dir: Path,
    output_dir: Optional[Path],
    no_cache: bool,
    force: bool,
) -> Optional[Path]:
    """Process a single attachment."""
    # Load attachment pointer
    pointer = _load_attachment_pointer(root, entity_id, attachment_id)
    
    # Determine target path
    if output_dir:
        target_path = output_dir / pointer.file_name
    else:
        # Use cache directory
        entity_cache_dir = cache_dir / entity_type.value / entity_id
        entity_cache_dir.mkdir(parents=True, exist_ok=True)
        target_path = entity_cache_dir / pointer.file_name
    
    # Check if file exists and is valid
    if target_path.exists() and not no_cache and not force:
        # Verify checksum
        if verify_checksum(target_path, pointer.checksum):
            print(f"[dim]Using cached: {pointer.file_name}[/dim]")
            return target_path
        else:
            print(f"[yellow]Cache corrupted, re-downloading: {pointer.file_name}[/yellow]")
    
    # Check if we should overwrite
    if target_path.exists() and not force:
        response = typer.confirm(f"File exists: {target_path.name}. Overwrite?")
        if not response:
            return None
    
    # Download file
    _download_attachment(pointer, target_path)
    
    # Verify checksum
    if not verify_checksum(target_path, pointer.checksum):
        target_path.unlink()  # Remove corrupted file
        raise GiraError(f"Checksum verification failed for {pointer.file_name}")
    
    return target_path


def _download_attachment(pointer: AttachmentPointer, target_path: Path) -> None:
    """Download attachment from storage with progress indicator."""
    try:
        # Load storage configuration
        provider_str = pointer.provider.value if hasattr(pointer.provider, 'value') else str(pointer.provider)
        storage_config = StorageConfig.load_credentials(provider_str)
        
        # Disable SSL warnings for R2
        if provider_str.lower() == "r2":
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get storage backend
        # Filter out keys that conflict with explicit parameters
        filtered_config = {k: v for k, v in storage_config.items() if k not in ['bucket', 'region']}
        backend = get_storage_backend(
            provider=provider_str,
            bucket=pointer.bucket,
            **filtered_config,
        )
        
        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(
                f"Downloading {pointer.file_name}",
                total=pointer.size,
            )
            
            # Download with progress callback
            def update_progress(download_progress) -> None:
                # Handle both int and DownloadProgress object
                if hasattr(download_progress, 'bytes_downloaded'):
                    # It's a DownloadProgress object
                    progress.update(task, completed=download_progress.bytes_downloaded)
                else:
                    # It's an int (bytes count)
                    progress.update(task, completed=download_progress)
            
            # Ensure parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            backend.download(
                object_key=pointer.object_key,
                file_path=target_path,
                progress_callback=update_progress if pointer.size > 1024 * 1024 else None,  # Only show progress for files > 1MB
            )
            
            # Complete progress
            progress.update(task, completed=pointer.size)
            
    except Exception as e:
        raise StorageError(f"Failed to download attachment: {e}")


def _open_file(file_path: Path) -> None:
    """Open file with system default application."""
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(file_path)], check=True)
        elif system == "Windows":
            os.startfile(str(file_path))
        elif system == "Linux":
            subprocess.run(["xdg-open", str(file_path)], check=True)
        else:
            raise GiraError(f"Unsupported operating system: {system}")
    except subprocess.CalledProcessError as e:
        raise GiraError(f"Failed to open file: {e}")
    except Exception as e:
        raise GiraError(f"Failed to open file: {e}")


def _get_cache_directory() -> Path:
    """Get the cache directory for attachments."""
    # Use XDG cache directory or fallback
    if platform.system() == "Linux":
        cache_base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    elif platform.system() == "Darwin":
        cache_base = Path.home() / "Library" / "Caches"
    elif platform.system() == "Windows":
        cache_base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        cache_base = Path.home() / ".cache"
    
    cache_dir = cache_base / "gira" / "attachments"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _infer_entity_type(entity_id: str) -> EntityType:
    """Infer entity type from ID format."""
    if entity_id.upper().startswith("EPIC-"):
        return EntityType.EPIC
    else:
        return EntityType.TICKET