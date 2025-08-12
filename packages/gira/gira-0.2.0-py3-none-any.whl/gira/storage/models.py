"""Storage models for upload/download progress tracking."""

from dataclasses import dataclass


@dataclass
class UploadProgress:
    """Represents upload progress for storage operations."""
    bytes_uploaded: int
    bytes_total: int
    
    @property
    def percentage(self) -> float:
        """Calculate upload percentage."""
        if self.bytes_total == 0:
            return 0.0
        return (self.bytes_uploaded / self.bytes_total) * 100


@dataclass
class DownloadProgress:
    """Represents download progress for storage operations."""
    bytes_downloaded: int
    bytes_total: int
    
    @property
    def percentage(self) -> float:
        """Calculate download percentage."""
        if self.bytes_total == 0:
            return 0.0
        return (self.bytes_downloaded / self.bytes_total) * 100