"""Storage-related exceptions."""


class StorageError(Exception):
    """Base exception for all storage-related errors."""
    pass


class StorageNotFoundError(StorageError):
    """Raised when an object is not found in storage."""
    pass


class StorageAuthenticationError(StorageError):
    """Raised when authentication with storage provider fails."""
    pass


class StoragePermissionError(StorageError):
    """Raised when lacking permissions for a storage operation."""
    pass


class StorageConnectionError(StorageError):
    """Raised when unable to connect to storage provider."""
    pass


class StorageConfigurationError(StorageError):
    """Raised when storage configuration is invalid or missing."""
    pass


class StorageQuotaExceededError(StorageError):
    """Raised when storage quota is exceeded."""
    pass


class StorageChecksumError(StorageError):
    """Raised when checksum validation fails."""
    pass