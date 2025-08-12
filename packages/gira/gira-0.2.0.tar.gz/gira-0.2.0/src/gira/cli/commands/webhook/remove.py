"""Remove webhook endpoint command."""

import typer
from gira.utils.config import load_config, save_config
from gira.utils.console import console
from gira.utils.project import ensure_gira_project


def remove(
    name: str = typer.Argument(..., help="Name of the webhook endpoint to remove"),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip confirmation prompt"
    )
):
    """Remove a webhook endpoint.
    
    Examples:
        gira webhook remove slack
        gira webhook remove jira --force
    """
    ensure_gira_project()
    
    try:
        config = load_config()
        
        # Check if webhooks configuration exists
        webhooks_config = config.get("extensibility", {}).get("webhooks", {})
        endpoints = webhooks_config.get("endpoints", [])
        
        # Find the webhook to remove
        webhook_to_remove = None
        for endpoint in endpoints:
            if endpoint.get("name") == name:
                webhook_to_remove = endpoint
                break
        
        if not webhook_to_remove:
            console.print(f"[red]Error:[/red] Webhook '{name}' not found")
            console.print("\nUse 'gira webhook list' to see available webhooks")
            raise typer.Exit(1)
        
        # Show webhook details
        console.print(f"[yellow]Webhook to remove:[/yellow]")
        console.print(f"  Name: {webhook_to_remove['name']}")
        console.print(f"  URL: {webhook_to_remove['url']}")
        console.print(f"  Events: {', '.join(webhook_to_remove.get('events', []))}")
        console.print(f"  Enabled: {'Yes' if webhook_to_remove.get('enabled', True) else 'No'}")
        
        # Confirm removal unless forced
        if not force:
            if not typer.confirm(f"\nAre you sure you want to remove webhook '{name}'?"):
                console.print("Removal cancelled")
                raise typer.Exit(0)
        
        # Remove the webhook
        updated_endpoints = [ep for ep in endpoints if ep.get("name") != name]
        webhooks_config["endpoints"] = updated_endpoints
        
        # Update configuration
        if "extensibility" not in config:
            config["extensibility"] = {}
        config["extensibility"]["webhooks"] = webhooks_config
        
        # Save configuration
        save_config(config)
        
        console.print(f"[green]✓[/green] Webhook '{name}' removed successfully")
        
        remaining_count = len(updated_endpoints)
        if remaining_count > 0:
            console.print(f"\n{remaining_count} webhook(s) remaining")
        else:
            console.print("\nNo webhooks configured")
            console.print("[dim]Add a new webhook with 'gira webhook add'[/dim]")
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error removing webhook:[/red] {e}")
        raise typer.Exit(1)