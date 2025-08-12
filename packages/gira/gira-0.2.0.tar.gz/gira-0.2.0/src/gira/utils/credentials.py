"""Storage credentials management utilities."""

import base64
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from gira.models.attachment import StorageProvider
from gira.storage.exceptions import StorageError


class CredentialsManager:
    """Manages secure storage and retrieval of storage provider credentials."""

    # Default paths for credential storage
    DEFAULT_CREDENTIAL_PATHS = [
        Path.home() / ".config" / "gira" / "storage.yml",
        Path.home() / ".config" / "gira" / "storage.yaml",
        Path.home() / ".gira" / "storage.yml",
        Path.home() / ".gira" / "storage.yaml",
    ]

    # Environment variable mappings for each provider
    ENV_MAPPINGS = {
        StorageProvider.S3: {
            "access_key_id": ["AWS_ACCESS_KEY_ID", "S3_ACCESS_KEY_ID"],
            "secret_access_key": ["AWS_SECRET_ACCESS_KEY", "S3_SECRET_ACCESS_KEY"],
            "session_token": ["AWS_SESSION_TOKEN", "S3_SESSION_TOKEN"],
            "region": ["AWS_DEFAULT_REGION", "S3_REGION"],
            "endpoint_url": ["S3_ENDPOINT_URL"],
        },
        StorageProvider.R2: {
            "access_key_id": ["R2_ACCESS_KEY_ID", "CLOUDFLARE_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID"],
            "secret_access_key": ["R2_SECRET_ACCESS_KEY", "CLOUDFLARE_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY"],
            "account_id": ["CLOUDFLARE_ACCOUNT_ID", "R2_ACCOUNT_ID"],
            "endpoint_url": ["R2_ENDPOINT_URL"],
        },
        StorageProvider.B2: {
            "application_key_id": ["B2_APPLICATION_KEY_ID", "B2_KEY_ID"],
            "application_key": ["B2_APPLICATION_KEY", "B2_KEY"],
            "endpoint_url": ["B2_ENDPOINT_URL"],
        },
        StorageProvider.GCS: {
            "service_account_key_path": ["GOOGLE_APPLICATION_CREDENTIALS", "GCS_KEY_PATH"],
            "project_id": ["GOOGLE_CLOUD_PROJECT", "GCP_PROJECT", "GCS_PROJECT"],
        },
        StorageProvider.AZURE: {
            "connection_string": ["AZURE_STORAGE_CONNECTION_STRING"],
            "account_name": ["AZURE_STORAGE_ACCOUNT_NAME", "AZURE_ACCOUNT_NAME"],
            "account_key": ["AZURE_STORAGE_ACCOUNT_KEY", "AZURE_ACCOUNT_KEY"],
            "sas_token": ["AZURE_STORAGE_SAS_TOKEN", "AZURE_SAS_TOKEN"],
        },
    }

    # Required credentials for each provider
    REQUIRED_CREDENTIALS = {
        StorageProvider.S3: ["access_key_id", "secret_access_key"],
        StorageProvider.R2: ["access_key_id", "secret_access_key", "account_id"],
        StorageProvider.B2: ["application_key_id", "application_key"],
        StorageProvider.GCS: ["service_account_key_path"],
        StorageProvider.AZURE: ["account_name"],  # Plus either account_key, sas_token, or connection_string
    }

    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize credentials manager.
        
        Args:
            encryption_key: Optional encryption key for storing credentials.
                           If not provided, credentials are stored in plain text.
        """
        self.encryption_key = encryption_key
        self._cipher = None
        if encryption_key:
            self._cipher = self._create_cipher(encryption_key)

    def load_credentials(
        self,
        provider: StorageProvider,
        credential_path: Optional[Path] = None,
        prefer_env: bool = True,
    ) -> Dict[str, Any]:
        """Load credentials for a storage provider.
        
        Args:
            provider: Storage provider enum
            credential_path: Optional path to credential file
            prefer_env: Whether to prefer environment variables over file
            
        Returns:
            Dictionary of credentials
            
        Raises:
            StorageError: If credentials cannot be loaded
        """
        # Try environment variables first (if preferred)
        if prefer_env:
            env_creds = self._load_from_environment(provider)
            if env_creds and self._validate_credentials(provider, env_creds):
                return env_creds

        # Then try credential files
        file_creds = self._load_from_file(provider, credential_path)
        if file_creds and self._validate_credentials(provider, file_creds):
            return file_creds

        # Try environment variables again (if not preferred initially)
        if not prefer_env:
            env_creds = self._load_from_environment(provider)
            if env_creds and self._validate_credentials(provider, env_creds):
                return env_creds

        # No valid credentials found
        raise StorageError(
            f"No valid credentials found for {provider.value}. "
            f"Please run 'gira storage configure' or set environment variables."
        )

    def save_credentials(
        self,
        provider: StorageProvider,
        credentials: Dict[str, Any],
        credential_path: Optional[Path] = None,
        encrypt: Optional[bool] = None,
    ) -> Path:
        """Save credentials to file.
        
        Args:
            provider: Storage provider enum
            credentials: Credentials dictionary
            credential_path: Optional path for credential file
            encrypt: Whether to encrypt credentials (uses instance setting if None)
            
        Returns:
            Path where credentials were saved
            
        Raises:
            StorageError: If credentials cannot be saved
        """
        if credential_path is None:
            credential_path = self.DEFAULT_CREDENTIAL_PATHS[0]

        # Validate credentials before saving
        if not self._validate_credentials(provider, credentials):
            raise StorageError(f"Invalid credentials for {provider.value}")

        # Create directory if needed
        credential_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data or create new
        if credential_path.exists():
            try:
                with open(credential_path) as f:
                    data = yaml.safe_load(f) or {}
            except Exception as e:
                raise StorageError(f"Failed to read existing credentials: {e}")
        else:
            data = {}

        # Ensure structure exists
        if "providers" not in data:
            data["providers"] = {}

        # Encrypt credentials if requested
        if encrypt is None:
            encrypt = self._cipher is not None

        if encrypt and self._cipher:
            # Encrypt sensitive fields
            encrypted_creds = self._encrypt_credentials(provider, credentials)
            data["providers"][provider.value] = encrypted_creds
            data["encrypted"] = True
        else:
            # Store in plain text
            data["providers"][provider.value] = credentials
            if "encrypted" not in data:
                data["encrypted"] = False

        # Save file with restricted permissions
        try:
            with open(credential_path, "w") as f:
                yaml.safe_dump(data, f, default_flow_style=False)

            # Set restrictive permissions (owner read/write only)
            credential_path.chmod(0o600)

            return credential_path

        except Exception as e:
            raise StorageError(f"Failed to save credentials: {e}")

    def check_availability(
        self,
        provider: StorageProvider,
        credential_path: Optional[Path] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Check if credentials are available for a provider.
        
        Args:
            provider: Storage provider enum
            credential_path: Optional path to credential file
            
        Returns:
            Tuple of (available, source) where source is 'env' or 'file' or None
        """
        # Check environment variables
        env_creds = self._load_from_environment(provider)
        if env_creds and self._validate_credentials(provider, env_creds):
            return True, "env"

        # Check file
        file_creds = self._load_from_file(provider, credential_path)
        if file_creds and self._validate_credentials(provider, file_creds):
            return True, "file"

        return False, None

    def validate_credentials(
        self,
        provider: StorageProvider,
        credentials: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """Validate credentials for a provider.
        
        Args:
            provider: Storage provider enum
            credentials: Credentials to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        try:
            if self._validate_credentials(provider, credentials):
                return True, None
            else:
                missing = self._get_missing_credentials(provider, credentials)
                return False, f"Missing required credentials: {', '.join(missing)}"
        except Exception as e:
            return False, str(e)

    def get_required_credentials(self, provider: StorageProvider) -> List[str]:
        """Get list of required credential fields for a provider.
        
        Args:
            provider: Storage provider enum
            
        Returns:
            List of required field names
        """
        return self.REQUIRED_CREDENTIALS.get(provider, [])

    def get_credential_help(self, provider: StorageProvider) -> str:
        """Get help text for configuring credentials for a provider.
        
        Args:
            provider: Storage provider enum
            
        Returns:
            Help text string
        """
        help_texts = {
            StorageProvider.S3: """AWS S3 Credentials:
- access_key_id: Your AWS Access Key ID
- secret_access_key: Your AWS Secret Access Key
- region: AWS region (e.g., us-east-1)
- session_token: Optional session token for temporary credentials

Get credentials from AWS IAM console or use AWS CLI credentials.""",

            StorageProvider.R2: """Cloudflare R2 Credentials:
- access_key_id: R2 Access Key ID from Cloudflare dashboard
- secret_access_key: R2 Secret Access Key
- account_id: Your Cloudflare account ID

Create API tokens at: Cloudflare Dashboard > R2 > Manage R2 API Tokens""",

            StorageProvider.B2: """Backblaze B2 Credentials:
- application_key_id: B2 Application Key ID
- application_key: B2 Application Key

Create application keys in B2 dashboard with read/write permissions.""",

            StorageProvider.GCS: """Google Cloud Storage Credentials:
- service_account_key_path: Path to service account JSON key file
- project_id: Optional GCP project ID

Create service account at: Console > IAM & Admin > Service Accounts""",

            StorageProvider.AZURE: """Azure Blob Storage Credentials:
Option 1 - Connection String:
- connection_string: Full Azure Storage connection string

Option 2 - Account Key:
- account_name: Storage account name
- account_key: Storage account key

Option 3 - SAS Token:
- account_name: Storage account name
- sas_token: Shared Access Signature token

Get credentials from Azure Portal > Storage Account > Access Keys""",
        }

        return help_texts.get(provider, f"No help available for {provider.value}")

    def _load_from_environment(self, provider: StorageProvider) -> Optional[Dict[str, Any]]:
        """Load credentials from environment variables."""
        if provider not in self.ENV_MAPPINGS:
            return None

        mappings = self.ENV_MAPPINGS[provider]
        credentials = {}

        for field, env_vars in mappings.items():
            for env_var in env_vars:
                value = os.environ.get(env_var)
                if value:
                    credentials[field] = value
                    break

        # Special handling for R2 endpoint URL
        if provider == StorageProvider.R2:
            if "account_id" in credentials and "endpoint_url" not in credentials:
                credentials["endpoint_url"] = f"https://{credentials['account_id']}.r2.cloudflarestorage.com"
            # R2 requires SSL verification to be disabled due to certificate issues
            credentials["verify_ssl"] = False

        return credentials if credentials else None

    def _load_from_file(
        self,
        provider: StorageProvider,
        credential_path: Optional[Path] = None,
    ) -> Optional[Dict[str, Any]]:
        """Load credentials from YAML file."""
        paths = [credential_path] if credential_path else self.DEFAULT_CREDENTIAL_PATHS

        for path in paths:
            if path and path.exists():
                try:
                    with open(path) as f:
                        data = yaml.safe_load(f)

                    if not isinstance(data, dict):
                        continue

                    # Check for provider in providers section
                    providers = data.get("providers", {})
                    if provider.value in providers:
                        creds = providers[provider.value]

                        # Decrypt if needed
                        if data.get("encrypted") and self._cipher:
                            creds = self._decrypt_credentials(provider, creds)

                        # Special handling for R2 endpoint URL
                        if provider == StorageProvider.R2:
                            if "account_id" in creds and "endpoint_url" not in creds:
                                creds["endpoint_url"] = f"https://{creds['account_id']}.r2.cloudflarestorage.com"
                            # R2 requires SSL verification to be disabled due to certificate issues
                            creds["verify_ssl"] = False

                        return creds

                    # Check for direct provider key (backward compatibility)
                    if provider.value in data:
                        return data[provider.value]

                except Exception:
                    continue

        return None

    def _validate_credentials(
        self,
        provider: StorageProvider,
        credentials: Dict[str, Any],
    ) -> bool:
        """Validate that credentials have all required fields."""
        required = self.REQUIRED_CREDENTIALS.get(provider, [])

        # Special handling for Azure (multiple auth options)
        if provider == StorageProvider.AZURE:
            if "connection_string" in credentials:
                return True
            if "account_name" in credentials:
                if "account_key" in credentials or "sas_token" in credentials:
                    return True
            return False

        # Check all required fields are present
        for field in required:
            if field not in credentials or not credentials[field]:
                return False

        return True

    def _get_missing_credentials(
        self,
        provider: StorageProvider,
        credentials: Dict[str, Any],
    ) -> List[str]:
        """Get list of missing required credentials."""
        required = self.REQUIRED_CREDENTIALS.get(provider, [])
        missing = []

        # Special handling for Azure
        if provider == StorageProvider.AZURE:
            if "connection_string" not in credentials:
                if "account_name" not in credentials:
                    missing.append("account_name or connection_string")
                elif "account_key" not in credentials and "sas_token" not in credentials:
                    missing.append("account_key or sas_token")
            return missing

        # Check all required fields
        for field in required:
            if field not in credentials or not credentials[field]:
                missing.append(field)

        return missing

    def _create_cipher(self, key: str) -> Fernet:
        """Create a Fernet cipher from a key string."""
        # Derive a proper key from the provided string
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'gira-storage-salt',  # Fixed salt for deterministic key derivation
            iterations=100000,
        )
        key_bytes = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        return Fernet(key_bytes)

    def _encrypt_credentials(
        self,
        provider: StorageProvider,
        credentials: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Encrypt sensitive credential fields."""
        if not self._cipher:
            return credentials

        # Fields to encrypt for each provider
        sensitive_fields = {
            StorageProvider.S3: ["secret_access_key", "session_token"],
            StorageProvider.R2: ["secret_access_key"],
            StorageProvider.B2: ["application_key"],
            StorageProvider.GCS: ["service_account_key_path"],  # Path is sensitive
            StorageProvider.AZURE: ["account_key", "sas_token", "connection_string"],
        }

        encrypted = credentials.copy()
        fields_to_encrypt = sensitive_fields.get(provider, [])

        for field in fields_to_encrypt:
            if field in encrypted and encrypted[field]:
                # Encrypt the value
                value = encrypted[field]
                if isinstance(value, str):
                    encrypted_value = self._cipher.encrypt(value.encode()).decode()
                    encrypted[field] = f"enc:{encrypted_value}"

        return encrypted

    def _decrypt_credentials(
        self,
        provider: StorageProvider,
        credentials: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Decrypt sensitive credential fields."""
        if not self._cipher:
            return credentials

        decrypted = credentials.copy()

        for field, value in decrypted.items():
            if isinstance(value, str) and value.startswith("enc:"):
                try:
                    encrypted_value = value[4:]  # Remove "enc:" prefix
                    decrypted_value = self._cipher.decrypt(encrypted_value.encode()).decode()
                    decrypted[field] = decrypted_value
                except Exception:
                    # If decryption fails, leave as is
                    pass

        return decrypted


# Convenience functions
def load_storage_credentials(
    provider: StorageProvider,
    credential_path: Optional[Path] = None,
    encryption_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Load credentials for a storage provider.
    
    Args:
        provider: Storage provider enum
        credential_path: Optional path to credential file
        encryption_key: Optional encryption key
        
    Returns:
        Dictionary of credentials
        
    Raises:
        StorageError: If credentials cannot be loaded
    """
    manager = CredentialsManager(encryption_key)
    return manager.load_credentials(provider, credential_path)


def save_storage_credentials(
    provider: StorageProvider,
    credentials: Dict[str, Any],
    credential_path: Optional[Path] = None,
    encryption_key: Optional[str] = None,
) -> Path:
    """Save credentials for a storage provider.
    
    Args:
        provider: Storage provider enum
        credentials: Credentials dictionary
        credential_path: Optional path for credential file
        encryption_key: Optional encryption key
        
    Returns:
        Path where credentials were saved
        
    Raises:
        StorageError: If credentials cannot be saved
    """
    manager = CredentialsManager(encryption_key)
    return manager.save_credentials(provider, credentials, credential_path)


def check_credential_availability(
    provider: StorageProvider,
    credential_path: Optional[Path] = None,
) -> Tuple[bool, Optional[str]]:
    """Check if credentials are available for a provider.
    
    Args:
        provider: Storage provider enum
        credential_path: Optional path to credential file
        
    Returns:
        Tuple of (available, source) where source is 'env' or 'file' or None
    """
    manager = CredentialsManager()
    return manager.check_availability(provider, credential_path)
