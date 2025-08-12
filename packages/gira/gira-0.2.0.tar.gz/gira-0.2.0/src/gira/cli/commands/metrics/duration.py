"""Status duration metrics command implementation."""

import json
import re
import subprocess
from datetime import datetime, timedelta, date, timezone
from typing import List, Dict, Any, Optional, Tuple, Callable
from collections import defaultdict
import statistics
from pathlib import Path

import typer
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TaskProgressColumn, TimeElapsedColumn

from gira.utils.project import ensure_gira_project
from gira.models.ticket import Ticket, TicketStatus
from gira.models.config import ProjectConfig
from gira.models.working_hours import WorkingHoursConfig
from gira.utils.console import console
from gira.utils.output import OutputFormat, print_output, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.metrics_cache import cached_git_history, get_metrics_cache
from gira.utils.git_batch_operations import get_batch_ticket_histories_cached
from gira.utils.working_hours import calculate_working_hours, format_working_hours


app = typer.Typer()


def _calculate_duration_statistics(
    status_durations: Dict[str, List[float]],
    cycle_times: List[float],
    lead_times: List[float],
    status_flow: Dict[str, Dict[str, int]],
    total_tickets: int,
    tickets_with_history: int,
    tickets_with_fallback: int,
    completed_tickets: int = 0,
    working_hours_config: Optional[WorkingHoursConfig] = None,
    working_status_durations: Optional[Dict[str, List[float]]] = None,
    working_cycle_times: Optional[List[float]] = None,
    working_lead_times: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Calculate statistics from collected duration data."""
    metrics = {
        "status_durations": {},
        "cycle_time": {},
        "lead_time": {},
        "status_flow": dict(status_flow),
        "total_tickets": total_tickets,
        "tickets_with_history": tickets_with_history,
        "tickets_with_fallback": tickets_with_fallback,
        "completed_tickets": completed_tickets
    }
    
    # Status duration statistics
    for status, durations in status_durations.items():
        if durations:
            metrics["status_durations"][status] = {
                "count": len(durations),
                "mean": statistics.mean(durations),
                "median": statistics.median(durations),
                "min": min(durations),
                "max": max(durations),
                "stdev": statistics.stdev(durations) if len(durations) > 1 else 0
            }
    
    # Cycle time statistics
    if cycle_times:
        metrics["cycle_time"] = {
            "count": len(cycle_times),
            "mean": statistics.mean(cycle_times),
            "median": statistics.median(cycle_times),
            "min": min(cycle_times),
            "max": max(cycle_times),
            "stdev": statistics.stdev(cycle_times) if len(cycle_times) > 1 else 0
        }
    
    # Lead time statistics
    if lead_times:
        metrics["lead_time"] = {
            "count": len(lead_times),
            "mean": statistics.mean(lead_times),
            "median": statistics.median(lead_times),
            "min": min(lead_times),
            "max": max(lead_times),
            "stdev": statistics.stdev(lead_times) if len(lead_times) > 1 else 0
        }
    
    # Working hours statistics (if configured)
    if working_hours_config and working_status_durations:
        metrics["working_hours_config"] = {
            "timezone": working_hours_config.timezone,
            "start_time": working_hours_config.start_time,
            "end_time": working_hours_config.end_time,
            "hours_per_day": working_hours_config.get_working_hours_per_day()
        }
        
        # Working hours status durations
        metrics["working_status_durations"] = {}
        for status, durations in working_status_durations.items():
            if durations:
                metrics["working_status_durations"][status] = {
                    "count": len(durations),
                    "mean": statistics.mean(durations),
                    "median": statistics.median(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "stdev": statistics.stdev(durations) if len(durations) > 1 else 0
                }
        
        # Working hours cycle time
        if working_cycle_times:
            metrics["working_cycle_time"] = {
                "count": len(working_cycle_times),
                "mean": statistics.mean(working_cycle_times),
                "median": statistics.median(working_cycle_times),
                "min": min(working_cycle_times),
                "max": max(working_cycle_times),
                "stdev": statistics.stdev(working_cycle_times) if len(working_cycle_times) > 1 else 0
            }
        
        # Working hours lead time
        if working_lead_times:
            metrics["working_lead_time"] = {
                "count": len(working_lead_times),
                "mean": statistics.mean(working_lead_times),
                "median": statistics.median(working_lead_times),
                "min": min(working_lead_times),
                "max": max(working_lead_times),
                "stdev": statistics.stdev(working_lead_times) if len(working_lead_times) > 1 else 0
            }
    
    return metrics




def calculate_status_durations_with_fallback(
    tickets: List[Ticket], 
    gira_root: Path, 
    no_cache: bool = False, 
    progress_callback: Optional[callable] = None, 
    force_batch: bool = False,
    working_hours_config: Optional[WorkingHoursConfig] = None
) -> Dict[str, Any]:
    """
    Calculate duration metrics using git history with timestamp fallback.
    
    Uses git history when available, falls back to timestamp-based calculation
    for tickets without git history.
    
    Args:
        tickets: List of tickets to analyze
        gira_root: Path to gira project root
        no_cache: Bypass cache if True
        progress_callback: Optional callback function(ticket_index, ticket_id) to update progress
        force_batch: Force batch operations regardless of ticket count
        working_hours_config: Optional working hours configuration
    """
    # Check if we should use batch operations
    use_batch = force_batch or len(tickets) > 10  # Use batch for more than 10 tickets
    
    if use_batch:
        return calculate_status_durations_batch(tickets, gira_root, no_cache, progress_callback, working_hours_config)
    else:
        return calculate_status_durations_individual(tickets, gira_root, no_cache, progress_callback, working_hours_config)


def calculate_status_durations_batch(
    tickets: List[Ticket], 
    gira_root: Path, 
    no_cache: bool = False, 
    progress_callback: Optional[callable] = None,
    working_hours_config: Optional[WorkingHoursConfig] = None
) -> Dict[str, Any]:
    """Calculate duration metrics using optimized batch git operations."""
    status_durations = defaultdict(list)
    cycle_times = []
    lead_times = []
    status_flow = defaultdict(lambda: defaultdict(int))
    
    # Working hours collections
    working_status_durations = defaultdict(list) if working_hours_config else None
    working_cycle_times = [] if working_hours_config else None
    working_lead_times = [] if working_hours_config else None
    
    tickets_with_history = 0
    tickets_with_fallback = 0
    
    # Extract ticket IDs
    ticket_ids = [ticket.id for ticket in tickets]
    ticket_map = {ticket.id: ticket for ticket in tickets}
    
    # Update progress for batch operation start
    if progress_callback:
        progress_callback(0, "Fetching git histories...")
    
    # Get all histories in one batch operation
    cache_instance = get_metrics_cache() if not no_cache else None
    all_histories = get_batch_ticket_histories_cached(
        ticket_ids, 
        gira_root, 
        cache_instance=cache_instance,
        no_cache=no_cache
    )
    
    # Process each ticket's history
    for idx, ticket in enumerate(tickets):
        if progress_callback:
            progress_callback(idx, ticket.id)
        
        history = all_histories.get(ticket.id, [])
        
        if history:
            tickets_with_history += 1
            
            # Calculate durations for each status using git history
            for i in range(len(history)):
                if history[i]['to_status']:
                    # Calculate time in this status
                    start_time = history[i]['timestamp']
                    
                    if i + 1 < len(history):
                        # Time until next transition
                        end_time = history[i + 1]['timestamp']
                        duration_hours = (end_time - start_time).total_seconds() / 3600
                        status_durations[history[i]['to_status']].append(duration_hours)
                        
                        # Calculate working hours if configured
                        if working_hours_config:
                            working_hours = calculate_working_hours(start_time, end_time, working_hours_config)
                            working_status_durations[history[i]['to_status']].append(working_hours)
                        
                        # Track status flow
                        from_status = history[i]['to_status']
                        to_status = history[i + 1]['to_status']
                        status_flow[from_status][to_status] += 1
                    else:
                        # Still in this status - use current time if not done/archived
                        if history[i]['to_status'] not in ['done', 'archived']:
                            end_time = datetime.now(timezone.utc)
                            duration_hours = (end_time - start_time).total_seconds() / 3600
                            status_durations[history[i]['to_status']].append(duration_hours)
                            
                            # Calculate working hours if configured
                            if working_hours_config:
                                working_hours = calculate_working_hours(start_time, end_time, working_hours_config)
                                working_status_durations[history[i]['to_status']].append(working_hours)
            
            # Calculate lead/cycle times for completed tickets
            if any(h['to_status'] == 'done' for h in history):
                creation_time = history[0]['timestamp']
                done_transitions = [h for h in history if h['to_status'] == 'done']
                if done_transitions:
                    done_time = done_transitions[-1]['timestamp']
                    lead_time = (done_time - creation_time).total_seconds() / 3600
                    lead_times.append(lead_time)
                    
                    # Calculate working hours lead time if configured
                    if working_hours_config:
                        working_lead_time = calculate_working_hours(creation_time, done_time, working_hours_config)
                        working_lead_times.append(working_lead_time)
                    
                    # Calculate cycle time (first work state to done)
                    work_starts = [h for h in history 
                                  if h['to_status'] in ['todo', 'in_progress'] 
                                  and (not h['from_status'] or h['from_status'] in ['backlog'])]
                    if work_starts:
                        cycle_start = work_starts[0]['timestamp']
                        cycle_time = (done_time - cycle_start).total_seconds() / 3600
                        cycle_times.append(cycle_time)
                        
                        # Calculate working hours cycle time if configured
                        if working_hours_config:
                            working_cycle_time = calculate_working_hours(cycle_start, done_time, working_hours_config)
                            working_cycle_times.append(working_cycle_time)
        else:
            # Fallback to timestamp-based calculation
            tickets_with_fallback += 1
            
            if ticket.status == "done":
                # Handle timezone differences
                updated_at = ticket.updated_at
                created_at = ticket.created_at
                
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                    
                lead_time = (updated_at - created_at).total_seconds() / 3600
                lead_times.append(lead_time)
                cycle_times.append(lead_time)  # Approximate
                
                # Add approximate status duration
                initial_status = "backlog" if ticket.status == "backlog" else "todo"
                duration = (updated_at - created_at).total_seconds() / 3600
                status_durations[initial_status].append(duration)
    
    # Calculate statistics
    metrics = _calculate_duration_statistics(
        status_durations, cycle_times, lead_times, status_flow,
        len(tickets), tickets_with_history, tickets_with_fallback,
        len([t for t in tickets if t.status == "done"]),
        working_hours_config, working_status_durations, working_cycle_times, working_lead_times
    )
    
    return metrics


def calculate_status_durations_individual(
    tickets: List[Ticket], 
    gira_root: Path, 
    no_cache: bool = False, 
    progress_callback: Optional[callable] = None,
    working_hours_config: Optional[WorkingHoursConfig] = None
) -> Dict[str, Any]:
    """Calculate duration metrics using individual git operations (original implementation)."""
    status_durations = defaultdict(list)  # status -> list of durations in hours
    cycle_times = []  # todo/backlog to done
    lead_times = []  # created to done
    
    # Status flow tracking
    status_flow = defaultdict(lambda: defaultdict(int))
    
    # Working hours collections
    working_status_durations = defaultdict(list) if working_hours_config else None
    working_cycle_times = [] if working_hours_config else None
    working_lead_times = [] if working_hours_config else None
    
    # Track tickets with git history
    tickets_with_history = 0
    tickets_with_fallback = 0
    
    for idx, ticket in enumerate(tickets):
        # Update progress if callback provided
        if progress_callback:
            progress_callback(idx, ticket.id)
            
        # Try git history first
        history = get_ticket_git_status_history(ticket.id, gira_root, no_cache=no_cache)
        
        if history:
            tickets_with_history += 1
            
            # Calculate durations for each status using git history
            for i in range(len(history)):
                if history[i]['to_status']:
                    # Calculate time in this status
                    start_time = history[i]['timestamp']
                    
                    if i + 1 < len(history):
                        # Time until next transition
                        end_time = history[i + 1]['timestamp']
                        duration_hours = (end_time - start_time).total_seconds() / 3600
                        status_durations[history[i]['to_status']].append(duration_hours)
                        
                        # Calculate working hours if configured
                        if working_hours_config:
                            working_hours = calculate_working_hours(start_time, end_time, working_hours_config)
                            working_status_durations[history[i]['to_status']].append(working_hours)
                        
                        # Track status flow
                        from_status = history[i]['to_status']
                        to_status = history[i + 1]['to_status']
                        status_flow[from_status][to_status] += 1
                    else:
                        # Still in this status - use current time if not done/archived
                        if history[i]['to_status'] not in ['done', 'archived']:
                            end_time = datetime.now(timezone.utc)
                            duration_hours = (end_time - start_time).total_seconds() / 3600
                            status_durations[history[i]['to_status']].append(duration_hours)
                            
                            # Calculate working hours if configured
                            if working_hours_config:
                                working_hours = calculate_working_hours(start_time, end_time, working_hours_config)
                                working_status_durations[history[i]['to_status']].append(working_hours)
            
            # Calculate lead/cycle times for completed tickets
            if any(h['to_status'] == 'done' for h in history):
                creation_time = history[0]['timestamp']
                done_transitions = [h for h in history if h['to_status'] == 'done']
                if done_transitions:
                    done_time = done_transitions[-1]['timestamp']
                    lead_time = (done_time - creation_time).total_seconds() / 3600
                    lead_times.append(lead_time)
                    
                    # Calculate working hours lead time if configured
                    if working_hours_config:
                        working_lead_time = calculate_working_hours(creation_time, done_time, working_hours_config)
                        working_lead_times.append(working_lead_time)
                    
                    # Calculate cycle time (first work state to done)
                    work_starts = [h for h in history 
                                  if h['to_status'] in ['todo', 'in_progress'] 
                                  and (not h['from_status'] or h['from_status'] in ['backlog'])]
                    if work_starts:
                        cycle_start = work_starts[0]['timestamp']
                        cycle_time = (done_time - cycle_start).total_seconds() / 3600
                        cycle_times.append(cycle_time)
                        
                        # Calculate working hours cycle time if configured
                        if working_hours_config:
                            working_cycle_time = calculate_working_hours(cycle_start, done_time, working_hours_config)
                            working_cycle_times.append(working_cycle_time)
        else:
            # Fallback to timestamp-based calculation
            tickets_with_fallback += 1
            
            if ticket.status == "done":
                # Handle timezone differences
                updated_at = ticket.updated_at
                created_at = ticket.created_at
                
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                    
                lead_time = (updated_at - created_at).total_seconds() / 3600
                lead_times.append(lead_time)
                cycle_times.append(lead_time)  # Approximate
                
                # Add approximate status duration
                initial_status = "backlog" if ticket.status == "backlog" else "todo"
                duration = (updated_at - created_at).total_seconds() / 3600
                status_durations[initial_status].append(duration)
    
    # Calculate statistics
    return _calculate_duration_statistics(
        status_durations, cycle_times, lead_times, status_flow,
        len(tickets), tickets_with_history, tickets_with_fallback,
        len([t for t in tickets if t.status == "done"]),
        working_hours_config, working_status_durations, working_cycle_times, working_lead_times
    )


def format_duration(hours: float) -> str:
    """Format duration in hours to human-readable string."""
    if hours < 1:
        return f"{int(hours * 60)}m"
    elif hours < 24:
        return f"{hours:.1f}h"
    elif hours < 168:  # Less than a week
        days = hours / 24
        return f"{days:.1f}d"
    else:
        weeks = hours / 168
        return f"{weeks:.1f}w"


def extract_status_from_path(path: str) -> Optional[str]:
    """Extract status from file path."""
    # Match patterns like .gira/board/todo/ or .gira/board/in_progress/
    match = re.search(r'\.gira/board/([^/]+)/', path)
    if match:
        return match.group(1)
    
    # Handle backlog
    if '.gira/backlog/' in path:
        return 'backlog'
    
    # Handle archived
    if '.gira/archived/' in path:
        return 'archived'
    
    return None


def parse_git_timestamp(timestamp_str: str) -> datetime:
    """Parse git timestamp string to datetime object."""
    # Git format: "2025-07-28 08:50:33 -0700"
    # Parse and convert to UTC
    dt = datetime.strptime(timestamp_str[:19], "%Y-%m-%d %H:%M:%S")
    
    # Extract timezone offset
    tz_str = timestamp_str[20:].strip()
    if tz_str and len(tz_str) >= 5:
        # Parse offset like "-0700" or "+0100"
        try:
            sign = 1 if tz_str[0] == '+' else -1
            hours = int(tz_str[1:3])
            minutes = int(tz_str[3:5]) if len(tz_str) >= 5 else 0
            offset = timedelta(hours=sign * hours, minutes=sign * minutes)
            
            # Apply offset to get UTC time (subtract for negative offsets, add for positive)
            if sign == -1:
                dt = dt + timedelta(hours=hours, minutes=minutes)
            else:
                dt = dt - timedelta(hours=hours, minutes=minutes)
        except (ValueError, IndexError):
            # If parsing fails, assume UTC
            pass
    
    # Make timezone-aware (UTC)
    return dt.replace(tzinfo=timezone.utc)


@cached_git_history()
def get_ticket_git_status_history(ticket_id: str, gira_root: Path, no_cache: bool = False) -> List[Dict[str, Any]]:
    """Extract full status history from git log."""
    
    # Change to gira root directory for git commands
    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(gira_root)
        
        # Get git log for this ticket
        cmd = [
            "git", "log", "--follow", "--name-status", 
            "--format=COMMIT|%H|%ai|%an|%s",
            "--", f"**/{ticket_id}.json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Try without wildcard if it fails
            cmd = [
                "git", "log", "--follow", "--name-status", 
                "--format=COMMIT|%H|%ai|%an|%s",
                "--all", "--", f"{ticket_id}.json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        history = []
        current_commit = None
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('COMMIT|'):
                parts = line.split('|', 4)
                if len(parts) >= 5:
                    current_commit = {
                        'hash': parts[1],
                        'timestamp': parse_git_timestamp(parts[2]),
                        'author': parts[3],
                        'message': parts[4]
                    }
            elif current_commit and line[0] in 'RAMD':
                # Parse file operation
                if line.startswith('R'):  # Rename/move
                    # Format: R100<tab>old_path<tab>new_path
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        old_path = parts[1]
                        new_path = parts[2]
                        
                        old_status = extract_status_from_path(old_path)
                        new_status = extract_status_from_path(new_path)
                        
                        if old_status and new_status and old_status != new_status:
                            history.append({
                                'from_status': old_status,
                                'to_status': new_status,
                                'timestamp': current_commit['timestamp'],
                                'commit': current_commit['hash'],
                                'author': current_commit['author'],
                                'message': current_commit['message']
                            })
                elif line.startswith('A'):  # Added
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        path = parts[1]
                        status = extract_status_from_path(path)
                        if status:
                            history.append({
                                'from_status': None,
                                'to_status': status,
                                'timestamp': current_commit['timestamp'],
                                'commit': current_commit['hash'],
                                'author': current_commit['author'],
                                'message': current_commit['message']
                            })
        
        # Sort by timestamp (oldest first)
        history.sort(key=lambda x: x['timestamp'])
        
        return history
        
    finally:
        os.chdir(original_cwd)




def display_duration_metrics(metrics: Dict[str, Any], console):
    """Display duration metrics in a formatted way."""
    console.print("\n[bold]Status Duration Analysis[/bold]")
    
    # Show git history coverage
    if "tickets_with_history" in metrics:
        history_count = metrics["tickets_with_history"]
        fallback_count = metrics.get("tickets_with_fallback", 0)
        total = metrics["total_tickets"]
        
        if history_count == total:
            console.print("[green]✓ All tickets analyzed using git history[/green]")
        elif history_count > 0:
            console.print(f"[dim]Git history: {history_count} tickets, Timestamp fallback: {fallback_count} tickets[/dim]")
        else:
            console.print("[yellow]Note: Using timestamp-based analysis (no git history available)[/yellow]")
    
    console.print("=" * 60)
    
    # Check if working hours data is available
    has_working_hours = "working_status_durations" in metrics and metrics["working_status_durations"]
    
    # Status durations table
    if metrics["status_durations"]:
        if has_working_hours:
            console.print("\n[cyan]Average Time in Each Status (Calendar Time | Working Hours)[/cyan]")
        else:
            console.print("\n[cyan]Average Time in Each Status[/cyan]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Status", style="white", width=15)
        table.add_column("Count", justify="right", width=8)
        
        if has_working_hours:
            table.add_column("Avg Calendar", justify="right", style="yellow", width=12)
            table.add_column("Avg Working", justify="right", style="green", width=12)
            table.add_column("Median", justify="right", style="dim", width=10)
            table.add_column("Min", justify="right", style="dim", width=8)
            table.add_column("Max", justify="right", style="dim", width=8)
        else:
            table.add_column("Average", justify="right", style="yellow", width=10)
            table.add_column("Median", justify="right", style="green", width=10)
            table.add_column("Min", justify="right", style="blue", width=8)
            table.add_column("Max", justify="right", style="red", width=8)
        
        # Order statuses logically
        status_order = ["backlog", "todo", "in_progress", "review", "done"]
        
        for status in status_order:
            if status in metrics["status_durations"]:
                data = metrics["status_durations"][status]
                
                if has_working_hours and status in metrics["working_status_durations"]:
                    working_data = metrics["working_status_durations"][status]
                    table.add_row(
                        status.replace("_", " ").title(),
                        str(data["count"]),
                        format_duration(data["mean"]),
                        format_working_hours(working_data["mean"]) if working_data else "-",
                        format_duration(data["median"]),
                        format_duration(data["min"]),
                        format_duration(data["max"])
                    )
                else:
                    table.add_row(
                        status.replace("_", " ").title(),
                        str(data["count"]),
                        format_duration(data["mean"]),
                        format_duration(data["median"]),
                        format_duration(data["min"]),
                        format_duration(data["max"])
                    )
        
        console.print(table)
    
    # Cycle and Lead Time
    console.print("\n[cyan]Flow Metrics[/cyan]")
    
    flow_table = Table(show_header=True, header_style="bold cyan", box=None)
    flow_table.add_column("Metric", style="white", width=20)
    
    if has_working_hours:
        flow_table.add_column("Avg Calendar", justify="right", style="yellow", width=12)
        flow_table.add_column("Avg Working", justify="right", style="green", width=12)
        flow_table.add_column("Median", justify="right", style="dim", width=10)
        flow_table.add_column("Min", justify="right", style="dim", width=8)
        flow_table.add_column("Max", justify="right", style="dim", width=8)
    else:
        flow_table.add_column("Average", justify="right", style="yellow", width=10)
        flow_table.add_column("Median", justify="right", style="green", width=10)
        flow_table.add_column("Min", justify="right", style="blue", width=8)
        flow_table.add_column("Max", justify="right", style="red", width=8)
    
    if metrics["cycle_time"]:
        ct = metrics["cycle_time"]
        
        if has_working_hours and "working_cycle_time" in metrics:
            wct = metrics["working_cycle_time"]
            flow_table.add_row(
                "Cycle Time",
                format_duration(ct["mean"]),
                format_working_hours(wct["mean"]) if wct else "-",
                format_duration(ct["median"]),
                format_duration(ct["min"]),
                format_duration(ct["max"])
            )
        else:
            flow_table.add_row(
                "Cycle Time",
                format_duration(ct["mean"]),
                format_duration(ct["median"]),
                format_duration(ct["min"]),
                format_duration(ct["max"])
            )
    
    if metrics["lead_time"]:
        lt = metrics["lead_time"]
        
        if has_working_hours and "working_lead_time" in metrics:
            wlt = metrics["working_lead_time"]
            flow_table.add_row(
                "Lead Time",
                format_duration(lt["mean"]),
                format_working_hours(wlt["mean"]) if wlt else "-",
                format_duration(lt["median"]),
                format_duration(lt["min"]),
                format_duration(lt["max"])
            )
        else:
            flow_table.add_row(
                "Lead Time",
                format_duration(lt["mean"]),
                format_duration(lt["median"]),
                format_duration(lt["min"]),
                format_duration(lt["max"])
            )
    
    console.print(flow_table)
    
    # Status flow visualization
    if metrics["status_flow"]:
        console.print("\n[cyan]Status Transitions[/cyan]")
        console.print("Shows how tickets move between statuses")
        
        flow = metrics["status_flow"]
        for from_status, transitions in flow.items():
            total = sum(transitions.values())
            console.print(f"\nFrom [bold]{from_status}[/bold] ({total} tickets):")
            
            with Progress(
                TextColumn("  → {task.fields[to_status]:12}", justify="left"),
                BarColumn(bar_width=30),
                TextColumn("{task.percentage:>3.0f}%"),
                console=console,
                transient=True
            ) as progress:
                for to_status, count in sorted(transitions.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total) * 100
                    task = progress.add_task(
                        "",
                        total=total,
                        completed=count,
                        to_status=to_status.replace("_", " ").title()
                    )
    
    # Summary statistics
    console.print(f"\n[bold]Summary[/bold]")
    console.print(f"Total tickets analyzed: {metrics['total_tickets']}")
    console.print(f"Completed tickets: {metrics['completed_tickets']}")
    
    if metrics["completed_tickets"] > 0:
        completion_rate = (metrics["completed_tickets"] / metrics["total_tickets"]) * 100
        console.print(f"Completion rate: {completion_rate:.1f}%")
    
    # Show working hours configuration if used
    if has_working_hours and "working_hours_config" in metrics:
        config = metrics["working_hours_config"]
        console.print(f"\n[dim]Working hours: {config['start_time']} - {config['end_time']} ({config['hours_per_day']:.1f}h/day), {config['timezone']}[/dim]")


def filter_tickets_by_criteria(
    tickets: List[Ticket],
    ticket_type: Optional[str] = None,
    priority: Optional[str] = None,
    days: Optional[int] = None,
) -> List[Ticket]:
    """Filter tickets based on criteria."""
    filtered = tickets
    
    if ticket_type:
        filtered = [t for t in filtered if t.type == ticket_type]
    
    if priority:
        filtered = [t for t in filtered if t.priority == priority]
    
    if days:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        # Handle both timezone-aware and naive datetimes
        new_filtered = []
        for t in filtered:  # Use filtered, not tickets
            created_at = t.created_at
            if created_at.tzinfo is None:
                # Make naive datetime timezone-aware
                created_at = created_at.replace(tzinfo=timezone.utc)
            if created_at >= cutoff_date:
                new_filtered.append(t)
        filtered = new_filtered
    
    return filtered


@app.command()
def duration(
    ctx: typer.Context,
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Analyze tickets from last N days"),
    format: str = typer.Option("human", "--format", "-f", help="Output format: human, json, csv"),
    ticket_type: Optional[str] = typer.Option(None, "--type", help="Filter by ticket type"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Filter by priority"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache and force fresh analysis"),
    no_progress: bool = typer.Option(False, "--no-progress", help="Disable progress indicator"),
    force_batch: bool = typer.Option(False, "--force-batch", help="Force batch git operations (for testing)"),
    working_hours: bool = typer.Option(False, "--working-hours", help="Calculate durations using business hours only"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
):
    """Analyze time tickets spend in each status to identify bottlenecks."""
    try:
        # Ensure we're in a Gira project
        gira_root = ensure_gira_project()
        
        # Load project configuration for working hours if requested
        working_hours_config = None
        if working_hours:
            config_path = gira_root / ".gira" / "config.json"
            project_config = ProjectConfig.from_json_file(str(config_path))
            if project_config.working_hours:
                working_hours_config = project_config.working_hours
            else:
                console.print("[yellow]Working hours not configured in project. Using calendar time.[/yellow]")
        
        # Load all tickets including archived ones
        from gira.utils.ticket_utils import load_all_tickets
        tickets = load_all_tickets(gira_root, include_archived=True)
        
        # Apply filters
        filtered_tickets = filter_tickets_by_criteria(tickets, ticket_type, priority, days)
        
        if not filtered_tickets:
            console.print("[yellow]No tickets found matching the specified criteria.[/yellow]")
            return
        
        # Calculate metrics using git history with fallback
        show_progress = format == "human" and not no_progress and len(filtered_tickets) > 1
        
        if show_progress:
            # Use progress bar for human format
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Analyzing ticket history...[/bold blue]"),
                BarColumn(),
                TaskProgressColumn(),
                TextColumn("• {task.fields[current_ticket]}"),
                TimeElapsedColumn(),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task(
                    "Processing", 
                    total=len(filtered_tickets),
                    current_ticket="Starting..."
                )
                
                if no_cache:
                    console.print("[dim]Cache bypassed - performing fresh analysis[/dim]")
                
                def update_progress(idx: int, ticket_id: str):
                    progress.update(task, completed=idx, current_ticket=ticket_id)
                
                metrics = calculate_status_durations_with_fallback(
                    filtered_tickets, gira_root, no_cache=no_cache, 
                    progress_callback=update_progress, force_batch=force_batch,
                    working_hours_config=working_hours_config
                )
                progress.update(task, completed=len(filtered_tickets), current_ticket="Complete")
        else:
            # No progress bar for JSON/CSV or when disabled
            if format != "json" and format != "csv":
                console.print("[dim]Analyzing ticket history...[/dim]")
                if no_cache:
                    console.print("[dim]Cache bypassed - performing fresh analysis[/dim]")
            metrics = calculate_status_durations_with_fallback(
                filtered_tickets, gira_root, no_cache=no_cache, force_batch=force_batch,
                working_hours_config=working_hours_config
            )
        
        # Add filter info to metrics
        metrics["filters"] = {
            "days": days,
            "type": ticket_type,
            "priority": priority,
            "ticket_count": len(filtered_tickets)
        }
        
        # Output based on format
        if format == "json":
            color_kwargs = get_color_kwargs(color, no_color)
            print_output(metrics, OutputFormat.JSON, **color_kwargs)
        
        elif format == "csv":
            # CSV header for status durations
            print("status,count,mean_hours,median_hours,min_hours,max_hours")
            for status, data in metrics["status_durations"].items():
                print(f"{status},{data['count']},{data['mean']:.2f},"
                      f"{data['median']:.2f},{data['min']:.2f},{data['max']:.2f}")
            
            # Add summary metrics
            print("\nmetric,value")
            print(f"total_tickets,{metrics['total_tickets']}")
            print(f"completed_tickets,{metrics['completed_tickets']}")
            
            if metrics["cycle_time"]:
                print(f"avg_cycle_time_hours,{metrics['cycle_time']['mean']:.2f}")
            
            if metrics["lead_time"]:
                print(f"avg_lead_time_hours,{metrics['lead_time']['mean']:.2f}")
        
        else:  # human format
            # Display filter info if any filters applied
            if any([ticket_type, priority, days]):
                filter_parts = []
                if ticket_type:
                    filter_parts.append(f"type={ticket_type}")
                if priority:
                    filter_parts.append(f"priority={priority}")
                if days:
                    filter_parts.append(f"last {days} days")
                
                console.print(f"\n[dim]Filters: {', '.join(filter_parts)}[/dim]")
            
            display_duration_metrics(metrics, console)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)