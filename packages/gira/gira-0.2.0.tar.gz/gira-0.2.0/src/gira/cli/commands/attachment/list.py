"""List attachments command for Gira."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.panel import Panel
from rich.table import Table

from gira.models.attachment import AttachmentPointer
from gira.models.ticket import Ticket
from gira.models.epic import Epic
from gira.utils.project import ensure_gira_project

def list_attachments(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or epic ID to list attachments for (e.g., PROJ-123 or EPIC-001)",
    ),
    entity_type: Optional[str] = typer.Option(
        None,
        "--type", "-t",
        help="Entity type: ticket or epic (auto-detected if not specified)",
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table, json, or simple",
    ),
    file_type: Optional[str] = typer.Option(
        None,
        "--file-type",
        help="Filter by file type/extension (e.g., pdf, png, xlsx)",
    ),
    uploaded_after: Optional[str] = typer.Option(
        None,
        "--after",
        help="Show attachments uploaded after date (YYYY-MM-DD)",
    ),
    uploaded_before: Optional[str] = typer.Option(
        None,
        "--before",
        help="Show attachments uploaded before date (YYYY-MM-DD)",
    ),
    show_provider: bool = typer.Option(
        False,
        "--show-provider", "-p",
        help="Show storage provider details",
    ),
) -> None:
    """List all attachments for a ticket or epic.
    
    This command displays all attachments associated with a ticket or epic,
    including metadata like file size, type, uploader, and upload date.
    """
    # Ensure we're in a Gira project
    root = ensure_gira_project()
    
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
    
    # Validate format
    if format not in ["table", "json", "simple"]:
        console.print(f"[red]Error:[/red] Invalid format: {format}")
        console.print("Must be 'table', 'json', or 'simple'")
        raise typer.Exit(1)
    
    # Validate entity exists
    try:
        if entity_type == "ticket":
            entity_dir = root / ".gira" / "board"
            entity_found = False
            
            # Search for ticket across all statuses
            for status_dir in entity_dir.iterdir():
                if status_dir.is_dir():
                    ticket_file = status_dir / f"{entity_id}.json"
                    if ticket_file.exists():
                        entity_found = True
                        break
            
            if not entity_found:
                console.print(f"[red]Error:[/red] Ticket not found: {entity_id}")
                raise typer.Exit(1)
        else:
            epic_file = root / ".gira" / "epics" / f"{entity_id}.json"
            if not epic_file.exists():
                console.print(f"[red]Error:[/red] Epic not found: {entity_id}")
                raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error validating {entity_type}:[/red] {e}")
        raise typer.Exit(1)
    
    # Parse date filters
    after_date = None
    before_date = None
    
    if uploaded_after:
        try:
            after_date = datetime.strptime(uploaded_after, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid date format for --after: {uploaded_after}")
            console.print("Use YYYY-MM-DD format")
            raise typer.Exit(1)
    
    if uploaded_before:
        try:
            before_date = datetime.strptime(uploaded_before, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid date format for --before: {uploaded_before}")
            console.print("Use YYYY-MM-DD format")
            raise typer.Exit(1)
    
    # Get attachments directory
    attachments_dir = root / ".gira" / "attachments" / entity_id
    
    # Check if attachments directory exists
    if not attachments_dir.exists():
        if format == "json":
            console.print(json.dumps({"attachments": [], "count": 0}))
        else:
            console.print(f"[dim]No attachments found for {entity_type} {entity_id}[/dim]")
        return
    
    # Load all attachment pointers
    attachments: List[AttachmentPointer] = []
    errors = []
    
    # Check if we're using Git LFS
    from gira.utils.config_utils import load_config
    config = load_config(root)
    is_git_lfs = config.get("storage.provider") == "git-lfs"
    
    if is_git_lfs:
        # For Git LFS, actual files are stored directly in the attachments directory
        import subprocess
        from gira.utils.storage import get_file_info
        
        for file_path in attachments_dir.iterdir():
            if file_path.is_file() and not file_path.name.endswith(".yml"):
                try:
                    # Get file info
                    file_info = get_file_info(file_path)
                    
                    # Get Git author info for the file
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
                    
                    # Create a pseudo-pointer for Git LFS files
                    pointer = AttachmentPointer(
                        provider="git-lfs",
                        object_key=f"{entity_id}/{file_path.name}",
                        file_name=file_path.name,
                        content_type=file_info["content_type"],
                        size=file_info["size"],
                        checksum=file_info["checksum"],
                        uploaded_at=uploaded_at,
                        added_by=added_by,
                        entity_type=entity_type,
                        entity_id=entity_id,
                    )
                    
                    # Apply filters
                    if file_type:
                        file_ext = Path(pointer.file_name).suffix.lower().lstrip(".")
                        if file_ext != file_type.lower():
                            continue
                    
                    if after_date:
                        if pointer.uploaded_at.replace(tzinfo=None) < after_date:
                            continue
                    
                    if before_date:
                        if pointer.uploaded_at.replace(tzinfo=None) > before_date:
                            continue
                    
                    attachments.append(pointer)
                except Exception as e:
                    errors.append(f"Error processing {file_path.name}: {e}")
    else:
        # For cloud storage, read YAML pointer files
        for pointer_file in attachments_dir.glob("*.yml"):
            try:
                pointer = AttachmentPointer.from_yaml(pointer_file.read_text())
                
                # Apply filters
                if file_type:
                    # Check file extension
                    file_ext = Path(pointer.file_name).suffix.lower().lstrip(".")
                    if file_ext != file_type.lower():
                        continue
                
                if after_date:
                    if pointer.uploaded_at.replace(tzinfo=None) < after_date:
                        continue
                
                if before_date:
                    if pointer.uploaded_at.replace(tzinfo=None) > before_date:
                        continue
                
                attachments.append(pointer)
            except Exception as e:
                errors.append(f"Error reading {pointer_file.name}: {e}")
    
    # Sort by upload date (newest first)
    attachments.sort(key=lambda x: x.uploaded_at, reverse=True)
    
    # Display results based on format
    if format == "json":
        # JSON output
        data = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "count": len(attachments),
            "attachments": [
                {
                    "file_name": att.file_name,
                    "size": att.size,
                    "size_display": att.get_display_size(),
                    "content_type": att.content_type,
                    "uploaded_at": att.uploaded_at.isoformat() + "Z",
                    "added_by": att.added_by,
                    "note": att.note,
                    "checksum": att.checksum,
                    "provider": att.provider if isinstance(att.provider, str) else att.provider.value,
                    "bucket": att.bucket,
                    "object_key": att.object_key,
                }
                for att in attachments
            ],
        }
        if errors:
            data["errors"] = errors
        
        console.print(json.dumps(data, indent=2))
    
    elif format == "simple":
        # Simple output (just file names)
        if attachments:
            console.print(f"[bold]Attachments for {entity_type} {entity_id}:[/bold]")
            for att in attachments:
                console.print(f"  • {att.file_name} ({att.get_display_size()})")
            console.print(f"\n[dim]Total: {len(attachments)} attachment(s)[/dim]")
        else:
            console.print(f"[dim]No attachments found for {entity_type} {entity_id}[/dim]")
        
        if errors:
            console.print("\n[yellow]Warnings:[/yellow]")
            for error in errors:
                console.print(f"  • {error}")
    
    else:
        # Table output (default)
        if attachments:
            console.print(Panel.fit(
                f"[bold]Attachments for {entity_type.capitalize()} {entity_id}[/bold]\n"
                f"Total: {len(attachments)} file(s)",
                border_style="cyan"
            ))
            
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("File Name", style="white")
            table.add_column("Size", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Uploaded", style="cyan")
            table.add_column("Added By", style="magenta")
            
            if show_provider:
                table.add_column("Provider", style="blue")
                table.add_column("Location", style="dim")
            
            for att in attachments:
                row = [
                    att.file_name,
                    att.get_display_size(),
                    att.content_type,
                    att.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                    att.added_by,
                ]
                
                if show_provider:
                    provider_name = att.provider if isinstance(att.provider, str) else att.provider.value
                    if provider_name == "git-lfs":
                        location = att.object_key[:50] + "..." if len(att.object_key) > 50 else att.object_key
                    else:
                        location = f"{att.bucket}/{att.object_key[:30]}..." if len(att.object_key) > 30 else f"{att.bucket}/{att.object_key}"
                    row.extend([
                        provider_name.upper(),
                        location,
                    ])
                
                table.add_row(*row)
                
                # Add note as a sub-row if present
                if att.note:
                    note_cols = [""] * (len(row) - 1) + [f"[dim]Note: {att.note}[/dim]"]
                    if show_provider:
                        note_cols = [f"[dim]Note: {att.note}[/dim]"] + [""] * (len(row) - 1)
                    else:
                        note_cols = [f"[dim]Note: {att.note}[/dim]"] + [""] * (len(row) - 1)
                    table.add_row(*note_cols)
            
            console.print(table)
            
            # Show applied filters
            filters = []
            if file_type:
                filters.append(f"type={file_type}")
            if after_date:
                filters.append(f"after={uploaded_after}")
            if before_date:
                filters.append(f"before={uploaded_before}")
            
            if filters:
                console.print(f"\n[dim]Filters applied: {', '.join(filters)}[/dim]")
        else:
            console.print(f"[dim]No attachments found for {entity_type} {entity_id}")
            
            if file_type or after_date or before_date:
                console.print("\n[yellow]Note:[/yellow] Filters are applied. Try removing filters to see all attachments.")
        
        if errors:
            console.print("\n[yellow]Warnings:[/yellow]")
            for error in errors:
                console.print(f"  • {error}")
    
    # Show commands for next actions
    if attachments and format == "table":
        console.print(f"\n[dim]To download an attachment: [cyan]gira attachment open {entity_id} <filename>[/cyan][/dim]")
        console.print(f"[dim]To add a new attachment: [cyan]gira attachment add {entity_id} <file>[/cyan][/dim]")