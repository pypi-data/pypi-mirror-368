"""Standardized error handling utilities for Gira.

This module provides consistent error handling with support for JSON output
when the --format option is set to json.
"""

from typing import Any, Dict, Optional

import typer

from gira.utils.console import console
from gira.utils.error_codes import ErrorCode, is_json_errors_enabled
from gira.utils.error_codes import handle_error as handle_json_error
from gira.utils.output import OutputFormat


class GiraError(Exception):
    """Base exception for Gira errors with structured error information."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
        self.suggestions = suggestions or []


class TicketNotFoundError(GiraError):
    """Error when a ticket is not found."""

    def __init__(self, ticket_id: str):
        # Normalize ticket ID for display consistency
        from gira.constants import normalize_ticket_id, get_project_prefix
        try:
            prefix = get_project_prefix()
            normalized_id = normalize_ticket_id(ticket_id, prefix)
        except ValueError:
            # If we can't get prefix, just uppercase the ID
            normalized_id = ticket_id.upper()
            
        super().__init__(
            message=f"Ticket {normalized_id} not found",
            error_code="TICKET_NOT_FOUND",
            details={"ticket_id": normalized_id},
            suggestions=["Check if the ticket ID is correct", "Use 'gira ticket list' to see available tickets"]
        )


class EpicNotFoundError(GiraError):
    """Error when an epic is not found."""

    def __init__(self, epic_id: str):
        # Normalize epic ID for display consistency
        from gira.constants import normalize_epic_id
        try:
            normalized_id = normalize_epic_id(epic_id)
        except ValueError:
            # If normalization fails, just use the raw ID
            normalized_id = epic_id.upper()
            
        super().__init__(
            message=f"Epic {normalized_id} not found",
            error_code="EPIC_NOT_FOUND",
            details={"epic_id": normalized_id},
            suggestions=["Check if the epic ID is correct", "Use 'gira epic list' to see available epics"]
        )


class SprintNotFoundError(GiraError):
    """Error when a sprint is not found."""

    def __init__(self, sprint_id: str):
        # Sprint IDs follow SPRINT-YYYY-MM-DD format, so normalization is different
        # For now, just ensure consistent formatting (uppercase)
        normalized_id = sprint_id.upper()
        if not normalized_id.startswith('SPRINT-'):
            # If user provided just a date or partial ID, add SPRINT- prefix
            if normalized_id.count('-') >= 2:  # Looks like a date
                normalized_id = f"SPRINT-{normalized_id}"
            
        super().__init__(
            message=f"Sprint {normalized_id} not found",
            error_code="SPRINT_NOT_FOUND",
            details={"sprint_id": normalized_id},
            suggestions=["Check if the sprint ID is correct", "Use 'gira sprint list' to see available sprints"]
        )


class ValidationError(GiraError):
    """Error for validation failures."""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            suggestions=["Check the input format and try again"]
        )


class ProjectNotFoundError(GiraError):
    """Error when not in a Gira project."""

    def __init__(self):
        super().__init__(
            message="Not in a Gira project",
            error_code="PROJECT_NOT_FOUND",
            suggestions=[
                "Run 'gira init' to initialize a new project",
                "Navigate to a directory with an existing Gira project"
            ]
        )


class WorkflowTransitionError(GiraError):
    """Error when a workflow transition is not allowed."""

    def __init__(self, ticket_id: str, current_status: str, target_status: str, allowed_transitions: list):
        current_display = current_status.replace("_", " ").title()
        target_display = target_status.replace("_", " ").title()
        allowed_display = [s.replace("_", " ").title() for s in allowed_transitions]
        
        super().__init__(
            message=f"Cannot move ticket {ticket_id} from '{current_display}' to '{target_display}'",
            error_code="WORKFLOW_TRANSITION_ERROR",
            details={
                "ticket_id": ticket_id,
                "current_status": current_status,
                "target_status": target_status,
                "allowed_transitions": allowed_transitions
            },
            suggestions=[
                f"Allowed transitions from {current_display}: {', '.join(allowed_display)}",
                "Use --force-transition to bypass workflow rules",
                f"Run 'gira workflow show {ticket_id}' to see workflow details"
            ]
        )


class ConfigurationError(GiraError):
    """Error in configuration or settings."""

    def __init__(self, message: str, config_key: Optional[str] = None, config_file: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_file:
            details["config_file"] = config_file
            
        suggestions = ["Check your configuration settings"]
        if config_file:
            suggestions.append(f"Review the configuration file: {config_file}")
        if config_key:
            suggestions.append(f"Verify the value for key: {config_key}")
            
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            suggestions=suggestions
        )


class DependencyError(GiraError):
    """Error related to ticket dependencies."""

    def __init__(self, message: str, ticket_id: str, blocking_tickets: Optional[list] = None):
        details = {"ticket_id": ticket_id}
        if blocking_tickets:
            details["blocking_tickets"] = blocking_tickets
            
        suggestions = [
            "Resolve blocking tickets first",
            "Use 'gira ticket deps' to view dependencies",
            "Consider using --force to bypass dependency checks (if available)"
        ]
        
        super().__init__(
            message=message,
            error_code="DEPENDENCY_ERROR",
            details=details,
            suggestions=suggestions
        )


class InputError(GiraError):
    """Error for invalid user input."""

    def __init__(self, message: str, expected_format: Optional[str] = None, examples: Optional[list] = None):
        details = {}
        suggestions = []
        
        if expected_format:
            details["expected_format"] = expected_format
            suggestions.append(f"Expected format: {expected_format}")
            
        if examples:
            details["examples"] = examples
            suggestions.extend([f"Example: {example}" for example in examples])
            
        super().__init__(
            message=message,
            error_code="INPUT_ERROR",
            details=details,
            suggestions=suggestions
        )


class OperationCancelledError(GiraError):
    """Error when user cancels an operation."""

    def __init__(self, operation: str = "Operation"):
        super().__init__(
            message=f"{operation} cancelled by user",
            error_code="OPERATION_CANCELLED",
            suggestions=["Run the command again when ready"]
        )


def handle_error(
    error: Exception,
    output_format: OutputFormat = OutputFormat.TABLE,
    exit_code: int = 1
) -> None:
    """Handle an error with appropriate output format.
    
    Args:
        error: The exception to handle
        output_format: The requested output format
        exit_code: Exit code to use (default: 1)
    """
    # If --json-errors is enabled, use the new JSON error system
    if is_json_errors_enabled():
        if isinstance(error, GiraError):
            # Map GiraError to ErrorCode
            error_code = _map_error_code(error.error_code)
            handle_json_error(
                code=error_code,
                message=error.message,
                details=error.details,
                exit_code=exit_code
            )
        else:
            handle_json_error(
                code=ErrorCode.UNKNOWN_ERROR,
                message=str(error),
                exit_code=exit_code
            )
    elif output_format == OutputFormat.JSON:
        _output_json_error(error)
    else:
        _output_console_error(error)

    raise typer.Exit(exit_code)


def _map_error_code(error_code_str: str) -> ErrorCode:
    """Map string error code to ErrorCode enum."""
    # Direct mapping for common error codes
    mapping = {
        "TICKET_NOT_FOUND": ErrorCode.TICKET_NOT_FOUND,
        "EPIC_NOT_FOUND": ErrorCode.EPIC_NOT_FOUND,
        "SPRINT_NOT_FOUND": ErrorCode.SPRINT_NOT_FOUND,
        "VALIDATION_ERROR": ErrorCode.VALIDATION_ERROR,
        "PROJECT_NOT_FOUND": ErrorCode.NOT_IN_GIRA_PROJECT,
        "GENERAL_ERROR": ErrorCode.UNKNOWN_ERROR,
        "WORKFLOW_TRANSITION_ERROR": ErrorCode.VALIDATION_ERROR,  # Map to closest existing
        "CONFIGURATION_ERROR": ErrorCode.INVALID_CONFIG_VALUE,
        "DEPENDENCY_ERROR": ErrorCode.VALIDATION_ERROR,  # Map to closest existing
        "INPUT_ERROR": ErrorCode.VALIDATION_ERROR,  # Map to closest existing
        "OPERATION_CANCELLED": ErrorCode.UNKNOWN_ERROR,  # Map to general error
    }

    return mapping.get(error_code_str, ErrorCode.UNKNOWN_ERROR)


def _output_json_error(error: Exception) -> None:
    """Output error in JSON format."""
    if isinstance(error, GiraError):
        error_data = {
            "error": {
                "message": error.message,
                "code": error.error_code,
                "details": error.details,
                "suggestions": error.suggestions
            }
        }
    else:
        error_data = {
            "error": {
                "message": str(error),
                "code": "UNKNOWN_ERROR",
                "details": {},
                "suggestions": []
            }
        }

    console.print_json(data=error_data)


def _output_console_error(error: Exception) -> None:
    """Output error in console format with Rich styling."""
    if isinstance(error, GiraError):
        console.print(f"[red]Error:[/red] {error.message}")

        if error.details:
            console.print("[dim]Details:[/dim]")
            for key, value in error.details.items():
                console.print(f"  • {key}: {value}")

        if error.suggestions:
            console.print("[dim]Suggestions:[/dim]")
            for suggestion in error.suggestions:
                console.print(f"  • {suggestion}")
    else:
        console.print(f"[red]Error:[/red] {error}")


def require_ticket(
    ticket_id: str,
    ticket_data: Optional[Any] = None,
    output_format: OutputFormat = OutputFormat.TABLE
) -> None:
    """Require that a ticket exists, raising appropriate error if not.
    
    Args:
        ticket_id: The ticket ID to check
        ticket_data: The ticket data (None if not found)
        output_format: Output format for error handling
    """
    if ticket_data is None:
        handle_error(TicketNotFoundError(ticket_id), output_format)


def require_epic(
    epic_id: str,
    epic_data: Optional[Any] = None,
    output_format: OutputFormat = OutputFormat.TABLE
) -> None:
    """Require that an epic exists, raising appropriate error if not.
    
    Args:
        epic_id: The epic ID to check
        epic_data: The epic data (None if not found)
        output_format: Output format for error handling
    """
    if epic_data is None:
        handle_error(EpicNotFoundError(epic_id), output_format)


def require_sprint(
    sprint_id: str,
    sprint_data: Optional[Any] = None,
    output_format: OutputFormat = OutputFormat.TABLE
) -> None:
    """Require that a sprint exists, raising appropriate error if not.
    
    Args:
        sprint_id: The sprint ID to check
        sprint_data: The sprint data (None if not found) 
        output_format: Output format for error handling
    """
    if sprint_data is None:
        handle_error(SprintNotFoundError(sprint_id), output_format)


def require_project(
    project_root: Optional[Any] = None,
    output_format: OutputFormat = OutputFormat.TABLE
) -> None:
    """Require that we're in a Gira project, raising appropriate error if not.
    
    Args:
        project_root: The project root (None if not found)
        output_format: Output format for error handling
    """
    if project_root is None:
        handle_error(ProjectNotFoundError(), output_format)


def validate_status(
    status: str,
    valid_statuses: list,
    output_format: OutputFormat = OutputFormat.TABLE
) -> None:
    """Validate that a status is in the list of valid statuses.
    
    Args:
        status: The status to validate
        valid_statuses: List of valid status values
        output_format: Output format for error handling
    """
    if status not in valid_statuses:
        error = ValidationError(
            message=f"Invalid status '{status}'. Valid statuses are: {', '.join(valid_statuses)}",
            field="status",
            value=status
        )
        error.suggestions = [f"Use one of: {', '.join(valid_statuses)}"]
        handle_error(error, output_format)


def validate_date_format(
    date_str: str,
    field_name: str = "date",
    output_format: OutputFormat = OutputFormat.TABLE
) -> None:
    """Validate that a date string is in the correct format.
    
    Args:
        date_str: The date string to validate
        field_name: Name of the field for error reporting
        output_format: Output format for error handling
    """
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        error = ValidationError(
            message=f"Invalid {field_name} format. Use YYYY-MM-DD",
            field=field_name,
            value=date_str
        )
        error.suggestions = ["Use format YYYY-MM-DD (e.g., 2025-01-15)"]
        handle_error(error, output_format)


def validate_date_range(
    start_date: str,
    end_date: str,
    output_format: OutputFormat = OutputFormat.TABLE
) -> None:
    """Validate that end date is after start date.
    
    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        output_format: Output format for error handling
    """
    from datetime import datetime

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        if end <= start:
            error = ValidationError(
                message="End date must be after start date"
            )
            error.details = {"start_date": start_date, "end_date": end_date}
            error.suggestions = ["Make sure the end date comes after the start date"]
            handle_error(error, output_format)

    except ValueError:
        error = ValidationError(
            message="Invalid date format in date range"
        )
        error.details = {"start_date": start_date, "end_date": end_date}
        error.suggestions = ["Use format YYYY-MM-DD for both dates"]
        handle_error(error, output_format)
