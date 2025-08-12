"""Velocity metrics command implementation."""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any

import typer
from rich.table import Table

from gira.utils.project import ensure_gira_project
from gira.models.sprint import Sprint
from gira.models.ticket import Ticket
from gira.utils.console import console
from gira.utils.output import OutputFormat, print_output, add_color_option, add_no_color_option, get_color_kwargs

app = typer.Typer()


def calculate_sprint_velocity(sprint: Sprint, tickets: List[Ticket], verbose: bool = False) -> Dict[str, Any]:
    """Calculate velocity metrics for a sprint."""
    # Filter tickets that belong to this sprint using BOTH tracking methods:
    # 1. Tickets listed in sprint.tickets[] array
    # 2. Tickets with sprint_id matching this sprint
    sprint_ticket_ids = set(sprint.tickets or [])
    
    # Also include tickets that have this sprint's ID set in their sprint_id field
    tickets_by_sprint_id = [t.id for t in tickets if t.sprint_id == sprint.id]
    sprint_ticket_ids.update(tickets_by_sprint_id)
    
    # Get the actual ticket objects
    sprint_tickets = [
        t for t in tickets 
        if t.id in sprint_ticket_ids
    ]
    
    # Data integrity check: warn if sprint tracking is inconsistent
    sprint_list_tickets = set(sprint.tickets or [])
    sprint_id_tickets = set(tickets_by_sprint_id)
    
    if verbose and sprint_list_tickets != sprint_id_tickets:
        # Log inconsistency for debugging (only visible in verbose mode)
        missing_from_list = sprint_id_tickets - sprint_list_tickets
        missing_from_tickets = sprint_list_tickets - sprint_id_tickets
        
        if missing_from_list:
            console.print(f"[yellow]Warning:[/yellow] Sprint {sprint.id} is missing tickets in sprint.tickets array: {', '.join(missing_from_list)}", style="dim")
        if missing_from_tickets:
            console.print(f"[yellow]Warning:[/yellow] Sprint {sprint.id} has tickets in sprint.tickets array but not in ticket.sprint_id: {', '.join(missing_from_tickets)}", style="dim")
    
    # Filter completed tickets in this sprint
    completed_in_sprint = [
        t for t in sprint_tickets
        if t.status == "done" and t.story_points is not None
    ]
    
    total_points = sum(t.story_points or 0 for t in sprint_tickets)
    completed_points = sum(t.story_points or 0 for t in completed_in_sprint)
    completion_rate = (completed_points / total_points * 100) if total_points > 0 else 0
    
    return {
        "sprint_id": sprint.id,
        "sprint_name": sprint.name,
        "total_points": total_points,
        "completed_points": completed_points,
        "completion_rate": completion_rate,
        "ticket_count": len(sprint_tickets),
        "completed_count": len(completed_in_sprint),
        "start_date": sprint.start_date.isoformat() if sprint.start_date else None,
        "end_date": sprint.end_date.isoformat() if sprint.end_date else None,
        "status": sprint.status,
    }


def display_velocity_chart(velocities: List[Dict[str, Any]], console):
    """Display velocity data as an ASCII chart."""
    console.print("\n[bold]Sprint Velocity Trend[/bold]")
    console.print("=" * 50)
    
    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Sprint", style="white", width=25)
    table.add_column("Points", justify="right", style="green", width=8)
    table.add_column("Completed", justify="right", style="yellow", width=10)
    table.add_column("Target", justify="right", style="blue", width=8)
    table.add_column("Progress", justify="left", width=25)
    
    for velocity in velocities:
        sprint_name = velocity["sprint_name"][:25]
        points = velocity["completed_points"]
        completion = f"{velocity['completion_rate']:.0f}%"
        target = velocity["total_points"]
        
        # Create progress bar
        bar_length = 20
        filled_length = int(bar_length * velocity['completion_rate'] / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        table.add_row(
            sprint_name,
            str(points),
            completion,
            str(target),
            f"[green]{bar}[/green]"
        )
    
    console.print(table)
    
    # Calculate and display summary stats
    if velocities:
        completed_sprints = [v for v in velocities if v["status"] == "completed"]
        if completed_sprints:
            avg_velocity = sum(v["completed_points"] for v in completed_sprints) / len(completed_sprints)
            
            # Calculate trend
            if len(completed_sprints) >= 2:
                recent = completed_sprints[-3:]  # Last 3 sprints
                older = completed_sprints[-6:-3] if len(completed_sprints) >= 6 else completed_sprints[:-3]
                
                if older:
                    recent_avg = sum(v["completed_points"] for v in recent) / len(recent)
                    older_avg = sum(v["completed_points"] for v in older) / len(older)
                    
                    # Handle special cases for trend calculation
                    if older_avg == 0 and recent_avg > 0:
                        # From 0 to positive is a significant increase
                        trend_pct = 100  # Show as 100% increase
                        trend_symbol = "↑"
                        trend_color = "green"
                    elif older_avg > 0:
                        trend_pct = ((recent_avg - older_avg) / older_avg * 100)
                        trend_symbol = "↑" if trend_pct > 0 else ("↓" if trend_pct < 0 else "→")
                        trend_color = "green" if trend_pct > 0 else ("red" if trend_pct < 0 else "yellow")
                    else:
                        # Both are 0
                        trend_pct = 0
                        trend_symbol = "→"
                        trend_color = "yellow"
                    
                    console.print(f"\nAverage velocity: [bold]{avg_velocity:.1f}[/bold] points/sprint")
                    if len(completed_sprints) >= 6:
                        console.print(f"Trend: [{trend_color}]{trend_symbol} {abs(trend_pct):.0f}% (comparing last 3 sprints vs previous 3)[/{trend_color}]")
                    else:
                        console.print(f"Trend: [{trend_color}]{trend_symbol} {abs(trend_pct):.0f}% (comparing last {len(recent)} sprints vs first {len(older)})[/{trend_color}]")
                else:
                    console.print(f"\nAverage velocity: [bold]{avg_velocity:.1f}[/bold] points/sprint")
            else:
                console.print(f"\nAverage velocity: [bold]{avg_velocity:.1f}[/bold] points/sprint")


@app.command()
def velocity(
    ctx: typer.Context,
    limit: int = typer.Option(5, "--limit", "-n", help="Number of sprints to display"),
    format: str = typer.Option("human", "--format", "-f", help="Output format: human, json, csv"),
    all_sprints: bool = typer.Option(False, "--all", help="Show all sprints including active ones"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
):
    """Display team velocity trends across sprints."""
    try:
        # Ensure we're in a Gira project
        gira_root = ensure_gira_project()
        
        # Load all sprints
        sprints = []
        
        # Load from all sprint directories
        for status_dir in ["active", "completed", "planned"]:
            sprint_dir = gira_root / ".gira" / "sprints" / status_dir
            if sprint_dir.exists():
                for sprint_file in sprint_dir.glob("*.json"):
                    try:
                        sprint = Sprint.model_validate_json(sprint_file.read_text())
                        sprints.append(sprint)
                    except Exception:
                        console.print(f"[yellow]Warning:[/yellow] Skipping invalid sprint file: {sprint_file.name}")
        
        # Sort sprints by start date (newest first)
        sprints = sorted(sprints, key=lambda s: s.start_date if s.start_date else s.created_at, reverse=True)
        
        if not all_sprints:
            # Filter to completed sprints by default
            sprints = [s for s in sprints if s.status == "completed"]
        
        # Limit the number of sprints
        if limit > 0:
            sprints = sprints[:limit]
        
        if not sprints:
            console.print("[yellow]No completed sprints found. Use --all to include active sprints.[/yellow]")
            return
        
        # Load all tickets including archived ones (completed sprints often have archived tickets)
        from gira.utils.ticket_utils import load_all_tickets
        tickets = load_all_tickets(gira_root, include_archived=True)
        
        # Calculate velocity for each sprint
        velocities = []
        for sprint in reversed(sprints):  # Show oldest first
            # Only show warnings in human format, not JSON/CSV
            show_warnings = format == "human"
            velocity_data = calculate_sprint_velocity(sprint, tickets, verbose=show_warnings)
            velocities.append(velocity_data)
        
        # Output based on format
        if format == "json":
            output = {
                "sprints": velocities,
                "summary": {
                    "total_sprints": len(velocities),
                    "average_velocity": sum(v["completed_points"] for v in velocities) / len(velocities) if velocities else 0,
                }
            }
            color_kwargs = get_color_kwargs(color, no_color)
            print_output(output, OutputFormat.JSON, **color_kwargs)
        
        elif format == "csv":
            # CSV header
            print("sprint_id,sprint_name,start_date,end_date,total_points,completed_points,completion_rate,status")
            for v in velocities:
                print(f"{v['sprint_id']},{v['sprint_name']},{v['start_date']},{v['end_date']},"
                      f"{v['total_points']},{v['completed_points']},{v['completion_rate']:.1f},{v['status']}")
        
        else:  # human format
            display_velocity_chart(velocities, console)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)