"""Generate historical sprints from completed epics and tickets."""

import json
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict
import statistics

import typer
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Confirm
from rich import box

from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets
from gira.models.sprint import Sprint, SprintStatus
from gira.models.ticket import Ticket
from gira.models.epic import Epic


def load_all_epics(root: Path, include_archived: bool = True) -> List[Epic]:
    """Load all epics from the project including archived ones."""
    epics = []
    
    # Load from main epics directory
    epics_dir = root / ".gira" / "epics"
    if epics_dir.exists():
        for epic_file in epics_dir.glob("*.json"):
            try:
                epic = Epic.from_json_file(str(epic_file))
                epics.append(epic)
            except Exception:
                continue
    
    # Load archived epics if requested
    if include_archived:
        archive_epics_dir = root / ".gira" / "archive" / "epics"
        if archive_epics_dir.exists():
            for epic_file in archive_epics_dir.glob("*.json"):
                try:
                    epic = Epic.from_json_file(str(epic_file))
                    epics.append(epic)
                except Exception:
                    continue
    
    return epics


def load_existing_sprints(root: Path) -> List[Sprint]:
    """Load all existing sprints to avoid conflicts."""
    sprints = []
    sprints_dir = root / ".gira" / "sprints"
    
    # Load from all status directories
    for status_dir in ["active", "completed", "planned"]:
        status_path = sprints_dir / status_dir
        if status_path.exists():
            for sprint_file in status_path.glob("*.json"):
                try:
                    sprint = Sprint.from_json_file(str(sprint_file))
                    sprints.append(sprint)
                except Exception:
                    continue
    
    # Load from root directory
    if sprints_dir.exists():
        for sprint_file in sprints_dir.glob("*.json"):
            try:
                sprint = Sprint.from_json_file(str(sprint_file))
                sprints.append(sprint)
            except Exception:
                continue
    
    return sprints


def analyze_epic_completion_patterns(epics: List[Epic], tickets: List[Ticket]) -> Dict[str, Any]:
    """Analyze completion patterns for epics to determine sprint timeframes."""
    epic_patterns = {}
    
    for epic in epics:
        if epic.status not in ["completed", "active"]:
            continue
            
        # Get tickets belonging to this epic
        epic_tickets = [t for t in tickets if t.epic_id == epic.id]
        completed_tickets = [t for t in epic_tickets if t.status == "done"]
        
        if not completed_tickets:
            continue
        
        # Extract completion dates
        completion_dates = []
        for ticket in completed_tickets:
            completion_date = ticket.updated_at
            if completion_date.tzinfo is None:
                completion_date = completion_date.replace(tzinfo=timezone.utc)
            completion_dates.append(completion_date.date())
        
        if completion_dates:
            start_date = min(completion_dates)
            end_date = max(completion_dates)
            
            # Calculate duration and average completion date
            duration = (end_date - start_date).days + 1
            avg_date = start_date + timedelta(days=duration // 2)
            
            epic_patterns[epic.id] = {
                "epic": epic,
                "tickets": epic_tickets,
                "completed_tickets": completed_tickets,
                "start_date": start_date,
                "end_date": end_date,
                "duration": duration,
                "avg_completion_date": avg_date,
                "story_points": sum(t.story_points or 0 for t in completed_tickets)
            }
    
    return epic_patterns


def group_orphaned_tickets(tickets: List[Ticket], sprint_duration: int = 14) -> List[Dict[str, Any]]:
    """Group tickets without epic assignments into time-based sprints."""
    # Filter tickets that are completed but not assigned to any epic
    orphaned_tickets = [
        t for t in tickets 
        if t.status == "done" and not t.epic_id and not t.sprint_id
    ]
    
    if not orphaned_tickets:
        return []
    
    # Sort by completion date
    sorted_tickets = sorted(
        orphaned_tickets,
        key=lambda t: t.updated_at.date() if t.updated_at.tzinfo else t.updated_at.replace(tzinfo=timezone.utc).date()
    )
    
    # Group into sprint-sized chunks
    sprint_groups = []
    current_group = []
    current_start_date = None
    
    for ticket in sorted_tickets:
        completion_date = ticket.updated_at
        if completion_date.tzinfo is None:
            completion_date = completion_date.replace(tzinfo=timezone.utc)
        completion_date = completion_date.date()
        
        # Start new group if needed
        if not current_start_date:
            current_start_date = completion_date
            current_group = [ticket]
        elif (completion_date - current_start_date).days <= sprint_duration:
            current_group.append(ticket)
        else:
            # Finalize current group
            if current_group:
                end_date = max(
                    t.updated_at.date() if t.updated_at.tzinfo else t.updated_at.replace(tzinfo=timezone.utc).date()
                    for t in current_group
                )
                
                sprint_groups.append({
                    "tickets": current_group,
                    "start_date": current_start_date,
                    "end_date": end_date,
                    "story_points": sum(t.story_points or 0 for t in current_group)
                })
            
            # Start new group
            current_start_date = completion_date
            current_group = [ticket]
    
    # Add final group
    if current_group:
        end_date = max(
            t.updated_at.date() if t.updated_at.tzinfo else t.updated_at.replace(tzinfo=timezone.utc).date()
            for t in current_group
        )
        
        sprint_groups.append({
            "tickets": current_group,
            "start_date": current_start_date,
            "end_date": end_date,
            "story_points": sum(t.story_points or 0 for t in current_group)
        })
    
    return sprint_groups


def generate_sprint_from_epic(epic_pattern: Dict[str, Any], sprint_duration: int = 14) -> Sprint:
    """Generate a sprint from an epic completion pattern."""
    epic = epic_pattern["epic"]
    
    # Use epic completion dates with some padding
    natural_start = epic_pattern["start_date"]
    natural_end = epic_pattern["end_date"]
    natural_duration = epic_pattern["duration"]
    
    # Adjust to sprint duration if needed
    if natural_duration <= sprint_duration and natural_duration > 0:
        # Use natural dates
        start_date = natural_start
        end_date = natural_end
    else:
        # Center around average completion date or use natural start
        if natural_duration > sprint_duration:
            # Use natural start and extend to sprint duration
            start_date = natural_start
            end_date = start_date + timedelta(days=sprint_duration - 1)
        else:
            # Single day completion or invalid range, create sprint around it
            start_date = natural_start
            end_date = start_date + timedelta(days=max(1, sprint_duration - 1))
    
    # Ensure end date is after start date
    if end_date <= start_date:
        end_date = start_date + timedelta(days=1)
    
    # Generate sprint ID and name
    sprint_id = f"SPRINT-{start_date.isoformat()}"
    sprint_name = f"{epic.title} Sprint"
    
    # Create sprint goal from epic description
    if epic.description and len(epic.description) > 100:
        goal = f"Complete {epic.title}: {epic.description[:100]}..."
    elif epic.description:
        goal = f"Complete {epic.title}: {epic.description}"
    else:
        goal = f"Complete {epic.title}"
    
    # Get ticket IDs
    ticket_ids = [t.id for t in epic_pattern["completed_tickets"]]
    
    sprint = Sprint(
        id=sprint_id,
        name=sprint_name,
        goal=goal,
        start_date=start_date,
        end_date=end_date,
        status=SprintStatus.COMPLETED,
        tickets=ticket_ids,
        retrospective={
            "what_went_well": [
                f"Completed {len(ticket_ids)} tickets",
                f"Delivered {epic_pattern['story_points']} story points",
                f"Successfully finished {epic.title}"
            ],
            "what_went_wrong": [
                "Historical sprint - actual challenges not recorded"
            ],
            "action_items": [
                "Continue maintaining current development velocity"
            ]
        }
    )
    
    return sprint


def generate_sprint_from_orphaned_group(group: Dict[str, Any], index: int) -> Sprint:
    """Generate a sprint from a group of orphaned tickets."""
    start_date = group["start_date"]
    end_date = group["end_date"]
    tickets = group["tickets"]
    
    # Ensure end date is after start date
    if end_date <= start_date:
        end_date = start_date + timedelta(days=1)
    
    # Generate sprint ID and name
    sprint_id = f"SPRINT-{start_date.isoformat()}"
    month_year = start_date.strftime("%B %Y")
    sprint_name = f"General Development Sprint {index} ({month_year})"
    
    # Create goal
    goal = f"Complete miscellaneous development tasks and improvements for {month_year}"
    
    # Get ticket IDs
    ticket_ids = [t.id for t in tickets]
    
    sprint = Sprint(
        id=sprint_id,
        name=sprint_name,
        goal=goal,
        start_date=start_date,
        end_date=end_date,
        status=SprintStatus.COMPLETED,
        tickets=ticket_ids,
        retrospective={
            "what_went_well": [
                f"Completed {len(ticket_ids)} tickets",
                f"Delivered {group['story_points']} story points",
                "Maintained steady development progress"
            ],
            "what_went_wrong": [
                "Historical sprint - actual challenges not recorded"
            ],
            "action_items": [
                "Better epic planning for future work organization"
            ]
        }
    )
    
    return sprint


def validate_sprint_conflicts(proposed_sprints: List[Sprint], existing_sprints: List[Sprint]) -> List[str]:
    """Check for conflicts with existing sprints."""
    conflicts = []
    
    for proposed in proposed_sprints:
        for existing in existing_sprints:
            # Check ID conflicts
            if proposed.id == existing.id:
                conflicts.append(f"Sprint ID conflict: {proposed.id} already exists")
            
            # Check date overlap conflicts
            if (proposed.start_date <= existing.end_date and 
                proposed.end_date >= existing.start_date):
                conflicts.append(
                    f"Date overlap: {proposed.id} ({proposed.start_date} to {proposed.end_date}) "
                    f"overlaps with {existing.id} ({existing.start_date} to {existing.end_date})"
                )
            
            # Check ticket assignment conflicts
            proposed_tickets = set(proposed.tickets)
            existing_tickets = set(existing.tickets)
            overlap = proposed_tickets & existing_tickets
            if overlap:
                conflicts.append(
                    f"Ticket assignment conflict: tickets {', '.join(list(overlap)[:3])}{'...' if len(overlap) > 3 else ''} "
                    f"already assigned to {existing.id}"
                )
    
    return conflicts


def save_historical_sprint(sprint: Sprint, root: Path) -> bool:
    """Save a historical sprint to the completed directory."""
    sprints_dir = root / ".gira" / "sprints" / "completed"
    sprints_dir.mkdir(parents=True, exist_ok=True)
    
    sprint_file = sprints_dir / f"{sprint.id}.json"
    
    try:
        # Update timestamp
        sprint.updated_at = datetime.now(timezone.utc)
        sprint.save_to_json_file(str(sprint_file))
        return True
    except Exception as e:
        console.print(f"[red]Error saving sprint {sprint.id}:[/red] {e}")
        return False


def generate_historical(
    epic_filter: Optional[str] = typer.Option(None, "--epic", help="Generate sprint only for specific epic"),
    start_date: Optional[str] = typer.Option(None, "--start", help="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end", help="End date filter (YYYY-MM-DD)"),
    sprint_duration: int = typer.Option(14, "--duration", help="Sprint duration in days"),
    include_orphaned: bool = typer.Option(True, "--include-orphaned/--no-orphaned", help="Include tickets without epic assignments"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview sprints without creating them")
):
    """Generate historical sprints from completed epics and tickets."""
    root = ensure_gira_project()
    
    console.print("[cyan]🏗️ Historical Sprint Generation[/cyan]\n")
    console.print("Analyzing completed epics and tickets...")
    
    # Load data
    epics = load_all_epics(root, include_archived=True)
    tickets = load_all_tickets(root, include_archived=True)
    existing_sprints = load_existing_sprints(root)
    
    # Filter by date if specified
    if start_date or end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
            
            if start_dt or end_dt:
                filtered_tickets = []
                for ticket in tickets:
                    completion_date = ticket.updated_at
                    if completion_date.tzinfo is None:
                        completion_date = completion_date.replace(tzinfo=timezone.utc)
                    completion_date = completion_date.date()
                    
                    if start_dt and completion_date < start_dt:
                        continue
                    if end_dt and completion_date > end_dt:
                        continue
                    
                    filtered_tickets.append(ticket)
                
                tickets = filtered_tickets
        except ValueError:
            console.print("[red]Error:[/red] Invalid date format. Use YYYY-MM-DD")
            raise typer.Exit(1)
    
    # Filter by epic if specified
    if epic_filter:
        epics = [e for e in epics if e.id.upper() == epic_filter.upper()]
        if not epics:
            console.print(f"[red]Error:[/red] Epic {epic_filter} not found")
            raise typer.Exit(1)
    
    console.print(f"Found [yellow]{len(epics)}[/yellow] epics and [yellow]{len(tickets)}[/yellow] tickets")
    console.print(f"Existing sprints: [cyan]{len(existing_sprints)}[/cyan]\n")
    
    # Analyze epic patterns
    epic_patterns = analyze_epic_completion_patterns(epics, tickets)
    console.print(f"Epic-based sprint candidates: [green]{len(epic_patterns)}[/green]")
    
    # Group orphaned tickets
    orphaned_groups = []
    if include_orphaned:
        orphaned_groups = group_orphaned_tickets(tickets, sprint_duration)
        console.print(f"Orphaned ticket groups: [yellow]{len(orphaned_groups)}[/yellow]")
    
    # Generate proposed sprints
    proposed_sprints = []
    
    # Epic-based sprints
    for epic_id, pattern in epic_patterns.items():
        sprint = generate_sprint_from_epic(pattern, sprint_duration)
        proposed_sprints.append(sprint)
    
    # Orphaned ticket sprints
    for i, group in enumerate(orphaned_groups, 1):
        sprint = generate_sprint_from_orphaned_group(group, i)
        proposed_sprints.append(sprint)
    
    if not proposed_sprints:
        console.print("[yellow]No historical sprints to generate[/yellow]")
        return
    
    # Sort by start date
    proposed_sprints.sort(key=lambda s: s.start_date)
    
    # Validate conflicts
    conflicts = validate_sprint_conflicts(proposed_sprints, existing_sprints)
    
    # Display summary
    console.print(f"\n[bold]Proposed Historical Sprints: {len(proposed_sprints)}[/bold]")
    
    # Create summary table
    table = Table(title="Sprint Generation Summary", box=box.ROUNDED)
    table.add_column("Sprint ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Dates", style="green")
    table.add_column("Tickets", justify="right", style="yellow")
    table.add_column("Points", justify="right", style="magenta")
    table.add_column("Type", style="blue")
    
    total_tickets = 0
    total_points = 0
    
    for sprint in proposed_sprints:
        sprint_type = "Epic-based" if any(pattern["epic"].id in [t.epic_id for t in tickets if t.id in sprint.tickets] for pattern in epic_patterns.values()) else "General"
        ticket_count = len(sprint.tickets)
        points = sum(t.story_points or 0 for t in tickets if t.id in sprint.tickets)
        
        total_tickets += ticket_count
        total_points += points
        
        table.add_row(
            sprint.id,
            sprint.name[:30] + "..." if len(sprint.name) > 30 else sprint.name,
            f"{sprint.start_date} to {sprint.end_date}",
            str(ticket_count),
            str(points),
            sprint_type
        )
    
    console.print(table)
    console.print(f"\nTotal: [yellow]{total_tickets}[/yellow] tickets, [magenta]{total_points}[/magenta] story points")
    
    # Show conflicts if any
    if conflicts:
        console.print(f"\n[red]⚠️ Conflicts Detected ({len(conflicts)}):[/red]")
        for conflict in conflicts[:5]:  # Show first 5 conflicts
            console.print(f"  • {conflict}")
        if len(conflicts) > 5:
            console.print(f"  • ... and {len(conflicts) - 5} more conflicts")
        
        if not dry_run:
            console.print("\n[yellow]Resolve conflicts before proceeding[/yellow]")
            return
    
    if dry_run:
        console.print("\n[yellow]DRY RUN:[/yellow] No sprints will be created")
        return
    
    # Confirm creation
    if not Confirm.ask(f"\nCreate {len(proposed_sprints)} historical sprints?"):
        console.print("[dim]Generation cancelled[/dim]")
        return
    
    # Create sprints
    created_count = 0
    failed_count = 0
    
    for sprint in proposed_sprints:
        if save_historical_sprint(sprint, root):
            created_count += 1
        else:
            failed_count += 1
    
    # Summary
    if created_count > 0:
        console.print(f"\n[green]✅ Successfully created {created_count} historical sprints[/green]")
    if failed_count > 0:
        console.print(f"[red]❌ Failed to create {failed_count} sprints[/red]")
    
    console.print(f"\n[cyan]📊 Historical velocity data is now available![/cyan]")
    console.print("Run [bold]gira metrics velocity --all[/bold] to see the complete timeline")