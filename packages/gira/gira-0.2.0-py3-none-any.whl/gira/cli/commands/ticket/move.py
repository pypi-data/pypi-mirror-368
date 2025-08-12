"""Move ticket command for Gira."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
import re

import typer
from gira.utils.console import console
from rich.prompt import Confirm
from rich.table import Table
from gira.constants import normalize_status
from gira.models import Ticket
from gira.utils.cache import invalidate_ticket_cache
from gira.utils.config import load_config, save_config
from gira.utils.board_config import get_board_configuration
from gira.utils.error_codes import ErrorCode, handle_error
from gira.utils.errors import GiraError
from gira.utils.errors import require_ticket
from gira.utils.confirmations import should_skip_confirmation
from gira.utils.hybrid_storage import migrate_ticket_location, get_ticket_storage_path
from gira.utils.output import OutputFormat
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, process_bulk_operation
from gira.utils.ticket_utils import find_ticket
from gira.models.board import Board
from gira.utils.hooks import execute_hook, build_ticket_move_event_data
from gira.utils.typer_completion import complete_ticket_ids, complete_status_values, complete_priority_values, complete_epic_ids, complete_sprint_ids

def move(
    ticket_ids: Optional[List[str]] = typer.Argument(None, help="Ticket ID(s) to move (use '-' to read from stdin)", autocompletion=complete_ticket_ids),
    target_status: str = typer.Argument(..., help="Target status to move ticket to", autocompletion=complete_status_values),
    position: Optional[int] = typer.Option(None, "--position", "-p", help="Position in new column (1-based)"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output ticket ID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview the move without performing it"),
    git: Optional[bool] = typer.Option(None, "--git/--no-git", help="Stage the move using 'git mv'"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    force_transition: bool = typer.Option(False, "--force-transition", help="Skip workflow validation and force the transition"),
    confirm: bool = typer.Option(False, "--confirm", help="Force confirmation prompt even if configured to skip"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Filter by assignee (use 'me' for current user)"),
    from_status: Optional[str] = typer.Option(None, "--from", help="Only move tickets from this status", autocompletion=complete_status_values),
    epic_id: Optional[str] = typer.Option(None, "--epic", "-e", help="Filter tickets by epic ID", autocompletion=complete_epic_ids),
    sprint_id: Optional[str] = typer.Option(None, "--sprint", "-s", help="Filter tickets by sprint ID (use 'current' for active sprint)", autocompletion=complete_sprint_ids),
    comment: Optional[str] = typer.Option(None, "--comment", "-c", help="Add comment to moved tickets"),
    assign: Optional[str] = typer.Option(None, "--assign", help="Assign tickets to user while moving"),
    add_label: Optional[str] = typer.Option(None, "--add-label", help="Add label to moved tickets"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Update priority while moving", autocompletion=complete_priority_values),
    check_deps: bool = typer.Option(False, "--check-dependencies", help="Check for blocking dependencies"),
    batch_id: Optional[str] = typer.Option(None, "--batch", "-b", help="Batch ID for undo operations"),
    if_no_blockers: bool = typer.Option(False, "--if-no-blockers", help="Only move if ticket has no unresolved blocking dependencies"),
    if_complete: bool = typer.Option(False, "--if-complete", help="Only move if ticket completion criteria are met"),
    if_allowed: bool = typer.Option(False, "--if-allowed", help="Only move if workflow transition is allowed"),
) -> None:
    """Move ticket(s) to a different status/swimlane.
    
    Can accept multiple ticket IDs as arguments, read from stdin, or filter by criteria.
    Supports pattern matching, bulk operations, and additional updates during move.
    
    Git Integration:
        By default, moves are automatically staged with 'git mv' if .gira is tracked.
        Control this behavior with:
        - --git / --no-git flags
        - GIRA_AUTO_GIT_MV environment variable
        - git.auto_stage_moves in config.json
    
    Examples:
        # Move a single ticket
        gira ticket move TEST-1 done
        
        # Move multiple tickets
        gira ticket move TEST-1 TEST-2 TEST-3 "in progress"
        
        # Move with force (no confirmation)
        gira ticket move TEST-1 TEST-2 done --force
        
        # Move tickets from a specific status
        gira ticket move --from todo "in progress" --assignee me
        
        # Move tickets in an epic
        gira ticket move --epic EPIC-001 --from todo "in progress"
        
        # Move and update fields
        gira ticket move TEST-1 TEST-2 review --assign alice --priority high
        
        # Move with comment
        gira ticket move TEST-1 done --comment "Completed in sprint 15"
        
        # Check dependencies before moving
        gira ticket move TEST-1 done --check-dependencies
        
        # Force transition bypassing workflow rules
        gira ticket move TEST-1 done --force-transition
        
        # Conditional moves (only move if conditions are met)
        gira ticket move TEST-1 done --if-no-blockers
        gira ticket move TEST-1 review --if-complete --if-allowed
        gira ticket move --from todo done --if-no-blockers --if-complete
        
        # Pattern matching (wildcards and ranges)
        gira ticket move "TEST-1*" done  # TEST-10, TEST-11, etc.
        gira ticket move "TEST-1..10" review  # TEST-1 through TEST-10
        
        # Move from stdin
        gira query "epic:EPIC-015" --format ids | gira ticket move - done
        
        # Dry run to preview changes
        gira ticket move TEST-1 TEST-2 done --dry-run
    """
    root = ensure_gira_project()

    # Determine whether to use git mv
    use_git_mv = _should_use_git_mv(root, git)

    # Determine output format based on output parameter
    output_format = OutputFormat.JSON if output == "json" else OutputFormat.TEXT
    
    # Load board configuration
    board = get_board_configuration()
    
    # Validate and normalize target status
    target_status = normalize_status(target_status)
    # Special handling for backlog - it's a valid status but not a board swimlane
    if target_status != "backlog" and not board.is_valid_status(target_status):
        valid_statuses = board.get_valid_statuses() + ["backlog"]  # Include backlog as valid
        handle_error(
            code=ErrorCode.INVALID_TICKET_STATUS,
            message=f"Invalid status: '{target_status}'",
            details={
                "status": target_status,
                "valid_statuses": valid_statuses
            },
            console=console
        )
    
    # Collect ticket IDs from various sources
    tickets_to_move = []
    
    # Check if we should read from stdin
    if ticket_ids and len(ticket_ids) == 1 and ticket_ids[0] == "-":
        return _move_bulk_from_stdin(root, target_status, position, output, quiet, use_git_mv, 
                                    force, from_status, assignee, epic_id, sprint_id, 
                                    comment, assign, add_label, priority, check_deps, batch_id, dry_run,
                                    if_no_blockers, if_complete, if_allowed)
    
    # Check for filter-based moving
    if from_status or assignee or epic_id or sprint_id:
        tickets_to_move.extend(_find_tickets_by_filter(root, from_status, assignee, epic_id, sprint_id))
    
    # Process provided ticket IDs (could include patterns)
    if ticket_ids:
        for ticket_id in ticket_ids:
            tickets_to_move.extend(_expand_ticket_pattern(root, ticket_id))
    
    # If no tickets specified and no filters, check stdin
    if not tickets_to_move and not ticket_ids and not sys.stdin.isatty():
        return _move_bulk_from_stdin(root, target_status, position, output, quiet, use_git_mv,
                                    force, from_status, assignee, epic_id, sprint_id,
                                    comment, assign, add_label, priority, check_deps, batch_id, dry_run,
                                    if_no_blockers, if_complete, if_allowed)
    
    # Validate we have tickets to move
    if not tickets_to_move:
        handle_error(
            code=ErrorCode.MISSING_ARGUMENT,
            message="No tickets specified for moving",
            details={"help": "Provide ticket IDs, use filters (--from, --assignee, --epic), or use '-' to read from stdin"},
            console=console
        )

    # Remove duplicates while preserving order
    seen = set()
    unique_tickets = []
    for ticket_id in tickets_to_move:
        if ticket_id not in seen:
            seen.add(ticket_id)
            unique_tickets.append(ticket_id)
    tickets_to_move = unique_tickets
    
    # Dry run mode - just show what would be moved
    if dry_run:
        _show_dry_run_preview(root, tickets_to_move, target_status, output)
        return
    
    # If only one ticket, use single ticket flow (it handles confirmations internally)
    if len(tickets_to_move) == 1:
        ticket_id = tickets_to_move[0]
        return _move_single_ticket_interactive(ticket_id, target_status, position, output, quiet, root, use_git_mv, 
                                              comment, assign, add_label, priority, check_deps, force_transition, force, confirm,
                                              if_no_blockers, if_complete, if_allowed)
    
    # Multiple tickets - use bulk move
    return _move_bulk_tickets(root, tickets_to_move, target_status, position, force, confirm, output, quiet, use_git_mv,
                             comment, assign, add_label, priority, check_deps, batch_id, force_transition,
                             if_no_blockers, if_complete, if_allowed)


def _show_dry_run_preview(root: Path, ticket_ids: List[str], target_status: str, output: Optional[str]) -> None:
    """Show preview of what would be moved."""
    if output == "json":
        # Load ticket details for JSON output
        tickets = []
        for ticket_id in ticket_ids:
            try:
                ticket, ticket_path = find_ticket(ticket_id, root)
                if ticket:
                    tickets.append({
                        "id": ticket.id,
                        "title": ticket.title,
                        "status": ticket.status,
                        "target_status": target_status
                    })
            except Exception:
                tickets.append({"id": ticket_id, "error": "Not found"})
        
        console.print_json(data={
            "dry_run": True,
            "action": "move",
            "target_status": target_status,
            "tickets": tickets,
            "count": len(tickets)
        })
    else:
        console.print(f"\n[bold]Dry Run - Would move {len(ticket_ids)} ticket(s) to {target_status}:[/bold]")
        
        # Create a table for better display
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Current Status", style="yellow")
        table.add_column("Target Status", style="green")
        
        for ticket_id in ticket_ids[:20]:  # Show first 20
            try:
                ticket, _ = find_ticket(ticket_id, root)
                if ticket:
                    table.add_row(ticket.id, ticket.title[:50], ticket.status, target_status)
                else:
                    table.add_row(ticket_id, "[red]Not found[/red]", "-", "-")
            except Exception:
                table.add_row(ticket_id, "[red]Error loading[/red]", "-", "-")
        
        console.print(table)
        
        if len(ticket_ids) > 20:
            console.print(f"\n... and {len(ticket_ids) - 20} more tickets")
        
        console.print(f"\n[dim]No changes made. Remove --dry-run to perform move.[/dim]")


def _move_single_ticket_interactive(ticket_id: str, target_status: str, position: Optional[int], output: Optional[str], 
                                   quiet: bool, root: Path, use_git_mv: bool, comment: Optional[str], assign: Optional[str],
                                   add_label: Optional[str], priority: Optional[str], check_deps: bool, force_transition: bool, force: bool = False, confirm: bool = False,
                                   if_no_blockers: bool = False, if_complete: bool = False, if_allowed: bool = False) -> None:
    """Move a single ticket with interactive confirmation."""
    # Ensure force and confirm are booleans
    # Handle case where typer OptionInfo object is passed instead of boolean
    if hasattr(confirm, 'default'):
        # This is a typer OptionInfo object, get the default value
        confirm = False
    else:
        confirm = bool(confirm) if confirm is not None else False
    
    force = bool(force) if force is not None else False
    # Find the ticket
    ticket, ticket_path = find_ticket(ticket_id, root)
    
    # Handle not found
    output_format = OutputFormat.JSON if output == "json" else OutputFormat.TEXT
    require_ticket(ticket_id.upper(), ticket, output_format)
    
    # Check if already in target status
    if ticket.status == target_status:
        if not quiet:
            console.print(f"Ticket {ticket.id} is already in {target_status}")
        raise typer.Exit(0)
    
    # Check conditional flags
    failed_conditions = []
    
    if if_no_blockers and not _check_if_no_blockers(root, ticket):
        blocked_by = _check_blocking_dependencies(root, ticket)
        blocking_ids = [b['id'] for b in blocked_by]
        failed_conditions.append(f"blocked by: {', '.join(blocking_ids)}")
    
    if if_complete and not _check_if_complete(root, ticket):
        failed_conditions.append("not complete (missing assignee or incomplete criteria)")
    
    if if_allowed and not _check_if_allowed(root, ticket, target_status):
        failed_conditions.append(f"transition not allowed from {ticket.status} to {target_status}")
    
    # If any conditions failed, skip the move
    if failed_conditions:
        if output == "json":
            console.print_json(data={
                "id": ticket.id,
                "status": ticket.status,
                "target_status": target_status,
                "moved": False,
                "reason": "conditions not met",
                "failed_conditions": failed_conditions
            })
        elif not quiet:
            console.print(f"[yellow]Skipped {ticket.id}:[/yellow] conditions not met")
            for condition in failed_conditions:
                console.print(f"  - {condition}")
        raise typer.Exit(0)
    
    # Check dependencies if requested
    if check_deps:
        blocked_by = _check_blocking_dependencies(root, ticket)
        if blocked_by:
            from gira.utils.errors import DependencyError, handle_error
            blocking_ids = [b['id'] for b in blocked_by]
            details = "\n".join([f"  - {b['id']}: {b['title']} (status: {b['status']})" for b in blocked_by])
            error = DependencyError(
                f"Cannot move ticket - blocked by unresolved dependencies:\n{details}",
                ticket.id,
                blocking_ids
            )
            handle_error(error)
    
    # Show ticket details and confirm
    if output != "json":
        from rich.panel import Panel
        console.print(Panel(
            f"[bold]{ticket.id}[/bold] - {ticket.title}\n"
            f"Status: {ticket.status} → {target_status}\n"
            f"Type: {ticket.type}\n"
            f"Priority: {ticket.priority or 'None'}\n"
            f"Assignee: {ticket.assignee or 'Unassigned'}",
            title="[blue]Ticket to Move[/blue]",
            border_style="blue"
        ))
        
        # Show additional updates if any
        if comment or assign or add_label or priority:
            console.print("\n[yellow]Additional Updates:[/yellow]")
            if comment:
                console.print(f"  • Add comment: {comment}")
            if assign:
                console.print(f"  • Assign to: {assign}")
            if add_label:
                console.print(f"  • Add label: {add_label}")
            if priority:
                console.print(f"  • Set priority: {priority}")
        
        if not should_skip_confirmation(force, confirm):
            from rich.prompt import Confirm
            if not Confirm.ask(f"\nMove this ticket to {target_status}?"):
                raise typer.Exit(0)
    
    # Perform the move with updates
    try:
        result = _move_single_ticket_with_updates(ticket_id, target_status, position, root, use_git_mv,
                                                comment, assign, add_label, priority, force_transition)
        
        if output == "json":
            console.print_json(data=result)
        elif quiet:
            console.print(ticket_id)
        else:
            console.print(f"✅ Moved ticket [cyan]{ticket.id}[/cyan] from [yellow]{result['original_status']}[/yellow] to [green]{target_status}[/green]")
    except GiraError as e:
        # Handle GiraError exceptions gracefully
        if output == "json":
            error_data = {
                "error": e.message,
                "error_code": e.error_code,
                "details": e.details,
                "suggestions": e.suggestions
            }
            console.print_json(data=error_data)
        else:
            console.print(f"[red]Error:[/red] {e.message}")
            if e.suggestions:
                for suggestion in e.suggestions:
                    console.print(f"  [dim]→ {suggestion}[/dim]")
        raise typer.Exit(1)


def _move_bulk_tickets(root: Path, ticket_ids: List[str], target_status: str, position: Optional[int], force: bool, confirm: bool,
                      output: Optional[str], quiet: bool, use_git_mv: bool, comment: Optional[str], assign: Optional[str],
                      add_label: Optional[str], priority: Optional[str], check_deps: bool, batch_id: Optional[str], force_transition: bool,
                      if_no_blockers: bool = False, if_complete: bool = False, if_allowed: bool = False) -> None:
    """Move multiple tickets with progress feedback."""
    # Generate batch ID if not provided
    if not batch_id and len(ticket_ids) > 1:
        batch_id = f"move-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Filter tickets based on conditional flags
    if if_no_blockers or if_complete or if_allowed:
        filtered_tickets = []
        skipped_tickets = []
        
        for ticket_id in ticket_ids:
            ticket, _ = find_ticket(ticket_id, root)
            if not ticket:
                skipped_tickets.append((ticket_id, ["ticket not found"]))
                continue
            
            failed_conditions = []
            
            if if_no_blockers and not _check_if_no_blockers(root, ticket):
                blocked_by = _check_blocking_dependencies(root, ticket)
                blocking_ids = [b['id'] for b in blocked_by]
                failed_conditions.append(f"blocked by: {', '.join(blocking_ids)}")
            
            if if_complete and not _check_if_complete(root, ticket):
                failed_conditions.append("not complete")
            
            if if_allowed and not _check_if_allowed(root, ticket, target_status):
                failed_conditions.append(f"transition not allowed from {ticket.status} to {target_status}")
            
            if failed_conditions:
                skipped_tickets.append((ticket_id, failed_conditions))
            else:
                filtered_tickets.append(ticket_id)
        
        # Update ticket_ids to only include filtered tickets
        ticket_ids = filtered_tickets
        
        # Show skipped tickets if any
        if skipped_tickets and not quiet and output != "json":
            console.print(f"\n[yellow]Skipped {len(skipped_tickets)} ticket(s) due to unmet conditions:[/yellow]")
            for ticket_id, conditions in skipped_tickets[:5]:  # Show first 5
                console.print(f"  - [cyan]{ticket_id}[/cyan]: {', '.join(conditions)}")
            if len(skipped_tickets) > 5:
                console.print(f"  ... and {len(skipped_tickets) - 5} more")
        
        # If no tickets left after filtering, exit
        if not ticket_ids:
            if output == "json":
                console.print_json(data={
                    "moved": 0,
                    "skipped": len(skipped_tickets),
                    "skipped_tickets": [{"id": tid, "reasons": reasons} for tid, reasons in skipped_tickets]
                })
            elif not quiet:
                console.print(f"[yellow]No tickets met the specified conditions for moving to {target_status}[/yellow]")
            return
    
    # Check dependencies if requested
    if check_deps:
        tickets_with_blockers = []
        for ticket_id in ticket_ids:
            ticket, _ = find_ticket(ticket_id, root)
            if ticket:
                blocked_by = _check_blocking_dependencies(root, ticket)
                if blocked_by:
                    tickets_with_blockers.append((ticket.id, blocked_by))
        
        if tickets_with_blockers:
            console.print(f"\n[red]Cannot move {len(tickets_with_blockers)} ticket(s) - blocked by dependencies:[/red]")
            for ticket_id, blockers in tickets_with_blockers[:5]:
                console.print(f"\n[cyan]{ticket_id}[/cyan] is blocked by:")
                for blocker in blockers:
                    console.print(f"  - {blocker['id']}: {blocker['title']} (status: {blocker['status']})")
            if len(tickets_with_blockers) > 5:
                console.print(f"\n... and {len(tickets_with_blockers) - 5} more tickets with blockers")
            raise typer.Exit(1)
    
    # Confirm bulk move if confirmations not skipped
    if not should_skip_confirmation(force, confirm) and output != "json":
        console.print(f"\n[yellow]About to move {len(ticket_ids)} ticket(s) to {target_status}:[/yellow]")
        
        # Show preview of tickets to be moved
        preview_count = min(10, len(ticket_ids))
        for i, ticket_id in enumerate(ticket_ids[:preview_count]):
            ticket, _ = find_ticket(ticket_id, root)
            if ticket:
                console.print(f"  - [cyan]{ticket.id}[/cyan]: {ticket.title[:50]}{'...' if len(ticket.title) > 50 else ''} (from {ticket.status})")
            else:
                console.print(f"  - [cyan]{ticket_id}[/cyan]: [red]Not found[/red]")
        
        if len(ticket_ids) > preview_count:
            console.print(f"  ... and {len(ticket_ids) - preview_count} more")
        
        # Show additional updates if any
        if comment or assign or add_label or priority:
            console.print("\n[yellow]Additional Updates:[/yellow]")
            if comment:
                console.print(f"  • Add comment to all: {comment}")
            if assign:
                console.print(f"  • Assign all to: {assign}")
            if add_label:
                console.print(f"  • Add label to all: {add_label}")
            if priority:
                console.print(f"  • Set priority for all: {priority}")
        
        from rich.prompt import Confirm
        if not Confirm.ask(f"\nMove these tickets to {target_status}?"):
            raise typer.Exit(0)
    
    # Record batch operation if batch_id provided
    if batch_id:
        _record_batch_operation(root, batch_id, ticket_ids, target_status)
    
    # Convert to format expected by process_bulk_operation
    items = [{"id": ticket_id} for ticket_id in ticket_ids]
    
    # Process bulk move
    def move_single_ticket(item):
        ticket_id = item["id"]
        return _move_single_ticket_with_updates(ticket_id, target_status, position, root, use_git_mv,
                                               comment, assign, add_label, priority, force_transition)
    
    result = process_bulk_operation(
        items,
        move_single_ticket,
        "ticket move",
        show_progress=not quiet and len(items) > 1 and output != "json"
    )
    
    # Output results
    if output == "json":
        output_data = result.to_dict()
        if batch_id:
            output_data["batch_id"] = batch_id
        console.print_json(data=output_data)
    elif quiet:
        # Output only successfully moved ticket IDs
        for success in result.successful:
            console.print(success["result"]["id"])
    else:
        result.print_summary("ticket move")
        
        if batch_id and result.success_count > 0:
            console.print(f"\n[dim]Batch ID: {batch_id}[/dim]")
        
        # Show successful moves
        if result.successful and len(result.successful) <= 10:
            console.print(f"\n✅ **Moved Tickets:**")
            for success in result.successful:
                ticket_data = success["result"]
                console.print(f"  - [cyan]{ticket_data['id']}[/cyan]: {ticket_data['original_status']} → {ticket_data['new_status']}")
        elif result.successful:
            console.print(f"\n✅ Moved {len(result.successful)} tickets to {target_status}")
    
    # Exit with error code if any failures
    if result.failure_count > 0:
        raise typer.Exit(1)


def _check_blocking_dependencies(root: Path, ticket: Ticket) -> List[dict]:
    """Check if ticket has unresolved blocking dependencies."""
    if not ticket.blocked_by:
        return []
    
    blockers = []
    for blocker_id in ticket.blocked_by:
        blocker_ticket, _ = find_ticket(blocker_id, root)
        if blocker_ticket and blocker_ticket.status not in ["done", "archived"]:
            blockers.append({
                "id": blocker_ticket.id,
                "title": blocker_ticket.title,
                "status": blocker_ticket.status
            })
    
    return blockers


def _check_if_no_blockers(root: Path, ticket: Ticket) -> bool:
    """Check if ticket has no unresolved blocking dependencies."""
    return len(_check_blocking_dependencies(root, ticket)) == 0


def _check_if_complete(root: Path, ticket: Ticket) -> bool:
    """Check if ticket completion criteria are met.
    
    For now, this is a basic implementation that considers a ticket complete if:
    - It has story points and is fully estimated
    - It has an assignee (someone is responsible)
    - It's not a bug with status todo (bugs in todo are not ready for done)
    
    This can be extended in the future with more sophisticated completion criteria.
    """
    # Basic completion criteria
    if ticket.type == "bug" and ticket.status == "todo":
        return False
    
    # Check if ticket has assignee (someone is responsible)
    if not ticket.assignee:
        return False
    
    # If ticket has story points, consider it estimated and complete
    if ticket.story_points and ticket.story_points > 0:
        return True
    
    # For tasks without story points, they're considered complete if assigned
    return ticket.assignee is not None


def _check_if_allowed(root: Path, ticket: Ticket, target_status: str) -> bool:
    """Check if workflow transition is allowed."""
    if ticket.status == target_status:
        return True
    
    # Backlog transitions are always allowed
    if ticket.status == "backlog" or target_status == "backlog":
        return True
    
    board = get_board_configuration()
    return board.can_transition(ticket.status, target_status)


def _move_single_ticket_with_updates(ticket_id: str, target_status: str, position: Optional[int], root: Path, use_git_mv: bool,
                                    comment: Optional[str], assign: Optional[str], add_label: Optional[str], 
                                    priority: Optional[str], force_transition: bool = False) -> dict:
    """Move a single ticket and apply additional updates."""
    # First do the basic move
    result = _move_single_ticket(ticket_id, target_status, position, root, use_git_mv, force_transition)
    
    # If move was successful and we have updates, apply them
    if result["changed"] and (comment or assign or add_label or priority):
        # Find the ticket in its new location
        ticket, ticket_path = find_ticket(ticket_id, root)
        if ticket:
            # Apply updates
            if assign:
                # Handle "me" assignment
                if assign == "me":
                    config = load_config()
                    assign = config.get("user.email") or config.get("user.name")
                ticket.assignee = assign
            
            if priority:
                ticket.priority = priority
            
            if add_label and add_label not in (ticket.labels or []):
                if not ticket.labels:
                    ticket.labels = []
                ticket.labels.append(add_label)
            
            # Update timestamp
            ticket.updated_at = datetime.now(timezone.utc)
            
            # Save updated ticket
            ticket.save_to_json_file(str(ticket_path))
            
            # Add comment if provided
            if comment:
                from gira.models.comment import Comment
                comments_dir = root / ".gira" / "comments" / ticket_id
                comments_dir.mkdir(parents=True, exist_ok=True)
                
                config = load_config()
                comment_obj = Comment(
                    id=f"comment-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    ticket_id=ticket_id,
                    content=comment,
                    author=config.get("user.email") or config.get("user.name") or "Unknown",
                    created_at=datetime.now(timezone.utc)
                )
                
                comment_file = comments_dir / f"{comment_obj.id}.json"
                comment_obj.save_to_json_file(str(comment_file))
            
            # Update result with additional changes
            result["updates"] = {
                "assignee": assign if assign else None,
                "priority": priority if priority else None,
                "label_added": add_label if add_label else None,
                "comment_added": bool(comment)
            }
    
    return result


def _record_batch_operation(root: Path, batch_id: str, ticket_ids: List[str], target_status: str) -> None:
    """Record batch operation for tracking."""
    batch_dir = root / ".gira" / "batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    batch_file = batch_dir / f"{batch_id}.json"
    batch_data = {
        "id": batch_id,
        "timestamp": datetime.now().isoformat(),
        "operation": "move",
        "target_status": target_status,
        "tickets": ticket_ids
    }
    
    batch_file.write_text(json.dumps(batch_data, indent=2))


def _expand_ticket_pattern(root: Path, pattern: str) -> List[str]:
    """Expand ticket pattern to list of ticket IDs.
    
    Supports:
    - Wildcards: TEST-1* matches TEST-10, TEST-11, etc.
    - Ranges: TEST-1..10 matches TEST-1 through TEST-10
    - Single IDs: TEST-1 returns [TEST-1]
    - Number-only: 673 returns [GCM-673] (using project prefix)
    """
    from gira.constants import parse_ticket_id_pattern, get_project_prefix
    
    # Normalize the pattern to add prefix if needed
    try:
        prefix = get_project_prefix()
        pattern = parse_ticket_id_pattern(pattern, prefix)
    except ValueError:
        # If we can't get prefix, use pattern as-is
        pass
    
    tickets = []
    
    # Check for range pattern (e.g., TEST-1..10)
    if ".." in pattern:
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
            # No range, treat as literal
            if _ticket_exists(root, pattern):
                tickets.append(pattern)
    
    # Check for wildcard pattern
    elif "*" in pattern:
        # Convert wildcard to regex
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")
        
        # Get swimlane IDs dynamically
        swimlane_ids = _get_swimlane_ids(root)
        
        # Search all ticket locations including backlog
        locations = [f"board/{swimlane}" for swimlane in swimlane_ids] + ["archive/tickets", "backlog"]
        for location in locations:
            ticket_dir = root / ".gira" / location
            if ticket_dir.exists():
                # For backlog, also search hybrid subdirectories
                if location == "backlog":
                    for ticket_file in ticket_dir.rglob("*.json"):
                        ticket_id = ticket_file.stem
                        if regex.match(ticket_id):
                            tickets.append(ticket_id)
                else:
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
    
    # If nothing found, use defaults
    if not swimlane_ids:
        swimlane_ids = {"backlog", "todo", "in_progress", "review", "done"}
    
    return list(swimlane_ids)


def _ticket_exists(root: Path, ticket_id: str) -> bool:
    """Check if a ticket exists in any location."""
    # Get swimlane IDs dynamically
    swimlane_ids = _get_swimlane_ids(root)
    
    locations = [root / ".gira" / "board" / swimlane / f"{ticket_id}.json" for swimlane in swimlane_ids]
    locations.append(root / ".gira" / "archive" / "tickets" / f"{ticket_id}.json")
    
    # Also check backlog location (both flat and hybrid storage)
    backlog_locations = [
        root / ".gira" / "backlog" / f"{ticket_id}.json",  # Flat storage
    ]
    
    # Check hybrid storage paths (GCM-750 would be in backlog/GC/M-/GCM-750.json)
    from gira.utils.hybrid_storage import get_ticket_storage_path
    try:
        hybrid_path = get_ticket_storage_path(ticket_id, "backlog", root)
        backlog_locations.append(hybrid_path)
    except Exception:
        # If hybrid path calculation fails, just skip it
        pass
    
    locations.extend(backlog_locations)
    
    return any(path.exists() for path in locations)


def _find_tickets_by_filter(root: Path, from_status: Optional[str], assignee: Optional[str], 
                           epic_id: Optional[str], sprint_id: Optional[str]) -> List[str]:
    """Find tickets matching filter criteria."""
    matching_tickets = []
    
    # Get swimlane IDs dynamically
    swimlane_ids = _get_swimlane_ids(root)
    
    # Determine locations to search
    locations = []
    if from_status:
        # Only search in the specified status
        if from_status == "archived":
            locations.append("archive/tickets")
        elif from_status == "backlog":
            locations.append("backlog")
        else:
            locations.append(f"board/{from_status}")
    else:
        # Search all locations including backlog
        locations = [f"board/{swimlane}" for swimlane in swimlane_ids] + ["backlog"]
    
    # Handle special assignee value "me"
    if assignee == "me":
        config = load_config()
        assignee = config.get("user.email") or config.get("user.name")
    
    # Handle special sprint value "current"
    if sprint_id == "current":
        # Find the current active sprint
        sprints_dir = root / ".gira" / "sprints"
        if sprints_dir.exists():
            from gira.models.sprint import Sprint
            for sprint_file in sprints_dir.glob("*.json"):
                try:
                    sprint = Sprint.from_json_file(str(sprint_file))
                    if sprint.status == "active":
                        sprint_id = sprint.id
                        break
                except Exception:
                    continue
    
    for location in locations:
        ticket_dir = root / ".gira" / location
        if ticket_dir.exists():
            # For backlog, search recursively to handle hybrid storage
            if location == "backlog":
                for ticket_file in ticket_dir.rglob("*.json"):
                    try:
                        ticket = Ticket.from_json_file(str(ticket_file))
                        
                        # Check assignee filter
                        if assignee and ticket.assignee != assignee:
                            continue
                        
                        # Check epic filter
                        if epic_id and ticket.epic_id != epic_id:
                            continue
                        
                        # Check sprint filter
                        if sprint_id:
                            # Check if ticket is in the sprint
                            sprint_file = root / ".gira" / "sprints" / f"{sprint_id}.json"
                            if sprint_file.exists():
                                from gira.models.sprint import Sprint
                                sprint = Sprint.from_json_file(str(sprint_file))
                                if ticket.id not in sprint.tickets:
                                    continue
                            else:
                                continue
                        
                        matching_tickets.append(ticket.id)
                    
                    except Exception:
                        # Skip invalid ticket files
                        continue
            else:
                for ticket_file in ticket_dir.glob("*.json"):
                    try:
                        ticket = Ticket.from_json_file(str(ticket_file))
                        
                        # Check assignee filter
                        if assignee and ticket.assignee != assignee:
                            continue
                        
                        # Check epic filter
                        if epic_id and ticket.epic_id != epic_id:
                            continue
                        
                        # Check sprint filter
                        if sprint_id:
                            # Check if ticket is in the sprint
                            sprint_file = root / ".gira" / "sprints" / f"{sprint_id}.json"
                            if sprint_file.exists():
                                from gira.models.sprint import Sprint
                                sprint = Sprint.from_json_file(str(sprint_file))
                                if ticket.id not in sprint.tickets:
                                    continue
                            else:
                                continue
                        
                        matching_tickets.append(ticket.id)
                    
                    except Exception:
                        # Skip invalid ticket files
                        continue
    
    return matching_tickets


def _move_bulk_from_stdin(root: Path, target_status: str, position: Optional[int], output: str, quiet: bool, use_git_mv: bool,
                         force: bool, from_status: Optional[str], assignee: Optional[str], epic_id: Optional[str], sprint_id: Optional[str],
                         comment: Optional[str], assign: Optional[str], add_label: Optional[str], priority: Optional[str], 
                         check_deps: bool, batch_id: Optional[str], dry_run: bool,
                         if_no_blockers: bool = False, if_complete: bool = False, if_allowed: bool = False) -> None:
    """Move multiple tickets from stdin input (one ticket ID per line)."""
    stdin_reader = StdinReader()
    ticket_ids = stdin_reader.read_lines()
    
    if not ticket_ids:
        console.print("[yellow]Warning:[/yellow] No ticket IDs provided on stdin")
        return
    
    # Apply filters if provided
    if from_status or assignee or epic_id or sprint_id:
        # Get all tickets matching filters
        filter_matches = _find_tickets_by_filter(root, from_status, assignee, epic_id, sprint_id)
        # Only keep tickets that are in both stdin and filter results
        ticket_ids = [tid for tid in ticket_ids if tid in filter_matches]
        
        if not ticket_ids:
            console.print("[yellow]Warning:[/yellow] No tickets from stdin matched the filters")
            return
    
    # Dry run mode
    if dry_run:
        _show_dry_run_preview(root, ticket_ids, target_status, output)
        return
    
    # Use bulk move
    _move_bulk_tickets(root, ticket_ids, target_status, position, True, False, output, quiet, use_git_mv,
                      comment, assign, add_label, priority, check_deps, batch_id, True,
                      if_no_blockers, if_complete, if_allowed)


def _move_single_ticket(ticket_id: str, target_status: str, position: Optional[int], root: Path, use_git_mv: bool, force_transition: bool = False) -> dict:
    """Move a single ticket and return result data."""
    ticket, ticket_path = find_ticket(ticket_id, root)
    
    if not ticket:
        raise ValueError(f"Ticket {ticket_id} not found")
    
    original_status = ticket.status
    
    if ticket.status == target_status:
        return {"id": ticket.id, "original_status": original_status, "new_status": target_status, "changed": False}
    
    board = get_board_configuration()
    
    if not force_transition and ticket.status != "backlog" and target_status != "backlog" and not board.can_transition(ticket.status, target_status):
        allowed = board.transitions.get(ticket.status, [])
        from gira.utils.errors import WorkflowTransitionError
        raise WorkflowTransitionError(ticket.id, ticket.status, target_status, allowed)
    
    ticket.status = target_status
    
    if position is not None:
        target_dir = root / ".gira" / "board" / target_status
        tickets_in_target = []
        if target_dir.exists():
            for ticket_file in target_dir.glob("*.json"):
                try:
                    t = Ticket.from_json_file(str(ticket_file))
                    tickets_in_target.append(t)
                except Exception:
                    continue
        tickets_in_target.sort(key=lambda t: (t.order if hasattr(t, 'order') and t.order > 0 else float('inf'), t.id))
        if position == 1:
            ticket.order = 10
        elif position > len(tickets_in_target):
            last_order = max((t.order for t in tickets_in_target if hasattr(t, 'order') and t.order > 0), default=0)
            ticket.order = last_order + 10
        else:
            prev_order = tickets_in_target[position - 2].order if position - 2 >= 0 and hasattr(tickets_in_target[position - 2], 'order') else 0
            next_order = tickets_in_target[position - 1].order if position - 1 < len(tickets_in_target) and hasattr(tickets_in_target[position - 1], 'order') else prev_order + 20
            ticket.order = (prev_order + next_order) // 2
    else:
        if hasattr(ticket, 'order'):
            ticket.order = 0
    
    ticket.updated_at = datetime.now(timezone.utc)
    
    if use_git_mv:
        new_path = get_ticket_storage_path(ticket.id, target_status, root)
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if source file exists before attempting git mv
        if not ticket_path.exists():
            raise ValueError(f"Source ticket file not found: {ticket_path}")
        
        # Use git_move utility which handles auto-adding untracked files
        from gira.utils.git_ops import git_move
        success, error_msg = git_move(ticket_path, new_path, root, silent=True)  # Silent for bulk operations
        
        if success:
            # After git mv, save the updated ticket data
            ticket.save_to_json_file(str(new_path))
        else:
            # If git mv fails, fall back to regular move
            # In bulk operations, we silently fall back to avoid spam
            new_path = migrate_ticket_location(ticket, ticket_path, target_status, root, use_git=False)
            # Save ticket data after migration
            ticket.save_to_json_file(str(new_path))
    else:
        new_path = migrate_ticket_location(ticket, ticket_path, target_status, root, use_git=use_git_mv)
        # Save ticket data after migration
        ticket.save_to_json_file(str(new_path))
    
    invalidate_ticket_cache()
    
    # Execute ticket-moved hook
    execute_hook("ticket-moved", build_ticket_move_event_data(ticket, original_status, target_status), silent=True)
    
    # Execute webhook for ticket move
    from gira.utils.hooks import execute_webhook_for_ticket_moved
    execute_webhook_for_ticket_moved(ticket, original_status, target_status)
    
    return {"id": ticket.id, "original_status": original_status, "new_status": target_status, "changed": True}


def _should_use_git_mv(root: Path, git_flag: Optional[bool]) -> bool:
    """Determine if git mv should be used based on flags, config, and repo state.
    
    Priority order:
    1. Command-line flag (--git/--no-git)
    2. Environment variable (GIRA_AUTO_GIT_MV)
    3. Config file setting (git.auto_stage_moves)
    4. Auto-detection (one-time check if .gira is tracked)
    
    For AI agents: Set GIRA_AUTO_GIT_MV=true to always use git mv.
    """
    # 1. Command-line flag has highest priority
    if git_flag is not None:
        return git_flag
    
    # 2. Check environment variable (useful for AI agents)
    env_var = os.getenv("GIRA_AUTO_GIT_MV", "").lower()
    if env_var in ("true", "1", "yes", "on"):
        return True
    elif env_var in ("false", "0", "no", "off"):
        return False

    # 3. Check config file
    config = load_config()
    auto_stage = config.get("git", {}).get("auto_stage_moves")
    if auto_stage is not None:
        return auto_stage

    # 4. One-time auto-detection
    try:
        # Check if we're in a git repository first
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            cwd=root,
        )
        
        # Check if the .gira directory is tracked by git
        gira_dir = root / ".gira"
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(gira_dir)],
            capture_output=True,
            text=True,
            cwd=root,
        )
        is_tracked = result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repo or git not available
        is_tracked = False

    # Save the result to the config for next time
    if "git" not in config:
        config["git"] = {}
    config["git"]["auto_stage_moves"] = is_tracked
    
    try:
        save_config(config)
    except Exception:
        # If we can't save config, just continue
        pass

    return is_tracked
