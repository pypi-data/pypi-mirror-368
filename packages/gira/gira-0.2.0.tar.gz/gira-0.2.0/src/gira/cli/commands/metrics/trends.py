"""Ticket trends metrics command implementation."""

import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from collections import defaultdict

import typer
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

from gira.utils.project import ensure_gira_project
from gira.models.ticket import Ticket
from gira.utils.console import console
from gira.utils.output import OutputFormat, print_output, add_color_option, add_no_color_option, get_color_kwargs


app = typer.Typer()


def collect_ticket_metrics(tickets: List[Ticket], days: int = 30) -> Dict[str, Any]:
    """Collect ticket metrics over the specified time period."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Initialize daily counters
    daily_metrics = defaultdict(lambda: {
        "created": 0,
        "completed": 0,
        "total_open": 0,
        "backlog_size": 0,
    })
    
    # Track cumulative open tickets
    open_tickets_by_date = defaultdict(set)
    
    for ticket in tickets:
        # Track creation
        if ticket.created_at:
            created_date = ticket.created_at.date()
            if start_date <= created_date <= end_date:
                daily_metrics[created_date]["created"] += 1
            
            # Add to open tickets from creation date onwards
            current = created_date
            while current <= end_date:
                if current >= start_date:
                    open_tickets_by_date[current].add(ticket.id)
                current += timedelta(days=1)
        
        # Track completion
        if ticket.status == "done" and ticket.updated_at:
            # Try to find when it was moved to done
            completed_date = ticket.updated_at.date()
            if start_date <= completed_date <= end_date:
                daily_metrics[completed_date]["completed"] += 1
            
            # Remove from open tickets after completion
            current = completed_date + timedelta(days=1)
            while current <= end_date:
                if current >= start_date:
                    open_tickets_by_date[current].discard(ticket.id)
                current += timedelta(days=1)
    
    # Calculate daily open counts
    for day in daily_metrics:
        daily_metrics[day]["total_open"] = len(open_tickets_by_date[day])
        # Backlog is open tickets excluding in-progress
        daily_metrics[day]["backlog_size"] = sum(
            1 for tid in open_tickets_by_date[day]
            if any(t.id == tid and t.status in ["todo", "backlog"] 
                   for t in tickets)
        )
    
    # Aggregate weekly metrics
    weekly_metrics = defaultdict(lambda: {
        "created": 0,
        "completed": 0,
        "avg_open": 0,
        "avg_backlog": 0,
    })
    
    for day in sorted(daily_metrics.keys()):
        week_start = day - timedelta(days=day.weekday())
        weekly_metrics[week_start]["created"] += daily_metrics[day]["created"]
        weekly_metrics[week_start]["completed"] += daily_metrics[day]["completed"]
        weekly_metrics[week_start]["avg_open"] += daily_metrics[day]["total_open"]
        weekly_metrics[week_start]["avg_backlog"] += daily_metrics[day]["backlog_size"]
    
    # Calculate weekly averages
    for week in weekly_metrics:
        weekly_metrics[week]["avg_open"] //= 7
        weekly_metrics[week]["avg_backlog"] //= 7
    
    return {
        "daily": dict(daily_metrics),
        "weekly": dict(weekly_metrics),
        "summary": {
            "total_created": sum(m["created"] for m in daily_metrics.values()),
            "total_completed": sum(m["completed"] for m in daily_metrics.values()),
            "current_open": len(open_tickets_by_date[end_date]),
            "current_backlog": daily_metrics[end_date]["backlog_size"],
            "avg_created_per_week": sum(m["created"] for m in weekly_metrics.values()) / max(len(weekly_metrics), 1),
            "avg_completed_per_week": sum(m["completed"] for m in weekly_metrics.values()) / max(len(weekly_metrics), 1),
        }
    }


def create_ascii_chart(data: List[int], max_height: int = 10, width: int = 40) -> List[str]:
    """Create a simple ASCII bar chart."""
    if not data:
        return []
    
    max_val = max(data) if data else 1
    if max_val == 0:
        max_val = 1
    
    # Scale data to fit height
    scaled = [int(v * max_height / max_val) for v in data]
    
    # Build chart from top to bottom
    lines = []
    for h in range(max_height, -1, -1):
        line = ""
        for val in scaled:
            if val >= h:
                line += "█"
            else:
                line += " "
        lines.append(line)
    
    return lines


def display_trends_chart(metrics: Dict[str, Any], console):
    """Display trends as ASCII charts."""
    console.print("\n[bold]Ticket Trends Analysis[/bold]")
    console.print("=" * 60)
    
    # Get weekly data sorted by date
    weekly_data = sorted(metrics["weekly"].items())
    if not weekly_data:
        console.print("[yellow]No data available for the specified period.[/yellow]")
        return
    
    # Extract data for charts
    weeks = [w[0] for w in weekly_data]
    created = [w[1]["created"] for w in weekly_data]
    completed = [w[1]["completed"] for w in weekly_data]
    backlog = [w[1]["avg_backlog"] for w in weekly_data]
    
    # Create charts
    created_chart = create_ascii_chart(created, max_height=8, width=len(weeks))
    completed_chart = create_ascii_chart(completed, max_height=8, width=len(weeks))
    backlog_chart = create_ascii_chart(backlog, max_height=8, width=len(weeks))
    
    # Display created vs completed
    console.print("\n[cyan]Weekly Ticket Flow[/cyan] (Created vs Completed)")
    console.print("─" * 50)
    
    # Overlay charts
    max_height = max(len(created_chart), len(completed_chart))
    for i in range(max_height - 1):
        line = ""
        for j in range(len(weeks)):
            if i < len(created_chart) and j < len(created_chart[i]):
                if created_chart[i][j] == "█":
                    line += "[green]█[/green]"
                elif i < len(completed_chart) and j < len(completed_chart[i]) and completed_chart[i][j] == "█":
                    line += "[blue]◆[/blue]"
                else:
                    line += " "
            else:
                line += " "
        console.print(line)
    
    # X-axis labels
    console.print("─" * len(weeks))
    week_labels = ""
    for i, week in enumerate(weeks):
        if i % 2 == 0:  # Show every other week to avoid crowding
            week_labels += week.strftime("%m/%d")[:5].ljust(6)
        else:
            week_labels += "      "
    console.print(week_labels[:len(weeks)])
    
    console.print("\n[green]█[/green] Created   [blue]◆[/blue] Completed")
    
    # Display backlog trend
    console.print("\n[cyan]Backlog Size Trend[/cyan]")
    console.print("─" * 50)
    
    for line in backlog_chart[:-1]:
        console.print("[yellow]" + line + "[/yellow]")
    
    console.print("─" * len(weeks))
    console.print(week_labels[:len(weeks)])
    
    # Summary statistics
    summary = metrics["summary"]
    console.print("\n[bold]Summary Statistics[/bold]")
    console.print("─" * 50)
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Total tickets created", f"{summary['total_created']}")
    table.add_row("Total tickets completed", f"{summary['total_completed']}")
    table.add_row("Current open tickets", f"{summary['current_open']}")
    table.add_row("Current backlog size", f"{summary['current_backlog']}")
    table.add_row("Avg created per week", f"{summary['avg_created_per_week']:.1f}")
    table.add_row("Avg completed per week", f"{summary['avg_completed_per_week']:.1f}")
    
    completion_rate = (summary['total_completed'] / summary['total_created'] * 100) if summary['total_created'] > 0 else 0
    table.add_row("Completion rate", f"{completion_rate:.1f}%")
    
    console.print(table)


def filter_tickets(
    tickets: List[Ticket],
    ticket_type: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    epic: Optional[str] = None,
) -> List[Ticket]:
    """Filter tickets based on specified criteria."""
    filtered = tickets
    
    if ticket_type:
        filtered = [t for t in filtered if t.type == ticket_type]
    
    if priority:
        filtered = [t for t in filtered if t.priority == priority]
    
    if assignee:
        filtered = [t for t in filtered if t.assignee == assignee]
    
    if epic:
        filtered = [t for t in filtered if t.epic_id == epic]
    
    return filtered


@app.command()
def trends(
    ctx: typer.Context,
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    format: str = typer.Option("human", "--format", "-f", help="Output format: human, json, csv"),
    ticket_type: Optional[str] = typer.Option(None, "--type", help="Filter by ticket type"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Filter by priority"),
    assignee: Optional[str] = typer.Option(None, "--assignee", help="Filter by assignee"),
    epic: Optional[str] = typer.Option(None, "--epic", help="Filter by epic ID"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
):
    """Display ticket creation, completion, and backlog trends over time."""
    try:
        # Ensure we're in a Gira project
        gira_root = ensure_gira_project()
        
        # Load all tickets including archived ones
        from gira.utils.ticket_utils import load_all_tickets
        tickets = load_all_tickets(gira_root, include_archived=True)
        
        # Apply filters
        filtered_tickets = filter_tickets(tickets, ticket_type, priority, assignee, epic)
        
        if not filtered_tickets:
            console.print("[yellow]No tickets found matching the specified criteria.[/yellow]")
            return
        
        # Collect metrics
        metrics = collect_ticket_metrics(filtered_tickets, days)
        
        # Output based on format
        if format == "json":
            # Convert date keys to strings for JSON serialization
            json_metrics = {
                "daily": {
                    str(k): v for k, v in metrics["daily"].items()
                },
                "weekly": {
                    str(k): v for k, v in metrics["weekly"].items()
                },
                "summary": metrics["summary"],
                "filters": {
                    "days": days,
                    "type": ticket_type,
                    "priority": priority,
                    "assignee": assignee,
                    "epic": epic,
                }
            }
            color_kwargs = get_color_kwargs(color, no_color)
            print_output(json_metrics, OutputFormat.JSON, **color_kwargs)
        
        elif format == "csv":
            # CSV header
            print("date,created,completed,open_tickets,backlog_size")
            for date_key in sorted(metrics["daily"].keys()):
                data = metrics["daily"][date_key]
                print(f"{date_key},{data['created']},{data['completed']},"
                      f"{data['total_open']},{data['backlog_size']}")
        
        else:  # human format
            # Display filter info if any filters applied
            if any([ticket_type, priority, assignee, epic]):
                filter_parts = []
                if ticket_type:
                    filter_parts.append(f"type={ticket_type}")
                if priority:
                    filter_parts.append(f"priority={priority}")
                if assignee:
                    filter_parts.append(f"assignee={assignee}")
                if epic:
                    filter_parts.append(f"epic={epic}")
                
                console.print(f"\n[dim]Filters: {', '.join(filter_parts)}[/dim]")
            
            display_trends_chart(metrics, console)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)