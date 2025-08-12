"""Remove attachments command for Gira."""

import typer
import urllib3
from pathlib import Path
from typing import List, Optional
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.table import Table
from rich.panel import Panel

from gira.models.attachment import AttachmentPointer, EntityType
from gira.storage import get_storage_backend
from gira.storage.config import StorageConfig
from gira.storage.exceptions import StorageError, StorageNotFoundError
from gira.utils.errors import GiraError
from gira.utils.project import ensure_gira_project
from gira.utils.git_ops import commit_changes

def remove_attachment(
    entity_id: str = typer.Argument(..., help="Entity ID (e.g., GCM-123 or EPIC-001)"),
    attachment_ids: List[str] = typer.Argument(..., help="Attachment filename(s) or ID(s) to remove"),
    entity_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Entity type (ticket or epic)"
    ),
    delete_remote: bool = typer.Option(
        False, "--delete-remote", "-r", help="Also delete files from remote storage"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview changes without executing"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompts"
    ),
    no_commit: bool = typer.Option(
        False, "--no-commit", help="Don't auto-commit changes to Git"
    ),
) -> None:
    f"""Remove attachments from a ticket or epic.
    
    This command removes attachment pointer files from the Git repository.
    With --delete-remote, it also deletes the actual files from storage.
    {format_examples_simple([
        create_example("Remove a single attachment (pointer only)", "gira attachment remove GCM-123 document.pdf"),
        create_example("Remove multiple attachments", "gira attachment remove GCM-123 doc1.pdf doc2.xlsx"),
        create_example("Remove from storage as well (destructive!)", "gira attachment remove GCM-123 doc.pdf --delete-remote"),
        create_example("Preview changes before executing", "gira attachment remove GCM-123 doc.pdf --dry-run"),
        create_example("Remove without confirmation (dangerous!)", "gira attachment remove GCM-123 doc.pdf --delete-remote --force")
    ])}"""
    try:
        # Ensure we're in a Gira project
        root = ensure_gira_project()
        
        # Determine entity type
        if entity_type:
            entity_type_enum = EntityType(entity_type.lower())
        else:
            entity_type_enum = _infer_entity_type(entity_id)
        
        # Validate entity exists
        _validate_entity_exists(root, entity_id, entity_type_enum)
        
        # Get attachments directory
        attachments_dir = root / ".gira" / "attachments" / entity_id
        
        if not attachments_dir.exists():
            console.print(f"[yellow]No attachments found for {entity_type_enum.value} {entity_id}[/yellow]")
            return
        
        # Process each attachment
        removal_plan = []
        for attachment_id in attachment_ids:
            try:
                plan_item = _plan_removal(attachments_dir, attachment_id, delete_remote)
                if plan_item:
                    removal_plan.append(plan_item)
            except Exception as e:
                console.print(f"[red]✗[/red] Error planning removal for {attachment_id}: {e}")
        
        if not removal_plan:
            console.print("[yellow]No attachments found to remove[/yellow]")
            return
        
        # Show preview
        _show_removal_preview(removal_plan, dry_run, delete_remote)
        
        # Exit if dry run
        if dry_run:
            console.print("\n[dim]Dry run completed. Use --force to execute changes.[/dim]")
            return
        
        # Confirm destructive actions
        if not force and not _confirm_removal(removal_plan, delete_remote):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
        
        # Execute removals
        removed_files = []
        failed_removals = []
        
        for plan_item in removal_plan:
            try:
                success = _execute_removal(plan_item, delete_remote)
                if success:
                    removed_files.append(plan_item)
                else:
                    failed_removals.append(plan_item)
            except Exception as e:
                console.print(f"[red]✗[/red] Failed to remove {plan_item['filename']}: {e}")
                failed_removals.append(plan_item)
        
        # Show results
        if removed_files:
            console.print(f"\n[green]✓ Successfully removed {len(removed_files)} attachment(s)[/green]")
            for item in removed_files:
                console.print(f"  [green]✓[/green] {item['filename']}")
        
        if failed_removals:
            console.print(f"\n[red]✗ Failed to remove {len(failed_removals)} attachment(s)[/red]")
            for item in failed_removals:
                console.print(f"  [red]✗[/red] {item['filename']}")
        
        # Commit changes if requested
        if removed_files and not no_commit:
            _commit_removal_changes(entity_id, entity_type_enum, removed_files)
        
        # Summary
        if removed_files:
            action = "removed from storage" if delete_remote else "removed from Git"
            console.print(f"\n[green]Summary: {len(removed_files)} attachment(s) {action}[/green]")
        else:
            console.print(f"\n[red]No attachments were removed[/red]")
            
    except Exception as e:
        raise GiraError(f"Failed to remove attachments: {e}")


def _infer_entity_type(entity_id: str) -> EntityType:
    """Infer entity type from ID format."""
    if entity_id.upper().startswith("EPIC-"):
        return EntityType.EPIC
    else:
        return EntityType.TICKET


def _validate_entity_exists(root: Path, entity_id: str, entity_type: EntityType) -> None:
    """Validate that the entity exists."""
    if entity_type == EntityType.EPIC:
        epic_file = root / ".gira" / "epics" / f"{entity_id}.json"
        if not epic_file.exists():
            raise GiraError(f"Epic not found: {entity_id}")
    else:
        # Search for ticket across all statuses
        board_dir = root / ".gira" / "board"
        found = False
        
        for status_dir in board_dir.iterdir():
            if status_dir.is_dir():
                ticket_file = status_dir / f"{entity_id}.json"
                if ticket_file.exists():
                    found = True
                    break
        
        if not found:
            raise GiraError(f"Ticket not found: {entity_id}")


def _plan_removal(attachments_dir: Path, attachment_id: str, delete_remote: bool) -> Optional[dict]:
    """Plan the removal of an attachment."""
    # Find the attachment file by ID (checking all yml files)
    for pointer_file in attachments_dir.glob("*.yml"):
        try:
            pointer = AttachmentPointer.from_yaml(pointer_file.read_text())
            
            # Check if the filename matches the attachment_id
            file_stem = Path(pointer.file_name).stem
            if attachment_id in [file_stem, pointer.file_name, pointer_file.stem]:
                return {
                    "attachment_id": attachment_id,
                    "filename": pointer.file_name,
                    "pointer_file": pointer_file,
                    "pointer": pointer,
                    "size": pointer.size,
                    "provider": pointer.provider.value if hasattr(pointer.provider, 'value') else str(pointer.provider),
                    "delete_remote": delete_remote,
                }
        except Exception:
            # Skip files that can't be parsed
            continue
    
    return None


def _show_removal_preview(removal_plan: List[dict], dry_run: bool, delete_remote: bool) -> None:
    """Show a preview of what will be removed."""
    title = "🔍 Dry Run Preview" if dry_run else "📋 Removal Plan"
    
    table = Table(title=title)
    table.add_column("Filename", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Provider", style="dim")
    table.add_column("Actions", style="yellow")
    
    for item in removal_plan:
        actions = ["Remove pointer"]
        if delete_remote:
            actions.append("Delete from storage")
        
        size_display = _format_bytes(item["size"])
        table.add_row(
            item["filename"],
            size_display,
            item["provider"],
            ", ".join(actions)
        )
    
    console.print("\n")
    console.print(table)
    
    if delete_remote:
        console.print("\n[red]⚠️  Warning: --delete-remote will permanently delete files from storage![/red]")


def _confirm_removal(removal_plan: List[dict], delete_remote: bool) -> bool:
    """Confirm the removal operation with the user."""
    console.print()
    
    if delete_remote:
        message = (
            f"Are you sure you want to remove {len(removal_plan)} attachment(s) "
            f"[red]and delete them from storage[/red]?"
        )
        warning = "[red]⚠️  This action cannot be undone![/red]"
    else:
        message = (
            f"Are you sure you want to remove {len(removal_plan)} attachment pointer(s) "
            f"from Git?"
        )
        warning = "[yellow]Note: Files will remain in storage[/yellow]"
    
    console.print(Panel(f"{message}\n\n{warning}", title="Confirmation Required"))
    
    return typer.confirm("Continue?", default=False)


def _execute_removal(plan_item: dict, delete_remote: bool) -> bool:
    """Execute the removal of a single attachment."""
    pointer_file = plan_item["pointer_file"]
    pointer = plan_item["pointer"]
    filename = plan_item["filename"]
    
    success = True
    
    # Delete from remote storage if requested
    if delete_remote:
        try:
            _delete_from_storage(pointer)
            console.print(f"[green]✓[/green] Deleted {filename} from storage")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to delete {filename} from storage: {e}")
            success = False
    
    # Remove pointer file
    try:
        pointer_file.unlink()
        console.print(f"[green]✓[/green] Removed pointer for {filename}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to remove pointer for {filename}: {e}")
        success = False
    
    return success


def _delete_from_storage(pointer: AttachmentPointer) -> None:
    """Delete a file from remote storage."""
    try:
        # Get provider as string
        provider_str = pointer.provider.value if hasattr(pointer.provider, 'value') else str(pointer.provider)
        
        # Load storage configuration
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
        
        # Delete the object
        backend.delete(pointer.object_key)
        
    except StorageNotFoundError:
        # File already deleted, not an error
        pass
    except Exception as e:
        raise StorageError(f"Failed to delete from storage: {e}")


def _commit_removal_changes(entity_id: str, entity_type: EntityType, removed_files: List[dict]) -> None:
    """Commit the removal changes to Git."""
    try:
        from gira.utils.project import ensure_gira_project
        
        root = ensure_gira_project()
        filenames = [item["filename"] for item in removed_files]
        
        # Get the relative paths of the removed pointer files
        removed_paths = []
        for item in removed_files:
            pointer_file = item["pointer_file"]
            # Get relative path from project root
            rel_path = pointer_file.relative_to(root)
            removed_paths.append(str(rel_path))
        
        if len(filenames) == 1:
            message = f"remove attachment: {filenames[0]} from {entity_type.value} {entity_id}"
        else:
            message = f"remove attachments: {len(filenames)} files from {entity_type.value} {entity_id}"
        
        commit_changes(
            repo_path=root,
            files=removed_paths,
            message=message,
        )
        
        console.print(f"[green]✓[/green] Committed removal changes to Git")
        
    except Exception as e:
        console.print(f"[yellow]⚠️[/yellow] Failed to commit changes: {e}")


def _format_bytes(size: int) -> str:
    """Format bytes as human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            if unit == 'B':
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"