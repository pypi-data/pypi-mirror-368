"""Standardized error codes and JSON error handling for Gira."""

import json
import sys
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Standardized error codes for Gira CLI."""

    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    MISSING_ARGUMENT = "MISSING_ARGUMENT"

    # Project errors
    NOT_IN_GIRA_PROJECT = "NOT_IN_GIRA_PROJECT"
    GIRA_PROJECT_EXISTS = "GIRA_PROJECT_EXISTS"
    INVALID_PROJECT_CONFIG = "INVALID_PROJECT_CONFIG"

    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"

    # Ticket errors
    TICKET_NOT_FOUND = "TICKET_NOT_FOUND"
    INVALID_TICKET_ID = "INVALID_TICKET_ID"
    INVALID_TICKET_STATUS = "INVALID_TICKET_STATUS"
    INVALID_TICKET_PRIORITY = "INVALID_TICKET_PRIORITY"
    INVALID_TICKET_TYPE = "INVALID_TICKET_TYPE"
    INVALID_TRANSITION = "INVALID_TRANSITION"

    # Epic errors
    EPIC_NOT_FOUND = "EPIC_NOT_FOUND"
    INVALID_EPIC_ID = "INVALID_EPIC_ID"
    INVALID_EPIC_STATUS = "INVALID_EPIC_STATUS"

    # Sprint errors
    SPRINT_NOT_FOUND = "SPRINT_NOT_FOUND"
    INVALID_SPRINT_ID = "INVALID_SPRINT_ID"
    INVALID_SPRINT_STATUS = "INVALID_SPRINT_STATUS"
    SPRINT_ALREADY_ACTIVE = "SPRINT_ALREADY_ACTIVE"

    # Team errors
    MEMBER_NOT_FOUND = "MEMBER_NOT_FOUND"
    MEMBER_ALREADY_EXISTS = "MEMBER_ALREADY_EXISTS"
    INVALID_EMAIL = "INVALID_EMAIL"

    # File/IO errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_READ_ERROR = "FILE_READ_ERROR"
    FILE_WRITE_ERROR = "FILE_WRITE_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_DATE = "INVALID_DATE"

    # Configuration errors
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND"
    INVALID_CONFIG_KEY = "INVALID_CONFIG_KEY"
    INVALID_CONFIG_VALUE = "INVALID_CONFIG_VALUE"

    # Archive errors
    ARCHIVE_ERROR = "ARCHIVE_ERROR"
    ALREADY_ARCHIVED = "ALREADY_ARCHIVED"
    NOT_ARCHIVED = "NOT_ARCHIVED"

    # JSONPath errors
    INVALID_JSONPATH = "INVALID_JSONPATH"
    JSONPATH_NO_MATCH = "JSONPATH_NO_MATCH"


class ErrorDetails(BaseModel):
    """Model for error details in JSON error responses."""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None


def format_json_error(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """Format an error as JSON string."""
    error = ErrorDetails(code=code, message=message, details=details)
    return json.dumps(error.model_dump(exclude_none=True), indent=2)


def print_json_error(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    exit_code: int = 1
) -> None:
    """Print an error in JSON format to stderr and exit."""
    error_json = format_json_error(code, message, details)
    print(error_json, file=sys.stderr)
    sys.exit(exit_code)


# Global flag to enable JSON error output
_json_errors_enabled = False


def enable_json_errors():
    """Enable JSON error output globally."""
    global _json_errors_enabled
    _json_errors_enabled = True


def disable_json_errors():
    """Disable JSON error output globally."""
    global _json_errors_enabled
    _json_errors_enabled = False


def is_json_errors_enabled() -> bool:
    """Check if JSON error output is enabled."""
    return _json_errors_enabled


def handle_error(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    exit_code: int = 1,
    console=None
) -> None:
    """Handle an error, outputting in JSON format if enabled, otherwise using console."""
    if is_json_errors_enabled():
        print_json_error(code, message, details, exit_code)
    else:
        if console:
            console.print(f"[red]Error:[/red] {message}")
            if details:
                for key, value in details.items():
                    console.print(f"  {key}: {value}", style="dim")
        else:
            print(f"Error: {message}", file=sys.stderr)
            if details:
                for key, value in details.items():
                    print(f"  {key}: {value}", file=sys.stderr)
        sys.exit(exit_code)
