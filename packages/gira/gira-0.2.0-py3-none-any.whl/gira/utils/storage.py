"""Storage utility functions for Gira."""

import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Dict


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get file information including size, content type, and checksum.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information:
        - size: File size in bytes
        - content_type: MIME type
        - checksum: SHA256 checksum
    """
    # Get file size
    size = file_path.stat().st_size

    # Guess content type
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "application/octet-stream"

    # Calculate SHA256 checksum
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)

    checksum = sha256_hash.hexdigest()

    return {
        "size": size,
        "content_type": content_type,
        "checksum": checksum,
    }
