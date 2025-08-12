"""Download attachments from comments."""

from pathlib import Path
from typing import Optional, List

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TimeRemainingColumn
)
from rich.table import Table

from gira.storage import get_storage_backend
from gira.storage.exceptions import StorageError
from gira.utils.config_utils import load_config
from gira.utils.credentials import CredentialsManager
from gira.utils.comment_attachments import (
    list_comment_attachments,
    find_comment_in_entity
)
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.epic_utils import find_epic
from gira.storage.utils import format_bytes


def download(
    entity_id: str = typer.Argument(
        ...,
        help="Ticket or Epic ID (e.g., GCM-123 or EPIC-001)"
    ),
    comment_id: str = typer.Argument(
        ...,
        help="Comment ID to download attachments from"
    ),
    filenames: Optional[List[str]] = typer.Argument(
        None,
        help="Specific filename(s) to download (downloads all if not specified)"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory (defaults to current directory)"
    ),
    all_attachments: bool = typer.Option(
        False,
        "--all", "-a",
        help="Download all attachments (default if no filenames specified)"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite", "-f",
        help="Overwrite existing files"
    ),
) -> None:
    f"""Download attachments from a comment.
    {format_examples_simple([
        create_example("Download all attachments", "gira comment download GCM-123 20250729-123456"),
        create_example("Download specific file", "gira comment download GCM-123 20250729-123456 screenshot.png"),
        create_example("Download to specific directory", "gira comment download GCM-123 20250729-123456 --output ./downloads/"),
        create_example("Download multiple files", "gira comment download GCM-123 20250729-123456 file1.pdf file2.log")
    ])}"""
    # Ensure we're in a Gira project
    gira_root = ensure_gira_project()
    
    # Determine entity type
    entity_id = entity_id.upper()
    is_epic = entity_id.startswith("EPIC-")
    entity_type = "epic" if is_epic else "ticket"
    
    # Find the entity
    if is_epic:
        entity, _ = find_epic(entity_id, gira_root, include_archived=True)
    else:
        entity, _ = find_ticket(entity_id, gira_root, include_archived=True)
    
    if not entity:
        console.print(f"[red]Error:[/red] {entity_type.capitalize()} {entity_id} not found")
        raise typer.Exit(1)
    
    # Find the comment
    comment = find_comment_in_entity(entity, comment_id)
    if not comment:
        console.print(f"[red]Error:[/red] Comment {comment_id} not found in {entity_type} {entity_id}")
        raise typer.Exit(1)
    
    # Get attachments
    attachments = list_comment_attachments(entity_type, entity_id, comment_id, gira_root)
    if not attachments:
        console.print(f"[yellow]No attachments found for comment {comment_id}[/yellow]")
        raise typer.Exit(0)
    
    # Determine which files to download
    files_to_download = []
    if not filenames or all_attachments:
        # Download all
        files_to_download = attachments
    else:
        # Match specific filenames
        attachment_map = {att.file_name: att for att in attachments}
        for filename in filenames:
            if filename in attachment_map:
                files_to_download.append(attachment_map[filename])
            else:
                console.print(f"[yellow]Warning:[/yellow] Attachment not found: {filename}")
    
    if not files_to_download:
        console.print("[yellow]No matching attachments to download[/yellow]")
        raise typer.Exit(0)
    
    # Determine output directory
    output_dir = Path(output) if output else Path.cwd()
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load storage configuration
    config = load_config(gira_root)
    
    if not config.get("storage.enabled", False):
        console.print("[red]Error:[/red] Storage is not enabled. Cannot download attachments.")
        raise typer.Exit(1)
    
    # Load credentials
    provider = config.get("storage.provider", "s3")
    try:
        from gira.models.attachment import StorageProvider
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
    
    # Show what will be downloaded
    table = Table(title="Attachments to Download")
    table.add_column("Filename", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Type")
    
    total_size = 0
    for att in files_to_download:
        table.add_row(
            att.file_name,
            att.get_display_size(),
            att.content_type
        )
        total_size += att.size
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(files_to_download)} file(s), {format_bytes(total_size)}[/dim]")
    console.print(f"[dim]Download to: {output_dir}[/dim]\n")
    
    # Download files
    downloaded = 0
    failed = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        for att in files_to_download:
            output_path = output_dir / att.file_name
            
            # Check if file exists
            if output_path.exists() and not overwrite:
                console.print(f"[yellow]Skipped:[/yellow] {att.file_name} (file exists, use --overwrite)")
                continue
            
            task = progress.add_task(f"Downloading {att.file_name}...", total=att.size)
            
            try:
                # Download with progress callback
                def update_progress(bytes_downloaded):
                    progress.update(task, completed=bytes_downloaded)
                
                storage.download(
                    att.object_key,
                    str(output_path),
                    progress_callback=update_progress
                )
                
                downloaded += 1
                progress.update(task, completed=att.size)
                
            except StorageError as e:
                console.print(f"[red]Error:[/red] Failed to download {att.file_name}: {e}")
                failed += 1
                progress.remove_task(task)
            except Exception as e:
                console.print(f"[red]Error:[/red] Unexpected error downloading {att.file_name}: {e}")
                failed += 1
                progress.remove_task(task)
    
    # Show summary
    if downloaded > 0:
        console.print(Panel(
            f"[green]✓[/green] Downloaded {downloaded} file(s) to {output_dir}",
            title="Download Complete",
            border_style="green"
        ))
    
    if failed > 0:
        console.print(f"\n[red]Failed to download {failed} file(s)[/red]")
        raise typer.Exit(1)