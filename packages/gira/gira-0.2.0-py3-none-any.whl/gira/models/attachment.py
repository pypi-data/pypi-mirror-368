"""Attachment pointer model for Gira."""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import Field, field_validator, model_validator

from gira.models.base import TimestampedModel
from gira.storage.utils import generate_unique_key, sanitize_object_key


class StorageProvider(str, Enum):
    """Supported storage providers."""
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"
    R2 = "r2"
    B2 = "b2"
    GIT_LFS = "git-lfs"
    
    @classmethod
    def from_string(cls, value: str) -> "StorageProvider":
        """Convert string to StorageProvider."""
        value_lower = value.lower()
        for provider in cls:
            if provider.value == value_lower:
                return provider
        raise ValueError(f"Invalid storage provider: {value}")


class EntityType(str, Enum):
    """Supported entity types for attachments."""
    TICKET = "ticket"
    EPIC = "epic"
    
    @classmethod
    def from_string(cls, value: str) -> "EntityType":
        """Convert string to EntityType."""
        value_lower = value.lower()
        for entity_type in cls:
            if entity_type.value == value_lower:
                return entity_type
        raise ValueError(f"Invalid entity type: {value}")


class AttachmentPointer(TimestampedModel):
    """Represents a pointer to an attachment stored in external storage.
    
    This model represents the small YAML file stored in the Git repository
    that points to the actual binary content in external storage.
    """
    
    # Storage location
    provider: StorageProvider = Field(
        ...,
        description="Storage provider (s3, gcs, azure, r2, b2)"
    )
    bucket: Optional[str] = Field(
        None,
        min_length=1,
        description="Storage bucket/container name (not used for git-lfs)"
    )
    object_key: str = Field(
        ...,
        min_length=1,
        description="Object key/path in storage"
    )
    
    # File metadata
    file_name: str = Field(
        ...,
        min_length=1,
        description="Original filename"
    )
    content_type: str = Field(
        default="application/octet-stream",
        description="MIME type of the content"
    )
    size: int = Field(
        ...,
        ge=0,
        description="File size in bytes"
    )
    checksum: str = Field(
        ...,
        description="SHA256 checksum of the file"
    )
    
    # Attachment metadata
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when file was uploaded"
    )
    added_by: str = Field(
        ...,
        min_length=1,
        description="User who added the attachment"
    )
    note: Optional[str] = Field(
        default=None,
        description="Optional description or note"
    )
    
    # Optional retention/expiry
    retention_days: Optional[int] = Field(
        default=None,
        ge=1,
        description="Retention period in days"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Expiration timestamp"
    )
    
    # Associated entity
    entity_type: str = Field(
        default="ticket",
        pattern=r"^(ticket|epic)$",
        description="Type of entity this attachment belongs to"
    )
    entity_id: str = Field(
        ...,
        min_length=1,
        description="ID of the entity (ticket/epic) this attachment belongs to"
    )
    
    @field_validator("provider", mode="before")
    @classmethod
    def validate_provider(cls, v: Any) -> StorageProvider:
        """Validate and convert provider to enum."""
        if isinstance(v, str):
            return StorageProvider.from_string(v)
        return v
    
    @field_validator("object_key")
    @classmethod
    def sanitize_key(cls, v: str) -> str:
        """Sanitize object key."""
        return sanitize_object_key(v)
    
    @field_validator("checksum")
    @classmethod
    def validate_checksum(cls, v: str) -> str:
        """Validate checksum format."""
        if not v:
            raise ValueError("Checksum cannot be empty")
        
        # Basic validation - should be hex string
        # SHA256 = 64 chars, SHA1 = 40 chars, MD5 = 32 chars
        if len(v) not in [32, 40, 64]:
            raise ValueError(
                f"Invalid checksum length: {len(v)}. "
                "Expected 32 (MD5), 40 (SHA1), or 64 (SHA256) characters."
            )
        
        # Check if it's valid hex
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("Checksum must be a hexadecimal string")
        
        return v.lower()
    
    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validate MIME type format."""
        if "/" not in v:
            raise ValueError(f"Invalid MIME type: {v}")
        return v
    
    @model_validator(mode="after")
    def validate_retention(self) -> "AttachmentPointer":
        """Validate retention and expiry fields."""
        if self.retention_days and self.expires_at:
            # Calculate expected expiry
            expected_expiry = self.uploaded_at + timedelta(days=self.retention_days)
            
            # Allow some tolerance (1 day)
            diff = abs((self.expires_at - expected_expiry).total_seconds())
            if diff > 86400:  # 1 day in seconds
                raise ValueError(
                    "expires_at doesn't match retention_days calculation"
                )
        
        return self
    
    @model_validator(mode="after")
    def validate_bucket(self) -> "AttachmentPointer":
        """Validate that bucket is provided for non-Git LFS providers."""
        if self.provider != StorageProvider.GIT_LFS and not self.bucket:
            raise ValueError(f"Bucket is required for {self.provider} storage provider")
        return self
    
    @classmethod
    def generate_object_key(
        cls,
        entity_type: str,
        entity_id: str,
        filename: str,
        base_path: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> str:
        """Generate a unique object key for the attachment.
        
        Args:
            entity_type: Type of entity (ticket/epic)
            entity_id: Entity ID
            filename: Original filename
            base_path: Optional base path in storage
            timestamp: Optional timestamp string
            
        Returns:
            Generated object key
        """
        from datetime import datetime
        
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # Build key components
        components = []
        
        if base_path:
            components.append(base_path)
        
        # Use appropriate directory based on entity type
        if entity_type == "epic":
            components.extend([
                "epics",
                entity_id,
                "attachments",
                f"{timestamp}_{filename}",
            ])
        else:
            components.extend([
                "tickets",
                entity_id,
                "attachments",
                f"{timestamp}_{filename}",
            ])
        
        # Join and sanitize
        key = "/".join(components)
        return sanitize_object_key(key)
    
    def to_yaml(self) -> str:
        """Serialize to YAML format for storage."""
        # Convert to dict, excluding None values
        data = self.model_dump(
            exclude_none=True,
            exclude={"created_at", "updated_at"},  # These are in TimestampedModel
        )
        
        # Convert datetime to ISO format strings
        if "uploaded_at" in data:
            data["uploaded_at"] = data["uploaded_at"].isoformat() + "Z"
        if "expires_at" in data:
            data["expires_at"] = data["expires_at"].isoformat() + "Z"
        
        # Convert enum to string (if it's still an enum)
        if "provider" in data and hasattr(data["provider"], "value"):
            data["provider"] = data["provider"].value
        
        # Order fields for readability
        ordered_fields = [
            "provider", "bucket", "object_key",
            "file_name", "content_type", "size", "checksum",
            "uploaded_at", "added_by", "note",
            "retention_days", "expires_at",
            "entity_type", "entity_id",
        ]
        
        ordered_data = {}
        for field in ordered_fields:
            if field in data:
                # Skip bucket field if it's None (for Git LFS)
                if field == "bucket" and data[field] is None:
                    continue
                ordered_data[field] = data[field]
        
        # Generate YAML with nice formatting
        return yaml.dump(
            ordered_data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=80,
        )
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> "AttachmentPointer":
        """Create AttachmentPointer from YAML content."""
        data = yaml.safe_load(yaml_content)
        
        # Convert ISO format strings back to datetime
        if "uploaded_at" in data and isinstance(data["uploaded_at"], str):
            # Remove 'Z' suffix if present and parse
            data["uploaded_at"] = datetime.fromisoformat(
                data["uploaded_at"].rstrip("Z")
            )
        if "expires_at" in data and isinstance(data["expires_at"], str):
            data["expires_at"] = datetime.fromisoformat(
                data["expires_at"].rstrip("Z")
            )
        
        return cls(**data)
    
    @classmethod
    def from_file(cls, file_path: Path) -> "AttachmentPointer":
        """Load AttachmentPointer from a YAML file."""
        with open(file_path, "r") as f:
            return cls.from_yaml(f.read())
    
    def save_to_file(self, file_path: Path) -> None:
        """Save AttachmentPointer to a YAML file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(self.to_yaml())
    
    def get_display_size(self) -> str:
        """Get human-readable file size."""
        from gira.storage.utils import format_bytes
        return format_bytes(self.size)
    
    def get_pointer_filename(self) -> str:
        """Get the filename for the pointer file."""
        # Use original filename but with .yml extension
        base_name = Path(self.file_name).stem
        return f"{base_name}.yml"


# Import at the end to avoid circular imports
from datetime import timedelta