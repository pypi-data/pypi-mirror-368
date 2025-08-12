"""Azure Blob Storage backend implementation.

This module provides Azure Blob Storage support for Gira attachments.

Features:
- Multiple authentication methods (connection string, account key, SAS token, managed identity)
- Full CRUD operations (upload, download, delete, list)
- Progress callbacks for large file operations
- Automatic retry handling with exponential backoff
- Storage tier support (Hot, Cool, Archive)
- Presigned URL generation for temporary access
- Comprehensive error handling and mapping

Authentication Methods:
1. Connection String: Full connection string with account and key
2. Account Name + Key: Storage account name and access key
3. SAS Token: Shared Access Signature for limited access
4. Managed Identity: Azure managed identity for cloud deployments

Example Usage:
    # Connection string authentication
    backend = AzureBackend(
        container="gira-attachments",
        connection_string="DefaultEndpointsProtocol=https;AccountName=..."
    )
    
    # Account key authentication
    backend = AzureBackend(
        container="gira-attachments",
        account_name="mystorageaccount",
        account_key="base64key=="
    )
    
    # Managed identity authentication
    backend = AzureBackend(
        container="gira-attachments",
        account_name="mystorageaccount",
        use_managed_identity=True,
        client_id="optional-client-id"
    )

Storage Configuration:
- Container names must be 3-63 characters, lowercase letters, numbers, and hyphens
- Supports standard Azure storage tiers (Hot, Cool, Archive)
- Automatic content type detection for uploads
- Metadata support for custom attributes
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional, Union, TYPE_CHECKING

from gira.storage.base import (
    DownloadProgress,
    StorageBackend,
    StorageObject,
    UploadProgress,
)
from gira.storage.exceptions import (
    StorageAuthenticationError,
    StorageConnectionError,
    StorageError,
    StorageNotFoundError,
    StoragePermissionError,
    StorageQuotaExceededError,
)
from gira.storage.retry import retryable_storage_operation
from gira.storage.utils import detect_content_type

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.core.exceptions import (
        AzureError,
        ClientAuthenticationError,
        HttpResponseError,
        ResourceNotFoundError,
        ResourceExistsError,
        ServiceRequestError,
    )
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False
    # Define dummy exceptions for type checking
    AzureError = Exception
    ClientAuthenticationError = Exception
    HttpResponseError = Exception
    ResourceNotFoundError = Exception
    ResourceExistsError = Exception
    ServiceRequestError = Exception
    DefaultAzureCredential = None
    ManagedIdentityCredential = None
    
    # For type checking only
    if TYPE_CHECKING:
        from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


class AzureBackend(StorageBackend):
    """Azure Blob Storage backend implementation.
    
    This backend provides storage operations using Azure Blob Storage.
    It supports multiple authentication methods including connection strings,
    SAS tokens, account keys, and managed identities.
    """
    
    def __init__(
        self,
        container: str,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        connection_string: Optional[str] = None,
        sas_token: Optional[str] = None,
        account_url: Optional[str] = None,
        use_managed_identity: bool = False,
        client_id: Optional[str] = None,
        tier: str = "Hot",
        **kwargs,
    ):
        """Initialize Azure backend.
        
        Args:
            container: Azure container name
            account_name: Storage account name
            account_key: Storage account key
            connection_string: Full connection string (alternative to account_name/key)
            sas_token: SAS token for authentication
            account_url: Custom account URL
            use_managed_identity: Use managed identity for authentication
            client_id: Client ID for managed identity
            tier: Storage tier (Hot, Cool, Archive)
            **kwargs: Additional arguments passed to parent class
        """
        if not HAS_AZURE:
            raise ImportError(
                "Azure Blob Storage support not installed. "
                "Install with: pip install gira[azure]"
            )
        
        # Store Azure-specific attributes
        self.container = container
        self.account_name = account_name
        self.account_key = account_key
        self.connection_string = connection_string
        self.sas_token = sas_token
        self.account_url = account_url
        self.use_managed_identity = use_managed_identity
        self.client_id = client_id
        self.tier = tier
        
        # Build config dict for parent class
        config = {
            "provider": "azure",
            "container": container,
            "account_name": account_name,
            "account_key": account_key,
            "connection_string": connection_string,
            "sas_token": sas_token,
            "account_url": account_url,
            "use_managed_identity": use_managed_identity,
            "client_id": client_id,
            "tier": tier,
            **kwargs,
        }
        
        super().__init__(config)
        
        # Initialize Azure client
        self._client: Optional["BlobServiceClient"] = None
        self._container_client: Optional["ContainerClient"] = None
    
    def _validate_config(self) -> None:
        """Validate Azure-specific configuration."""
        if not self.container:
            raise StorageError("Container name is required")
        
        # Validate authentication configuration
        auth_methods = [
            self.connection_string,
            self.account_name and self.account_key,
            self.sas_token,
            self.use_managed_identity,
        ]
        
        if not any(auth_methods):
            raise StorageError(
                "At least one authentication method must be provided: "
                "connection_string, account_name+account_key, sas_token, or managed_identity"
            )
    
    def _get_client(self) -> "BlobServiceClient":
        """Get or create Azure Blob Storage client."""
        if self._client is None:
            try:
                if self.connection_string:
                    self._client = BlobServiceClient.from_connection_string(
                        self.connection_string
                    )
                elif self.use_managed_identity:
                    if self.client_id:
                        credential = ManagedIdentityCredential(client_id=self.client_id)
                    else:
                        credential = DefaultAzureCredential()
                    
                    account_url = (
                        self.account_url or 
                        f"https://{self.account_name}.blob.core.windows.net"
                    )
                    self._client = BlobServiceClient(account_url, credential=credential)
                elif self.sas_token:
                    account_url = (
                        self.account_url or 
                        f"https://{self.account_name}.blob.core.windows.net"
                    )
                    self._client = BlobServiceClient(
                        account_url=f"{account_url}?{self.sas_token}"
                    )
                elif self.account_name and self.account_key:
                    account_url = (
                        self.account_url or 
                        f"https://{self.account_name}.blob.core.windows.net"
                    )
                    self._client = BlobServiceClient(
                        account_url=account_url,
                        credential=self.account_key
                    )
                else:
                    raise StorageError("No valid authentication method configured")
                    
            except ClientAuthenticationError as e:
                raise StorageAuthenticationError(f"Azure authentication failed: {e}")
            except AzureError as e:
                raise StorageError(f"Failed to create Azure client: {e}")
        
        return self._client
    
    def _get_container_client(self) -> "ContainerClient":
        """Get or create container client."""
        if self._container_client is None:
            client = self._get_client()
            self._container_client = client.get_container_client(self.container)
        return self._container_client
    
    def _handle_azure_error(self, error: Exception, operation: str) -> None:
        """Convert Azure exceptions to storage exceptions."""
        if isinstance(error, ResourceNotFoundError):
            raise StorageNotFoundError(f"Resource not found during {operation}: {error}")
        elif isinstance(error, ClientAuthenticationError):
            raise StorageAuthenticationError(f"Authentication failed during {operation}: {error}")
        elif isinstance(error, HttpResponseError):
            if error.status_code == 403:
                raise StoragePermissionError(f"Permission denied during {operation}: {error}")
            elif error.status_code == 413:
                raise StorageQuotaExceededError(f"Quota exceeded during {operation}: {error}")
            else:
                raise StorageError(f"HTTP error during {operation}: {error}")
        elif isinstance(error, ServiceRequestError):
            raise StorageConnectionError(f"Connection error during {operation}: {error}")
        else:
            raise StorageError(f"Azure error during {operation}: {error}")
    
    @retryable_storage_operation
    def upload(
        self,
        file_path: Union[str, Path],
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None,
    ) -> StorageObject:
        """Upload a file to Azure Blob Storage."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = detect_content_type(file_path)
        
        file_size = file_path.stat().st_size
        
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(object_key)
            
            # Create progress callback wrapper
            def azure_progress_callback(current: int, total: int) -> None:
                if progress_callback:
                    percentage = (current / total) * 100 if total > 0 else 0
                    progress_callback(UploadProgress(current, total, percentage))
            
            # Upload file
            with open(file_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    blob_type="BlockBlob",
                    content_type=content_type,
                    metadata=metadata,
                    tier=self.tier,
                    overwrite=True,
                    progress_hook=azure_progress_callback if progress_callback else None,
                )
            
            # Get blob properties for return value
            properties = blob_client.get_blob_properties()
            
            return StorageObject(
                key=object_key,
                size=properties.size,
                content_type=properties.content_settings.content_type or content_type,
                last_modified=properties.last_modified,
                etag=properties.etag,
                metadata=properties.metadata,
            )
            
        except AzureError as e:
            self._handle_azure_error(e, "upload")
    
    @retryable_storage_operation
    def download(
        self,
        object_key: str,
        file_path: Union[str, Path],
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
    ) -> Path:
        """Download an object from Azure Blob Storage."""
        file_path = Path(file_path)
        
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(object_key)
            
            # Get blob size for progress tracking
            properties = blob_client.get_blob_properties()
            total_size = properties.size
            
            # Create progress callback wrapper
            bytes_downloaded = 0
            
            def azure_progress_callback(current: int, total: int) -> None:
                nonlocal bytes_downloaded
                bytes_downloaded = current
                if progress_callback:
                    percentage = (current / total) * 100 if total > 0 else 0
                    progress_callback(DownloadProgress(current, total, percentage))
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            with open(file_path, "wb") as download_file:
                download_stream = blob_client.download_blob(
                    progress_hook=azure_progress_callback if progress_callback else None
                )
                download_stream.readinto(download_file)
            
            return file_path
            
        except AzureError as e:
            self._handle_azure_error(e, "download")
    
    @retryable_storage_operation
    def delete(self, object_key: str) -> None:
        """Delete an object from Azure Blob Storage."""
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(object_key)
            blob_client.delete_blob()
            
        except AzureError as e:
            self._handle_azure_error(e, "delete")
    
    @retryable_storage_operation
    def exists(self, object_key: str) -> bool:
        """Check if an object exists in Azure Blob Storage."""
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(object_key)
            return blob_client.exists()
            
        except AzureError as e:
            self._handle_azure_error(e, "exists check")
    
    @retryable_storage_operation
    def get_metadata(self, object_key: str) -> StorageObject:
        """Get metadata for an object in Azure Blob Storage."""
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(object_key)
            properties = blob_client.get_blob_properties()
            
            return StorageObject(
                key=object_key,
                size=properties.size,
                content_type=properties.content_settings.content_type or "application/octet-stream",
                last_modified=properties.last_modified,
                etag=properties.etag,
                metadata=properties.metadata,
            )
            
        except AzureError as e:
            self._handle_azure_error(e, "metadata retrieval")
    
    @retryable_storage_operation
    def list_objects(
        self,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Iterator[StorageObject]:
        """List objects in Azure Blob Storage."""
        try:
            container_client = self._get_container_client()
            
            # Azure blob listing parameters
            kwargs = {}
            if prefix:
                kwargs["name_starts_with"] = prefix
            if max_results:
                kwargs["results_per_page"] = max_results
            
            for blob in container_client.list_blobs(**kwargs):
                # Skip directories if delimiter is specified
                if delimiter and blob.name.endswith(delimiter):
                    continue
                
                yield StorageObject(
                    key=blob.name,
                    size=blob.size,
                    content_type=blob.content_settings.content_type or "application/octet-stream",
                    last_modified=blob.last_modified,
                    etag=blob.etag,
                    metadata=blob.metadata,
                )
                
        except AzureError as e:
            self._handle_azure_error(e, "object listing")
    
    @retryable_storage_operation
    def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for temporary access to Azure Blob."""
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            from datetime import datetime, timedelta
            
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(object_key)
            
            # Convert method to Azure permissions
            if method.upper() == "GET":
                permissions = BlobSasPermissions(read=True)
            elif method.upper() == "PUT":
                permissions = BlobSasPermissions(write=True, create=True)
            elif method.upper() == "DELETE":
                permissions = BlobSasPermissions(delete=True)
            else:
                raise StorageError(f"Unsupported method for presigned URL: {method}")
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container,
                blob_name=object_key,
                account_key=self.account_key,
                permission=permissions,
                expiry=datetime.utcnow() + timedelta(seconds=expiration),
            )
            
            # Return full URL with SAS token
            return f"{blob_client.url}?{sas_token}"
            
        except AzureError as e:
            self._handle_azure_error(e, "presigned URL generation")
    
    @retryable_storage_operation
    def test_connection(self) -> bool:
        """Test if Azure Blob Storage is accessible."""
        try:
            container_client = self._get_container_client()
            # Try to get container properties as a simple test
            container_client.get_container_properties()
            return True
            
        except AzureError:
            return False
    
    def copy(
        self,
        source_key: str,
        destination_key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> StorageObject:
        """Copy an object within Azure Blob Storage."""
        try:
            container_client = self._get_container_client()
            source_blob = container_client.get_blob_client(source_key)
            dest_blob = container_client.get_blob_client(destination_key)
            
            # Start copy operation
            copy_props = dest_blob.start_copy_from_url(source_blob.url)
            
            # Wait for copy to complete (Azure copies are usually fast)
            import time
            while copy_props.get("copy_status") == "pending":
                time.sleep(0.1)
                copy_props = dest_blob.get_blob_properties()
            
            if copy_props.get("copy_status") != "success":
                raise StorageError(f"Copy operation failed: {copy_props.get('copy_status')}")
            
            # Update metadata if provided
            if metadata:
                dest_blob.set_blob_metadata(metadata)
            
            # Return metadata for copied object
            return self.get_metadata(destination_key)
            
        except AzureError as e:
            self._handle_azure_error(e, "copy")