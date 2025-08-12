"""Estimate commands for story point management."""

import json
import re
from pathlib import Path
from typing import List, Optional

import typer
from rich.prompt import IntPrompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, get_ticket_path
from gira.utils.config import load_config
from gira.utils.board_config import get_board_configuration
from gira.cli.commands.ticket.update import _apply_ticket_updates
from gira.utils.typer_completion import complete_ticket_ids
from gira.utils.help_formatter import create_example, format_examples_simple


estimate_app = typer.Typer(help="Story point estimation commands")


def _expand_ticket_ids(ticket_ids: List[str], root: Path) -> List[str]:
    """Expand list of ticket ID patterns to individual ticket IDs."""
    all_ticket_ids = []
    
    for ticket_id_pattern in ticket_ids:
        expanded = _expand_ticket_pattern(root, ticket_id_pattern)
        all_ticket_ids.extend(expanded)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ticket_ids = []
    for ticket_id in all_ticket_ids:
        if ticket_id not in seen:
            seen.add(ticket_id)
            unique_ticket_ids.append(ticket_id)
    
    return unique_ticket_ids


def _expand_ticket_pattern(root: Path, pattern: str) -> List[str]:
    """Expand ticket pattern to list of ticket IDs.
    
    Supports:
    - Wildcards: TEST-1* matches TEST-10, TEST-11, etc.
    - Full prefix ranges: TEST-1..10 matches TEST-1 through TEST-10  
    - Number-only ranges: 1..10 matches TEST-1 through TEST-10 (uses project prefix)
    - Single IDs: TEST-1 or 1 returns [TEST-1]
    """
    tickets = []
    
    # Check for range pattern (e.g., TEST-1..10 or 1..10)
    if ".." in pattern:
        # Handle number-only ranges (e.g., "742..743")
        if pattern.count("-") == 0 and ".." in pattern:
            # This is a number-only range, add the project prefix
            prefix = _get_project_prefix(root)
            start_str, end_str = pattern.split("..", 1)
            try:
                start = int(start_str)
                end = int(end_str)
                for i in range(start, end + 1):
                    ticket_id = f"{prefix}-{i}"
                    if _ticket_exists(root, ticket_id):
                        tickets.append(ticket_id)
            except ValueError:
                # Not a valid range, treat as literal
                if _ticket_exists(root, pattern):
                    tickets.append(pattern)
        # Handle full prefix ranges (e.g., "GCM-1..10")
        elif "-" in pattern and ".." in pattern:
            prefix, range_part = pattern.rsplit("-", 1)
            if ".." in range_part:
                start_str, end_str = range_part.split("..", 1)
                try:
                    start = int(start_str)
                    end = int(end_str)
                    for i in range(start, end + 1):
                        ticket_id = f"{prefix}-{i}"
                        if _ticket_exists(root, ticket_id):
                            tickets.append(ticket_id)
                except ValueError:
                    # Not a valid range, treat as literal
                    if _ticket_exists(root, pattern):
                        tickets.append(pattern)
            else:
                # No range in the part after dash, treat as literal
                if _ticket_exists(root, pattern):
                    tickets.append(pattern)
        else:
            # Contains ".." but not a recognizable range pattern, treat as literal
            if _ticket_exists(root, pattern):
                tickets.append(pattern)
    
    # Check for wildcard pattern
    elif "*" in pattern:
        # Convert wildcard to regex
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")
        
        # Get swimlane IDs dynamically
        swimlane_ids = _get_swimlane_ids(root)
        
        # Search all ticket locations
        locations = [f"board/{swimlane}" for swimlane in swimlane_ids] + ["archive/tickets"]
        for location in locations:
            ticket_dir = root / ".gira" / location
            if ticket_dir.exists():
                for ticket_file in ticket_dir.glob("*.json"):
                    ticket_id = ticket_file.stem
                    if regex.match(ticket_id):
                        tickets.append(ticket_id)
    
    # Regular ticket ID
    else:
        if _ticket_exists(root, pattern):
            tickets.append(pattern)
    
    return tickets


def _get_swimlane_ids(root: Path) -> List[str]:
    """Get swimlane IDs from board configuration and actual directories."""
    swimlane_ids = set()
    
    # Get configured swimlanes from board config
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        board = get_board_configuration()
        swimlane_ids.update(swimlane.id for swimlane in board.swimlanes)
    
    # Also include any actual directories that exist in board/
    board_dir = root / ".gira" / "board"
    if board_dir.exists():
        for item in board_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                swimlane_ids.add(item.name)
    
    return list(swimlane_ids)


def _get_project_prefix(root: Path) -> str:
    """Get the project ticket ID prefix from configuration."""
    try:
        config = load_config()
        return config.get('ticket_id_prefix', 'TICKET')
    except Exception:
        # Fallback - try to infer from existing tickets
        board_dir = root / ".gira" / "board"
        if board_dir.exists():
            for status_dir in board_dir.iterdir():
                if status_dir.is_dir():
                    for ticket_file in status_dir.glob("*.json"):
                        ticket_id = ticket_file.stem
                        if "-" in ticket_id:
                            return ticket_id.split("-")[0]
        return "TICKET"  # Ultimate fallback


def _ticket_exists(root: Path, ticket_id: str) -> bool:
    """Check if a ticket exists in any location."""
    # Use find_ticket which properly handles all ticket locations
    from gira.utils.ticket_utils import find_ticket
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    return ticket is not None


@estimate_app.command("set")
def estimate_set(
    story_points: int = typer.Argument(..., help="Story points to assign (0-100)"),
    ticket_ids: List[str] = typer.Argument(..., help="Ticket ID(s) to estimate (supports patterns)", autocompletion=complete_ticket_ids),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket IDs"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without saving"),
) -> None:
    """Set story points for one or more tickets.
    
    Supports all ticket ID patterns including wildcards and ranges.
    
    Examples:
        gira ticket estimate set 5 GCM-123
        gira ticket estimate set 8 GCM-1 GCM-2 GCM-3
        gira ticket estimate set 3 "GCM-1*"
        gira ticket estimate set 5 "GCM-1..10"
    """
    root = ensure_gira_project()
    
    # Validate story points
    if not (0 <= story_points <= 100):
        console.print("[red]Error:[/red] Story points must be between 0 and 100")
        raise typer.Exit(1)
    
    # Expand ticket IDs using existing pattern support
    try:
        all_ticket_ids = _expand_ticket_ids(ticket_ids, root)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    if not all_ticket_ids:
        console.print("[red]Error:[/red] No tickets found matching the provided IDs")
        raise typer.Exit(1)
    
    # Show preview for multiple tickets or dry run
    if len(all_ticket_ids) > 1 or dry_run:
        console.print(f"\n[bold]Setting story points to {story_points} for {len(all_ticket_ids)} ticket(s):[/bold]")
        for ticket_id in all_ticket_ids:
            console.print(f"  • {ticket_id}")
        
        if dry_run:
            console.print("\n[yellow]Dry run - no changes made[/yellow]")
            return
    
    # Apply updates using existing bulk update infrastructure
    updated_tickets = []
    failed_tickets = []
    
    for ticket_id in all_ticket_ids:
        try:
            ticket, ticket_path = find_ticket(ticket_id, root)
            if not ticket:
                failed_tickets.append(f"{ticket_id}: Ticket not found")
                continue
            
            # Use existing update logic
            _apply_ticket_updates(
                ticket=ticket,
                ticket_path=ticket_path,
                root=root,
                strict=False,
                title=None,
                description=None,
                status=None,
                priority=None,
                ticket_type=None,
                assignee=None,
                add_labels=None,
                remove_labels=None,
                epic=None,
                parent=None,
                sprint=None,
                story_points=story_points
            )
            updated_tickets.append(ticket_id)
            
        except Exception as e:
            failed_tickets.append(f"{ticket_id}: {str(e)}")
    
    # Output results
    if output == "json":
        result = {
            "updated": updated_tickets,
            "failed": failed_tickets,
            "story_points": story_points
        }
        console.print(json.dumps(result, indent=2))
    else:
        if updated_tickets:
            if quiet:
                for ticket_id in updated_tickets:
                    console.print(ticket_id)
            else:
                console.print(f"\n[green]✅ Updated {len(updated_tickets)} ticket(s) with {story_points} story points[/green]")
                for ticket_id in updated_tickets:
                    console.print(f"  • {ticket_id}")
        
        if failed_tickets:
            console.print(f"\n[red]❌ Failed to update {len(failed_tickets)} ticket(s):[/red]")
            for error in failed_tickets:
                console.print(f"  • {error}")


@estimate_app.command("compare")
def estimate_compare(
    ticket_id_1: str = typer.Argument(..., help="First ticket ID", autocompletion=complete_ticket_ids),
    ticket_id_2: str = typer.Argument(..., help="Second ticket ID", autocompletion=complete_ticket_ids),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """Compare two tickets side-by-side for relative estimation.
    
    Shows ticket details in a comparison format to help with relative sizing.
    
    Examples:
        gira ticket estimate compare GCM-123 GCM-124
        gira ticket estimate compare GCM-100 GCM-200 --output json
    """
    root = ensure_gira_project()
    
    # Find both tickets
    ticket1, _ = find_ticket(ticket_id_1, root)
    ticket2, _ = find_ticket(ticket_id_2, root)
    
    if not ticket1:
        console.print(f"[red]Error:[/red] Ticket {ticket_id_1} not found")
        raise typer.Exit(1)
    
    if not ticket2:
        console.print(f"[red]Error:[/red] Ticket {ticket_id_2} not found")
        raise typer.Exit(1)
    
    if output == "json":
        result = {
            "ticket_1": {
                "id": ticket1.id,
                "title": ticket1.title,
                "description": ticket1.description,
                "type": ticket1.type,
                "priority": ticket1.priority,
                "story_points": ticket1.story_points,
                "status": ticket1.status
            },
            "ticket_2": {
                "id": ticket2.id,
                "title": ticket2.title,
                "description": ticket2.description,
                "type": ticket2.type,
                "priority": ticket2.priority,
                "story_points": ticket2.story_points,
                "status": ticket2.status
            }
        }
        console.print(json.dumps(result, indent=2))
        return
    
    # Create side-by-side comparison
    def create_ticket_panel(ticket, side_title):
        content_lines = []
        content_lines.append(f"[bold]{ticket.id}[/bold] - {ticket.title}")
        content_lines.append("")
        content_lines.append(f"[yellow]Type:[/yellow] {ticket.type}")
        content_lines.append(f"[yellow]Priority:[/yellow] {ticket.priority}")
        content_lines.append(f"[yellow]Status:[/yellow] {ticket.status}")
        
        story_points_display = str(ticket.story_points) if ticket.story_points else "[dim]Not estimated[/dim]"
        content_lines.append(f"[yellow]Story Points:[/yellow] {story_points_display}")
        
        if ticket.description:
            content_lines.append("")
            content_lines.append("[yellow]Description:[/yellow]")
            # Truncate long descriptions
            desc_lines = ticket.description.split('\n')
            for line in desc_lines[:5]:  # Show first 5 lines
                content_lines.append(f"  {line}")
            if len(desc_lines) > 5:
                content_lines.append("  [dim]...[/dim]")
        
        return Panel("\n".join(content_lines), title=side_title, title_align="left")
    
    panel1 = create_ticket_panel(ticket1, "Ticket 1")
    panel2 = create_ticket_panel(ticket2, "Ticket 2")
    
    console.print("\n[bold]Ticket Comparison for Relative Estimation[/bold]\n")
    console.print(Columns([panel1, panel2], equal=True))


@estimate_app.command("relative")
def estimate_relative(
    base_ticket_id: str = typer.Argument(..., help="Base ticket ID for comparison", autocompletion=complete_ticket_ids),
    ticket_ids: List[str] = typer.Argument(..., help="Ticket ID(s) to estimate relative to base", autocompletion=complete_ticket_ids),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """Show base ticket details while estimating other tickets.
    
    Displays the base ticket information and prompts for estimation of other tickets.
    
    Examples:
        gira ticket estimate relative GCM-100 GCM-101 GCM-102
        gira ticket estimate relative GCM-baseline "GCM-1*"
    """
    root = ensure_gira_project()
    
    # Find base ticket
    base_ticket, _ = find_ticket(base_ticket_id, root)
    if not base_ticket:
        console.print(f"[red]Error:[/red] Base ticket {base_ticket_id} not found")
        raise typer.Exit(1)
    
    # Expand and find target tickets
    try:
        all_ticket_ids = _expand_ticket_ids(ticket_ids, root)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    target_tickets = []
    for ticket_id in all_ticket_ids:
        ticket, _ = find_ticket(ticket_id, root)
        if ticket:
            target_tickets.append(ticket)
        else:
            console.print(f"[yellow]Warning:[/yellow] Ticket {ticket_id} not found, skipping")
    
    if not target_tickets:
        console.print("[red]Error:[/red] No valid target tickets found")
        raise typer.Exit(1)
    
    if output == "json":
        result = {
            "base_ticket": {
                "id": base_ticket.id,
                "title": base_ticket.title,
                "story_points": base_ticket.story_points,
                "type": base_ticket.type,
                "priority": base_ticket.priority
            },
            "target_tickets": [
                {
                    "id": t.id,
                    "title": t.title,
                    "current_story_points": t.story_points,
                    "type": t.type,
                    "priority": t.priority
                }
                for t in target_tickets
            ]
        }
        console.print(json.dumps(result, indent=2))
        return
    
    # Show base ticket info
    base_points = base_ticket.story_points or "[dim]Not estimated[/dim]"
    base_panel = Panel(
        f"[bold]{base_ticket.id}[/bold] - {base_ticket.title}\n\n"
        f"[yellow]Story Points:[/yellow] {base_points}\n"
        f"[yellow]Type:[/yellow] {base_ticket.type}\n"
        f"[yellow]Priority:[/yellow] {base_ticket.priority}\n\n"
        f"[dim]Use this ticket as your reference point for relative estimation[/dim]",
        title="Base Ticket for Comparison",
        title_align="left"
    )
    
    console.print("\n[bold]Relative Estimation[/bold]\n")
    console.print(base_panel)
    console.print(f"\n[bold]Target tickets to estimate ({len(target_tickets)}):[/bold]")
    
    # Display target tickets
    for i, ticket in enumerate(target_tickets, 1):
        current_points = str(ticket.story_points) if ticket.story_points else "[dim]Not estimated[/dim]"
        console.print(f"\n{i}. [bold]{ticket.id}[/bold] - {ticket.title}")
        console.print(f"   [yellow]Current points:[/yellow] {current_points}")
        console.print(f"   [yellow]Type:[/yellow] {ticket.type} | [yellow]Priority:[/yellow] {ticket.priority}")


@estimate_app.command("batch")
def estimate_batch(
    ticket_ids: List[str] = typer.Argument(..., help="Ticket ID(s) to estimate interactively", autocompletion=complete_ticket_ids),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    skip_estimated: bool = typer.Option(False, "--skip-estimated", help="Skip tickets that already have story points"),
) -> None:
    """Interactive batch estimation of multiple tickets.
    
    Prompts for story points for each ticket in sequence.
    
    Examples:
        gira ticket estimate batch GCM-101 GCM-102 GCM-103
        gira ticket estimate batch "GCM-1*" --skip-estimated
    """
    root = ensure_gira_project()
    
    # Expand and find tickets
    try:
        all_ticket_ids = _expand_ticket_ids(ticket_ids, root)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    tickets = []
    for ticket_id in all_ticket_ids:
        ticket, _ = find_ticket(ticket_id, root)
        if ticket:
            if skip_estimated and ticket.story_points is not None:
                continue
            tickets.append(ticket)
        else:
            console.print(f"[yellow]Warning:[/yellow] Ticket {ticket_id} not found, skipping")
    
    if not tickets:
        message = "No tickets need estimation" if skip_estimated else "No valid tickets found"
        console.print(f"[yellow]{message}[/yellow]")
        return
    
    console.print(f"\n[bold]Interactive Batch Estimation ({len(tickets)} tickets)[/bold]\n")
    
    estimated_tickets = []
    skipped_tickets = []
    
    for i, ticket in enumerate(tickets, 1):
        current_points = str(ticket.story_points) if ticket.story_points else "[dim]Not estimated[/dim]"
        
        # Show ticket info
        console.print(f"\n[bold]Ticket {i}/{len(tickets)}:[/bold]")
        ticket_panel = Panel(
            f"[bold]{ticket.id}[/bold] - {ticket.title}\n\n"
            f"[yellow]Type:[/yellow] {ticket.type} | [yellow]Priority:[/yellow] {ticket.priority}\n"
            f"[yellow]Current points:[/yellow] {current_points}\n\n"
            f"[yellow]Description:[/yellow]\n{ticket.description[:200]}{'...' if len(ticket.description) > 200 else ''}",
            title=f"Estimate Ticket {ticket.id}",
            title_align="left"
        )
        console.print(ticket_panel)
        
        # Prompt for estimation
        try:
            while True:
                points = IntPrompt.ask(
                    "Enter story points (0-100, or -1 to skip)",
                    default=-1
                )
                
                if points == -1:
                    skipped_tickets.append(ticket.id)
                    break
                elif 0 <= points <= 100:
                    # Get ticket path - find it again to get the path
                    _, ticket_path = find_ticket(ticket.id, root)
                    
                    # Apply update
                    _apply_ticket_updates(
                        ticket=ticket,
                        ticket_path=ticket_path,
                        root=root,
                        strict=False,
                        title=None,
                        description=None,
                        status=None,
                        priority=None,
                        ticket_type=None,
                        assignee=None,
                        add_labels=None,
                        remove_labels=None,
                        epic=None,
                        parent=None,
                        sprint=None,
                        story_points=points
                    )
                    estimated_tickets.append((ticket.id, points))
                    console.print(f"[green]✅ Set {ticket.id} to {points} story points[/green]")
                    break
                else:
                    console.print("[red]Story points must be between 0 and 100[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Estimation cancelled[/yellow]")
            break
    
    # Show summary
    if output == "json":
        result = {
            "estimated": [{"id": tid, "story_points": points} for tid, points in estimated_tickets],
            "skipped": skipped_tickets,
            "total_processed": len(estimated_tickets) + len(skipped_tickets)
        }
        console.print(json.dumps(result, indent=2))
    else:
        console.print(f"\n[bold]Batch Estimation Summary:[/bold]")
        console.print(f"  • [green]Estimated:[/green] {len(estimated_tickets)} tickets")
        console.print(f"  • [yellow]Skipped:[/yellow] {len(skipped_tickets)} tickets")
        
        if estimated_tickets:
            console.print(f"\n[green]Estimated tickets:[/green]")
            for ticket_id, points in estimated_tickets:
                console.print(f"  • {ticket_id}: {points} points")