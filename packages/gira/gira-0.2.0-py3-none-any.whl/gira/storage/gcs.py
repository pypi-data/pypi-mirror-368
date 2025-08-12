"""Google Cloud Storage backend implementation."""

import io
import json
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from datetime import datetime, timedelta

from gira.storage.base import StorageBackend, StorageObject
from gira.storage.exceptions import (
    StorageError,
    StorageAuthenticationError,
    StorageNotFoundError,
    StoragePermissionError,
)
from gira.storage.retry import retryable_storage_operation

try:
    from google.cloud import storage
    from google.cloud.exceptions import (
        NotFound,
        Forbidden,
        Conflict,
        TooManyRequests,
        ServiceUnavailable,
    )
    from google.api_core.exceptions import (
        GoogleAPIError,
        RetryError,
    )
    from google.auth.exceptions import (
        DefaultCredentialsError,
        RefreshError,
    )
    HAS_GCS = True
except ImportError:
    HAS_GCS = False
    # Define dummy exceptions for type checking
    NotFound = Exception
    Forbidden = Exception
    Conflict = Exception
    TooManyRequests = Exception
    ServiceUnavailable = Exception
    GoogleAPIError = Exception
    RetryError = Exception
    DefaultCredentialsError = Exception
    RefreshError = Exception
    
    # For type checking only
    if TYPE_CHECKING:
        from google.cloud import storage


class GCSBackend(StorageBackend):
    """Google Cloud Storage backend implementation.
    
    This backend provides storage operations using Google Cloud Storage.
    It supports service account authentication via JSON key files and
    all standard storage operations.
    """
    
    def __init__(
        self,
        bucket: str,
        service_account_key_path: Optional[str] = None,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        storage_class: str = "STANDARD",
        **kwargs,
    ):
        """Initialize GCS backend.
        
        Args:
            bucket: GCS bucket name
            service_account_key_path: Path to service account JSON key file
            project_id: GCP project ID (optional, will be inferred from credentials)
            location: Default location for new buckets
            storage_class: Storage class for objects (STANDARD, NEARLINE, COLDLINE, ARCHIVE)
            **kwargs: Additional arguments passed to parent class
        """
        if not HAS_GCS:
            raise ImportError(
                "Google Cloud Storage support not installed. "
                "Install with: pip install gira[gcs]"
            )
        
        # Store GCS-specific attributes
        self.bucket = bucket
        self.service_account_key_path = service_account_key_path
        self.project_id = project_id
        self.location = location
        self.storage_class = storage_class
        
        # Build config dict for parent class
        config = {
            "provider": "gcs",
            "bucket": bucket,
            "service_account_key_path": service_account_key_path,
            "project_id": project_id,
            "location": location,
            "storage_class": storage_class,
            **kwargs,
        }
        
        super().__init__(config)
        
        # Initialize client
        self._client: Optional["storage.Client"] = None
        self._bucket_obj: Optional["storage.Bucket"] = None
    
    def _validate_config(self) -> None:
        """Validate GCS backend configuration.
        
        Raises:
            StorageError: If configuration is invalid
        """
        if not self.bucket:
            raise StorageError("Bucket name is required for GCS backend")
        
        # Validate service account key path if provided
        if self.service_account_key_path:
            key_path = Path(self.service_account_key_path).expanduser()
            if not key_path.exists():
                raise StorageError(
                    f"Service account key file not found: {key_path}"
                )
            if not key_path.is_file():
                raise StorageError(
                    f"Service account key path is not a file: {key_path}"
                )
    
    def _get_client(self) -> "storage.Client":
        """Get or create GCS client."""
        if self._client is None:
            try:
                if self.service_account_key_path:
                    # Use service account key file
                    key_path = Path(self.service_account_key_path).expanduser()
                    self._client = storage.Client.from_service_account_json(
                        str(key_path),
                        project=self.project_id,
                    )
                else:
                    # Use default credentials (gcloud, env var, or metadata service)
                    self._client = storage.Client(project=self.project_id)
                    
            except FileNotFoundError as e:
                raise StorageAuthenticationError(
                    f"Service account key file not found: {self.service_account_key_path}"
                )
            except (DefaultCredentialsError, RefreshError, ValueError) as e:
                raise StorageAuthenticationError(
                    f"Failed to authenticate with GCS: {e}"
                )
            except Exception as e:
                raise StorageError(f"Failed to create GCS client: {e}")
        
        return self._client
    
    def _get_bucket(self) -> "storage.Bucket":
        """Get or create bucket object."""
        if self._bucket_obj is None:
            client = self._get_client()
            try:
                self._bucket_obj = client.get_bucket(self.bucket)
            except NotFound:
                raise StorageNotFoundError(
                    f"Bucket not found: {self.bucket}. "
                    f"Create it first or check the bucket name."
                )
            except Forbidden:
                raise StoragePermissionError(
                    f"Access denied to bucket: {self.bucket}. "
                    f"Check your credentials and permissions."
                )
            except Exception as e:
                raise StorageError(f"Failed to access bucket: {e}")
        
        return self._bucket_obj
    
    @retryable_storage_operation
    def upload(
        self,
        file_path: Union[str, Path],
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[callable] = None,
    ) -> StorageObject:
        """Upload a file to GCS.
        
        Args:
            file_path: Local file path to upload
            object_key: Object key in bucket
            content_type: MIME type of the file
            metadata: Additional metadata
            progress_callback: Callback for progress updates
            
        Returns:
            StorageObject with upload details
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        # Set content type
        if content_type:
            blob.content_type = content_type
        
        # Set metadata
        if metadata:
            blob.metadata = metadata
        
        # Upload file
        file_size = file_path.stat().st_size
        
        try:
            # For large files, use resumable upload
            if file_size > 5 * 1024 * 1024:  # 5MB
                with open(file_path, "rb") as f:
                    blob.upload_from_file(
                        f,
                        content_type=content_type,
                        num_retries=3,
                        timeout=300,  # 5 minutes
                    )
            else:
                blob.upload_from_filename(
                    str(file_path),
                    content_type=content_type,
                    num_retries=3,
                )
            
            # Reload to get updated metadata
            blob.reload()
            
            return StorageObject(
                key=blob.name,
                size=blob.size,
                last_modified=blob.updated,
                etag=blob.etag,
                content_type=blob.content_type,
                metadata=blob.metadata or {},
            )
            
        except Exception as e:
            raise StorageError(f"Upload failed: {e}")
    
    @retryable_storage_operation
    def download(
        self,
        object_key: str,
        file_path: Union[str, Path],
        progress_callback: Optional[callable] = None,
    ) -> Path:
        """Download an object from GCS.
        
        Args:
            object_key: Object key in bucket
            file_path: Local file path to save to
            progress_callback: Callback for progress updates
            
        Returns:
            Path to downloaded file
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        try:
            # Check if blob exists
            if not blob.exists():
                raise StorageNotFoundError(f"Object not found: {object_key}")
            
            # Download file
            blob.download_to_filename(str(file_path), timeout=300)
            
            return file_path
            
        except NotFound:
            raise StorageNotFoundError(f"Object not found: {object_key}")
        except Exception as e:
            raise StorageError(f"Download failed: {e}")
    
    @retryable_storage_operation
    def delete(self, object_key: str) -> None:
        """Delete an object from GCS.
        
        Args:
            object_key: Object key to delete
        """
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        try:
            blob.delete()
        except NotFound:
            # Already deleted, not an error
            pass
        except Exception as e:
            raise StorageError(f"Delete failed: {e}")
    
    @retryable_storage_operation
    def exists(self, object_key: str) -> bool:
        """Check if an object exists in GCS.
        
        Args:
            object_key: Object key to check
            
        Returns:
            True if object exists, False otherwise
        """
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        return blob.exists()
    
    @retryable_storage_operation
    def get_metadata(self, object_key: str) -> Dict[str, Any]:
        """Get object metadata from GCS.
        
        Args:
            object_key: Object key
            
        Returns:
            Dictionary of metadata
        """
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        try:
            # Reload to get latest metadata
            blob.reload()
            
            return {
                "size": blob.size,
                "content_type": blob.content_type,
                "etag": blob.etag,
                "last_modified": blob.updated.isoformat() if blob.updated else None,
                "storage_class": blob.storage_class,
                "metadata": blob.metadata or {},
                "md5_hash": blob.md5_hash,
                "crc32c": blob.crc32c,
                "generation": blob.generation,
                "metageneration": blob.metageneration,
            }
            
        except NotFound:
            raise StorageNotFoundError(f"Object not found: {object_key}")
        except Exception as e:
            raise StorageError(f"Get metadata failed: {e}")
    
    @retryable_storage_operation
    def list_objects(
        self,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> List[StorageObject]:
        """List objects in GCS bucket.
        
        Args:
            prefix: Filter objects by prefix
            delimiter: Delimiter for grouping (e.g., '/')
            max_results: Maximum number of results
            
        Returns:
            List of StorageObject instances
        """
        bucket = self._get_bucket()
        
        try:
            # List blobs
            blobs = bucket.list_blobs(
                prefix=prefix,
                delimiter=delimiter,
                max_results=max_results,
            )
            
            objects = []
            for blob in blobs:
                objects.append(
                    StorageObject(
                        key=blob.name,
                        size=blob.size,
                        last_modified=blob.updated,
                        etag=blob.etag,
                        content_type=blob.content_type,
                        metadata=blob.metadata or {},
                    )
                )
            
            return objects
            
        except Exception as e:
            raise StorageError(f"List objects failed: {e}")
    
    @retryable_storage_operation
    def copy(
        self,
        source_key: str,
        dest_key: str,
        source_bucket: Optional[str] = None,
    ) -> StorageObject:
        """Copy an object within GCS.
        
        Args:
            source_key: Source object key
            dest_key: Destination object key
            source_bucket: Source bucket (if different)
            
        Returns:
            StorageObject for the copied object
        """
        bucket = self._get_bucket()
        
        try:
            # Get source blob
            if source_bucket and source_bucket != self.bucket:
                source_bucket_obj = self._get_client().get_bucket(source_bucket)
                source_blob = source_bucket_obj.blob(source_key)
            else:
                source_blob = bucket.blob(source_key)
            
            # Copy to destination
            dest_blob = bucket.copy_blob(source_blob, bucket, dest_key)
            
            # Reload to get metadata
            dest_blob.reload()
            
            return StorageObject(
                key=dest_blob.name,
                size=dest_blob.size,
                last_modified=dest_blob.updated,
                etag=dest_blob.etag,
                content_type=dest_blob.content_type,
                metadata=dest_blob.metadata or {},
            )
            
        except NotFound:
            raise StorageNotFoundError(f"Source object not found: {source_key}")
        except Exception as e:
            raise StorageError(f"Copy failed: {e}")
    
    def move(
        self,
        source_key: str,
        dest_key: str,
        source_bucket: Optional[str] = None,
    ) -> StorageObject:
        """Move an object within GCS.
        
        Args:
            source_key: Source object key
            dest_key: Destination object key
            source_bucket: Source bucket (if different)
            
        Returns:
            StorageObject for the moved object
        """
        # Copy then delete
        result = self.copy(source_key, dest_key, source_bucket)
        
        # Delete source
        if source_bucket and source_bucket != self.bucket:
            source_bucket_obj = self._get_client().get_bucket(source_bucket)
            source_blob = source_bucket_obj.blob(source_key)
            source_blob.delete()
        else:
            self.delete(source_key)
        
        return result
    
    def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for GCS object.
        
        Args:
            object_key: Object key
            expiration: URL expiration in seconds
            method: HTTP method (GET, PUT, etc.)
            
        Returns:
            Presigned URL
        """
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        try:
            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(seconds=expiration),
                method=method,
            )
            
            return url
            
        except Exception as e:
            raise StorageError(f"Generate presigned URL failed: {e}")
    
    def upload_stream(
        self,
        stream: BinaryIO,
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> StorageObject:
        """Upload from a stream to GCS.
        
        Args:
            stream: Binary stream to upload
            object_key: Object key in bucket
            content_type: MIME type
            metadata: Additional metadata
            
        Returns:
            StorageObject with upload details
        """
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        # Set content type
        if content_type:
            blob.content_type = content_type
        
        # Set metadata
        if metadata:
            blob.metadata = metadata
        
        try:
            # Upload from stream
            blob.upload_from_file(stream, content_type=content_type)
            
            # Reload to get metadata
            blob.reload()
            
            return StorageObject(
                key=blob.name,
                size=blob.size,
                last_modified=blob.updated,
                etag=blob.etag,
                content_type=blob.content_type,
                metadata=blob.metadata or {},
            )
            
        except Exception as e:
            raise StorageError(f"Stream upload failed: {e}")
    
    def download_stream(self, object_key: str) -> BinaryIO:
        """Download an object to a stream from GCS.
        
        Args:
            object_key: Object key
            
        Returns:
            Binary stream containing object data
        """
        bucket = self._get_bucket()
        blob = bucket.blob(object_key)
        
        try:
            # Download to bytes
            data = blob.download_as_bytes()
            return io.BytesIO(data)
            
        except NotFound:
            raise StorageNotFoundError(f"Object not found: {object_key}")
        except Exception as e:
            raise StorageError(f"Stream download failed: {e}")
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test connection to GCS.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Try to get bucket
            bucket = self._get_bucket()
            
            # Try to list a few objects (with limit)
            list(bucket.list_blobs(max_results=1))
            
            return True, None
            
        except StorageAuthenticationError as e:
            return False, f"Authentication failed: {e}"
        except StoragePermissionError as e:
            return False, f"Permission denied: {e}"
        except StorageNotFoundError as e:
            return False, f"Bucket not found: {e}"
        except Exception as e:
            return False, f"Connection test failed: {e}"
    
    def create_bucket(self, location: Optional[str] = None) -> None:
        """Create the GCS bucket if it doesn't exist.
        
        Args:
            location: GCS location (e.g., 'us-central1')
        """
        client = self._get_client()
        
        try:
            # Check if bucket exists
            try:
                client.get_bucket(self.bucket)
                return  # Bucket already exists
            except NotFound:
                pass  # Bucket doesn't exist, create it
            
            # Create bucket
            bucket = client.create_bucket(
                self.bucket,
                location=location or self.location,
            )
            
            # Set storage class
            bucket.storage_class = self.storage_class
            bucket.patch()
            
            # Clear cached bucket
            self._bucket_obj = None
            
        except Conflict:
            # Bucket already exists (race condition)
            pass
        except Exception as e:
            raise StorageError(f"Failed to create bucket: {e}")
    
    def set_lifecycle_policy(
        self,
        rules: List[Dict[str, Any]],
    ) -> None:
        """Set lifecycle policy for the bucket.
        
        Args:
            rules: List of lifecycle rules
        """
        bucket = self._get_bucket()
        
        try:
            bucket.lifecycle_rules = rules
            bucket.patch()
        except Exception as e:
            raise StorageError(f"Failed to set lifecycle policy: {e}")
    
    def enable_versioning(self) -> None:
        """Enable versioning for the bucket."""
        bucket = self._get_bucket()
        
        try:
            bucket.versioning_enabled = True
            bucket.patch()
        except Exception as e:
            raise StorageError(f"Failed to enable versioning: {e}")
    
    def set_retention_policy(
        self,
        retention_period_seconds: int,
    ) -> None:
        """Set retention policy for the bucket.
        
        Args:
            retention_period_seconds: Retention period in seconds
        """
        bucket = self._get_bucket()
        
        try:
            bucket.retention_period = retention_period_seconds
            bucket.patch()
        except Exception as e:
            raise StorageError(f"Failed to set retention policy: {e}")