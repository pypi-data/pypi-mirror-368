"""Add webhook endpoint command."""

import typer
from typing import List, Optional
from rich.table import Table

from gira.utils.config import load_config, save_config
from gira.utils.console import console
from gira.utils.project import ensure_gira_project


def add(
    name: str = typer.Argument(..., help="Name for the webhook endpoint"),
    url: str = typer.Argument(..., help="Webhook URL to send events to"),
    events: Optional[str] = typer.Option(
        "ticket_created,ticket_updated,ticket_moved", 
        "--events", "-e",
        help="Comma-separated list of events to send (or '*' for all)"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t",
        help="Template to apply for formatting (slack, discord, etc.)"
    ),
    filter_query: Optional[str] = typer.Option(
        None, "--filter", "-f",
        help="Filter events using Gira query language"
    ),
    auth_type: Optional[str] = typer.Option(
        None, "--auth-type",
        help="Authentication type (bearer, api_key, basic)"
    ),
    auth_token: Optional[str] = typer.Option(
        None, "--auth-token",
        help="Authentication token (use ${ENV_VAR} for environment variables)"
    ),
    auth_key: Optional[str] = typer.Option(
        None, "--auth-key",
        help="Authentication header key (for api_key auth)"
    ),
    auth_username: Optional[str] = typer.Option(
        None, "--auth-username",
        help="Username for basic auth (use ${ENV_VAR} for environment variables)"
    ),
    auth_password: Optional[str] = typer.Option(
        None, "--auth-password",
        help="Password for basic auth (use ${ENV_VAR} for environment variables)"
    ),
    timeout: Optional[int] = typer.Option(
        None, "--timeout",
        help="Request timeout in seconds (default: global setting)"
    ),
    retry_attempts: Optional[int] = typer.Option(
        None, "--retry-attempts",
        help="Number of retry attempts (default: global setting)"
    ),
    headers: Optional[str] = typer.Option(
        None, "--headers",
        help="Additional headers as JSON string"
    ),
    enabled: bool = typer.Option(
        True, "--enabled/--disabled",
        help="Whether the webhook is enabled"
    )
):
    """Add a new webhook endpoint.
    
    Examples:
        gira webhook add slack "https://hooks.slack.com/services/..." --template slack
        
        gira webhook add jira "https://company.atlassian.net/webhooks" \\
            --auth-type bearer --auth-token "${JIRA_TOKEN}" \\
            --filter "priority:high OR type:bug"
            
        gira webhook add custom "https://api.example.com/webhook" \\
            --events "ticket_created,ticket_moved" \\
            --headers '{"X-Custom-Header": "value"}'
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
        endpoints = webhooks_config.get("endpoints", [])
        
        # Check if webhook with this name already exists
        for endpoint in endpoints:
            if endpoint.get("name") == name:
                console.print(f"[red]Error:[/red] Webhook '{name}' already exists")
                console.print("Use 'gira webhook remove' to remove it first")
                raise typer.Exit(1)
        
        # Parse events
        event_list = []
        if events:
            if events.strip() == "*":
                event_list = ["*"]
            else:
                event_list = [event.strip() for event in events.split(",")]
        
        # Build endpoint configuration
        endpoint_config = {
            "name": name,
            "url": url,
            "enabled": enabled,
            "events": event_list
        }
        
        # Add optional configurations
        if template:
            endpoint_config["template"] = template
        
        if filter_query:
            endpoint_config["filter"] = filter_query
        
        if timeout is not None:
            endpoint_config["timeout"] = timeout
        
        if retry_attempts is not None:
            endpoint_config["retry_attempts"] = retry_attempts
        
        # Handle authentication
        if auth_type:
            auth_config = {"type": auth_type.lower()}
            
            if auth_type.lower() == "bearer" and auth_token:
                auth_config["token"] = auth_token
            elif auth_type.lower() == "api_key" and auth_token and auth_key:
                auth_config["key"] = auth_key
                auth_config["value"] = auth_token
            elif auth_type.lower() == "basic" and auth_username and auth_password:
                auth_config["username"] = auth_username
                auth_config["password"] = auth_password
            else:
                console.print(f"[red]Error:[/red] Invalid authentication configuration for type '{auth_type}'")
                console.print("Required parameters:")
                console.print("  - bearer: --auth-token")
                console.print("  - api_key: --auth-key and --auth-token")
                console.print("  - basic: --auth-username and --auth-password")
                raise typer.Exit(1)
            
            endpoint_config["auth"] = auth_config
        
        # Handle custom headers
        if headers:
            import json
            try:
                headers_dict = json.loads(headers)
                endpoint_config["headers"] = headers_dict
            except json.JSONDecodeError:
                console.print(f"[red]Error:[/red] Invalid JSON in headers: {headers}")
                raise typer.Exit(1)
        
        # Add the new endpoint
        endpoints.append(endpoint_config)
        webhooks_config["endpoints"] = endpoints
        
        # Save configuration
        save_config(config)
        
        console.print(f"[green]✓[/green] Webhook '{name}' added successfully")
        
        # Display the configuration
        table = Table(title="Webhook Configuration")
        table.add_column("Property", style="cyan")
        table.add_column("Value")
        
        table.add_row("Name", name)
        table.add_row("URL", url)
        table.add_row("Events", ", ".join(event_list))
        table.add_row("Enabled", "✅ Yes" if enabled else "❌ No")
        
        if template:
            table.add_row("Template", template)
        if filter_query:
            table.add_row("Filter", filter_query)
        if auth_type:
            table.add_row("Authentication", auth_type)
        if timeout is not None:
            table.add_row("Timeout", f"{timeout}s")
        if retry_attempts is not None:
            table.add_row("Retry Attempts", str(retry_attempts))
        
        console.print("\n")
        console.print(table)
        
        console.print(f"\n[dim]Test your webhook with:[/dim]")
        console.print(f"  gira webhook test {name}")
        
    except Exception as e:
        console.print(f"[red]Error adding webhook:[/red] {e}")
        raise typer.Exit(1)