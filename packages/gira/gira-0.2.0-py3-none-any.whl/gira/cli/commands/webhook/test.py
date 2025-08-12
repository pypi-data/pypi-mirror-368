"""Test webhook endpoint command."""

import typer
from typing import Optional

from gira.utils.config import load_config
from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.webhooks import get_webhook_client


def test(
    name: str = typer.Argument(..., help="Name of the webhook endpoint to test"),
    event_type: Optional[str] = typer.Option(
        "test", "--event", "-e",
        help="Event type for the test payload (default: test)"
    )
):
    """Test a webhook endpoint with a sample payload.
    
    Sends a test payload to the specified webhook endpoint to verify
    connectivity and configuration.
    
    Examples:
        gira webhook test slack
        gira webhook test jira --event ticket_created
    """
    ensure_gira_project()
    
    try:
        config = load_config()
        
        # Check if webhooks are enabled
        webhooks_config = config.get("extensibility", {}).get("webhooks", {})
        if not webhooks_config.get("enabled", True):
            console.print("[yellow]⚠️  Webhook system is disabled globally[/yellow]")
            console.print("Enable with: [dim]gira webhook enable[/dim]")
            raise typer.Exit(1)
        
        endpoints = webhooks_config.get("endpoints", [])
        
        # Find the webhook to test
        webhook_to_test = None
        for endpoint in endpoints:
            if endpoint.get("name") == name:
                webhook_to_test = endpoint
                break
        
        if not webhook_to_test:
            console.print(f"[red]Error:[/red] Webhook '{name}' not found")
            console.print("\nUse 'gira webhook list' to see available webhooks")
            raise typer.Exit(1)
        
        if not webhook_to_test.get("enabled", True):
            console.print(f"[yellow]⚠️  Webhook '{name}' is disabled[/yellow]")
            if not typer.confirm("Test anyway?"):
                raise typer.Exit(0)
        
        # Show webhook details
        console.print(f"[cyan]Testing webhook:[/cyan] {name}")
        console.print(f"[dim]URL:[/dim] {webhook_to_test['url']}")
        console.print(f"[dim]Event Type:[/dim] {event_type}")
        
        # Test the webhook
        console.print(f"\n[dim]Sending test payload...[/dim]")
        
        client = get_webhook_client()
        success, error = client.test_endpoint(name, event_type)
        
        if success:
            console.print(f"[green]✓[/green] Webhook test successful!")
            console.print(f"[dim]The endpoint '{name}' is responding correctly[/dim]")
        else:
            console.print(f"[red]✗[/red] Webhook test failed")
            if error:
                console.print(f"[red]Error:[/red] {error}")
            
            console.print(f"\n[dim]Troubleshooting tips:[/dim]")
            console.print("• Check that the webhook URL is correct and accessible")
            console.print("• Verify authentication credentials (if used)")
            console.print("• Ensure the endpoint accepts POST requests with JSON payload")
            console.print("• Check firewall/network connectivity")
            
            if webhook_to_test.get("auth"):
                auth_type = webhook_to_test["auth"].get("type")
                console.print(f"• Verify {auth_type} authentication is configured correctly")
                if "${" in str(webhook_to_test["auth"]):
                    console.print("• Check that environment variables are set and accessible")
            
            raise typer.Exit(1)
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error testing webhook:[/red] {e}")
        raise typer.Exit(1)