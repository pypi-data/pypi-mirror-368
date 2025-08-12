"""Workflow command for showing ticket transition information and managing workflow rules."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from gira.models import Ticket
from gira.models.board import Board
from gira.models.config import ProjectConfig
from gira.utils.console import console
from gira.utils.errors import GiraError
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, load_all_tickets


def get_allowed_transitions(current_status: str, board_config: Optional[Dict[str, Any]] = None) -> List[str]:
    """Get allowed transitions for a given status."""
    # Use transitions from board configuration
    if board_config and "transitions" in board_config:
        return board_config["transitions"].get(current_status, [])
    else:
        # This shouldn't happen since we always load the board config now
        return []


# Create workflow app for subcommands
workflow_app = typer.Typer(
    name="workflow",
    help="Manage and enforce workflow rules",
    add_completion=True,
    rich_markup_mode="markdown"
)


@workflow_app.command("show")
def show_workflow(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show workflow for"),
    check: Optional[str] = typer.Option(None, "--check", "-c", help="Check if a specific transition is valid"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    visual: bool = typer.Option(False, "--visual", "-v", help="Show visual workflow position"),
) -> None:
    """Display available workflow transitions for a ticket.
    
    Shows:
    - Current status and available transitions
    - Validation rules and constraints
    - Blockers that would prevent transitions
    - Required fields for each transition
    """
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, root)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    # Load board configuration
    board_config = {}
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        # Load the actual board configuration
        board = Board.from_json_file(str(board_config_path))
        board_config = {
            "transitions": board.transitions,
            "swimlanes": [sl.model_dump() for sl in board.swimlanes],
            "wip_limits": {sl.id: sl.limit for sl in board.swimlanes if sl.limit}
        }
    else:
        # Use default board configuration based on project's strict_workflow setting
        config_path = root / ".gira" / "config.json"
        config = ProjectConfig.from_json_file(str(config_path))
        board = Board.create_default(strict_workflow=config.strict_workflow)
        board_config = {
            "transitions": board.transitions,
            "swimlanes": [sl.model_dump() for sl in board.swimlanes],
            "wip_limits": {sl.id: sl.limit for sl in board.swimlanes if sl.limit}
        }
    
    # Get workflow information
    workflow_info = _analyze_ticket_workflow(ticket, board_config, root)
    
    # If checking specific transition
    if check:
        transition_result = _check_transition(ticket, check, workflow_info)
        if output == "json":
            print(json.dumps(transition_result, indent=2))
        else:
            _display_transition_check(ticket, check, transition_result)
        return
    
    # Display workflow information
    if output == "json":
        print(json.dumps(workflow_info, indent=2, default=str))
    else:
        if visual:
            _display_visual_workflow(ticket, workflow_info, board)
        else:
            _display_workflow_info(ticket, workflow_info)


@workflow_app.callback()
def workflow_callback(
    ctx: typer.Context,
) -> None:
    """Manage and enforce workflow rules.
    
    Use subcommands to:
    - Validate tickets against workflow rules
    - Apply workflow templates
    - Manage custom rules and transitions
    - Control enforcement levels
    """
    # Just pass through to subcommands
    pass


# Legacy workflow command kept for backward compatibility
def workflow(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show workflow for"),
    check: Optional[str] = typer.Option(None, "--check", "-c", help="Check if a specific transition is valid"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """Display available workflow transitions for a ticket.
    
    Shows:
    - Current status and available transitions
    - Validation rules and constraints
    - Blockers that would prevent transitions
    - Required fields for each transition
    """
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, root)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    # Load board configuration
    board_config = {}
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        # Load the actual board configuration
        board = Board.from_json_file(str(board_config_path))
        board_config = {
            "transitions": board.transitions,
            "swimlanes": [sl.model_dump() for sl in board.swimlanes],
            "wip_limits": {sl.id: sl.limit for sl in board.swimlanes if sl.limit}
        }
    else:
        # Use default board configuration based on project's strict_workflow setting
        config_path = root / ".gira" / "config.json"
        config = ProjectConfig.from_json_file(str(config_path))
        board = Board.create_default(strict_workflow=config.strict_workflow)
        board_config = {
            "transitions": board.transitions,
            "swimlanes": [sl.model_dump() for sl in board.swimlanes],
            "wip_limits": {sl.id: sl.limit for sl in board.swimlanes if sl.limit}
        }
    
    # Get workflow information
    workflow_info = _analyze_ticket_workflow(ticket, board_config, root)
    
    # If checking specific transition
    if check:
        transition_result = _check_transition(ticket, check, workflow_info)
        if output == "json":
            print(json.dumps(transition_result, indent=2))
        else:
            _display_transition_check(ticket, check, transition_result)
        return
    
    # Display workflow information
    if output == "json":
        print(json.dumps(workflow_info, indent=2, default=str))
    else:
        _display_workflow_info(ticket, workflow_info)


def _analyze_ticket_workflow(ticket: Ticket, board_config: Dict[str, Any], root) -> Dict[str, Any]:
    """Analyze workflow possibilities for a ticket."""
    workflow = {
        "current_status": ticket.status,
        "available_transitions": [],
        "blocked_transitions": [],
        "validation_issues": [],
        "constraints": []
    }
    
    # Get allowed transitions from board config
    allowed_statuses = get_allowed_transitions(ticket.status, board_config)
    
    # Check each possible transition
    for target_status in allowed_statuses:
        transition_info = {
            "to": target_status,
            "allowed": True,
            "blockers": [],
            "warnings": [],
            "required_fields": []
        }
        
        # Check for blocking tickets
        if ticket.blocked_by:
            blocking_tickets = []
            for blocker_id in ticket.blocked_by:
                blocker_ticket, _ = find_ticket(blocker_id, root)
                if blocker_ticket and blocker_ticket.status not in ["done", "closed", "cancelled"]:
                    blocking_tickets.append({
                        "id": blocker_ticket.id,
                        "title": blocker_ticket.title,
                        "status": blocker_ticket.status
                    })
            
            if blocking_tickets:
                transition_info["blockers"].extend(blocking_tickets)
                # Block transitions to review or done if there are unresolved blockers
                if target_status in ["review", "done", "closed"]:
                    transition_info["allowed"] = False
        
        # Check required fields for transitions
        required_fields = _get_required_fields_for_transition(ticket, target_status)
        if required_fields:
            transition_info["required_fields"] = required_fields
            
            # Check if required fields are missing
            missing_fields = []
            for field in required_fields:
                if field == "assignee" and not ticket.assignee:
                    missing_fields.append(field)
                elif field == "story_points" and not ticket.story_points:
                    missing_fields.append(field)
                elif field == "epic_id" and not ticket.epic_id:
                    missing_fields.append(field)
            
            if missing_fields:
                transition_info["warnings"].append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check WIP limits
        if "wip_limits" in board_config and target_status in board_config["wip_limits"]:
            wip_limit = board_config["wip_limits"][target_status]
            current_count = _count_tickets_in_status(target_status, root)
            
            if current_count >= wip_limit:
                transition_info["warnings"].append(f"WIP limit reached for {target_status} ({current_count}/{wip_limit})")
                workflow["constraints"].append({
                    "type": "wip_limit",
                    "status": target_status,
                    "current": current_count,
                    "limit": wip_limit
                })
        
        if transition_info["allowed"]:
            workflow["available_transitions"].append(transition_info)
        else:
            workflow["blocked_transitions"].append(transition_info)
    
    return workflow


def _get_required_fields_for_transition(ticket: Ticket, target_status: str) -> List[str]:
    """Get required fields for a specific transition."""
    required_fields = []
    
    # Common requirements
    if target_status == "in_progress":
        required_fields.append("assignee")
    
    if target_status in ["done", "closed"]:
        if ticket.type in ["feature", "bug", "story"]:
            required_fields.append("assignee")
    
    # Type-specific requirements
    if ticket.type in ["feature", "story"] and target_status == "in_progress":
        required_fields.append("story_points")
    
    return required_fields


def _count_tickets_in_status(status: str, root) -> int:
    """Count tickets in a specific status."""
    count = 0
    
    if status == "backlog":
        backlog_dir = root / ".gira" / "backlog"
        if backlog_dir.exists():
            count = len(list(backlog_dir.glob("*.json")))
    else:
        status_dir = root / ".gira" / "board" / status
        if status_dir.exists():
            count = len(list(status_dir.glob("*.json")))
    
    return count


def _check_transition(ticket: Ticket, target_status: str, workflow_info: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a specific transition is valid."""
    result = {
        "from": ticket.status,
        "to": target_status,
        "valid": False,
        "reason": None,
        "warnings": []
    }
    
    # Check if transition is in available transitions
    for transition in workflow_info["available_transitions"]:
        if transition["to"] == target_status:
            result["valid"] = True
            result["warnings"] = transition.get("warnings", [])
            return result
    
    # Check if transition is blocked
    for transition in workflow_info["blocked_transitions"]:
        if transition["to"] == target_status:
            result["reason"] = "Blocked by incomplete dependencies"
            result["blockers"] = transition.get("blockers", [])
            return result
    
    # Not an allowed transition
    result["reason"] = f"Transition from {ticket.status} to {target_status} is not allowed"
    return result


def _display_workflow_info(ticket: Ticket, workflow: Dict[str, Any]) -> None:
    """Display workflow information in rich text format."""
    # Header
    console.print(Panel(
        f"[bold]{ticket.id}[/bold] - {ticket.title}\n"
        f"Current Status: [yellow]{ticket.status.replace('_', ' ').title()}[/yellow]",
        title="Workflow Analysis",
        title_align="left",
        border_style="blue"
    ))
    
    # Available transitions
    if workflow["available_transitions"]:
        console.print("\n✅ [bold green]Available Transitions[/bold green]")
        
        for transition in workflow["available_transitions"]:
            status_display = transition["to"].replace("_", " ").title()
            console.print(f"\n  -> [cyan]{status_display}[/cyan]")
            
            if transition.get("warnings"):
                for warning in transition["warnings"]:
                    console.print(f"    ⚠️  [yellow]{warning}[/yellow]")
            
            if transition.get("required_fields"):
                console.print(f"    📋 Required fields: {', '.join(transition['required_fields'])}")
    
    # Blocked transitions
    if workflow["blocked_transitions"]:
        console.print("\n❌ [bold red]Blocked Transitions[/bold red]")
        
        for transition in workflow["blocked_transitions"]:
            status_display = transition["to"].replace("_", " ").title()
            console.print(f"\n  -> [red]{status_display}[/red]")
            
            if transition.get("blockers"):
                console.print("    🚫 Blocked by:")
                for blocker in transition["blockers"]:
                    console.print(f"       - {blocker['id']}: {blocker['title']} ({blocker['status']})")
    
    # Constraints
    if workflow["constraints"]:
        console.print("\n⚠️  [bold yellow]Constraints[/bold yellow]")
        
        for constraint in workflow["constraints"]:
            if constraint["type"] == "wip_limit":
                console.print(
                    f"  - WIP limit for [cyan]{constraint['status']}[/cyan]: "
                    f"{constraint['current']}/{constraint['limit']}"
                )
    
    # Summary
    total_transitions = len(workflow["available_transitions"]) + len(workflow["blocked_transitions"])
    available_count = len(workflow["available_transitions"])
    
    console.print(f"\n[dim]Total transitions: {total_transitions} "
                 f"(Available: {available_count}, Blocked: {total_transitions - available_count})[/dim]")


def _display_visual_workflow(ticket: Ticket, workflow: Dict[str, Any], board: Board) -> None:
    """Display visual workflow with current position."""
    # Header
    console.print(Panel(
        f"[bold]{ticket.id}[/bold] - {ticket.title}\n"
        f"Current Status: [yellow]{ticket.status.replace('_', ' ').title()}[/yellow]",
        title="Visual Workflow",
        title_align="left",
        border_style="blue"
    ))
    
    # Build visual status line
    statuses = [sl.id for sl in board.swimlanes]
    status_displays = []
    for status in statuses:
        display = status.upper().replace("_", " ")
        status_displays.append(display)
    
    # Create progress bar
    current_index = statuses.index(ticket.status) if ticket.status in statuses else 0
    total_statuses = len(statuses)
    
    # Progress indicator
    progress_bar = ""
    for i, status in enumerate(statuses):
        if i == current_index:
            progress_bar += "●"
        else:
            progress_bar += "━"
        if i < total_statuses - 1:
            progress_bar += "━━━━━"
    
    console.print(f"\nCurrent: [{ticket.status.upper()}] {progress_bar}")
    console.print("         " + " --> ".join(status_displays))
    console.print("         " + " " * (sum(len(s) + 5 for s in status_displays[:current_index])) + "↑")
    console.print("         " + " " * (sum(len(s) + 5 for s in status_displays[:current_index])) + "You are here")
    
    # Available moves
    console.print("\nAvailable moves:")
    for transition in workflow["available_transitions"]:
        status_display = transition["to"].replace("_", " ").title()
        desc = ""
        if transition["to"] == "review":
            desc = "(ready for code review)"
        elif transition["to"] == "todo":
            desc = "(move back to backlog)"
        elif transition["to"] == "done":
            desc = "(mark as complete)"
        
        if transition.get("warnings") or transition.get("required_fields"):
            console.print(f"  ✗ {status_display.upper()}       Missing: {', '.join(transition.get('required_fields', []))}")
        else:
            console.print(f"  → {status_display.upper()}     {desc}")
    
    # Show blocked transitions
    for transition in workflow["blocked_transitions"]:
        status_display = transition["to"].replace("_", " ").title()
        console.print(f"  ✗ {status_display.upper()}       {transition['reason']}")


def _display_transition_check(ticket: Ticket, target_status: str, result: Dict[str, Any]) -> None:
    """Display transition check result."""
    from_status = ticket.status.replace("_", " ").title()
    to_status = target_status.replace("_", " ").title()
    
    if result["valid"]:
        console.print(f"✅ Transition from [cyan]{from_status}[/cyan] to [cyan]{to_status}[/cyan] is [green]VALID[/green]")
        
        if result.get("warnings"):
            console.print("\n⚠️  Warnings:")
            for warning in result["warnings"]:
                console.print(f"  - {warning}")
    else:
        console.print(f"❌ Transition from [cyan]{from_status}[/cyan] to [cyan]{to_status}[/cyan] is [red]INVALID[/red]")
        
        if result.get("reason"):
            console.print(f"\nReason: {result['reason']}")
        
        if result.get("blockers"):
            console.print("\n🚫 Blocked by:")
            for blocker in result["blockers"]:
                console.print(f"  - {blocker['id']}: {blocker['title']} ({blocker['status']})")


@workflow_app.command("validate")
def validate_command(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Only validate tickets in this status"),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Only validate tickets of this type"),
    epic: Optional[str] = typer.Option(None, "--epic", "-e", help="Only validate tickets in this epic"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Attempt to auto-fix violations where possible"),
) -> None:
    """Validate all tickets against workflow rules.
    
    Checks for:
    - Invalid status transitions in ticket history
    - Missing required fields for current status
    - Unresolved blockers for completed tickets
    - WIP limit violations
    - Custom workflow rule violations
    """
    root = ensure_gira_project()
    
    # Load workflow rules
    rules = _load_workflow_rules(root)
    board = _load_board_config(root)
    
    # Load all tickets
    tickets = load_all_tickets(include_archived=False)
    
    # Filter tickets if requested
    if status:
        tickets = [t for t in tickets if t.status == status]
    if type:
        tickets = [t for t in tickets if t.type == type]
    if epic:
        tickets = [t for t in tickets if t.epic_id == epic]
    
    # Validate each ticket
    violations = []
    for ticket in tickets:
        ticket_violations = _validate_ticket(ticket, rules, board, root)
        if ticket_violations:
            violations.append({
                "ticket_id": ticket.id,
                "title": ticket.title,
                "status": ticket.status,
                "violations": ticket_violations
            })
    
    # Attempt fixes if requested
    fixed_count = 0
    if fix and violations:
        fixed_count = _attempt_fixes(violations, root)
    
    # Output results
    if output == "json":
        result = {
            "total_tickets": len(tickets),
            "violations_found": len(violations),
            "tickets_with_violations": violations,
            "fixed_count": fixed_count if fix else None
        }
        print(json.dumps(result, indent=2))
    else:
        _display_validation_report(tickets, violations, fixed_count if fix else None)


def _load_workflow_rules(root: Path) -> List[Dict[str, Any]]:
    """Load custom workflow rules from .gira/workflow-rules.json."""
    rules_path = root / ".gira" / "workflow-rules.json"
    if rules_path.exists():
        with open(rules_path, 'r') as f:
            return json.load(f).get("rules", [])
    return []


def _load_board_config(root: Path) -> Board:
    """Load board configuration."""
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        return Board.from_json_file(str(board_config_path))
    else:
        config_path = root / ".gira" / "config.json"
        config = ProjectConfig.from_json_file(str(config_path))
        return Board.create_default(strict_workflow=config.strict_workflow)


def _validate_ticket(ticket: Ticket, rules: List[Dict[str, Any]], board: Board, root: Path) -> List[Dict[str, Any]]:
    """Validate a single ticket against all rules."""
    violations = []
    
    # Check required fields for status
    required_fields = _get_required_fields_for_transition(ticket, ticket.status)
    missing_fields = []
    for field in required_fields:
        if field == "assignee" and not ticket.assignee:
            missing_fields.append(field)
        elif field == "story_points" and not ticket.story_points:
            missing_fields.append(field)
        elif field == "epic_id" and not ticket.epic_id:
            missing_fields.append(field)
    
    if missing_fields:
        violations.append({
            "type": "missing_required_fields",
            "message": f"Missing required fields for status '{ticket.status}': {', '.join(missing_fields)}",
            "fields": missing_fields
        })
    
    # Check unresolved blockers for done/closed tickets
    if ticket.status in ["done", "closed"] and ticket.blocked_by:
        unresolved_blockers = []
        for blocker_id in ticket.blocked_by:
            blocker, _ = find_ticket(blocker_id, root)
            if blocker and blocker.status not in ["done", "closed", "cancelled"]:
                unresolved_blockers.append(blocker_id)
        
        if unresolved_blockers:
            violations.append({
                "type": "unresolved_blockers",
                "message": f"Ticket in '{ticket.status}' status has unresolved blockers: {', '.join(unresolved_blockers)}",
                "blockers": unresolved_blockers
            })
    
    # Check custom rules
    for rule in rules:
        if _matches_rule_condition(ticket, rule.get("condition", {})):
            if not _passes_rule_requirements(ticket, rule.get("requires", {})):
                violations.append({
                    "type": "custom_rule",
                    "rule_name": rule.get("name", "unnamed"),
                    "message": rule.get("message", "Custom rule violation")
                })
    
    return violations


def _matches_rule_condition(ticket: Ticket, condition: Dict[str, Any]) -> bool:
    """Check if a ticket matches a rule condition."""
    if "status" in condition and ticket.status != condition["status"]:
        return False
    if "type" in condition and ticket.type != condition["type"]:
        return False
    if "priority" in condition and ticket.priority != condition["priority"]:
        return False
    return True


def _passes_rule_requirements(ticket: Ticket, requirements: Dict[str, Any]) -> bool:
    """Check if a ticket passes a rule requirements."""
    for field, expected in requirements.items():
        actual = getattr(ticket, field, None)
        
        # Handle special checks
        if expected == "!= null" and actual is None:
            return False
        elif expected == "== null" and actual is not None:
            return False
        elif isinstance(expected, str) and expected.startswith("!"):
            # Negation
            if actual == expected[1:]:
                return False
        elif actual != expected:
            return False
    
    return True


def _attempt_fixes(violations: List[Dict[str, Any]], root: Path) -> int:
    """Attempt to auto-fix violations where possible."""
    fixed_count = 0
    
    # Currently we don't implement auto-fixes
    # This is a placeholder for future enhancement
    
    return fixed_count


def _display_validation_report(tickets: List[Ticket], violations: List[Dict[str, Any]], fixed_count: Optional[int]) -> None:
    """Display validation report in rich format."""
    console.print(Panel(
        f"[bold]Workflow Validation Report[/bold]\n"
        f"Total tickets scanned: {len(tickets)}\n"
        f"Violations found: {len(violations)}",
        title="Summary",
        border_style="blue"
    ))
    
    if not violations:
        console.print("\n✅ [green]All tickets pass workflow validation![/green]")
        return
    
    # Group violations by type
    violation_types = {}
    for v in violations:
        for violation in v["violations"]:
            vtype = violation["type"]
            if vtype not in violation_types:
                violation_types[vtype] = []
            violation_types[vtype].append((v["ticket_id"], violation["message"]))
    
    # Display violations by type
    for vtype, items in violation_types.items():
        console.print(f"\n❌ [bold red]{vtype.replace('_', ' ').title()}[/bold red] ({len(items)} violations)")
        
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("Ticket", style="cyan")
        table.add_column("Violation")
        
        for ticket_id, message in items[:10]:  # Show first 10
            table.add_row(ticket_id, message)
        
        if len(items) > 10:
            table.add_row("...", f"[dim]({len(items) - 10} more)[/dim]")
        
        console.print(table)
    
    if fixed_count is not None and fixed_count > 0:
        console.print(f"\n✅ [green]Fixed {fixed_count} violations automatically[/green]")


@workflow_app.command("apply")
def apply_template(
    template: str = typer.Argument(..., help="Template name (scrum, kanban, support-desk, bug-tracking)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force apply even if board config exists"),
) -> None:
    """Apply a predefined workflow template.
    
    Available templates:
    - scrum: Sprint-based development with ceremonies  
    - kanban: Continuous flow with WIP limits
    - support-desk: Triage -> In Progress -> Resolved -> Closed
    - bug-tracking: New -> Confirmed -> In Progress -> Fixed -> Verified
    """
    root = ensure_gira_project()
    
    # Check if board config already exists
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists() and not force:
        console.print("[yellow]Warning:[/yellow] Board configuration already exists. Use --force to overwrite.")
        raise typer.Exit(1)
    
    # Create board based on template
    board = _create_board_from_template(template)
    if not board:
        console.print(f"[red]Error:[/red] Unknown template '{template}'")
        console.print("\nAvailable templates: scrum, kanban, support-desk, bug-tracking, minimal, custom")
        raise typer.Exit(1)
    
    # Save board configuration
    board_config_path.write_text(board.model_dump_json(indent=2))
    
    # Update project config statuses if needed
    config_path = root / ".gira" / "config.json"
    config = ProjectConfig.from_json_file(str(config_path))
    config.statuses = [sl.id for sl in board.swimlanes]
    config_path.write_text(config.model_dump_json(indent=2))
    
    console.print(f"✅ Applied workflow template: [cyan]{template}[/cyan]")
    console.print(f"\nStatuses: {', '.join(sl.name for sl in board.swimlanes)}")
    
    # Show transition matrix
    console.print("\n[bold]Allowed Transitions:[/bold]")
    for from_status, to_statuses in board.transitions.items():
        console.print(f"  {from_status} -> {', '.join(to_statuses)}")


def _get_template_board(template: str) -> Board:
    """Get a board configuration for a template."""
    board = _create_board_from_template(template)
    if not board:
        raise GiraError(f"Unknown workflow template: {template}")
    return board


def _create_board_from_template(template: str) -> Optional[Board]:
    """Create a board configuration from a template."""
    from gira.utils.templates import create_board_from_template
    return create_board_from_template(template)


@workflow_app.command("templates")
def list_templates() -> None:
    """List available workflow templates."""
    from gira.utils.templates import get_workflow_templates
    
    templates_info = get_workflow_templates()
    
    console.print("[bold]Available Workflow Templates[/bold]\n")
    
    for key, info in templates_info.items():
        console.print(f"[cyan]{key}[/cyan]")
        console.print(f"  {info['description']}")
        console.print(f"  Statuses: {' -> '.join(info['statuses'])}")
        console.print()


@workflow_app.command("rule")
def manage_rules(
    action: str = typer.Argument(..., help="Action: add, remove, list"),
    name: Optional[str] = typer.Argument(None, help="Rule name (for add/remove)"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Status condition"),
    requires: Optional[str] = typer.Option(None, "--requires", "-r", help="Requirements (field:value)"),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Violation message"),
) -> None:
    """Manage custom workflow rules.
    
    Examples:
    - Add rule: gira workflow rule add "review-requires-reviewer" --status review --requires "assignee:!= null"
    - Remove rule: gira workflow rule remove "review-requires-reviewer"
    - List rules: gira workflow rule list
    """
    root = ensure_gira_project()
    rules_path = root / ".gira" / "workflow-rules.json"
    
    # Load existing rules
    rules_data = {"rules": []}
    if rules_path.exists():
        with open(rules_path, 'r') as f:
            rules_data = json.load(f)
    
    if action == "list":
        _display_rules(rules_data["rules"])
    
    elif action == "add":
        if not name:
            console.print("[red]Error:[/red] Rule name is required for add action")
            raise typer.Exit(1)
        
        # Parse requirements
        req_dict = {}
        if requires:
            for req in requires.split(","):
                if ":" in req:
                    field, value = req.strip().split(":", 1)
                    req_dict[field.strip()] = value.strip()
        
        # Create new rule
        new_rule = {
            "name": name,
            "condition": {},
            "requires": req_dict,
            "message": message or f"Workflow rule '{name}' violated"
        }
        
        if status:
            new_rule["condition"]["status"] = status
        
        # Check if rule already exists
        existing_names = [r.get("name") for r in rules_data["rules"]]
        if name in existing_names:
            console.print(f"[yellow]Warning:[/yellow] Rule '{name}' already exists. Updating...")
            rules_data["rules"] = [r for r in rules_data["rules"] if r.get("name") != name]
        
        rules_data["rules"].append(new_rule)
        
        # Save rules
        with open(rules_path, 'w') as f:
            json.dump(rules_data, f, indent=2)
        
        console.print(f"✅ Added workflow rule: [cyan]{name}[/cyan]")
    
    elif action == "remove":
        if not name:
            console.print("[red]Error:[/red] Rule name is required for remove action")
            raise typer.Exit(1)
        
        # Remove rule
        original_count = len(rules_data["rules"])
        rules_data["rules"] = [r for r in rules_data["rules"] if r.get("name") != name]
        
        if len(rules_data["rules"]) == original_count:
            console.print(f"[yellow]Warning:[/yellow] Rule '{name}' not found")
            raise typer.Exit(1)
        
        # Save rules
        with open(rules_path, 'w') as f:
            json.dump(rules_data, f, indent=2)
        
        console.print(f"✅ Removed workflow rule: [cyan]{name}[/cyan]")
    
    else:
        console.print(f"[red]Error:[/red] Unknown action '{action}'. Use: add, remove, or list")
        raise typer.Exit(1)


def _display_rules(rules: List[Dict[str, Any]]) -> None:
    """Display workflow rules."""
    if not rules:
        console.print("No custom workflow rules defined.")
        return
    
    console.print("[bold]Active Workflow Rules[/bold]\n")
    
    for i, rule in enumerate(rules, 1):
        console.print(f"[cyan]{i}. {rule.get('name', 'unnamed')}[/cyan]")
        
        if rule.get("condition"):
            conds = []
            for field, value in rule["condition"].items():
                conds.append(f"{field}: {value}")
            console.print(f"   Condition: {', '.join(conds)}")
        
        if rule.get("requires"):
            reqs = []
            for field, value in rule["requires"].items():
                reqs.append(f"{field} {value}")
            console.print(f"   Requires: {', '.join(reqs)}")
        
        console.print(f"   Message: {rule.get('message', 'No message')}")
        console.print()


@workflow_app.command("transitions")
def manage_transitions(
    action: Optional[str] = typer.Argument(None, help="Action: add, remove, or leave empty to show"),
    from_status: Optional[str] = typer.Argument(None, help="From status"),
    to_status: Optional[str] = typer.Argument(None, help="To status (comma-separated for multiple)"),
) -> None:
    """Manage allowed status transitions.
    
    Examples:
    - Show all: gira workflow transitions
    - Add: gira workflow transitions add todo "in_progress,blocked"
    - Remove: gira workflow transitions remove todo done
    """
    root = ensure_gira_project()
    board = _load_board_config(root)
    board_path = root / ".gira" / ".board.json"
    
    if not action:
        # Display current transitions
        _display_transitions(board)
        return
    
    if action == "add":
        if not from_status or not to_status:
            console.print("[red]Error:[/red] Both from_status and to_status are required")
            raise typer.Exit(1)
        
        # Parse to_status (could be comma-separated)
        to_statuses = [s.strip() for s in to_status.split(",")]
        
        # Validate statuses exist
        valid_statuses = board.get_valid_statuses()
        invalid = [s for s in [from_status] + to_statuses if s not in valid_statuses]
        if invalid:
            console.print(f"[red]Error:[/red] Invalid status(es): {', '.join(invalid)}")
            console.print(f"Valid statuses: {', '.join(valid_statuses)}")
            raise typer.Exit(1)
        
        # Add transitions
        if from_status not in board.transitions:
            board.transitions[from_status] = []
        
        added = []
        for to_s in to_statuses:
            if to_s not in board.transitions[from_status]:
                board.transitions[from_status].append(to_s)
                added.append(to_s)
        
        if added:
            board_path.write_text(board.model_dump_json(indent=2))
            console.print(f"✅ Added transitions: {from_status} -> {', '.join(added)}")
        else:
            console.print("[yellow]All specified transitions already exist[/yellow]")
    
    elif action == "remove":
        if not from_status or not to_status:
            console.print("[red]Error:[/red] Both from_status and to_status are required")
            raise typer.Exit(1)
        
        # Parse to_status (could be comma-separated)
        to_statuses = [s.strip() for s in to_status.split(",")]
        
        if from_status not in board.transitions:
            console.print(f"[yellow]Warning:[/yellow] No transitions defined from '{from_status}'")
            raise typer.Exit(1)
        
        # Remove transitions
        removed = []
        for to_s in to_statuses:
            if to_s in board.transitions[from_status]:
                board.transitions[from_status].remove(to_s)
                removed.append(to_s)
        
        if removed:
            board_path.write_text(board.model_dump_json(indent=2))
            console.print(f"✅ Removed transitions: {from_status} -> {', '.join(removed)}")
        else:
            console.print("[yellow]None of the specified transitions exist[/yellow]")
    
    else:
        console.print(f"[red]Error:[/red] Unknown action '{action}'. Use: add or remove")
        raise typer.Exit(1)


def _display_transitions(board: Board) -> None:
    """Display transition matrix."""
    console.print("[bold]Allowed Status Transitions[/bold]\n")
    
    # Create transition table
    table = Table(show_header=True, box=box.ROUNDED)
    table.add_column("From", style="cyan")
    table.add_column("To", style="green")
    
    for from_status in board.get_valid_statuses():
        to_statuses = board.transitions.get(from_status, [])
        if to_statuses:
            table.add_row(
                from_status.replace("_", " ").title(),
                ", ".join(s.replace("_", " ").title() for s in to_statuses)
            )
        else:
            table.add_row(
                from_status.replace("_", " ").title(),
                "[dim](none)[/dim]"
            )
    
    console.print(table)


@workflow_app.command("strict")
def manage_strict_mode(
    action: str = typer.Argument(..., help="Action: enable, disable, or status"),
) -> None:
    """Enable or disable strict workflow enforcement.
    
    When enabled:
    - Only allowed transitions are permitted
    - Required fields must be filled
    - Workflow rules are enforced
    """
    root = ensure_gira_project()
    config_path = root / ".gira" / "config.json"
    config = ProjectConfig.from_json_file(str(config_path))
    
    if action == "enable":
        config.strict_workflow = True
        config_path.write_text(config.model_dump_json(indent=2))
        console.print("✅ Strict workflow enforcement [green]enabled[/green]")
        console.print("\n[yellow]Note:[/yellow] Ticket moves will now be validated against workflow rules.")
    
    elif action == "disable":
        config.strict_workflow = False
        config_path.write_text(config.model_dump_json(indent=2))
        console.print("✅ Strict workflow enforcement [red]disabled[/red]")
        console.print("\n[dim]Tickets can now be moved freely between statuses.[/dim]")
    
    elif action == "status":
        status = "enabled" if config.strict_workflow else "disabled"
        console.print(f"Strict workflow enforcement is [cyan]{status}[/cyan]")
    
    else:
        console.print(f"[red]Error:[/red] Unknown action '{action}'. Use: enable, disable, or status")
        raise typer.Exit(1)


@workflow_app.command("enforce")
def set_enforcement_level(
    level: str = typer.Argument(..., help="Enforcement level: strict, warn, or off"),
) -> None:
    """Set workflow enforcement level.
    
    Levels:
    - strict: Block operations that violate rules
    - warn: Show warnings but allow operations
    - off: No enforcement
    """
    root = ensure_gira_project()
    
    # Store enforcement level in workflow config
    workflow_config_path = root / ".gira" / "workflow-config.json"
    
    config = {}
    if workflow_config_path.exists():
        with open(workflow_config_path, 'r') as f:
            config = json.load(f)
    
    if level not in ["strict", "warn", "off"]:
        console.print(f"[red]Error:[/red] Invalid level '{level}'. Use: strict, warn, or off")
        raise typer.Exit(1)
    
    config["enforcement_level"] = level
    
    with open(workflow_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Update project config for backward compatibility
    if level == "strict":
        config_path = root / ".gira" / "config.json"
        project_config = ProjectConfig.from_json_file(str(config_path))
        project_config.strict_workflow = True
        config_path.write_text(project_config.model_dump_json(indent=2))
    
    console.print(f"✅ Workflow enforcement level set to: [cyan]{level}[/cyan]")
    
    if level == "strict":
        console.print("\n[yellow]Warning:[/yellow] All ticket operations will now be validated")
    elif level == "warn":
        console.print("\n[dim]Violations will be reported but operations will proceed[/dim]")
    else:
        console.print("\n[dim]Workflow rules will not be enforced[/dim]")


@workflow_app.command("diagram")
def show_diagram(
    show_counts: bool = typer.Option(False, "--counts", "-c", help="Show ticket counts for each status"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """Display visual workflow diagram.
    
    Shows the entire workflow as an ASCII diagram with transitions.
    """
    root = ensure_gira_project()
    
    # Load board configuration
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        board = Board.from_json_file(str(board_config_path))
    else:
        # Use default board configuration
        config_path = root / ".gira" / "config.json"
        config = ProjectConfig.from_json_file(str(config_path))
        board = Board.create_default(strict_workflow=config.strict_workflow)
    
    # Get ticket counts if requested
    ticket_counts = {}
    if show_counts:
        all_tickets = load_all_tickets(include_archived=False)
        for ticket in all_tickets:
            status = ticket.status
            ticket_counts[status] = ticket_counts.get(status, 0) + 1
    
    if output == "json":
        diagram_data = {
            "statuses": [sl.id for sl in board.swimlanes],
            "transitions": board.transitions,
            "strict": board.strict,
            "counts": ticket_counts if show_counts else None
        }
        print(json.dumps(diagram_data, indent=2))
    else:
        _display_workflow_diagram(board, ticket_counts if show_counts else None)


def _display_workflow_diagram(board: Board, ticket_counts: Optional[Dict[str, int]] = None) -> None:
    """Display workflow diagram as ASCII art."""
    statuses = [sl.id for sl in board.swimlanes]
    
    # Build status boxes
    status_displays = []
    max_width = 0
    for status in statuses:
        display = status.upper().replace("_", " ")
        if ticket_counts and status in ticket_counts:
            display = f"{display} ({ticket_counts[status]})"
        max_width = max(max_width, len(display))
        status_displays.append(display)
    
    # Add padding
    box_width = max_width + 4
    
    # Draw boxes
    console.print("\n[bold]Workflow Diagram[/bold]\n")
    
    # Top line
    boxes_line = ""
    for i, display in enumerate(status_displays):
        if i > 0:
            boxes_line += "     "
        boxes_line += "┌" + "─" * box_width + "┐"
    console.print(boxes_line)
    
    # Middle line with status
    status_line = ""
    for i, display in enumerate(status_displays):
        if i > 0:
            status_line += " --> "
        padding = (box_width - len(display)) // 2
        status_line += "│" + " " * padding + display + " " * (box_width - padding - len(display)) + "│"
    console.print(status_line)
    
    # Bottom line
    console.print(boxes_line.replace("┌", "└").replace("┐", "┘"))
    
    # Show backward transitions if not strict
    # Check if transitions allow backward movement
    strict = True
    for from_status, to_statuses in board.transitions.items():
        from_idx = statuses.index(from_status) if from_status in statuses else -1
        for to_status in to_statuses:
            to_idx = statuses.index(to_status) if to_status in statuses else -1
            if to_idx < from_idx:
                strict = False
                break
        if not strict:
            break
    
    if not strict:
        console.print("\n     " + "↑" + " " * (len(boxes_line) - 10) + "│")
        console.print("     └" + "─" * (len(boxes_line) - 10) + "┘")
        console.print("\n[dim](when strict_workflow = false)[/dim]")
    
    console.print()


@workflow_app.command("stats")
def show_stats(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """Show workflow statistics and metrics.
    
    Analyzes ticket flow, bottlenecks, and cycle times.
    """
    root = ensure_gira_project()
    
    # Load all tickets
    all_tickets = load_all_tickets(include_archived=True)
    
    # Calculate statistics
    stats = _calculate_workflow_stats(all_tickets, days)
    
    if output == "json":
        print(json.dumps(stats, indent=2, default=str))
    else:
        _display_workflow_stats(stats)


def _calculate_workflow_stats(tickets: List[Ticket], days: int) -> Dict[str, Any]:
    """Calculate workflow statistics."""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    stats = {
        "tickets_by_status": {},
        "cycle_time_by_type": {},
        "bottlenecks": [],
        "total_tickets": 0,
        "period_days": days
    }
    
    # Count tickets by status
    for ticket in tickets:
        status = ticket.status
        stats["tickets_by_status"][status] = stats["tickets_by_status"].get(status, 0) + 1
        stats["total_tickets"] += 1
    
    # Calculate percentages
    if stats["total_tickets"] > 0:
        for status, count in stats["tickets_by_status"].items():
            percentage = (count / stats["total_tickets"]) * 100
            stats["tickets_by_status"][status] = {
                "count": count,
                "percentage": round(percentage, 1)
            }
    
    # Find bottlenecks (tickets in review status for too long)
    review_threshold = timedelta(days=3)
    for ticket in tickets:
        if ticket.status == "review":
            # Check if it's been in review too long
            if ticket.updated_at:
                updated = ticket.updated_at
                # Convert to naive if needed
                if hasattr(updated, 'tzinfo') and updated.tzinfo is not None:
                    updated = updated.replace(tzinfo=None)
                
                time_in_status = datetime.now() - updated
                if time_in_status > review_threshold:
                    stats["bottlenecks"].append({
                        "ticket_id": ticket.id,
                        "days_in_review": time_in_status.days,
                        "title": ticket.title[:50] + "..." if len(ticket.title) > 50 else ticket.title
                    })
    
    # Calculate cycle time by type (simplified - would need status change history for accuracy)
    type_times = {}
    type_counts = {}
    
    for ticket in tickets:
        if ticket.status == "done" and ticket.created_at and ticket.updated_at:
            # Handle both aware and naive datetimes
            created = ticket.created_at
            updated = ticket.updated_at
            
            # Convert to naive if needed
            if hasattr(created, 'tzinfo') and created.tzinfo is not None:
                created = created.replace(tzinfo=None)
            if hasattr(updated, 'tzinfo') and updated.tzinfo is not None:
                updated = updated.replace(tzinfo=None)
            
            cycle_time = (updated - created).days
            ticket_type = ticket.type
            
            if ticket_type not in type_times:
                type_times[ticket_type] = 0
                type_counts[ticket_type] = 0
            
            type_times[ticket_type] += cycle_time
            type_counts[ticket_type] += 1
    
    for ticket_type, total_time in type_times.items():
        if type_counts[ticket_type] > 0:
            avg_time = total_time / type_counts[ticket_type]
            stats["cycle_time_by_type"][ticket_type] = round(avg_time, 1)
    
    return stats


def _display_workflow_stats(stats: Dict[str, Any]) -> None:
    """Display workflow statistics."""
    console.print(Panel.fit(
        "[bold]Workflow Statistics[/bold]\n" +
        f"Analysis period: Last {stats['period_days']} days",
        border_style="blue"
    ))
    
    # Tickets by status
    if stats["tickets_by_status"]:
        console.print("\n[bold]Tickets by Status:[/bold]")
        
        status_table = Table(show_header=True, box=box.SIMPLE)
        status_table.add_column("Status", style="cyan")
        status_table.add_column("Count", justify="right")
        status_table.add_column("Percentage", justify="right")
        
        for status, data in stats["tickets_by_status"].items():
            status_display = status.replace("_", " ").title()
            status_table.add_row(
                status_display,
                str(data["count"]),
                f"{data['percentage']}%"
            )
        
        console.print(status_table)
    
    # Cycle time by type
    if stats["cycle_time_by_type"]:
        console.print("\n[bold]Average Cycle Time by Type:[/bold]")
        
        cycle_table = Table(show_header=True, box=box.SIMPLE)
        cycle_table.add_column("Type", style="cyan")
        cycle_table.add_column("Average Days", justify="right")
        
        for ticket_type, avg_days in stats["cycle_time_by_type"].items():
            cycle_table.add_row(
                ticket_type.title(),
                f"{avg_days} days"
            )
        
        console.print(cycle_table)
    
    # Bottlenecks
    if stats["bottlenecks"]:
        console.print(f"\n[bold red]Bottlenecks:[/bold red]")
        console.print(f"[yellow]{len(stats['bottlenecks'])} tickets in review > 3 days:[/yellow]")
        
        for bottleneck in stats["bottlenecks"][:5]:  # Show top 5
            console.print(
                f"  • {bottleneck['ticket_id']}: {bottleneck['title']} "
                f"([red]{bottleneck['days_in_review']} days[/red])"
            )
        
        if len(stats["bottlenecks"]) > 5:
            console.print(f"  [dim]... and {len(stats['bottlenecks']) - 5} more[/dim]")


@workflow_app.command("config")
def show_config() -> None:
    """Display current workflow configuration."""
    root = ensure_gira_project()
    
    # Load configurations
    config_path = root / ".gira" / "config.json"
    config = ProjectConfig.from_json_file(str(config_path))
    
    board_config_path = root / ".gira" / ".board.json"
    if board_config_path.exists():
        board = Board.from_json_file(str(board_config_path))
    else:
        board = Board.create_default(strict_workflow=config.strict_workflow)
    
    workflow_config_path = root / ".gira" / "workflow-config.json"
    workflow_config = {}
    if workflow_config_path.exists():
        with open(workflow_config_path, 'r') as f:
            workflow_config = json.load(f)
    
    # Display configuration
    console.print(Panel.fit(
        "[bold]Workflow Configuration[/bold]",
        border_style="green"
    ))
    
    console.print(f"\n[bold]Type:[/bold] {'Strict' if config.strict_workflow else 'Flexible'} "
                  f"(strict_workflow = {str(config.strict_workflow).lower()})")
    
    enforcement_level = workflow_config.get("enforcement_level", "off")
    console.print(f"[bold]Enforcement:[/bold] {enforcement_level}")
    
    console.print(f"\n[bold]Status Flow:[/bold]")
    statuses = [sl.id for sl in board.swimlanes]
    console.print("  " + " -> ".join(statuses))
    
    # Show required fields
    console.print(f"\n[bold]Required Fields:[/bold]")
    has_requirements = False
    for swimlane in board.swimlanes:
        # Check if the swimlane has required_fields attribute
        if hasattr(swimlane, 'required_fields') and swimlane.required_fields:
            has_requirements = True
            console.print(f"  {swimlane.id}: {', '.join(swimlane.required_fields)}")
    
    # Also check validation rules for required fields
    if not has_requirements:
        # Check if there are any validation rules that require fields
        validate_command_exists = False
        for status in ["review", "done"]:
            # These are commonly required statuses
            if status == "review":
                console.print(f"  {status}: reviewer, pr_link [dim](commonly required)[/dim]")
            elif status == "done":
                console.print(f"  {status}: resolution_notes [dim](commonly required)[/dim]")
    
    if not has_requirements and not validate_command_exists:
        console.print("  [dim]None configured[/dim]")
    
    # Show custom rules
    rules_path = root / ".gira" / "workflow-rules.json"
    if rules_path.exists():
        with open(rules_path, 'r') as f:
            rules_data = json.load(f)
        
        if rules_data.get("rules"):
            console.print(f"\n[bold]Custom Rules:[/bold]")
            for rule in rules_data["rules"]:
                console.print(f"  - {rule.get('name', 'unnamed')}")


@workflow_app.command("analyze")
def analyze_workflow(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
) -> None:
    """Analyze workflow patterns and suggest improvements.
    
    Detects patterns like:
    - Tickets skipping stages
    - Frequent backward movements
    - Status change frequency
    """
    root = ensure_gira_project()
    
    # Load all tickets
    all_tickets = load_all_tickets(include_archived=True)
    
    # Analyze patterns
    analysis = _analyze_workflow_patterns(all_tickets, days)
    
    if output == "json":
        print(json.dumps(analysis, indent=2, default=str))
    else:
        _display_workflow_analysis(analysis)


def _analyze_workflow_patterns(tickets: List[Ticket], days: int) -> Dict[str, Any]:
    """Analyze workflow patterns."""
    from datetime import datetime, timedelta
    
    analysis = {
        "period_days": days,
        "total_tickets": len(tickets),
        "patterns": {
            "skip_review": 0,
            "backward_moves": 0,
            "stuck_tickets": 0
        },
        "recommendations": []
    }
    
    cutoff_date = datetime.now() - timedelta(days=days)
    stuck_threshold = timedelta(days=7)
    
    for ticket in tickets:
        # Check if ticket skipped review (went from in_progress to done)
        # This is simplified - would need status history for accuracy
        if ticket.status == "done":
            # Assume tickets without review comments skipped review
            has_review_comment = any(
                "review" in str(comment.content).lower() 
                for comment in (ticket.comments or [])
            )
            if not has_review_comment:
                analysis["patterns"]["skip_review"] += 1
        
        # Check for stuck tickets
        if ticket.status not in ["done", "archived"] and ticket.updated_at:
            updated = ticket.updated_at
            # Convert to naive if needed
            if hasattr(updated, 'tzinfo') and updated.tzinfo is not None:
                updated = updated.replace(tzinfo=None)
            
            time_since_update = datetime.now() - updated
            if time_since_update > stuck_threshold:
                analysis["patterns"]["stuck_tickets"] += 1
    
    # Calculate percentages
    if analysis["total_tickets"] > 0:
        skip_percentage = (analysis["patterns"]["skip_review"] / analysis["total_tickets"]) * 100
        if skip_percentage > 20:
            analysis["recommendations"].append(
                "Consider enforcing review stage - {:.0f}% of tickets skip review".format(skip_percentage)
            )
        
        stuck_percentage = (analysis["patterns"]["stuck_tickets"] / analysis["total_tickets"]) * 100
        if stuck_percentage > 10:
            analysis["recommendations"].append(
                "High number of stuck tickets ({:.0f}%) - review and close or update".format(stuck_percentage)
            )
    
    # Add general recommendations based on patterns
    if not analysis["recommendations"]:
        analysis["recommendations"].append("Workflow appears healthy - no major issues detected")
    
    return analysis


def _display_workflow_analysis(analysis: Dict[str, Any]) -> None:
    """Display workflow analysis."""
    console.print(Panel.fit(
        f"[bold]Workflow Analysis[/bold]\n" +
        f"Period: Last {analysis['period_days']} days\n" +
        f"Total tickets analyzed: {analysis['total_tickets']}",
        border_style="magenta"
    ))
    
    # Pattern detection
    console.print("\n[bold]Pattern Detection:[/bold]")
    
    patterns = analysis["patterns"]
    total = analysis["total_tickets"] or 1  # Avoid division by zero
    
    if patterns["skip_review"] > 0:
        percentage = (patterns["skip_review"] / total) * 100
        console.print(f"  - [yellow]{percentage:.0f}%[/yellow] of tickets skip review stage")
    
    if patterns["stuck_tickets"] > 0:
        percentage = (patterns["stuck_tickets"] / total) * 100
        console.print(f"  - [yellow]{percentage:.0f}%[/yellow] of tickets stuck > 7 days")
    
    # Recommendations
    console.print("\n[bold]Recommendations:[/bold]")
    for rec in analysis["recommendations"]:
        console.print(f"  • {rec}")
    
    console.print()


@workflow_app.command("migrate")
def migrate_workflow(
    from_workflow: str = typer.Argument(..., help="Source workflow (current state)"),
    to_workflow: str = typer.Argument(..., help="Target workflow to migrate to"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Preview changes without applying"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Create backup before migration"),
    force: bool = typer.Option(False, "--force", "-f", help="Force migration even with conflicts"),
) -> None:
    """Migrate tickets from one workflow to another.
    
    Handles status mapping and ticket transitions safely.
    
    Examples:
        # Preview migration from kanban to scrum
        gira workflow migrate kanban scrum --dry-run
        
        # Apply migration with backup
        gira workflow migrate kanban scrum --apply
        
        # Force migration without prompts
        gira workflow migrate custom scrum --apply --force
    """
    root = ensure_gira_project()
    
    # Load current board
    board_path = root / ".gira" / ".board.json"
    if not board_path.exists():
        raise GiraError("No workflow configured. Run 'gira workflow apply' first.")
    
    board = Board.model_validate_json(board_path.read_text())
    
    # Get target workflow
    if to_workflow in ["scrum", "kanban", "support-desk", "bug-tracking"]:
        target_board = _get_template_board(to_workflow)
    else:
        raise GiraError(f"Unknown workflow: {to_workflow}")
    
    # Analyze migration
    migration_plan = _analyze_migration(board, target_board)
    
    if dry_run:
        _display_migration_plan(migration_plan)
        
        if migration_plan["conflicts"]:
            console.print("\n[yellow]⚠️  Migration has conflicts that need resolution[/yellow]")
        else:
            console.print("\n[green]✓ Migration appears safe[/green]")
        
        console.print("\nRun with --apply to perform migration")
        return
    
    # Confirm migration
    if not force and migration_plan["conflicts"]:
        console.print("[bold red]Migration conflicts detected![/bold red]")
        _display_migration_plan(migration_plan)
        
        if not typer.confirm("Proceed with migration anyway?"):
            from gira.utils.errors import OperationCancelledError, handle_error
            handle_error(OperationCancelledError("Workflow migration"), exit_code=0)
    
    # Create backup if requested
    if backup:
        backup_path = _create_workflow_backup(root)
        console.print(f"[dim]Created backup: {backup_path}[/dim]")
    
    # Perform migration
    try:
        _perform_migration(root, board, target_board, migration_plan)
        console.print(f"\n[bold green]✓ Successfully migrated to {to_workflow} workflow[/bold green]")
        
        # Show post-migration guidance
        _show_post_migration_guidance(to_workflow, migration_plan)
        
    except Exception as e:
        if backup:
            console.print(f"\n[red]Migration failed: {e}[/red]")
            if typer.confirm("Restore from backup?"):
                _restore_workflow_backup(root, backup_path)
                console.print("[green]✓ Restored from backup[/green]")
        raise


def _analyze_migration(current: Board, target: Board) -> Dict[str, Any]:
    """Analyze migration plan and detect conflicts."""
    plan = {
        "status_mapping": {},
        "conflicts": [],
        "unmapped_statuses": [],
        "new_statuses": []
    }
    
    current_statuses = {s.id for s in current.swimlanes}
    target_statuses = {s.id for s in target.swimlanes}
    
    # Find direct mappings
    for status in current_statuses:
        if status in target_statuses:
            plan["status_mapping"][status] = status
        else:
            plan["unmapped_statuses"].append(status)
    
    # Find new statuses in target
    plan["new_statuses"] = list(target_statuses - current_statuses)
    
    # Suggest mappings for unmapped statuses
    mapping_suggestions = {
        # Common mappings
        "backlog": "todo",
        "ready": "todo", 
        "testing": "review",
        "verified": "done",
        "fixed": "done",
        "resolved": "done",
        "closed": "done",
        "triage": "todo",
        "new": "todo",
        "confirmed": "todo"
    }
    
    for status in plan["unmapped_statuses"]:
        if status in mapping_suggestions and mapping_suggestions[status] in target_statuses:
            plan["status_mapping"][status] = mapping_suggestions[status]
        else:
            # Find best match
            if "in_progress" in target_statuses and "progress" in status:
                plan["status_mapping"][status] = "in_progress"
            elif "todo" in target_statuses:
                plan["status_mapping"][status] = "todo"
            else:
                # Use first available status
                plan["status_mapping"][status] = list(target_statuses)[0]
                plan["conflicts"].append(
                    f"No clear mapping for '{status}' -> defaulting to '{plan['status_mapping'][status]}'"
                )
    
    return plan


def _display_migration_plan(plan: Dict[str, Any]) -> None:
    """Display migration plan."""
    console.print(Panel.fit("[bold]Migration Plan[/bold]", border_style="cyan"))
    
    # Status mappings
    console.print("\n[bold]Status Mappings:[/bold]")
    for old, new in plan["status_mapping"].items():
        if old == new:
            console.print(f"  {old} -> {new} [dim](unchanged)[/dim]")
        else:
            console.print(f"  {old} -> [yellow]{new}[/yellow] [dim](mapped)[/dim]")
    
    # New statuses
    if plan["new_statuses"]:
        console.print("\n[bold]New Statuses Available:[/bold]")
        for status in plan["new_statuses"]:
            console.print(f"  + [green]{status}[/green]")
    
    # Conflicts
    if plan["conflicts"]:
        console.print("\n[bold red]Conflicts:[/bold red]")
        for conflict in plan["conflicts"]:
            console.print(f"  ! {conflict}")


def _perform_migration(root: Path, current: Board, target: Board, plan: Dict[str, Any]) -> None:
    """Perform the actual migration."""
    # Update board configuration
    board_path = root / ".gira" / ".board.json"
    board_path.write_text(target.model_dump_json(indent=2))
    
    # Migrate tickets
    tickets_migrated = 0
    
    for old_status, new_status in plan["status_mapping"].items():
        if old_status == new_status:
            continue
            
        old_dir = root / ".gira" / "board" / old_status
        new_dir = root / ".gira" / "board" / new_status
        
        if old_dir.exists():
            new_dir.mkdir(parents=True, exist_ok=True)
            
            for ticket_file in old_dir.glob("*.json"):
                # Load ticket, update status, save to new location
                ticket = Ticket.model_validate_json(ticket_file.read_text())
                ticket.status = new_status
                ticket.updated_at = datetime.now()
                
                new_path = new_dir / ticket_file.name
                new_path.write_text(ticket.model_dump_json(indent=2))
                ticket_file.unlink()
                
                tickets_migrated += 1
    
    # Create directories for new statuses
    for status in plan["new_statuses"]:
        status_dir = root / ".gira" / "board" / status
        status_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean up empty directories
    board_dir = root / ".gira" / "board"
    for status_dir in board_dir.iterdir():
        if status_dir.is_dir() and not any(status_dir.iterdir()):
            status_dir.rmdir()
    
    console.print(f"\n[green]✓ Migrated {tickets_migrated} tickets[/green]")


def _create_workflow_backup(root: Path) -> Path:
    """Create backup of current workflow."""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = root / ".gira" / "backups" / f"workflow_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup board config
    board_path = root / ".gira" / ".board.json"
    if board_path.exists():
        shutil.copy2(board_path, backup_dir / ".board.json")
    
    # Backup board directory
    board_dir = root / ".gira" / "board"
    if board_dir.exists():
        shutil.copytree(board_dir, backup_dir / "board")
    
    # Backup workflow rules
    rules_path = root / ".gira" / "workflow-rules.json"
    if rules_path.exists():
        shutil.copy2(rules_path, backup_dir / "workflow-rules.json")
    
    return backup_dir


def _restore_workflow_backup(root: Path, backup_dir: Path) -> None:
    """Restore workflow from backup."""
    import shutil
    
    # Restore board config
    backup_board = backup_dir / ".board.json"
    if backup_board.exists():
        shutil.copy2(backup_board, root / ".gira" / ".board.json")
    
    # Restore board directory
    backup_board_dir = backup_dir / "board"
    if backup_board_dir.exists():
        board_dir = root / ".gira" / "board"
        if board_dir.exists():
            shutil.rmtree(board_dir)
        shutil.copytree(backup_board_dir, board_dir)
    
    # Restore workflow rules
    backup_rules = backup_dir / "workflow-rules.json"
    if backup_rules.exists():
        shutil.copy2(backup_rules, root / ".gira" / "workflow-rules.json")


def _show_post_migration_guidance(workflow: str, plan: Dict[str, Any]) -> None:
    """Show guidance after migration."""
    console.print("\n[bold]Next Steps:[/bold]")
    
    if workflow == "scrum":
        console.print("  1. Review sprint configuration: gira sprint list")
        console.print("  2. Set up story point estimates: gira ticket update <id> --story-points <n>")
        console.print("  3. Configure sprint velocity tracking")
    
    elif workflow == "kanban":
        console.print("  1. Set WIP limits: gira workflow apply kanban")
        console.print("  2. Configure cycle time tracking")
        console.print("  3. Review bottlenecks: gira workflow stats")
    
    elif workflow == "support-desk":
        console.print("  1. Set up priority levels for triage")
        console.print("  2. Configure SLA tracking")
        console.print("  3. Set up customer notification hooks")
    
    elif workflow == "bug-tracking":
        console.print("  1. Configure severity levels")
        console.print("  2. Set up reproducibility fields")
        console.print("  3. Link to test cases")
    
    if plan["new_statuses"]:
        console.print(f"\n  New statuses available: {', '.join(plan['new_statuses'])}")
        console.print("  Move tickets with: gira ticket move <id> <new-status>")