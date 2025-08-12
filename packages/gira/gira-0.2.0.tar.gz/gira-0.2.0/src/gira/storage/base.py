"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional, Union

from gira.storage.exceptions import StorageError, StorageNotFoundError


@dataclass
class StorageObject:
    """Metadata for a stored object."""
    key: str
    size: int
    content_type: str
    last_modified: datetime
    etag: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class UploadProgress:
    """Progress information for uploads."""
    bytes_uploaded: int
    total_bytes: int
    percentage: float


@dataclass
class DownloadProgress:
    """Progress information for downloads."""
    bytes_downloaded: int
    total_bytes: int
    percentage: float


class StorageBackend(ABC):
    """Abstract base class for storage backends.
    
    This class defines the interface that all storage backends must implement.
    It provides a consistent API for storing and retrieving attachments,
    regardless of the underlying storage provider.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the storage backend.
        
        Args:
            config: Backend-specific configuration
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate backend-specific configuration.
        
        Raises:
            StorageError: If configuration is invalid
        """
        pass

    @abstractmethod
    def upload(
        self,
        file_path: Union[str, Path],
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None,
    ) -> StorageObject:
        """Upload a file to storage.
        
        Args:
            file_path: Path to the file to upload
            object_key: Key/path for the object in storage
            content_type: MIME type of the content
            metadata: Additional metadata to store with the object
            progress_callback: Optional callback for upload progress
            
        Returns:
            StorageObject with upload details
            
        Raises:
            StorageError: If upload fails
            FileNotFoundError: If file_path doesn't exist
        """
        pass

    @abstractmethod
    def download(
        self,
        object_key: str,
        file_path: Union[str, Path],
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
    ) -> Path:
        """Download an object from storage.
        
        Args:
            object_key: Key/path of the object in storage
            file_path: Path where the file should be saved
            progress_callback: Optional callback for download progress
            
        Returns:
            Path to the downloaded file
            
        Raises:
            StorageNotFoundError: If object doesn't exist
            StorageError: If download fails
        """
        pass

    @abstractmethod
    def delete(self, object_key: str) -> None:
        """Delete an object from storage.
        
        Args:
            object_key: Key/path of the object to delete
            
        Raises:
            StorageNotFoundError: If object doesn't exist
            StorageError: If deletion fails
        """
        pass

    @abstractmethod
    def exists(self, object_key: str) -> bool:
        """Check if an object exists in storage.
        
        Args:
            object_key: Key/path of the object to check
            
        Returns:
            True if object exists, False otherwise
        """
        pass

    @abstractmethod
    def get_metadata(self, object_key: str) -> StorageObject:
        """Get metadata for an object without downloading it.
        
        Args:
            object_key: Key/path of the object
            
        Returns:
            StorageObject with metadata
            
        Raises:
            StorageNotFoundError: If object doesn't exist
            StorageError: If metadata retrieval fails
        """
        pass

    @abstractmethod
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
            max_results: Maximum number of results to return
            
        Yields:
            StorageObject instances
            
        Raises:
            StorageError: If listing fails
        """
        pass

    @abstractmethod
    def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for temporary access.
        
        Args:
            object_key: Key/path of the object
            expiration: URL expiration time in seconds
            method: HTTP method (GET, PUT, etc.)
            
        Returns:
            Presigned URL
            
        Raises:
            StorageError: If URL generation fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the storage backend is properly configured and accessible.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass

    def copy(
        self,
        source_key: str,
        destination_key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> StorageObject:
        """Copy an object within storage.
        
        Default implementation downloads and re-uploads.
        Backends can override for more efficient copying.
        
        Args:
            source_key: Key of the source object
            destination_key: Key for the destination object
            metadata: Optional metadata for the copy
            
        Returns:
            StorageObject for the copied object
            
        Raises:
            StorageNotFoundError: If source doesn't exist
            StorageError: If copy fails
        """
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
            
        try:
            # Download source to temp file
            self.download(source_key, tmp_path)
            
            # Get source metadata
            source_obj = self.get_metadata(source_key)
            
            # Upload to destination
            return self.upload(
                tmp_path,
                destination_key,
                content_type=source_obj.content_type,
                metadata=metadata or source_obj.metadata,
            )
        finally:
            # Clean up temp file
            if tmp_path.exists():
                tmp_path.unlink()

    def move(self, source_key: str, destination_key: str) -> StorageObject:
        """Move an object within storage.
        
        Args:
            source_key: Key of the source object
            destination_key: Key for the destination object
            
        Returns:
            StorageObject for the moved object
            
        Raises:
            StorageNotFoundError: If source doesn't exist
            StorageError: If move fails
        """
        # Copy then delete
        result = self.copy(source_key, destination_key)
        self.delete(source_key)
        return result