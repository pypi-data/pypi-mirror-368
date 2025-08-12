"""Stream attachment content to stdout - agent-friendly content access."""

import sys
import tempfile
from pathlib import Path
from typing import Optional

import typer
import urllib3
from gira.utils.help_formatter import create_example, format_examples_simple

from gira.models.attachment import AttachmentPointer, EntityType
from gira.storage import get_storage_backend
from gira.storage.config import StorageConfig
from gira.storage.exceptions import StorageError, StorageNotFoundError
from gira.utils.errors import GiraError
from gira.utils.project import ensure_gira_project


def cat_attachment(
    entity_id: str = typer.Argument(..., help="Entity ID (e.g., GCM-123 or EPIC-001)"),
    filename: str = typer.Argument(..., help="Attachment filename to stream"),
    entity_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Entity type (ticket or epic)"
    ),
) -> None:
    f"""Stream attachment content to stdout for piping and processing.
    
    This command outputs file content directly to stdout, making it ideal
    for AI agents and scripts that need to process text-based attachments.
    Binary files will result in an error with a helpful message.
    {format_examples_simple([
        create_example("Stream a text file", "gira attachment cat GCM-123 README.md"),
        create_example("Pipe to grep", "gira attachment cat GCM-123 log.txt | grep ERROR"),
        create_example("Parse JSON", "gira attachment cat GCM-123 config.json | jq '.database'"),
        create_example("Process CSV", "gira attachment cat GCM-123 data.csv | cut -d',' -f2")
    ])}"""
    try:
        # Ensure we're in a Gira project
        root = ensure_gira_project()
        
        # Determine entity type
        if entity_type:
            entity_type_enum = EntityType(entity_type.lower())
        else:
            entity_type_enum = _infer_entity_type(entity_id)
        
        # Load attachment pointer
        pointer = _load_attachment_pointer(root, entity_id, filename)
        
        # Check if file is likely binary
        if _is_binary_type(pointer):
            raise GiraError(
                f"Cannot stream binary file: {filename}\n"
                f"Content type: {pointer.content_type}\n"
                f"Use 'gira attachment download' for binary files."
            )
        
        # Stream file content
        _stream_file(pointer)
        
    except typer.Exit:
        raise
    except GiraError as e:
        # Handle our custom errors nicely
        if "Multiple attachments match" in str(e):
            print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        else:
            print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
    except Exception as e:
        raise GiraError(f"Failed to stream attachment: {e}")


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


def _is_binary_type(pointer: AttachmentPointer) -> bool:
    """Check if file is likely binary based on content type and extension."""
    # Text content types
    text_types = [
        "text/", "application/json", "application/xml", "application/yaml",
        "application/x-yaml", "application/javascript", "application/typescript",
        "application/x-sh", "application/x-python", "application/x-ruby",
        "application/toml", "application/sql", "application/x-httpd-php",
    ]
    
    # Check content type
    content_type = pointer.content_type.lower()
    for text_type in text_types:
        if content_type.startswith(text_type):
            return False
    
    # Check file extension
    text_extensions = {
        ".txt", ".md", ".rst", ".log", ".csv", ".tsv", ".json", ".xml", ".yaml", ".yml",
        ".toml", ".ini", ".cfg", ".conf", ".config", ".sh", ".bash", ".zsh", ".fish",
        ".py", ".pyw", ".rb", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
        ".java", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".cs", ".go", ".rs",
        ".php", ".pl", ".lua", ".r", ".R", ".sql", ".html", ".htm", ".css", ".scss",
        ".sass", ".less", ".vue", ".svelte", ".astro", ".tex", ".bib", ".dockerfile",
        ".dockerignore", ".gitignore", ".env", ".editorconfig", ".prettierrc",
        ".eslintrc", ".babelrc", ".vimrc", ".bashrc", ".zshrc", ".profile",
    }
    
    ext = Path(pointer.file_name).suffix.lower()
    if ext in text_extensions:
        return False
    
    # Default to binary for unknown types
    return True


def _stream_file(pointer: AttachmentPointer) -> None:
    """Stream file content to stdout."""
    try:
        # Load storage configuration
        provider_str = pointer.provider.value if hasattr(pointer.provider, 'value') else str(pointer.provider)
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
        
        # Download to temporary file and stream
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_path = Path(temp_file.name)
            
            # Download without progress (stderr would interfere with piping)
            backend.download(
                object_key=pointer.object_key,
                file_path=temp_path,
            )
            
            # Stream to stdout
            with open(temp_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    sys.stdout.buffer.write(chunk)
            
            # Ensure stdout is flushed
            sys.stdout.buffer.flush()
            
    except Exception as e:
        raise StorageError(f"Stream failed: {e}")