"""Storage configuration helpers."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from gira.models.attachment import StorageProvider
from gira.storage.exceptions import StorageError
from gira.utils.credentials import CredentialsManager


class StorageConfig:
    """Helper for loading storage configuration and credentials."""
    
    # Default paths for credential storage
    DEFAULT_CREDENTIAL_PATHS = [
        Path.home() / ".config" / "gira" / "storage.yml",
        Path.home() / ".config" / "gira" / "storage.yaml",
        Path.home() / ".gira" / "storage.yml",
        Path.home() / ".gira" / "storage.yaml",
    ]
    
    @classmethod
    def load_credentials(
        cls,
        provider: str,
        credential_path: Optional[Path] = None,
        encryption_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Load credentials for a storage provider.
        
        Args:
            provider: Storage provider name (s3, gcs, azure, r2, b2)
            credential_path: Optional path to credential file
            encryption_key: Optional encryption key for decrypting credentials
            
        Returns:
            Dictionary of credentials
            
        Raises:
            StorageError: If credentials cannot be loaded
        """
        # Use CredentialsManager for loading
        try:
            provider_enum = StorageProvider(provider)
            manager = CredentialsManager(encryption_key)
            return manager.load_credentials(provider_enum, credential_path)
        except Exception as e:
            raise StorageError(f"Failed to load credentials: {e}")
    
    @classmethod
    def save_credentials(
        cls,
        provider: str,
        credentials: Dict[str, Any],
        credential_path: Optional[Path] = None,
        encryption_key: Optional[str] = None,
    ) -> Path:
        """Save credentials to file.
        
        Args:
            provider: Storage provider name
            credentials: Credentials dictionary
            credential_path: Optional path for credential file
            encryption_key: Optional encryption key for encrypting credentials
            
        Returns:
            Path where credentials were saved
        """
        # Use CredentialsManager for saving
        try:
            provider_enum = StorageProvider(provider)
            manager = CredentialsManager(encryption_key)
            return manager.save_credentials(
                provider_enum,
                credentials,
                credential_path,
                encrypt=(encryption_key is not None)
            )
        except Exception as e:
            raise StorageError(f"Failed to save credentials: {e}")
    
    @classmethod
    def merge_configs(
        cls,
        project_config: Dict[str, Any],
        credentials: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge project configuration with credentials.
        
        Args:
            project_config: Project-level storage configuration
            credentials: User credentials
            
        Returns:
            Merged configuration
        """
        # Start with project config
        config = project_config.copy()
        
        # Add credentials
        config.update(credentials)
        
        return config