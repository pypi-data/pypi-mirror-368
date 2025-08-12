"""Download attachments command for Gira - agent-friendly file retrieval."""

import os
import fnmatch
from pathlib import Path
from typing import Optional, List

import typer
import urllib3
from rich import print
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn

from gira.models.attachment import AttachmentPointer, EntityType
from gira.storage import get_storage_backend
from gira.storage.config import StorageConfig
from gira.storage.exceptions import StorageError, StorageNotFoundError
from gira.storage.utils import verify_checksum
from gira.utils.errors import GiraError
from gira.utils.project import ensure_gira_project

def download_attachment(
    entity_id: str = typer.Argument(..., help="Entity ID (e.g., GCM-123 or EPIC-001)"),
    patterns: List[str] = typer.Argument(..., help="Attachment filename(s) or pattern(s) to download"),
    entity_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Entity type (ticket or epic)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory (defaults to current directory)"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Suppress progress output"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing files without prompting"
    ),
    all_files: bool = typer.Option(
        False, "--all", "-a", help="Download all attachments for the entity"
    ),
) -> None:
    """Download attachment(s) to specified location without opening.
    
    This command is designed for AI agents and automation scripts that need
    to programmatically download files for processing. Supports multiple files
    and wildcard patterns.
    
    Examples:
        gira attachment download GCM-123 document.pdf
        gira attachment download GCM-123 spec.pdf design.png report.docx
        gira attachment download GCM-123 "*.pdf"
        gira attachment download GCM-123 "*.pdf" "*.png" "*.jpg"
        gira attachment download GCM-123 --all
        gira attachment download GCM-123 "*.csv" --output /tmp/data/
        gira attachment download GCM-123 config.yaml --quiet
        gira attachment download GCM-123 data.csv --force
    """
    try:
        # Ensure we're in a Gira project
        root = ensure_gira_project()
        
        # Determine entity type
        if entity_type:
            entity_type_enum = EntityType(entity_type.lower())
        else:
            entity_type_enum = _infer_entity_type(entity_id)
        
        # Determine output directory
        output_dir = output if output else Path.cwd()
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        elif not output_dir.is_dir():
            raise GiraError(f"Output path exists but is not a directory: {output_dir}")
        
        # Collect all attachments to download
        if all_files:
            # Download all attachments
            pointers_to_download = _get_all_attachment_pointers(root, entity_id)
        else:
            # Match against patterns
            pointers_to_download = _match_attachment_patterns(root, entity_id, patterns)
        
        if not pointers_to_download:
            if not quiet:
                console.print(f"[yellow]No attachments found matching the specified patterns[/yellow]")
            raise typer.Exit(0)
        
        # Show download plan
        if not quiet:
            total_size = sum(p.size for p in pointers_to_download)
            console.print(f"\n[cyan]Downloading {len(pointers_to_download)} file(s) ({_format_bytes(total_size)})[/cyan]")
        
        # Download files
        downloaded_files = []
        failed_downloads = []
        
        for pointer in pointers_to_download:
            target_path = output_dir / pointer.file_name
            
            # Check if file exists
            if target_path.exists() and not force:
                if not quiet:
                    response = typer.confirm(f"File exists: {target_path}. Overwrite?")
                    if not response:
                        console.print(f"[yellow]Skipped:[/yellow] {pointer.file_name}")
                        continue
                else:
                    # In quiet mode, skip without --force
                    failed_downloads.append((pointer.file_name, "File exists. Use --force to overwrite."))
                    continue
            
            try:
                # Download file
                _download_file(pointer, target_path, quiet)
                
                # Verify checksum
                if not verify_checksum(target_path, pointer.checksum):
                    target_path.unlink()  # Remove corrupted file
                    raise GiraError("Checksum verification failed")
                
                downloaded_files.append(target_path)
                
                # Output result
                if not quiet:
                    console.print(f"[green]✓[/green] Downloaded: {target_path}")
                else:
                    # In quiet mode, just print the path
                    print(str(target_path))
                    
            except Exception as e:
                failed_downloads.append((pointer.file_name, str(e)))
                if not quiet:
                    console.print(f"[red]✗[/red] Failed to download {pointer.file_name}: {e}")
        
        # Summary
        if not quiet and len(pointers_to_download) > 1:
            console.print(f"\n[green]Summary:[/green]")
            console.print(f"  • Downloaded: {len(downloaded_files)} file(s)")
            if failed_downloads:
                console.print(f"  • Failed: {len(failed_downloads)} file(s)")
                for filename, error in failed_downloads:
                    console.print(f"    - {filename}: {error}")
        
        # Exit with error if all downloads failed
        if downloaded_files == [] and failed_downloads:
            raise typer.Exit(1)
            
    except typer.Exit:
        raise
    except GiraError as e:
        # Handle our custom errors nicely
        if quiet:
            import sys
            print(f"Error: {e}", file=sys.stderr)
            raise typer.Exit(1)
        else:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
    except Exception as e:
        if quiet:
            # In quiet mode, print minimal error to stderr
            import sys
            print(f"Error: {e}", file=sys.stderr)
            raise typer.Exit(1)
        else:
            raise GiraError(f"Failed to download attachment: {e}")


def _infer_entity_type(entity_id: str) -> EntityType:
    """Infer entity type from ID format."""
    if entity_id.upper().startswith("EPIC-"):
        return EntityType.EPIC
    else:
        return EntityType.TICKET


def _load_attachment_pointer(root: Path, entity_id: str, filename: str) -> AttachmentPointer:
    """Load attachment pointer by filename (supports partial matching)."""
    attachments_dir = root / ".gira" / "attachments" / entity_id
    
    if not attachments_dir.exists():
        raise StorageNotFoundError(f"No attachments directory for {entity_id}")
    
    # First try exact match
    exact_matches = []
    partial_matches = []
    
    for pointer_file in attachments_dir.glob("*.yml"):
        try:
            candidate_pointer = AttachmentPointer.from_yaml(pointer_file.read_text())
            if candidate_pointer.file_name == filename:
                # Exact match found - but collect all in case there are duplicates
                exact_matches.append((candidate_pointer, pointer_file))
            elif filename.lower() in candidate_pointer.file_name.lower():
                # Partial match
                partial_matches.append((candidate_pointer, pointer_file))
        except Exception:
            continue
    
    # If we have exact matches
    if exact_matches:
        if len(exact_matches) == 1:
            return exact_matches[0][0]
        else:
            # Multiple files with same name - use the most recent one
            # Sort by upload time, newest first
            exact_matches.sort(key=lambda x: x[0].uploaded_at, reverse=True)
            newest = exact_matches[0][0]
            
            # Show a note about using the newest
            print(f"[yellow]Note:[/yellow] Found {len(exact_matches)} attachments named '{filename}'")
            print(f"[yellow]Using the most recent one uploaded at {newest.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}[/yellow]")
            print(f"[dim]To see all versions, use: gira attachment list {entity_id}[/dim]\n")
            
            return newest
    
    # If no exact match, check partial matches
    if len(partial_matches) == 1:
        # Single partial match - use it
        return partial_matches[0][0]
    elif len(partial_matches) > 1:
        # Multiple partial matches - show them with additional info
        matches_info = []
        for pointer, _ in partial_matches:
            info = f"  - {pointer.file_name}"
            # Add upload time if names are identical
            if sum(1 for p, _ in partial_matches if p.file_name == pointer.file_name) > 1:
                info += f" (uploaded: {pointer.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
            matches_info.append(info)
        
        matches_list = "\n".join(matches_info)
        raise GiraError(
            f"Multiple attachments match '{filename}':\n{matches_list}\n\n"
            f"Please use a more specific filename or the full filename."
        )
    
    raise StorageNotFoundError(f"No attachment found matching: {filename}")


def _get_all_attachment_pointers(root: Path, entity_id: str) -> List[AttachmentPointer]:
    """Get all attachment pointers for an entity."""
    attachments_dir = root / ".gira" / "attachments" / entity_id
    
    if not attachments_dir.exists():
        return []
    
    # Check if we're using Git LFS
    from gira.utils.config_utils import load_config
    config = load_config(root)
    is_git_lfs = config.get("storage.provider") == "git-lfs"
    
    pointers = []
    
    if is_git_lfs:
        # For Git LFS, create pointers from actual files
        import subprocess
        from gira.utils.storage import get_file_info
        from datetime import datetime, timezone
        
        for file_path in attachments_dir.iterdir():
            if file_path.is_file() and not file_path.name.endswith(".yml"):
                try:
                    # Get file info
                    file_info = get_file_info(file_path)
                    
                    # Get Git author info
                    try:
                        result = subprocess.run(
                            ["git", "log", "-1", "--format=%ae %aI", str(file_path)],
                            cwd=root,
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        if result.stdout:
                            parts = result.stdout.strip().split()
                            added_by = parts[0] if parts else "unknown"
                            uploaded_at_str = parts[1] if len(parts) > 1 else None
                            uploaded_at = datetime.fromisoformat(uploaded_at_str.replace("Z", "+00:00")) if uploaded_at_str else datetime.now(timezone.utc)
                        else:
                            added_by = "unknown"
                            uploaded_at = datetime.now(timezone.utc)
                    except:
                        added_by = "unknown"
                        uploaded_at = datetime.now(timezone.utc)
                    
                    # Create pseudo-pointer
                    pointer = AttachmentPointer(
                        provider="git-lfs",
                        object_key=f"{entity_id}/{file_path.name}",
                        file_name=file_path.name,
                        content_type=file_info["content_type"],
                        size=file_info["size"],
                        checksum=file_info["checksum"],
                        uploaded_at=uploaded_at,
                        added_by=added_by,
                        entity_type="ticket",  # Will be corrected based on entity_id
                        entity_id=entity_id,
                    )
                    pointers.append(pointer)
                except Exception:
                    continue
    else:
        # For cloud storage, read YAML pointer files
        for pointer_file in attachments_dir.glob("*.yml"):
            try:
                pointer = AttachmentPointer.from_yaml(pointer_file.read_text())
                pointers.append(pointer)
            except Exception:
                continue
    
    # Sort by upload time, newest first
    pointers.sort(key=lambda x: x.uploaded_at, reverse=True)
    return pointers


def _match_attachment_patterns(root: Path, entity_id: str, patterns: List[str]) -> List[AttachmentPointer]:
    """Match attachment pointers against filename patterns."""
    attachments_dir = root / ".gira" / "attachments" / entity_id
    
    if not attachments_dir.exists():
        return []
    
    # Get all pointers (handles both Git LFS and cloud storage)
    all_pointers = _get_all_attachment_pointers(root, entity_id)
    
    # Match against patterns
    matched_pointers = []
    seen_files = set()  # Track unique files to avoid duplicates
    
    for pattern in patterns:
        pattern_matched = False
        
        for pointer in all_pointers:
            # Check if already matched
            if pointer.file_name in seen_files:
                continue
            
            # Try exact match first
            if pointer.file_name == pattern:
                matched_pointers.append(pointer)
                seen_files.add(pointer.file_name)
                pattern_matched = True
            # Try wildcard match
            elif '*' in pattern or '?' in pattern:
                if fnmatch.fnmatch(pointer.file_name, pattern):
                    matched_pointers.append(pointer)
                    seen_files.add(pointer.file_name)
                    pattern_matched = True
            # Try partial match
            elif pattern.lower() in pointer.file_name.lower():
                matched_pointers.append(pointer)
                seen_files.add(pointer.file_name)
                pattern_matched = True
        
        # If pattern didn't match anything and it doesn't contain wildcards,
        # it might be a specific file that doesn't exist
        if not pattern_matched and '*' not in pattern and '?' not in pattern:
            # Check if it's a partial match situation
            partial_matches = [p for p in all_pointers if pattern.lower() in p.file_name.lower()]
            if len(partial_matches) > 1:
                # Multiple partial matches - show them
                matches_info = []
                for pointer in partial_matches:
                    info = f"  - {pointer.file_name}"
                    # Add upload time if names are identical
                    if sum(1 for p in partial_matches if p.file_name == pointer.file_name) > 1:
                        info += f" (uploaded: {pointer.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
                    matches_info.append(info)
                
                matches_list = "\n".join(matches_info)
                raise GiraError(
                    f"Multiple attachments match '{pattern}':\n{matches_list}\n\n"
                    f"Please use a more specific filename or the full filename."
                )
    
    # Sort by upload time, newest first
    matched_pointers.sort(key=lambda x: x.uploaded_at, reverse=True)
    return matched_pointers


def _format_bytes(size: int) -> str:
    """Format bytes as human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            if unit == 'B':
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def _download_file(pointer: AttachmentPointer, target_path: Path, quiet: bool) -> None:
    """Download file from storage."""
    try:
        # Load storage configuration
        provider_str = pointer.provider.value if hasattr(pointer.provider, 'value') else str(pointer.provider)
        
        if provider_str == "git-lfs":
            # For Git LFS, just copy the file
            import shutil
            from gira.utils.project import ensure_gira_project
            root = ensure_gira_project()
            source_path = root / ".gira" / "attachments" / pointer.object_key
            if not source_path.exists():
                raise StorageNotFoundError(f"File not found: {pointer.object_key}")
            shutil.copy2(source_path, target_path)
            return
        
        storage_config = StorageConfig.load_credentials(provider_str)
        
        # Disable SSL warnings for R2
        if provider_str.lower() == "r2":
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get storage backend
        filtered_config = {k: v for k, v in storage_config.items() if k not in ['bucket', 'region']}
        backend = get_storage_backend(
            provider=provider_str,
            bucket=pointer.bucket,
            **filtered_config,
        )
        
        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not quiet:
            # Download with progress
            from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                DownloadColumn(),
                TransferSpeedColumn(),
            ) as progress:
                task = progress.add_task(
                    f"Downloading {pointer.file_name}",
                    total=pointer.size,
                )
                
                def update_progress(download_progress) -> None:
                    if hasattr(download_progress, 'bytes_downloaded'):
                        progress.update(task, completed=download_progress.bytes_downloaded)
                    else:
                        progress.update(task, completed=download_progress)
                
                backend.download(
                    object_key=pointer.object_key,
                    file_path=target_path,
                    progress_callback=update_progress if pointer.size > 1024 * 1024 else None,
                )
                
                progress.update(task, completed=pointer.size)
        else:
            # Simple download without progress
            backend.download(
                object_key=pointer.object_key,
                file_path=target_path,
            )
            
    except Exception as e:
        raise StorageError(f"Download failed: {e}")