"""Storage backend abstraction for Gira attachments."""

from typing import Any, Optional

from gira.storage.base import StorageBackend, StorageObject
from gira.storage.exceptions import (
    StorageAuthenticationError,
    StorageChecksumError,
    StorageConnectionError,
    StorageConfigurationError,
    StorageError,
    StorageNotFoundError,
    StoragePermissionError,
    StorageQuotaExceededError,
)

# Import S3 backend if boto3 is available
try:
    from gira.storage.s3 import S3Backend
    S3_AVAILABLE = True
except ImportError:
    S3Backend = None
    S3_AVAILABLE = False

# Import GCS backend if google-cloud-storage is available
try:
    from gira.storage.gcs import GCSBackend
    GCS_AVAILABLE = True
except ImportError:
    GCSBackend = None
    GCS_AVAILABLE = False

# Import Azure backend if azure-storage-blob is available
try:
    from gira.storage.azure import AzureBackend
    AZURE_AVAILABLE = True
except ImportError:
    AzureBackend = None
    AZURE_AVAILABLE = False


def get_storage_backend(
    provider: str,
    bucket: Optional[str] = None,
    region: Optional[str] = None,
    **kwargs: Any
) -> StorageBackend:
    """Factory function to create storage backend instances.
    
    Args:
        provider: Storage provider name (s3, r2, b2, gcs, azure, git-lfs, mock)
        bucket: Bucket/container name (not used for git-lfs)
        region: Optional region for the storage
        **kwargs: Provider-specific configuration
        
    Returns:
        StorageBackend instance
        
    Raises:
        ValueError: If provider is not supported
        ImportError: If required dependencies are not installed
    """
    provider = provider.lower()
    
    if provider in ["s3", "r2", "b2"]:
        if not S3_AVAILABLE:
            raise ImportError(
                "boto3 is required for S3-compatible storage. "
                "Install with: pip install gira[s3]"
            )
        if not bucket:
            raise ValueError(f"Bucket name is required for {provider} storage")
        config = {"bucket": bucket, "region": region, **kwargs}
        return S3Backend(config)
    
    elif provider == "gcs":
        if not GCS_AVAILABLE:
            raise ImportError(
                "google-cloud-storage is required for GCS storage. "
                "Install with: pip install gira[gcs]"
            )
        if not bucket:
            raise ValueError("Bucket name is required for GCS storage")
        return GCSBackend(bucket=bucket, **kwargs)
    
    elif provider == "azure":
        if not AZURE_AVAILABLE:
            raise ImportError(
                "azure-storage-blob is required for Azure storage. "
                "Install with: pip install gira[azure]"
            )
        if not bucket:
            raise ValueError("Container name is required for Azure storage")
        return AzureBackend(container=bucket, **kwargs)
    
    elif provider == "git-lfs":
        # Git LFS backend doesn't need external dependencies
        from gira.storage.git_lfs import GitLFSStorage
        return GitLFSStorage(**kwargs)
    
    elif provider == "mock":
        # Mock backend is always available (no external dependencies)
        from gira.storage.mock import MockBackend
        config = {"bucket": bucket or "mock-bucket", **kwargs}
        return MockBackend(config)
    
    else:
        raise ValueError(f"Unsupported storage provider: {provider}")


__all__ = [
    "StorageBackend",
    "StorageObject",
    "StorageError",
    "StorageNotFoundError",
    "StorageAuthenticationError",
    "StorageChecksumError",
    "StorageConnectionError",
    "StorageConfigurationError",
    "StoragePermissionError",
    "StorageQuotaExceededError",
    "get_storage_backend",
]

if S3_AVAILABLE:
    __all__.append("S3Backend")

if GCS_AVAILABLE:
    __all__.append("GCSBackend")

if AZURE_AVAILABLE:
    __all__.append("AzureBackend")