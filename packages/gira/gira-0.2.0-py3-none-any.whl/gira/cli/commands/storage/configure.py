"""Storage configuration command for Gira."""

import re
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import yaml
from gira.utils.console import console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from gira.models.attachment import StorageProvider
from gira.models.config import ProjectConfig, StorageConfig
from gira.storage.config import StorageConfig as StorageCredentialConfig
from gira.utils.board_config import get_valid_statuses
from gira.utils.config_utils import load_config, save_config
from gira.utils.credentials import CredentialsManager
from gira.utils.project import ensure_gira_project

# Provider-specific configuration guides
PROVIDER_GUIDES = {
    "s3": {
        "name": "Amazon S3",
        "credentials": ["access_key_id", "secret_access_key"],
        "optional": ["region", "endpoint_url"],
        "docs": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/",
        "examples": {
            "bucket": "my-project-attachments",
            "region": "us-east-1",
        },
        "notes": [
            "Ensure your AWS credentials have s3:PutObject, s3:GetObject, s3:DeleteObject permissions",
            "Use IAM roles for EC2 instances when possible",
            "Consider enabling versioning and lifecycle policies",
        ],
    },
    "r2": {
        "name": "Cloudflare R2",
        "credentials": ["access_key_id", "secret_access_key", "account_id"],
        "optional": ["endpoint_url"],
        "docs": "https://developers.cloudflare.com/r2/",
        "examples": {
            "bucket": "gira-attachments",
            "endpoint_url": "https://<account_id>.r2.cloudflarestorage.com",
        },
        "notes": [
            "R2 is S3-compatible with no egress fees",
            "Get credentials from Cloudflare dashboard > R2 > Manage R2 API Tokens",
            "Endpoint URL format: https://<account_id>.r2.cloudflarestorage.com",
        ],
    },
    "b2": {
        "name": "Backblaze B2",
        "credentials": ["application_key_id", "application_key"],
        "optional": ["endpoint_url"],
        "docs": "https://www.backblaze.com/b2/docs/",
        "examples": {
            "bucket": "gira-attachments",
            "endpoint_url": "https://s3.us-west-002.backblazeb2.com",
        },
        "notes": [
            "B2 is S3-compatible with competitive pricing",
            "Create application keys in B2 dashboard with read/write permissions",
            "Find your endpoint URL in bucket details",
        ],
    },
    "gcs": {
        "name": "Google Cloud Storage",
        "credentials": ["service_account_key_path"],
        "optional": ["project_id"],
        "docs": "https://cloud.google.com/storage/docs",
        "examples": {
            "bucket": "gira-attachments",
            "project_id": "my-gcp-project",
        },
        "notes": [
            "Use service account JSON key file for authentication",
            "Ensure service account has storage.objects.* permissions",
            "Consider using uniform bucket-level access",
        ],
    },
    "azure": {
        "name": "Azure Blob Storage",
        "credentials": ["account_name", "account_key"],
        "optional": ["container"],
        "docs": "https://docs.microsoft.com/en-us/azure/storage/blobs/",
        "examples": {
            "bucket": "giraattachments",  # Container name in Azure
            "account_name": "mystorageaccount",
        },
        "notes": [
            "Container names must be lowercase, 3-63 characters",
            "Get account key from Azure Portal > Storage Account > Access Keys",
            "Consider using SAS tokens for more granular access control",
        ],
    },
}


def validate_bucket_name(bucket: str) -> tuple[bool, Optional[str]]:
    """Validate bucket name according to common rules."""
    if len(bucket) < 3 or len(bucket) > 63:
        return False, "Bucket name must be between 3 and 63 characters"
    
    if not re.match(r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$", bucket):
        return False, "Bucket name must start and end with lowercase letter or number"
    
    if ".." in bucket or ".-" in bucket or "-." in bucket:
        return False, "Bucket name cannot contain .., .-, or -."
    
    return True, None


def validate_region(region: str) -> tuple[bool, Optional[str]]:
    """Validate AWS-style region format."""
    if not re.match(r"^[a-z]{2}-[a-z]+-\d+$", region):
        return False, "Region should be in format like us-east-1, eu-west-2"
    return True, None


def prompt_for_provider() -> str:
    """Prompt user to select a storage provider."""
    console.print("\n[bold]Available Storage Providers:[/bold]")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Provider", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Description")
    
    table.add_row("s3", "Amazon S3", "AWS Simple Storage Service")
    table.add_row("r2", "Cloudflare R2", "S3-compatible with no egress fees")
    table.add_row("b2", "Backblaze B2", "Cost-effective S3-compatible storage")
    table.add_row("gcs", "Google Cloud Storage", "Google's object storage service")
    table.add_row("azure", "Azure Blob Storage", "Microsoft Azure storage service")
    
    console.print(table)
    
    while True:
        provider = Prompt.ask(
            "\nSelect storage provider",
            choices=["s3", "r2", "b2", "gcs", "azure"],
        )
        
        if provider in PROVIDER_GUIDES:
            return provider
        
        console.print("[red]Invalid provider. Please choose from the list above.[/red]")


def prompt_for_bucket(provider: str) -> str:
    """Prompt for bucket name with validation."""
    guide = PROVIDER_GUIDES[provider]
    
    if "bucket" in guide["examples"]:
        console.print(f"\n[dim]Example: {guide['examples']['bucket']}[/dim]")
    
    while True:
        bucket = Prompt.ask("Bucket name").lower()
        
        valid, error = validate_bucket_name(bucket)
        if valid:
            return bucket
        
        console.print(f"[red]Error:[/red] {error}")


def prompt_for_region(provider: str, required: bool = False) -> Optional[str]:
    """Prompt for region if applicable."""
    if provider not in ["s3", "r2"]:
        return None
    
    default = "us-east-1" if provider == "s3" else None
    
    if not required and provider == "r2":
        # R2 doesn't require region
        return None
    
    while True:
        if default:
            region = Prompt.ask("Region", default=default)
        else:
            region = Prompt.ask("Region (press Enter to skip)", default="")
        
        if not region and not required:
            return None
        
        if region:
            if provider == "s3":
                valid, error = validate_region(region)
                if not valid:
                    console.print(f"[red]Error:[/red] {error}")
                    continue
            
            return region


def prompt_for_credentials(provider: str) -> Dict[str, Any]:
    """Prompt for provider-specific credentials."""
    guide = PROVIDER_GUIDES[provider]
    credentials = {}
    
    console.print(f"\n[bold]Configure {guide['name']} Credentials[/bold]")
    
    # Show provider-specific notes
    if guide["notes"]:
        console.print("\n[dim]Notes:[/dim]")
        for note in guide["notes"]:
            console.print(f"  • {note}")
    
    console.print(f"\n[dim]Documentation: {guide['docs']}[/dim]")
    
    # Collect required credentials
    for cred in guide["credentials"]:
        if cred == "service_account_key_path":
            while True:
                path = Prompt.ask("\nPath to service account JSON key file")
                path = Path(path).expanduser()
                if path.exists() and path.is_file():
                    credentials[cred] = str(path)
                    break
                console.print("[red]Error:[/red] File not found")
        else:
            # Use password prompt for sensitive fields
            if "key" in cred or "secret" in cred or "password" in cred:
                value = Prompt.ask(f"\n{cred.replace('_', ' ').title()}", password=True)
            else:
                value = Prompt.ask(f"\n{cred.replace('_', ' ').title()}")
            credentials[cred] = value
    
    # Collect optional credentials
    for opt in guide.get("optional", []):
        if opt == "endpoint_url" and provider in ["r2", "b2"]:
            if opt in guide["examples"]:
                console.print(f"\n[dim]Example: {guide['examples'][opt]}[/dim]")
            
            value = Prompt.ask(f"\n{opt.replace('_', ' ').title()} (optional)", default="")
            if value:
                credentials[opt] = value
        elif opt == "project_id" and provider == "gcs":
            value = Prompt.ask("\nGCP Project ID (optional)", default="")
            if value:
                credentials[opt] = value
    
    return credentials


def test_storage_connection(
    provider: str,
    bucket: str,
    credentials: Dict[str, Any],
    region: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    """Test the storage connection with provided credentials."""
    try:
        # Import here to avoid circular imports
        from gira.storage import get_storage_backend
        
        # Create a test backend
        backend = get_storage_backend(
            provider=provider,
            bucket=bucket,
            region=region,
            **credentials
        )
        
        # Test connection
        success = backend.test_connection()
        return success, None if success else "Connection test failed"
        
    except Exception as e:
        return False, str(e)


def configure(
    provider: Optional[str] = typer.Option(
        None,
        "--provider", "-p",
        help="Storage provider (s3, r2, b2, gcs, azure)",
    ),
    bucket: Optional[str] = typer.Option(
        None,
        "--bucket", "-b",
        help="Storage bucket name",
    ),
    test: bool = typer.Option(
        True,
        "--test/--no-test",
        help="Test connection after configuration",
    ),
    update_project: bool = typer.Option(
        True,
        "--update-project/--no-update-project",
        help="Update project configuration",
    ),
    encrypt: bool = typer.Option(
        False,
        "--encrypt/--no-encrypt",
        help="Encrypt stored credentials",
    ),
) -> None:
    """Configure storage backend for attachments.
    
    This command helps you set up a storage provider for binary attachments.
    It will guide you through:
    
    1. Selecting a storage provider (S3, R2, B2, GCS, Azure)
    2. Configuring bucket and region settings
    3. Setting up authentication credentials
    4. Testing the connection
    5. Saving credentials securely
    
    Credentials are stored in ~/.config/gira/storage.yml with restricted permissions.
    """
    # Ensure we're in a Gira project
    root = ensure_gira_project()
    
    console.print(Panel.fit(
        "[bold]Storage Configuration Wizard[/bold]\n\n"
        "This wizard will help you configure external storage for attachments.",
        border_style="cyan"
    ))
    
    # Interactive prompts if not provided
    if not provider:
        provider = prompt_for_provider()
    else:
        # Validate provider
        if provider not in PROVIDER_GUIDES:
            console.print(f"[red]Error:[/red] Invalid provider '{provider}'")
            raise typer.Exit(1)
    
    guide = PROVIDER_GUIDES[provider]
    console.print(f"\n[bold]Configuring {guide['name']}[/bold]")
    
    # Get bucket name
    if not bucket:
        bucket = prompt_for_bucket(provider)
    else:
        # Validate bucket
        valid, error = validate_bucket_name(bucket)
        if not valid:
            console.print(f"[red]Error:[/red] {error}")
            raise typer.Exit(1)
    
    # Get region if applicable
    region = None
    if provider in ["s3", "r2"]:
        region = prompt_for_region(provider, required=(provider == "s3"))
    
    # Get credentials
    console.print("\n[yellow]Note:[/yellow] Credentials will be stored securely in ~/.config/gira/")
    credentials = prompt_for_credentials(provider)
    
    # Test connection if requested
    if test:
        console.print("\n[cyan]Testing connection...[/cyan]")
        success, error = test_storage_connection(provider, bucket, credentials, region)
        
        if not success:
            console.print(f"[red]Connection test failed:[/red] {error}")
            if not Confirm.ask("\nDo you want to save the configuration anyway?"):
                raise typer.Exit(1)
        else:
            console.print("[green]✓ Connection test successful![/green]")
    
    # Save credentials
    console.print("\n[cyan]Saving credentials...[/cyan]")
    
    try:
        # Initialize credentials manager
        encryption_key = None
        if encrypt:
            # Ask for encryption key
            console.print("\n[yellow]Note:[/yellow] You'll need this key to decrypt credentials later.")
            encryption_key = Prompt.ask("Enter encryption key", password=True)
            confirm_key = Prompt.ask("Confirm encryption key", password=True)
            if encryption_key != confirm_key:
                console.print("[red]Error:[/red] Encryption keys don't match")
                raise typer.Exit(1)
        
        # Convert provider string to enum
        provider_enum = StorageProvider(provider)
        
        # Use CredentialsManager to save
        manager = CredentialsManager(encryption_key)
        
        # Save credentials along with bucket info
        all_credentials = credentials.copy()
        all_credentials["bucket"] = bucket
        if region:
            all_credentials["region"] = region
        
        credential_path = manager.save_credentials(
            provider=provider_enum,
            credentials=all_credentials,
            encrypt=encrypt
        )
        console.print(f"[green]✓ Credentials saved {'(encrypted) ' if encrypt else ''}to {credential_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving credentials:[/red] {e}")
        raise typer.Exit(1)
    
    # Update project configuration if requested
    if update_project:
        console.print("\n[cyan]Updating project configuration...[/cyan]")
        
        # Load current config
        config = load_config(root)
        
        # Update storage settings
        config["storage.enabled"] = True
        config["storage.provider"] = provider
        config["storage.bucket"] = bucket
        if region:
            config["storage.region"] = region
        config["storage.credential_source"] = "file"
        
        # Save config
        save_config(root, config)
        console.print("[green]✓ Project configuration updated[/green]")
    
    # Success message
    console.print("\n[green]✓ Storage configuration complete![/green]")
    console.print("\nYou can now use attachments with your tickets and epics.")
    console.print("\nNext steps:")
    console.print("  • Attach files: [cyan]gira attach add <ticket-id> <file>[/cyan]")
    console.print("  • List attachments: [cyan]gira attach list <ticket-id>[/cyan]")
    console.print("  • Download attachments: [cyan]gira attach get <ticket-id> <file>[/cyan]")


