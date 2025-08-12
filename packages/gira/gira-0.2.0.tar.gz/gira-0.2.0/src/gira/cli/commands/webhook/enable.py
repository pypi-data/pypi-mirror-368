"""Enable/disable webhook commands."""

import typer
from typing import Optional

from gira.utils.config import load_config, save_config
from gira.utils.console import console
from gira.utils.project import ensure_gira_project


def enable(
    name: Optional[str] = typer.Argument(
        None, help="Name of specific webhook to enable (omit to enable globally)"
    )
):
    """Enable webhooks globally or a specific webhook endpoint.
    
    If no name is provided, enables the webhook system globally.
    If a name is provided, enables that specific webhook endpoint.
    
    Examples:
        gira webhook enable              # Enable webhook system globally
        gira webhook enable slack        # Enable specific webhook
    """
    ensure_gira_project()
    
    try:
        config = load_config()
        
        # Initialize webhook configuration if it doesn't exist
        if "extensibility" not in config:
            config["extensibility"] = {}
        if "webhooks" not in config["extensibility"]:
            config["extensibility"]["webhooks"] = {
                "enabled": True,
                "timeout": 30,
                "retry_attempts": 3,
                "endpoints": []
            }
        
        webhooks_config = config["extensibility"]["webhooks"]
        
        if name is None:
            # Enable globally
            webhooks_config["enabled"] = True
            save_config(config)
            
            console.print("[green]✅ Webhooks enabled globally[/green]")
            
            endpoints = webhooks_config.get("endpoints", [])
            active_endpoints = [ep for ep in endpoints if ep.get("enabled", True)]
            
            if active_endpoints:
                console.print(f"[dim]{len(active_endpoints)} webhook endpoint(s) will now receive events[/dim]")
            else:
                console.print("[dim]No webhook endpoints configured yet[/dim]")
                console.print("Add a webhook with: [dim]gira webhook add <name> <url>[/dim]")
        
        else:
            # Enable specific webhook
            endpoints = webhooks_config.get("endpoints", [])
            webhook_found = False
            
            for endpoint in endpoints:
                if endpoint.get("name") == name:
                    endpoint["enabled"] = True
                    webhook_found = True
                    break
            
            if not webhook_found:
                console.print(f"[red]Error:[/red] Webhook '{name}' not found")
                console.print("\nUse 'gira webhook list' to see available webhooks")
                raise typer.Exit(1)
            
            save_config(config)
            
            console.print(f"[green]✅ Webhook '{name}' enabled[/green]")
            
            # Check if webhooks are globally enabled
            if not webhooks_config.get("enabled", True):
                console.print("[yellow]⚠️  Note: Webhook system is disabled globally[/yellow]")
                console.print("Enable globally with: [dim]gira webhook enable[/dim]")
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error enabling webhook:[/red] {e}")
        raise typer.Exit(1)


def disable(
    name: Optional[str] = typer.Argument(
        None, help="Name of specific webhook to disable (omit to disable globally)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip confirmation prompt for global disable"
    )
):
    """Disable webhooks globally or a specific webhook endpoint.
    
    If no name is provided, disables the webhook system globally.
    If a name is provided, disables that specific webhook endpoint.
    
    Examples:
        gira webhook disable             # Disable webhook system globally
        gira webhook disable slack       # Disable specific webhook
        gira webhook disable --force     # Disable globally without confirmation
    """
    ensure_gira_project()
    
    try:
        config = load_config()
        
        # Get webhook configuration
        webhooks_config = config.get("extensibility", {}).get("webhooks", {})
        
        if name is None:
            # Disable globally
            endpoints = webhooks_config.get("endpoints", [])
            active_endpoints = [ep for ep in endpoints if ep.get("enabled", True)]
            
            if active_endpoints and not force:
                console.print("[yellow]Warning:[/yellow] This will disable all webhook delivery")
                console.print(f"Affected endpoints: {', '.join(ep.get('name', 'unnamed') for ep in active_endpoints)}")
                
                if not typer.confirm("Are you sure you want to disable webhooks globally?"):
                    console.print("Operation cancelled")
                    raise typer.Exit(0)
            
            # Initialize webhooks config if needed
            if "extensibility" not in config:
                config["extensibility"] = {}
            if "webhooks" not in config["extensibility"]:
                config["extensibility"]["webhooks"] = {"enabled": False, "endpoints": []}
            else:
                config["extensibility"]["webhooks"]["enabled"] = False
            
            save_config(config)
            
            console.print("[yellow]❌ Webhooks disabled globally[/yellow]")
            if active_endpoints:
                console.print(f"[dim]{len(active_endpoints)} endpoint(s) will no longer receive events[/dim]")
            
            console.print("Re-enable with: [dim]gira webhook enable[/dim]")
        
        else:
            # Disable specific webhook
            endpoints = webhooks_config.get("endpoints", [])
            webhook_found = False
            
            for endpoint in endpoints:
                if endpoint.get("name") == name:
                    endpoint["enabled"] = False
                    webhook_found = True
                    break
            
            if not webhook_found:
                console.print(f"[red]Error:[/red] Webhook '{name}' not found")
                console.print("\nUse 'gira webhook list' to see available webhooks")
                raise typer.Exit(1)
            
            save_config(config)
            
            console.print(f"[yellow]❌ Webhook '{name}' disabled[/yellow]")
            console.print(f"Re-enable with: [dim]gira webhook enable {name}[/dim]")
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error disabling webhook:[/red] {e}")
        raise typer.Exit(1)