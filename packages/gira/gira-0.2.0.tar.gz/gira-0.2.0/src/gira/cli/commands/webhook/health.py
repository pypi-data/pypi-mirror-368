"""Webhook health check and monitoring commands."""

import typer
from typing import Optional
from rich.table import Table
from rich.panel import Panel

from gira.utils.config import load_config
from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.webhooks import get_webhook_client


def health(
    name: Optional[str] = typer.Argument(
        None, help="Name of webhook to check (omit to check all)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show detailed health information"
    )
):
    """Check webhook endpoint health and connectivity.
    
    Performs health checks on webhook endpoints to verify they are
    reachable and responding correctly.
    
    Examples:
        gira webhook health              # Check all webhooks
        gira webhook health slack        # Check specific webhook
        gira webhook health --verbose    # Detailed health info
    """
    ensure_gira_project()
    
    try:
        config = load_config()
        webhooks_config = config.get("extensibility", {}).get("webhooks", {})
        endpoints = webhooks_config.get("endpoints", [])
        
        if not endpoints:
            console.print("[yellow]No webhook endpoints configured[/yellow]")
            console.print("Add a webhook with: [dim]gira webhook add <name> <url>[/dim]")
            return
        
        client = get_webhook_client()
        
        if name:
            # Check specific webhook
            endpoint_found = False
            for endpoint in endpoints:
                if endpoint.get("name") == name:
                    endpoint_found = True
                    break
            
            if not endpoint_found:
                console.print(f"[red]Error:[/red] Webhook '{name}' not found")
                console.print("\nUse 'gira webhook list' to see available webhooks")
                raise typer.Exit(1)
            
            console.print(f"[cyan]Checking webhook health:[/cyan] {name}")
            is_healthy, health_info = client.check_endpoint_health(name)
            
            _display_health_info(health_info, is_healthy, verbose)
        
        else:
            # Check all webhooks
            console.print(f"[cyan]Checking health of {len(endpoints)} webhook endpoint(s)...[/cyan]\n")
            
            if verbose:
                # Detailed view for each webhook
                for i, endpoint in enumerate(endpoints):
                    endpoint_name = endpoint.get("name", "Unnamed")
                    
                    if i > 0:
                        console.print()
                    
                    console.print(f"[bold]{endpoint_name}[/bold]")
                    is_healthy, health_info = client.check_endpoint_health(endpoint_name)
                    _display_health_info(health_info, is_healthy, verbose)
            
            else:
                # Summary table
                table = Table(title="Webhook Health Status")
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Status", width=10)
                table.add_column("Response Time", width=13)
                table.add_column("URL", style="blue", overflow="ellipsis", max_width=40)
                table.add_column("Error", style="red", overflow="ellipsis", max_width=30)
                
                healthy_count = 0
                for endpoint in endpoints:
                    endpoint_name = endpoint.get("name", "Unnamed")
                    is_healthy, health_info = client.check_endpoint_health(endpoint_name)
                    
                    if is_healthy:
                        healthy_count += 1
                        status = "🟢 Healthy"
                    else:
                        status = "🔴 Unhealthy"
                    
                    response_time = health_info.get("response_time")
                    response_time_str = f"{response_time}ms" if response_time else "N/A"
                    
                    error = health_info.get("error", "")
                    
                    table.add_row(
                        endpoint_name,
                        status,
                        response_time_str,
                        health_info.get("url", ""),
                        error
                    )
                
                console.print(table)
                console.print(f"\n[dim]Health Summary: {healthy_count}/{len(endpoints)} endpoints healthy[/dim]")
        
        # Show delivery statistics if available
        if verbose:
            stats = client.get_delivery_stats(name)
            if stats:
                console.print("\n[bold]Delivery Statistics:[/bold]")
                _display_delivery_stats(stats, name)
    
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error checking webhook health:[/red] {e}")
        raise typer.Exit(1)


def stats(
    name: Optional[str] = typer.Argument(
        None, help="Name of webhook to show stats for (omit to show all)"
    )
):
    """Show webhook delivery statistics.
    
    Displays delivery success rates, failure counts, and recent activity
    for webhook endpoints.
    
    Examples:
        gira webhook stats           # Show stats for all webhooks
        gira webhook stats slack     # Show stats for specific webhook
    """
    ensure_gira_project()
    
    try:
        client = get_webhook_client()
        stats = client.get_delivery_stats(name)
        
        if not stats:
            if name:
                console.print(f"[yellow]No delivery statistics found for webhook '{name}'[/yellow]")
            else:
                console.print("[yellow]No delivery statistics available[/yellow]")
            
            console.print("[dim]Statistics are collected after webhook deliveries[/dim]")
            return
        
        if name:
            # Show detailed stats for specific webhook
            console.print(f"[cyan]Delivery Statistics:[/cyan] {name}")
            _display_delivery_stats({name: stats}, name)
        
        else:
            # Show summary for all webhooks
            console.print("[cyan]Webhook Delivery Statistics[/cyan]\n")
            _display_delivery_stats(stats)
    
    except Exception as e:
        console.print(f"[red]Error retrieving webhook statistics:[/red] {e}")
        raise typer.Exit(1)


def _display_health_info(health_info: dict, is_healthy: bool, verbose: bool = False):
    """Display health information for a webhook endpoint."""
    if verbose:
        # Detailed panel display
        status = "🟢 Healthy" if is_healthy else "🔴 Unhealthy"
        content = []
        
        content.append(f"[bold]Status:[/bold] {status}")
        content.append(f"[bold]URL:[/bold] {health_info.get('url', 'N/A')}")
        content.append(f"[bold]Enabled:[/bold] {'Yes' if health_info.get('enabled', True) else 'No'}")
        content.append(f"[bold]Reachable:[/bold] {'Yes' if health_info.get('reachable', False) else 'No'}")
        
        if health_info.get('response_time'):
            content.append(f"[bold]Response Time:[/bold] {health_info['response_time']}ms")
        
        if health_info.get('status_code'):
            content.append(f"[bold]HTTP Status:[/bold] {health_info['status_code']}")
        
        if health_info.get('error'):
            content.append(f"[bold]Error:[/bold] [red]{health_info['error']}[/red]")
        
        panel_content = "\n".join(content)
        console.print(Panel(panel_content, expand=False))
    
    else:
        # Simple status display
        status = "🟢 Healthy" if is_healthy else "🔴 Unhealthy"
        console.print(f"  Status: {status}")
        
        if health_info.get('error'):
            console.print(f"  Error: [red]{health_info['error']}[/red]")


def _display_delivery_stats(stats: dict, specific_endpoint: Optional[str] = None):
    """Display delivery statistics for webhooks."""
    if specific_endpoint and specific_endpoint in stats:
        # Show detailed stats for one endpoint
        endpoint_stats = stats[specific_endpoint]
        
        total = endpoint_stats.get('total_attempts', 0)
        success = endpoint_stats.get('successful_deliveries', 0)
        failed = endpoint_stats.get('failed_deliveries', 0)
        
        if total > 0:
            success_rate = (success / total) * 100
            console.print(f"  Total Attempts: {total}")
            console.print(f"  Successful: {success}")
            console.print(f"  Failed: {failed}")
            console.print(f"  Success Rate: {success_rate:.1f}%")
            
            if endpoint_stats.get('last_success'):
                console.print(f"  Last Success: {endpoint_stats['last_success']}")
            
            if endpoint_stats.get('last_failure'):
                console.print(f"  Last Failure: {endpoint_stats['last_failure']}")
                if endpoint_stats.get('last_error'):
                    console.print(f"  Last Error: {endpoint_stats['last_error']}")
        else:
            console.print("  No delivery attempts recorded")
    
    else:
        # Show summary table for all endpoints
        table = Table(title="Delivery Statistics")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Total", width=8)
        table.add_column("Success", width=8)
        table.add_column("Failed", width=8)
        table.add_column("Success Rate", width=12)
        table.add_column("Last Activity", width=20)
        
        for endpoint_name, endpoint_stats in stats.items():
            total = endpoint_stats.get('total_attempts', 0)
            success = endpoint_stats.get('successful_deliveries', 0)
            failed = endpoint_stats.get('failed_deliveries', 0)
            
            if total > 0:
                success_rate = f"{(success / total) * 100:.1f}%"
            else:
                success_rate = "N/A"
            
            # Get most recent activity
            last_success = endpoint_stats.get('last_success')
            last_failure = endpoint_stats.get('last_failure')
            
            if last_success and last_failure:
                last_activity = max(last_success, last_failure)[:16]  # Truncate timestamp
            elif last_success:
                last_activity = last_success[:16]
            elif last_failure:
                last_activity = last_failure[:16]
            else:
                last_activity = "None"
            
            table.add_row(
                endpoint_name,
                str(total),
                str(success),
                str(failed),
                success_rate,
                last_activity
            )
        
        console.print(table)