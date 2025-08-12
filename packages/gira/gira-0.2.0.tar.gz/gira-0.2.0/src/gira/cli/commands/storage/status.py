"""Storage status command for checking configuration and credentials."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.panel import Panel
from rich.table import Table

from gira.models.attachment import StorageProvider
from gira.utils.config_utils import load_config
from gira.utils.credentials import CredentialsManager
from gira.utils.project import ensure_gira_project

def status() -> None:
    """Check storage configuration and credential status.
    
    This command shows:
    - Current storage configuration in the project
    - Available credentials for each provider
    - Validation status of credentials
    """
    # Ensure we're in a Gira project
    root = ensure_gira_project()
    
    # Load project configuration
    config = load_config(root)
    
    # Check if storage is enabled
    storage_enabled = config.get("storage.enabled", False)
    storage_provider = config.get("storage.provider", None)
    storage_bucket = config.get("storage.bucket", None)
    
    # Display project configuration
    console.print(Panel.fit(
        "[bold]Storage Configuration Status[/bold]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Project Configuration:[/bold]")
    console.print(f"  Storage enabled: {'[green]Yes[/green]' if storage_enabled else '[red]No[/red]'}")
    if storage_enabled and storage_provider:
        console.print(f"  Provider: [cyan]{storage_provider}[/cyan]")
        console.print(f"  Bucket: [cyan]{storage_bucket or 'Not configured'}[/cyan]")
    else:
        console.print("  Provider: [dim]Not configured[/dim]")
    
    # Check credentials for all providers
    console.print("\n[bold]Credential Availability:[/bold]")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Provider", style="cyan")
    table.add_column("Available", style="white")
    table.add_column("Source", style="white")
    table.add_column("Status", style="white")
    
    manager = CredentialsManager()
    
    for provider in StorageProvider:
        try:
            available, source = manager.check_availability(provider)
            
            if available:
                # Try to validate the credentials
                if source == "env":
                    creds = manager._load_from_environment(provider)
                else:
                    creds = manager._load_from_file(provider)
                
                valid, error = manager.validate_credentials(provider, creds)
                
                if valid:
                    status = "[green]✓ Valid[/green]"
                else:
                    status = f"[yellow]⚠ Invalid: {error}[/yellow]"
                
                table.add_row(
                    provider.value,
                    "[green]Yes[/green]",
                    source or "-",
                    status
                )
            else:
                table.add_row(
                    provider.value,
                    "[red]No[/red]",
                    "-",
                    "[dim]No credentials[/dim]"
                )
        except Exception as e:
            table.add_row(
                provider.value,
                "[red]Error[/red]",
                "-",
                f"[red]{str(e)}[/red]"
            )
    
    console.print(table)
    
    # Show help for missing credentials
    if not storage_enabled:
        console.print("\n[yellow]Tip:[/yellow] Run 'gira storage configure' to set up storage.")
    elif storage_provider:
        provider_enum = StorageProvider(storage_provider)
        available, _ = manager.check_availability(provider_enum)
        if not available:
            console.print(f"\n[yellow]Warning:[/yellow] No credentials found for {storage_provider}.")
            console.print("Run 'gira storage configure' to set up credentials.")
            
            # Show required credentials
            required = manager.get_required_credentials(provider_enum)
            if required:
                console.print(f"\nRequired credentials for {storage_provider}:")
                for cred in required:
                    console.print(f"  • {cred}")


def validate(
    provider: Optional[str] = typer.Option(
        None,
        "--provider", "-p",
        help="Storage provider to validate (s3, r2, b2, gcs, azure)",
    ),
    show_help: bool = typer.Option(
        False,
        "--help-credentials",
        help="Show credential help for providers",
    ),
) -> None:
    """Validate storage credentials and show detailed information.
    
    This command validates credentials and shows what's required for each provider.
    """
    manager = CredentialsManager()
    
    if show_help:
        # Show help for all providers or specific one
        if provider:
            try:
                provider_enum = StorageProvider(provider)
                console.print(manager.get_credential_help(provider_enum))
            except ValueError:
                console.print(f"[red]Error:[/red] Invalid provider '{provider}'")
                raise typer.Exit(1)
        else:
            # Show help for all providers
            for prov in StorageProvider:
                console.print(f"\n[bold cyan]{prov.value.upper()}[/bold cyan]")
                console.print(manager.get_credential_help(prov))
                console.print()
        return
    
    # Validate specific provider or current configuration
    if provider:
        try:
            provider_enum = StorageProvider(provider)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid provider '{provider}'")
            raise typer.Exit(1)
        
        # Check if credentials exist
        available, source = manager.check_availability(provider_enum)
        if not available:
            console.print(f"[red]No credentials found for {provider}[/red]")
            console.print("\nRequired credentials:")
            for cred in manager.get_required_credentials(provider_enum):
                console.print(f"  • {cred}")
            raise typer.Exit(1)
        
        # Load and validate
        try:
            creds = manager.load_credentials(provider_enum)
            valid, error = manager.validate_credentials(provider_enum, creds)
            
            if valid:
                console.print(f"[green]✓ Credentials for {provider} are valid![/green]")
                console.print(f"  Source: {source}")
                
                # Show non-sensitive credential info
                console.print("\nConfigured credentials:")
                for key in creds:
                    if "secret" not in key.lower() and "key" not in key.lower():
                        console.print(f"  • {key}: {creds[key]}")
                    else:
                        console.print(f"  • {key}: [dim]***[/dim]")
            else:
                console.print(f"[red]✗ Invalid credentials for {provider}[/red]")
                console.print(f"  Error: {error}")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]Error validating credentials:[/red] {e}")
            raise typer.Exit(1)
    else:
        # Validate current project configuration
        root = ensure_gira_project()
        config = load_config(root)
        
        storage_provider = config.get("storage.provider")
        if not storage_provider:
            console.print("[yellow]No storage provider configured in project[/yellow]")
            console.print("Run 'gira storage configure' to set up storage.")
            raise typer.Exit(1)
        
        # Recursively call with the configured provider
        validate(provider=storage_provider, show_help=False)