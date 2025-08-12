"""Mock storage backend for testing."""

import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, Optional, Union

from gira.storage.base import StorageBackend, StorageObject
from gira.storage.exceptions import StorageError, StorageNotFoundError


class MockBackend(StorageBackend):
    """Mock storage backend for testing purposes.
    
    This backend stores files in memory and can simulate various
    storage conditions like delays, errors, and size limits.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize mock backend.
        
        Args:
            config: Configuration dictionary with optional keys:
                - delay: Simulated operation delay in seconds
                - error_rate: Probability of simulated errors (0.0-1.0)
                - max_file_size: Maximum allowed file size in bytes
        """
        super().__init__(config)
        self.files: Dict[str, Dict[str, Any]] = {}
        self.delay = config.get("delay", 0)
        self.error_rate = config.get("error_rate", 0)
        self.max_file_size = config.get("max_file_size", 100 * 1024 * 1024)  # 100MB default
    
    def _validate_config(self) -> None:
        """Validate configuration.
        
        Mock backend has no required configuration.
        """
        # Mock backend doesn't require any specific configuration
        pass
    
    def _simulate_delay(self) -> None:
        """Simulate network delay if configured."""
        if self.delay > 0:
            time.sleep(self.delay)
    
    def _simulate_error(self) -> None:
        """Simulate random errors if configured."""
        if self.error_rate > 0 and random.random() < self.error_rate:
            raise StorageError("Simulated storage error")
    
    def upload(
        self,
        file_path: Union[str, Path],
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[Any] = None,
    ) -> StorageObject:
        """Upload a file to mock storage.
        
        Args:
            file_path: Path to the file to upload
            object_key: Key/path for the object in storage
            content_type: MIME type of the content
            metadata: Additional metadata to store
            progress_callback: Callback for progress updates
            
        Returns:
            StorageObject representing the uploaded file
            
        Raises:
            StorageError: If upload fails or file exceeds size limit
        """
        self._simulate_delay()
        self._simulate_error()
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise StorageError(f"File not found: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise StorageError(
                f"File size {file_size} exceeds maximum {self.max_file_size}"
            )
        
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Simulate progress updates
        if progress_callback:
            chunk_size = 8192
            bytes_read = 0
            while bytes_read < file_size:
                bytes_read = min(bytes_read + chunk_size, file_size)
                progress_callback(bytes_read)
        
        # Store in memory
        now = datetime.utcnow()
        self.files[object_key] = {
            "content": content,
            "size": file_size,
            "content_type": content_type or "application/octet-stream",
            "last_modified": now,
            "metadata": metadata or {},
        }
        
        return StorageObject(
            key=object_key,
            size=file_size,
            content_type=content_type or "application/octet-stream",
            last_modified=now,
            etag=f"mock-etag-{hash(content)}",
            metadata=metadata,
        )
    
    def download(
        self,
        object_key: str,
        file_path: Union[str, Path],
        progress_callback: Optional[Any] = None,
    ) -> None:
        """Download a file from mock storage.
        
        Args:
            object_key: Key/path of the object to download
            file_path: Local path to save the file
            progress_callback: Callback for progress updates
            
        Raises:
            StorageNotFoundError: If object doesn't exist
            StorageError: If download fails
        """
        self._simulate_delay()
        self._simulate_error()
        
        if object_key not in self.files:
            raise StorageNotFoundError(f"Object not found: {object_key}")
        
        file_data = self.files[object_key]
        content = file_data["content"]
        
        # Simulate progress updates
        if progress_callback:
            chunk_size = 8192
            bytes_written = 0
            total_size = len(content)
            while bytes_written < total_size:
                bytes_written = min(bytes_written + chunk_size, total_size)
                progress_callback(bytes_written)
        
        # Write to file
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
    
    def exists(self, object_key: str) -> bool:
        """Check if an object exists.
        
        Args:
            object_key: Key/path of the object
            
        Returns:
            True if object exists, False otherwise
        """
        self._simulate_delay()
        return object_key in self.files
    
    def delete(self, object_key: str) -> None:
        """Delete an object from storage.
        
        Args:
            object_key: Key/path of the object to delete
        """
        self._simulate_delay()
        self._simulate_error()
        
        # Idempotent - don't error if doesn't exist
        self.files.pop(object_key, None)
    
    def get_metadata(self, object_key: str) -> StorageObject:
        """Get object metadata.
        
        Args:
            object_key: Key/path of the object
            
        Returns:
            StorageObject with metadata
            
        Raises:
            StorageNotFoundError: If object doesn't exist
        """
        self._simulate_delay()
        
        if object_key not in self.files:
            raise StorageNotFoundError(f"Object not found: {object_key}")
        
        file_data = self.files[object_key]
        return StorageObject(
            key=object_key,
            size=file_data["size"],
            content_type=file_data["content_type"],
            last_modified=file_data["last_modified"],
            etag=f"mock-etag-{hash(file_data['content'])}",
            metadata=file_data["metadata"],
        )
    
    def list_objects(
        self,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Iterator[StorageObject]:
        """List objects in storage.
        
        Args:
            prefix: Filter objects by prefix
            delimiter: Delimiter for hierarchical listing
            max_results: Maximum number of results
            
        Yields:
            StorageObject instances
        """
        self._simulate_delay()
        
        count = 0
        for key, file_data in self.files.items():
            if prefix and not key.startswith(prefix):
                continue
            
            yield StorageObject(
                key=key,
                size=file_data["size"],
                content_type=file_data["content_type"],
                last_modified=file_data["last_modified"],
                etag=f"mock-etag-{hash(file_data['content'])}",
                metadata=file_data["metadata"],
            )
            
            count += 1
            if max_results and count >= max_results:
                break
    
    def copy(
        self,
        source_key: str,
        dest_key: str,
        source_bucket: Optional[str] = None,
    ) -> None:
        """Copy an object within storage.
        
        Args:
            source_key: Source object key
            dest_key: Destination object key
            source_bucket: Source bucket (ignored for mock)
            
        Raises:
            StorageNotFoundError: If source doesn't exist
        """
        self._simulate_delay()
        self._simulate_error()
        
        if source_key not in self.files:
            raise StorageNotFoundError(f"Source object not found: {source_key}")
        
        # Deep copy the file data
        import copy
        self.files[dest_key] = copy.deepcopy(self.files[source_key])
        self.files[dest_key]["last_modified"] = datetime.utcnow()
    
    def move(self, source_key: str, dest_key: str) -> None:
        """Move an object within storage.
        
        Args:
            source_key: Source object key
            dest_key: Destination object key
            
        Raises:
            StorageNotFoundError: If source doesn't exist
        """
        self.copy(source_key, dest_key)
        self.delete(source_key)
    
    def generate_presigned_url(
        self,
        object_key: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL.
        
        Args:
            object_key: Key/path of the object
            expires_in: URL expiration time in seconds
            method: HTTP method (GET or PUT)
            
        Returns:
            Mock presigned URL
            
        Raises:
            StorageNotFoundError: If object doesn't exist (for GET)
        """
        self._simulate_delay()
        
        if method == "GET" and object_key not in self.files:
            raise StorageNotFoundError(f"Object not found: {object_key}")
        
        expires_at = int(time.time()) + expires_in
        return f"mock://{object_key}?method={method}&expires={expires_at}"
    
    def test_connection(self) -> bool:
        """Test storage connection.
        
        Returns:
            Always True for mock backend
        """
        self._simulate_delay()
        return True
    
    def get_url(self, object_key: str) -> str:
        """Get the URL for an object.
        
        Args:
            object_key: Key/path of the object
            
        Returns:
            Mock URL for the object
        """
        return f"mock://{object_key}"