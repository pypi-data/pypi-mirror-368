"""Shared ticket creation and validation operations for CLI and MCP interfaces.

This module provides unified ticket creation logic to ensure both CLI and MCP
interfaces behave identically while respecting their different UI paradigms.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from gira.models import ProjectConfig, Ticket
from gira.models.ticket import TicketPriority, TicketType
from gira.utils.config import get_default_reporter
from gira.utils.epic_utils import add_ticket_to_epic
from gira.utils.hooks import execute_hook, build_ticket_event_data, execute_webhook_for_ticket_created
from gira.utils.ticket_creation import (
    determine_initial_status,
    parse_labels,
    resolve_assignee,
    validate_ticket_fields,
)
from gira.utils.ticket_utils import find_ticket, get_ticket_path, save_ticket, _would_create_parent_cycle

logger = logging.getLogger(__name__)


class TicketOperationResult:
    """Result of a ticket operation with warnings and errors."""
    
    def __init__(self):
        self.ticket: Optional[Ticket] = None
        self.ticket_path: Optional[Path] = None
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.success: bool = False
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
        logger.warning(f"Ticket operation warning: {message}")
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        logger.error(f"Ticket operation error: {message}")
    
    def is_valid(self) -> bool:
        """Check if the operation is valid (no errors)."""
        return len(self.errors) == 0


def resolve_and_validate_assignee(
    assignee: Optional[str],
    root: Path, 
    strict: bool = False,
    interface_type: str = "cli"
) -> Tuple[Optional[str], List[str]]:
    """Resolve and validate assignee with interface-aware warning handling.
    
    Args:
        assignee: Assignee email or name
        root: Project root path
        strict: Whether to enforce strict validation
        interface_type: "cli" or "mcp" for interface-specific behavior
        
    Returns:
        Tuple of (resolved_email, warnings)
    """
    if not assignee:
        return None, []
    
    try:
        resolved_assignee, warnings = resolve_assignee(assignee, root, strict)
        
        # For CLI, warnings will be displayed by caller
        # For MCP, warnings are returned for inclusion in OperationResult
        return resolved_assignee, warnings
        
    except ValueError as e:
        # Convert validation errors to consistent format
        error_msg = f"Assignee error: {str(e)}"
        raise ValueError(error_msg) from e


def handle_epic_associations(
    ticket_id: str,
    epic_id: Optional[str],
    root: Path,
    interface_type: str = "cli"
) -> List[str]:
    """Handle epic-ticket associations with bidirectional relationship sync.
    
    Args:
        ticket_id: ID of the ticket to associate
        epic_id: Epic ID to associate with (if any)
        root: Project root path
        interface_type: Interface type for error handling
        
    Returns:
        List of warnings
    """
    warnings = []
    
    if not epic_id:
        return warnings
    
    # Normalize epic ID
    normalized_epic = epic_id.upper()
    
    try:
        # Sync bidirectional epic-ticket relationship
        if not add_ticket_to_epic(ticket_id, normalized_epic, root):
            warning = f"Epic {normalized_epic} not found, but ticket created with epic_id"
            warnings.append(warning)
    except Exception as e:
        warning = f"Failed to sync epic relationship: {str(e)}"
        warnings.append(warning)
    
    return warnings


def manage_ticket_lifecycle(
    ticket: Ticket,
    initial_status: str,
    root: Path,
    interface_type: str = "cli"
) -> Tuple[Path, List[str]]:
    """Manage ticket lifecycle including file saving and hooks.
    
    Args:
        ticket: Ticket object to save
        initial_status: Initial status of the ticket
        root: Project root path
        interface_type: Interface type for behavior customization
        
    Returns:
        Tuple of (ticket_path, warnings)
    """
    warnings = []
    
    try:
        # Determine file path and save ticket
        ticket_path = get_ticket_path(ticket.id, initial_status, root)
        save_ticket(ticket, ticket_path)
        
        # Execute lifecycle hooks
        try:
            # Execute ticket-created hook
            execute_hook("ticket-created", build_ticket_event_data(ticket), silent=(interface_type == "mcp"))
            
            # Execute webhook for ticket creation
            execute_webhook_for_ticket_created(ticket)
            
        except Exception as e:
            warning = f"Hook execution failed: {str(e)}"
            warnings.append(warning)
        
        return ticket_path, warnings
        
    except Exception as e:
        raise ValueError(f"Failed to save ticket: {str(e)}") from e


def process_custom_fields(
    custom_fields: Optional[Dict[str, Any]],
    config: ProjectConfig,
    interface_type: str = "cli",
    interactive: bool = True
) -> Tuple[Dict[str, Any], List[str]]:
    """Process and validate custom fields with interface-aware handling.
    
    Args:
        custom_fields: Custom field values to process
        config: Project configuration
        interface_type: Interface type for behavior customization
        interactive: Whether to allow interactive field creation (CLI only)
        
    Returns:
        Tuple of (validated_fields, warnings)
    """
    warnings = []
    
    if not custom_fields:
        return {}, warnings
    
    # For now, return fields as-is with basic validation
    # TODO: Add comprehensive custom field validation when needed
    validated_fields = custom_fields.copy()
    
    return validated_fields, warnings


def create_ticket_with_validation(
    title: str,
    root: Path,
    description: str = "",
    priority: str = "medium", 
    ticket_type: str = "task",
    assignee: Optional[str] = None,
    epic: Optional[str] = None,
    parent: Optional[str] = None,
    labels: Optional[Union[str, List[str]]] = None,
    story_points: Optional[int] = None,
    status: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    interface_type: str = "cli",
    strict_assignee: bool = False,
    interactive_fields: bool = True
) -> TicketOperationResult:
    """Create a ticket with comprehensive validation and lifecycle management.
    
    This is the main orchestrator function that coordinates all ticket creation steps
    while maintaining interface-specific behaviors.
    
    Args:
        title: Ticket title (required)
        root: Project root path (required)
        description: Ticket description
        priority: Priority level (low, medium, high, critical)
        ticket_type: Ticket type (task, bug, feature, epic, subtask)
        assignee: Assignee email or name
        epic: Epic ID to associate with
        parent: Parent ticket ID for subtasks
        labels: Labels as string or list
        story_points: Story points estimate (0-100)
        status: Initial status (defaults to project default)
        custom_fields: Custom field values
        interface_type: "cli" or "mcp" for interface-specific behavior
        strict_assignee: Enforce strict assignee validation
        interactive_fields: Allow interactive custom field creation (CLI only)
        
    Returns:
        TicketOperationResult with ticket, warnings, and errors
    """
    result = TicketOperationResult()
    
    try:
        # Load project config and state
        config_path = root / ".gira" / "config.json"
        if not config_path.exists():
            result.add_error("Project configuration not found")
            return result
        
        config = ProjectConfig.from_json_file(str(config_path))
        
        state_path = root / ".gira" / ".state.json"
        if not state_path.exists():
            result.add_error("Project state not found")
            return result
        
        with open(state_path) as f:
            state = json.load(f)
        
        # Validate basic inputs
        if not title or not title.strip():
            result.add_error("Title cannot be empty")
            return result
        
        title = title.strip()
        if len(title) > 200:
            result.add_error("Title cannot exceed 200 characters")
            return result
        
        # Determine initial status
        initial_status = determine_initial_status(status, config, root)
        
        # Validate ticket fields
        validation_errors = validate_ticket_fields(ticket_type, priority, initial_status, story_points)
        if validation_errors:
            for error in validation_errors:
                result.add_error(error)
            return result
        
        # Generate ticket ID
        ticket_id = f"{config.ticket_id_prefix}-{state['next_ticket_number']}"
        
        # Get reporter
        reporter = get_default_reporter()
        
        # Parse labels
        label_list = parse_labels(",".join(labels) if isinstance(labels, list) else labels)
        
        # Resolve assignee with warnings
        resolved_assignee = None
        if assignee:
            try:
                resolved_assignee, assignee_warnings = resolve_and_validate_assignee(
                    assignee, root, strict_assignee, interface_type
                )
                for warning in assignee_warnings:
                    result.add_warning(warning)
            except ValueError as e:
                result.add_error(str(e))
                return result
        
        # Process custom fields
        try:
            validated_custom_fields, cf_warnings = process_custom_fields(
                custom_fields, config, interface_type, interactive_fields
            )
            for warning in cf_warnings:
                result.add_warning(warning)
        except Exception as e:
            result.add_error(f"Custom field validation failed: {str(e)}")
            return result
        
        # Validate parent relationship
        validated_parent = None
        if parent:
            # Normalize parent ID (use same logic as MCP for consistency)
            normalized_parent = parent.upper()
            
            # Check if the proposed parent exists
            parent_ticket, _ = find_ticket(normalized_parent, root)
            if not parent_ticket:
                result.add_error(f"Parent ticket {normalized_parent} not found")
                return result
            
            # Check for circular dependency
            if _would_create_parent_cycle(ticket_id, normalized_parent, root):
                result.add_error(
                    f"Cannot set {normalized_parent} as parent of {ticket_id}: "
                    f"this would create a circular parent-child dependency"
                )
                return result
            
            validated_parent = normalized_parent
        
        # Create ticket object
        ticket = Ticket(
            id=ticket_id,
            title=title,
            description=description,
            status=initial_status,
            priority=TicketPriority(priority.lower()),
            type=TicketType(ticket_type.lower()),
            reporter=reporter,
            assignee=resolved_assignee,
            labels=label_list,
            epic_id=epic,
            parent_id=validated_parent,
            story_points=story_points,
            custom_fields=validated_custom_fields,
        )
        
        # Handle ticket lifecycle (saving and hooks)
        try:
            ticket_path, lifecycle_warnings = manage_ticket_lifecycle(
                ticket, initial_status, root, interface_type
            )
            for warning in lifecycle_warnings:
                result.add_warning(warning)
            
            result.ticket = ticket
            result.ticket_path = ticket_path
            
        except Exception as e:
            result.add_error(str(e))
            return result
        
        # Handle epic associations
        if epic:
            epic_warnings = handle_epic_associations(ticket_id, epic, root, interface_type)
            for warning in epic_warnings:
                result.add_warning(warning)
        
        # Update state (increment ticket counter)
        state['next_ticket_number'] += 1
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        result.success = True
        return result
        
    except Exception as e:
        result.add_error(f"Unexpected error during ticket creation: {str(e)}")
        logger.exception("Unexpected error in create_ticket_with_validation")
        return result