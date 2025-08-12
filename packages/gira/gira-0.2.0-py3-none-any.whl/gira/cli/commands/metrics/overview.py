"""Metrics overview command - provides comprehensive project health summary."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
import statistics

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich import box

from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets
from gira.models.ticket import Ticket, TicketStatus
from gira.models.sprint import Sprint
# Sprint utilities will be imported or implemented inline
from gira.utils.console import console
from gira.cli.commands.metrics.duration import calculate_status_durations_with_fallback
from gira.utils.output import OutputFormat, print_output, add_color_option, add_no_color_option, get_color_kwargs


def get_active_sprint(gira_root: Path) -> Optional[Sprint]:
    """Get the currently active sprint from the project state."""
    state_file = gira_root / ".gira" / ".state.json"
    if not state_file.exists():
        return None
    
    import json
    with open(state_file) as f:
        state = json.load(f)
    
    active_sprint_id = state.get("active_sprint")
    if not active_sprint_id:
        return None
    
    # Load the sprint
    sprint_file = gira_root / ".gira" / "sprints" / f"{active_sprint_id}.json"
    if not sprint_file.exists():
        return None
    
    return Sprint.from_json_file(str(sprint_file))


def calculate_sprint_velocity(tickets: List[Ticket]) -> int:
    """Calculate velocity (total story points) for a list of tickets."""
    return sum(t.story_points or 0 for t in tickets if t.story_points is not None)


def calculate_ticket_flow(tickets: List[Ticket], days: int = 30) -> Dict[str, Any]:
    """Calculate ticket creation and completion flow over the specified period."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    created_tickets = []
    completed_tickets = []
    
    for ticket in tickets:
        # Ensure timezone awareness
        created_at = ticket.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        updated_at = ticket.updated_at
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        
        # Count created tickets
        if created_at >= cutoff_date:
            created_tickets.append(ticket)
        
        # Count completed tickets
        if ticket.status == "done" and updated_at >= cutoff_date:
            completed_tickets.append(ticket)
    
    return {
        "created": len(created_tickets),
        "completed": len(completed_tickets),
        "net_change": len(created_tickets) - len(completed_tickets),
        "created_tickets": created_tickets,
        "completed_tickets": completed_tickets
    }


def calculate_status_distribution(tickets: List[Ticket]) -> Dict[str, Any]:
    """Calculate the distribution of tickets across different statuses."""
    status_counts = defaultdict(int)
    
    # Count tickets by status
    for ticket in tickets:
        status_counts[ticket.status] += 1
    
    total = len(tickets)
    
    # Calculate percentages
    distribution = {}
    for status, count in status_counts.items():
        percentage = (count / total * 100) if total > 0 else 0
        distribution[status] = {
            "count": count,
            "percentage": percentage
        }
    
    return {
        "total": total,
        "distribution": distribution
    }


def identify_bottlenecks(metrics: Dict[str, Any], max_bottlenecks: int = 3) -> List[Dict[str, Any]]:
    """Identify the top bottlenecks based on status duration metrics."""
    bottlenecks = []
    
    if "status_durations" not in metrics:
        return bottlenecks
    
    # Extract status transitions and their durations
    status_flow = metrics.get("status_flow", {})
    status_durations = metrics.get("status_durations", {})
    
    # Calculate average time for each transition
    transition_times = []
    
    for from_status, transitions in status_flow.items():
        if from_status in status_durations:
            avg_duration = status_durations[from_status].get("mean", 0)
            
            # Find the most common transition from this status
            if transitions:
                most_common_to = max(transitions.items(), key=lambda x: x[1])
                to_status = most_common_to[0]
                count = most_common_to[1]
                
                transition_times.append({
                    "from": from_status,
                    "to": to_status,
                    "avg_duration": avg_duration,
                    "count": count
                })
    
    # Sort by average duration and get top bottlenecks
    transition_times.sort(key=lambda x: x["avg_duration"], reverse=True)
    
    return transition_times[:max_bottlenecks]


def format_duration_short(hours: float) -> str:
    """Format duration in a short, readable format."""
    if hours < 24:
        return f"{hours:.1f}h"
    else:
        days = hours / 24
        return f"{days:.1f}d"


def create_sprint_summary_panel(sprint: Optional[Sprint], tickets: List[Ticket]) -> Panel:
    """Create a panel showing sprint summary information."""
    if not sprint:
        content = Align.center(
            Text("🚫 No Active Sprint", style="dim italic")
        )
    else:
        # Calculate sprint progress
        sprint_tickets = [t for t in tickets if t.sprint_id == sprint.id]
        completed = len([t for t in sprint_tickets if t.status == "done"])
        total = len(sprint_tickets)
        
        # Calculate velocity
        velocity = calculate_sprint_velocity(sprint_tickets)
        
        # Calculate days remaining
        end_date = sprint.end_date
        days_remaining = (end_date - datetime.now(timezone.utc).date()).days
        
        # Create progress bar
        progress_pct = (completed / total * 100) if total > 0 else 0
        bar_length = 20
        filled = int(bar_length * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Status colors
        velocity_color = "bright_green" if velocity > 20 else "yellow" if velocity > 0 else "red"
        days_color = "red" if days_remaining < 3 else "yellow" if days_remaining < 7 else "green"
        progress_color = "bright_green" if progress_pct > 75 else "yellow" if progress_pct > 50 else "red"
        
        # Build content with better formatting
        lines = [
            f"🎯 [bold bright_cyan]{sprint.name}[/bold bright_cyan]",
            f"📅 [dim]{sprint.start_date} → {end_date}[/dim]",
            "",
            f"⚡ Velocity: [{velocity_color}]{velocity}[/{velocity_color}] [dim]story points[/dim]",
            f"📊 Progress: [{progress_color}]{completed}[/{progress_color}]/[bright_white]{total}[/bright_white] [dim]tickets[/dim] ([{progress_color}]{progress_pct:.1f}%[/{progress_color}])",
            f"[{progress_color}]{bar}[/{progress_color}]",
            "",
            f"⏰ Days remaining: [{days_color}]{days_remaining}[/{days_color}]"
        ]
        
        content = "\n".join(lines)
    
    return Panel(
        content, 
        title="🏃 Current Sprint", 
        title_align="left",
        border_style="bright_cyan",
        box=box.ROUNDED
    )


def create_ticket_flow_panel(flow_data: Dict[str, Any]) -> Panel:
    """Create a panel showing ticket flow information."""
    created = flow_data["created"]
    completed = flow_data["completed"]
    net_change = flow_data["net_change"]
    
    # Determine colors and icons based on flow
    if net_change > 5:
        net_color = "red"
        net_icon = "📈"
        flow_status = "Growing backlog"
    elif net_change < 0:
        net_color = "bright_green"
        net_icon = "📉"
        flow_status = "Reducing backlog"
    else:
        net_color = "yellow"
        net_icon = "➖"
        flow_status = "Stable"
    
    # Create visual flow indicator
    if created > 0 and completed > 0:
        flow_ratio = completed / created
        flow_bar_length = 15
        completed_bar = int(flow_bar_length * min(flow_ratio, 1.0))
        created_bar = flow_bar_length - completed_bar
        flow_viz = f"[bright_green]{'█' * completed_bar}[/bright_green][red]{'█' * created_bar}[/red]"
    else:
        flow_viz = "[dim]No data[/dim]"
    
    lines = [
        f"📥 Created: [bright_yellow]{created}[/bright_yellow] [dim]tickets[/dim]",
        f"✅ Completed: [bright_green]{completed}[/bright_green] [dim]tickets[/dim]",
        f"{net_icon} Net flow: [{net_color}]{'+' if net_change > 0 else ''}{net_change}[/{net_color}] [dim]({flow_status})[/dim]",
        "",
        f"[dim]Completion ratio:[/dim] {flow_viz}"
    ]
    
    content = "\n".join(lines)
    
    return Panel(
        content, 
        title="📊 Ticket Flow (Last 30 days)", 
        title_align="left",
        border_style="bright_blue",
        box=box.ROUNDED
    )


def create_status_distribution_table(distribution_data: Dict[str, Any]) -> Table:
    """Create a table showing status distribution."""
    table = Table(
        title="📋 Status Distribution", 
        title_style="bold bright_magenta",
        show_header=True, 
        header_style="bold bright_white",
        border_style="bright_magenta",
        box=box.ROUNDED
    )
    
    table.add_column("Status", style="bright_white", width=15)
    table.add_column("Count", justify="right", style="bright_white", width=8)
    table.add_column("Percentage", justify="right", width=12)
    table.add_column("Visual", width=20)
    
    # Define status order with icons and colors
    status_config = {
        "backlog": {"icon": "📦", "color": "bright_blue", "name": "Backlog"},
        "todo": {"icon": "📋", "color": "cyan", "name": "Todo"},
        "in_progress": {"icon": "🔄", "color": "bright_yellow", "name": "In Progress"},
        "review": {"icon": "👀", "color": "magenta", "name": "Review"},
        "done": {"icon": "✅", "color": "bright_green", "name": "Done"},
        "archived": {"icon": "📁", "color": "dim", "name": "Archived"}
    }
    
    distribution = distribution_data["distribution"]
    total = distribution_data["total"]
    
    for status, config in status_config.items():
        if status in distribution:
            data = distribution[status]
            count = data["count"]
            percentage = data["percentage"]
            
            # Create visual bar
            bar_length = 15
            filled = int(bar_length * percentage / 100)
            bar = f"[{config['color']}]{'█' * filled}[/{config['color']}]{'░' * (bar_length - filled)}"
            
            table.add_row(
                f"{config['icon']} {config['name']}",
                f"[bright_white]{count}[/bright_white]",
                f"[{config['color']}]{percentage:.1f}%[/{config['color']}]",
                bar
            )
    
    # Add total row
    table.add_section()
    table.add_row(
        "[bold]📊 Total[/bold]",
        f"[bold bright_white]{total}[/bold bright_white]",
        "[bold]100.0%[/bold]",
        "[dim]━━━━━━━━━━━━━━━[/dim]"
    )
    
    return table


def create_bottlenecks_panel(bottlenecks: List[Dict[str, Any]]) -> Panel:
    """Create a panel showing top bottlenecks."""
    if not bottlenecks:
        content = Align.center(
            Text("🎉 No bottlenecks identified!", style="bright_green italic")
        )
    else:
        lines = []
        for i, bottleneck in enumerate(bottlenecks):
            from_status = bottleneck["from"].replace("_", " ").title()
            to_status = bottleneck["to"].replace("_", " ").title()
            duration = format_duration_short(bottleneck["avg_duration"])
            count = bottleneck["count"]
            
            # Icons and colors based on severity
            if bottleneck["avg_duration"] > 48:  # More than 2 days
                icon = "🚨"
                duration_style = "bright_red"
                severity = "Critical"
            elif bottleneck["avg_duration"] > 24:  # More than 1 day
                icon = "⚠️"
                duration_style = "bright_yellow"
                severity = "Warning"
            else:
                icon = "ℹ️"
                duration_style = "bright_green"
                severity = "Minor"
            
            # Rank indicator
            rank_colors = ["bright_red", "bright_yellow", "cyan"]
            rank_color = rank_colors[min(i, len(rank_colors) - 1)]
            
            lines.append(
                f"[{rank_color}]#{i+1}[/{rank_color}] {icon} "
                f"[bright_white]{from_status}[/bright_white] → [bright_white]{to_status}[/bright_white]"
            )
            lines.append(
                f"    [{duration_style}]avg {duration}[/{duration_style}] "
                f"[dim]({count} transitions)[/dim]"
            )
            if i < len(bottlenecks) - 1:
                lines.append("")
    
        content = "\n".join(lines)
    
    return Panel(
        content, 
        title="🐌 Performance Bottlenecks", 
        title_align="left",
        border_style="bright_red",
        box=box.ROUNDED
    )


def display_human_overview(
    sprint: Optional[Sprint],
    tickets: List[Ticket],
    flow_data: Dict[str, Any],
    distribution_data: Dict[str, Any],
    bottlenecks: List[Dict[str, Any]]
):
    """Display the metrics overview in human-readable format."""
    # Header with project info
    console.print()
    header_text = Text("📊 Gira Project Metrics Dashboard", style="bold bright_magenta")
    console.print(Align.center(header_text))
    
    # Stylish separator
    console.print(Rule(
        "📈 Real-time insights for your development workflow 📈", 
        style="bright_magenta"
    ))
    console.print()
    
    # Create panels and tables
    sprint_panel = create_sprint_summary_panel(sprint, tickets)
    flow_panel = create_ticket_flow_panel(flow_data)
    distribution_table = create_status_distribution_table(distribution_data)
    bottlenecks_panel = create_bottlenecks_panel(bottlenecks)
    
    # Top row: Sprint and Flow panels side by side
    console.print(Columns([sprint_panel, flow_panel], equal=True, expand=True))
    console.print()
    
    # Middle: Status distribution table (centered)
    console.print(Align.center(distribution_table))
    console.print()
    
    # Bottom: Bottlenecks panel
    console.print(bottlenecks_panel)
    
    # Enhanced insights section
    insights = create_insights_panel(sprint, tickets, flow_data, bottlenecks)
    console.print()
    console.print(insights)
    console.print()


def create_insights_panel(
    sprint: Optional[Sprint],
    tickets: List[Ticket], 
    flow_data: Dict[str, Any],
    bottlenecks: List[Dict[str, Any]]
) -> Panel:
    """Create a panel with actionable insights and recommendations."""
    insights = []
    
    # Sprint health insights
    if sprint:
        sprint_tickets = [t for t in tickets if t.sprint_id == sprint.id]
        if sprint_tickets:
            completion_rate = len([t for t in sprint_tickets if t.status == "done"]) / len(sprint_tickets) * 100
            if completion_rate < 30:
                insights.append("🚨 [bright_red]Sprint at risk![/bright_red] Only {:.0f}% complete - urgent action needed".format(completion_rate))
            elif completion_rate < 50:
                insights.append("⚠️ [bright_yellow]Sprint behind schedule[/bright_yellow] ({:.0f}% complete) - consider scope adjustment".format(completion_rate))
            elif completion_rate > 80:
                insights.append("🎉 [bright_green]Sprint on track for success![/bright_green] {:.0f}% complete".format(completion_rate))
            elif completion_rate > 60:
                insights.append("👍 [green]Sprint progressing well[/green] ({:.0f}% complete)".format(completion_rate))
    else:
        insights.append("💡 [cyan]Consider starting a sprint to track team velocity and progress[/cyan]")
    
    # Flow health insights
    net_change = flow_data["net_change"]
    created = flow_data["created"]
    completed = flow_data["completed"]
    
    if net_change > 15:
        insights.append("📈 [bright_red]Backlog growing rapidly![/bright_red] Created {}, completed {} (+{} net)".format(created, completed, net_change))
    elif net_change > 5:
        insights.append("📊 [bright_yellow]Backlog growing[/bright_yellow] - consider increasing team capacity")
    elif net_change < -5:
        insights.append("📉 [bright_green]Excellent backlog reduction![/bright_green] Keep up the momentum")
    elif created == 0 and completed == 0:
        insights.append("😴 [dim]Low activity period[/dim] - no tickets created or completed")
    else:
        insights.append("⚖️ [green]Balanced ticket flow[/green] - sustainable pace")
    
    # Bottleneck insights
    if bottlenecks:
        worst_bottleneck = bottlenecks[0]
        duration_hours = worst_bottleneck["avg_duration"]
        
        if duration_hours > 168:  # 1 week
            insights.append("🐌 [bright_red]Critical workflow bottleneck![/bright_red] {:.1f} days average in {}".format(
                duration_hours/24, worst_bottleneck["from"]))
        elif duration_hours > 72:  # 3 days
            insights.append("⏰ [bright_yellow]Significant delay[/bright_yellow] in {} workflow ({:.1f} days average)".format(
                worst_bottleneck["from"], duration_hours/24))
        elif len(bottlenecks) >= 3:
            insights.append("🔍 [cyan]Multiple workflow stages need attention[/cyan] - review process efficiency")
    else:
        insights.append("🚀 [bright_green]Smooth workflow![/bright_green] No significant bottlenecks detected")
    
    # Performance recommendations
    if not insights:
        insights.append("✅ [bright_green]All systems running smoothly![/bright_green]")
    
    content = "\n".join(f"  {insight}" for insight in insights)
    
    return Panel(
        content,
        title="💡 AI Insights & Recommendations",
        title_align="left",
        border_style="bright_green",
        box=box.ROUNDED
    )


def overview(
    format: str = typer.Option("human", "--format", "-f", help="Output format: human, json"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze for trends"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
):
    """Display comprehensive metrics overview for the project."""
    try:
        # Ensure we're in a Gira project
        gira_root = ensure_gira_project()
        
        # Load all tickets
        tickets = load_all_tickets(gira_root, include_archived=False)
        
        if not tickets:
            console.print("[yellow]No tickets found in the project[/yellow]")
            return
        
        # Get active sprint
        sprint = get_active_sprint(gira_root)
        
        # Calculate ticket flow
        flow_data = calculate_ticket_flow(tickets, days)
        
        # Calculate status distribution
        distribution_data = calculate_status_distribution(tickets)
        
        # Calculate duration metrics for bottleneck analysis
        with console.status("[dim]Analyzing ticket metrics...[/dim]"):
            duration_metrics = calculate_status_durations_with_fallback(
                tickets, gira_root, no_cache=False
            )
        
        # Identify bottlenecks
        bottlenecks = identify_bottlenecks(duration_metrics)
        
        # Prepare data for output
        overview_data = {
            "sprint": {
                "name": sprint.name if sprint else None,
                "start_date": sprint.start_date.isoformat() if sprint else None,
                "end_date": sprint.end_date.isoformat() if sprint else None,
                "velocity": calculate_sprint_velocity([t for t in tickets if sprint and t.sprint_id == sprint.id]) if sprint else 0,
                "progress": {
                    "completed": len([t for t in tickets if sprint and t.sprint_id == sprint.id and t.status == "done"]) if sprint else 0,
                    "total": len([t for t in tickets if sprint and t.sprint_id == sprint.id]) if sprint else 0
                }
            } if sprint else None,
            "ticket_flow": {
                "created": flow_data["created"],
                "completed": flow_data["completed"],
                "net_change": flow_data["net_change"]
            },
            "status_distribution": distribution_data["distribution"],
            "bottlenecks": [
                {
                    "from": b["from"],
                    "to": b["to"],
                    "avg_duration_hours": b["avg_duration"],
                    "count": b["count"]
                }
                for b in bottlenecks
            ],
            "analysis_period_days": days,
            "total_tickets": len(tickets)
        }
        
        # Format output
        if format == "human":
            display_human_overview(sprint, tickets, flow_data, distribution_data, bottlenecks)
        else:
            # Use print_output for JSON formatting
            color_kwargs = get_color_kwargs(color, no_color)
            print_output(overview_data, OutputFormat.JSON, **color_kwargs)
    
    except Exception as e:
        console.print(f"[red]Error generating metrics overview: {e}[/red]")
        raise typer.Exit(1)