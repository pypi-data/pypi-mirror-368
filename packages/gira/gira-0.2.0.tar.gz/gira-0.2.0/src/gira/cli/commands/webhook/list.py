"""List webhook endpoints command."""

import typer
from rich.table import Table
from rich.panel import Panel

from gira.utils.config import load_config
from gira.utils.console import console
from gira.utils.project import ensure_gira_project


def list_webhooks(
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show detailed information about each webhook"
    )
):
    """List configured webhook endpoints.
    
    Shows all webhook endpoints with their status, events, and configuration.
    
    Examples:
        gira webhook list
        gira webhook list --verbose
    """
    ensure_gira_project()
    
    try:
        config = load_config()
        
        # Get webhook configuration
        webhooks_config = config.get("extensibility", {}).get("webhooks", {})
        endpoints = webhooks_config.get("endpoints", [])
        global_enabled = webhooks_config.get("enabled", True)
        global_timeout = webhooks_config.get("timeout", 30)
        global_retry_attempts = webhooks_config.get("retry_attempts", 3)
        
        # Show global webhook status
        status_icon = "🟢" if global_enabled else "🔴"
        status_text = "Enabled" if global_enabled else "Disabled"
        
        console.print(f"\n[bold]Webhook System Status:[/bold] {status_icon} {status_text}")
        if global_enabled:
            console.print(f"[bold]Global Timeout:[/bold] {global_timeout} seconds")
            console.print(f"[bold]Global Retry Attempts:[/bold] {global_retry_attempts}")
        console.print()
        
        if not endpoints:
            console.print("[yellow]No webhook endpoints configured[/yellow]")
            console.print("Add a webhook with: [dim]gira webhook add <name> <url>[/dim]")
            console.print("\nExample integrations:")
            console.print("  • Slack: [dim]gira webhook add slack <webhook-url> --template slack[/dim]")
            console.print("  • Discord: [dim]gira webhook add discord <webhook-url> --template discord[/dim]")
            console.print("  • Custom API: [dim]gira webhook add api <url> --auth-type bearer --auth-token ${TOKEN}[/dim]")
            return
        
        if verbose:
            # Show detailed information for each webhook
            for i, endpoint in enumerate(endpoints):
                if i > 0:
                    console.print()
                
                name = endpoint.get("name", "Unnamed")
                url = endpoint.get("url", "")
                enabled = endpoint.get("enabled", True)
                events = endpoint.get("events", [])
                template = endpoint.get("template")
                filter_query = endpoint.get("filter")
                auth = endpoint.get("auth", {})
                timeout = endpoint.get("timeout")
                retry_attempts = endpoint.get("retry_attempts")
                headers = endpoint.get("headers", {})
                
                # Create detailed panel for each webhook
                status_icon = "✅" if enabled else "❌"
                title = f"{status_icon} {name}"
                
                content = []
                content.append(f"[bold]URL:[/bold] {url}")
                content.append(f"[bold]Events:[/bold] {', '.join(events)}")
                
                if template:
                    content.append(f"[bold]Template:[/bold] {template}")
                
                if filter_query:
                    content.append(f"[bold]Filter:[/bold] {filter_query}")
                
                if auth:
                    auth_type = auth.get("type", "none")
                    content.append(f"[bold]Authentication:[/bold] {auth_type}")
                
                if timeout is not None:
                    content.append(f"[bold]Timeout:[/bold] {timeout}s")
                else:
                    content.append(f"[bold]Timeout:[/bold] {global_timeout}s (global)")
                
                if retry_attempts is not None:
                    content.append(f"[bold]Retry Attempts:[/bold] {retry_attempts}")
                else:
                    content.append(f"[bold]Retry Attempts:[/bold] {global_retry_attempts} (global)")
                
                if headers:
                    header_list = [f"{k}: {v}" for k, v in headers.items()]
                    content.append(f"[bold]Custom Headers:[/bold] {', '.join(header_list)}")
                
                panel_content = "\n".join(content)
                panel = Panel(panel_content, title=title, expand=False)
                console.print(panel)
        
        else:
            # Show summary table
            table = Table(title="Webhook Endpoints")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Status", width=8)
            table.add_column("Events", style="dim")
            table.add_column("Template", width=10)
            table.add_column("URL", style="blue", overflow="ellipsis", max_width=40)
            
            for endpoint in endpoints:
                name = endpoint.get("name", "Unnamed")
                enabled = endpoint.get("enabled", True)
                events = endpoint.get("events", [])
                template = endpoint.get("template", "")
                url = endpoint.get("url", "")
                
                status_icon = "✅ Yes" if enabled else "❌ No"
                events_str = ", ".join(events) if len(", ".join(events)) <= 30 else ", ".join(events)[:27] + "..."
                
                table.add_row(
                    name,
                    status_icon,
                    events_str,
                    template,
                    url
                )
            
            console.print(table)
        
        # Show summary
        active_count = sum(1 for ep in endpoints if ep.get("enabled", True))
        total_count = len(endpoints)
        
        console.print(f"\n[dim]Total: {total_count} webhook(s), {active_count} active[/dim]")
        
        if not global_enabled:
            console.print("\n[yellow]⚠️  Webhook system is disabled globally[/yellow]")
            console.print("Enable with: [dim]gira webhook enable[/dim]")
        
        console.print(f"\n[dim]Test a webhook with:[/dim] gira webhook test <name>")
        
    except Exception as e:
        console.print(f"[red]Error listing webhooks:[/red] {e}")
        raise typer.Exit(1)