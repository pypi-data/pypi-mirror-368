"""Common utilities for storage operations."""

import hashlib
import mimetypes
from pathlib import Path
from typing import BinaryIO, Optional, Union

from gira.storage.exceptions import StorageChecksumError


def calculate_checksum(
    file_path: Union[str, Path],
    algorithm: str = "sha256",
    chunk_size: int = 8192,
) -> str:
    """Calculate checksum of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (sha256, sha1, md5)
        chunk_size: Size of chunks to read
        
    Returns:
        Hex digest of the checksum
        
    Raises:
        ValueError: If algorithm is not supported
        FileNotFoundError: If file doesn't exist
    """
    if algorithm not in ["sha256", "sha1", "md5"]:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hasher = getattr(hashlib, algorithm)()
    
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def verify_checksum(
    file_path: Union[str, Path],
    expected_checksum: str,
    algorithm: str = "sha256",
) -> bool:
    """Verify file checksum matches expected value.
    
    Args:
        file_path: Path to the file
        expected_checksum: Expected checksum value
        algorithm: Hash algorithm used
        
    Returns:
        True if checksum matches, False otherwise
    """
    try:
        actual_checksum = calculate_checksum(file_path, algorithm)
        return actual_checksum == expected_checksum
    except (FileNotFoundError, ValueError):
        return False


def verify_checksum_strict(
    file_path: Union[str, Path],
    expected_checksum: str,
    algorithm: str = "sha256",
) -> None:
    """Verify file checksum matches expected value (raises exception on mismatch).
    
    Args:
        file_path: Path to the file
        expected_checksum: Expected checksum value
        algorithm: Hash algorithm used
        
    Raises:
        StorageChecksumError: If checksum doesn't match
    """
    actual_checksum = calculate_checksum(file_path, algorithm)
    if actual_checksum != expected_checksum:
        raise StorageChecksumError(
            f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}"
        )


def detect_content_type(file_path: Union[str, Path]) -> str:
    """Detect MIME type of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string (defaults to 'application/octet-stream')
    """
    file_path = Path(file_path)
    
    # First try to guess from filename
    content_type, _ = mimetypes.guess_type(str(file_path))
    
    if content_type:
        return content_type
    
    # Common extensions that mimetypes might miss
    extension_map = {
        ".log": "text/plain",
        ".diff": "text/plain",
        ".patch": "text/plain",
        ".csv": "text/csv",
        ".tsv": "text/tab-separated-values",
        ".jsonl": "application/x-ndjson",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
        ".toml": "text/plain",
        ".rst": "text/x-rst",
        ".adoc": "text/asciidoc",
    }
    
    suffix = file_path.suffix.lower()
    if suffix in extension_map:
        return extension_map[suffix]
    
    # Default for unknown types
    return "application/octet-stream"


def format_bytes(size: int) -> str:
    """Format byte size in human-readable format.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    
    if size == 0:
        return "0 B"
    
    for unit in units[:-1]:
        if abs(size) < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} {units[-1]}"


def sanitize_object_key(key: str) -> str:
    """Sanitize object key for safe storage.
    
    Removes or replaces problematic characters that might cause
    issues with certain storage backends.
    
    Args:
        key: Original object key
        
    Returns:
        Sanitized key
    """
    # Replace backslashes with forward slashes
    key = key.replace("\\", "/")
    
    # Remove leading slashes
    key = key.lstrip("/")
    
    # Replace multiple consecutive slashes with single slash
    while "//" in key:
        key = key.replace("//", "/")
    
    # Remove trailing slashes unless it's the only character
    if len(key) > 1:
        key = key.rstrip("/")
    
    return key


def generate_unique_key(
    base_path: str,
    filename: str,
    ticket_id: str,
    timestamp: Optional[str] = None,
) -> str:
    """Generate a unique object key for an attachment.
    
    Args:
        base_path: Base path in storage (e.g., project name)
        filename: Original filename
        ticket_id: Ticket ID the attachment belongs to
        timestamp: Optional timestamp to include
        
    Returns:
        Unique object key
    """
    from datetime import datetime
    
    if timestamp is None:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Build key components
    components = []
    
    if base_path:
        components.append(base_path)
    
    components.extend([
        "tickets",
        ticket_id,
        "attachments",
        f"{timestamp}_{filename}",
    ])
    
    # Join and sanitize
    key = "/".join(components)
    return sanitize_object_key(key)


class ChunkedReader:
    """Read file in chunks for streaming uploads."""
    
    def __init__(
        self,
        file_obj: BinaryIO,
        chunk_size: int = 8192,
        total_size: Optional[int] = None,
    ):
        self.file_obj = file_obj
        self.chunk_size = chunk_size
        self.total_size = total_size
        self.bytes_read = 0
    
    def __iter__(self):
        return self
    
    def __next__(self) -> bytes:
        chunk = self.file_obj.read(self.chunk_size)
        if not chunk:
            raise StopIteration
        
        self.bytes_read += len(chunk)
        return chunk
    
    @property
    def progress_percentage(self) -> float:
        """Get read progress as percentage."""
        if not self.total_size:
            return 0.0
        return (self.bytes_read / self.total_size) * 100