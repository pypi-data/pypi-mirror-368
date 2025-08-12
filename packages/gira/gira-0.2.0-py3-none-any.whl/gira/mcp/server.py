"""Gira MCP Server implementation using FastMCP."""

import asyncio
import logging
import sys
from typing import Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from gira import __version__ as gira_version

# Import all MCP tools to register them with the global registry
from gira.mcp import ticket_tools  # noqa: F401
from gira.mcp import epic_tools  # noqa: F401
from gira.mcp import sprint_tools  # noqa: F401
from gira.mcp import board_tools  # noqa: F401
from gira.mcp import project_tools  # noqa: F401
from gira.mcp.config import get_config
from gira.mcp.validation import (
    coerce_array_parameter,
    coerce_integer_parameter,
    coerce_boolean_parameter,
    ParameterValidationError,
    get_helpful_error_message,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configure audit logging (will be setup after config is loaded)
audit_logger = logging.getLogger('gira.mcp.audit')


class ServerInfo(BaseModel):
    """Server information model."""
    name: str
    version: str
    gira_version: str
    working_directory: str
    dry_run: bool
    transport: str
    active_project: Optional[str]
    total_projects: int
    legacy_mode: bool


def create_mcp_server() -> FastMCP:
    """Create and configure the FastMCP server instance."""
    config = get_config()

    # Configure audit logging with working directory
    if not audit_logger.handlers:
        audit_log_path = config.working_directory / 'gira-mcp-audit.log'
        audit_handler = logging.FileHandler(str(audit_log_path))
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)

    # Configure logging level
    if config.enable_debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(getattr(logging, config.log_level.upper()))

    logger.info(f"Initializing Gira MCP Server v{config.version}")
    logger.info(f"Working directory: {config.working_directory}")
    logger.info(f"Dry run mode: {config.dry_run}")
    logger.info(f"Transport: {config.transport}")

    # Create FastMCP server
    mcp = FastMCP(
        name=config.name,
        version=config.version
    )

    # Add server info tool
    @mcp.tool()
    def get_server_info() -> ServerInfo:
        """Get information about the Gira MCP server."""
        # Determine if we're in legacy mode
        legacy_mode = not config.active_project and len(config.projects) == 0
        
        return ServerInfo(
            name=config.name,
            version=config.version,
            gira_version=gira_version,
            working_directory=str(config.working_directory),
            dry_run=config.dry_run,
            transport=config.transport,
            active_project=config.active_project,
            total_projects=len(config.projects),
            legacy_mode=legacy_mode
        )

    # Add health check tool
    @mcp.tool()
    def health_check() -> dict:
        """Perform a health check of the Gira MCP server."""
        try:
            # Basic checks
            working_dir_exists = config.working_directory.exists()
            working_dir_readable = config.working_directory.is_dir()

            status = "healthy" if working_dir_exists and working_dir_readable else "unhealthy"

            return {
                "status": status,
                "working_directory_exists": working_dir_exists,
                "working_directory_readable": working_dir_readable,
                "dry_run_enabled": config.dry_run,
                "confirmation_required": config.require_confirmation
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    # Register ticket management tools directly with FastMCP
    # FastMCP requires explicit function signatures, so we create specific wrappers

    @mcp.tool()
    def list_tickets(
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        priority: Optional[str] = None,
        type: Optional[str] = None,
        epic: Optional[str] = None,
        labels: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> dict:
        """List tickets with optional filtering."""
        try:
            # Validate array parameters (now coming as strings from Claude Desktop)
            validated_labels = None
            if labels is not None and labels.strip():
                validated_labels = coerce_array_parameter(labels, 'labels')
            
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.ticket_tools import list_tickets as list_tickets_impl
            result = list_tickets_impl(
                status=status,
                assignee=assignee,
                priority=priority,
                type=type,
                epic=epic,
                labels=validated_labels,
                limit=validated_limit,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in list_tickets: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "list_tickets"
            }

    @mcp.tool()
    def get_ticket(ticket_id: str) -> dict:
        """Get detailed information about a specific ticket."""
        try:
            from gira.mcp.ticket_tools import get_ticket as get_ticket_impl
            result = get_ticket_impl(ticket_id=ticket_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in get_ticket: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_ticket"
            }

    @mcp.tool()
    def create_ticket(
        title: str,
        description: str = "",
        priority: str = "medium",
        type: str = "task",
        assignee: Optional[str] = None,
        epic: Optional[str] = None,
        parent: Optional[str] = None,
        labels: Optional[str] = None,  # Accept as string, parse internally
        story_points: Optional[str] = None,  # Accept as string, parse internally
        status: Optional[str] = None,
        custom_fields: Optional[str] = None,  # Accept as string, parse internally
    ) -> dict:
        """Create a new ticket."""
        try:
            # Validate array parameters (now coming as strings from Claude Desktop)
            validated_labels = None
            if labels is not None and labels.strip():
                validated_labels = coerce_array_parameter(labels, 'labels')
            
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_story_points = None
            if story_points is not None and story_points.strip():
                validated_story_points = coerce_integer_parameter(story_points, 'story_points', min_value=0, max_value=100)
            
            # Validate custom_fields if provided
            validated_custom_fields = None
            if custom_fields is not None and custom_fields.strip():
                try:
                    import json
                    validated_custom_fields = json.loads(custom_fields)
                    if not isinstance(validated_custom_fields, dict):
                        raise ValueError("custom_fields must be a JSON object")
                except (json.JSONDecodeError, ValueError) as e:
                    return {
                        "success": False,
                        "error": f"Invalid custom_fields format: {e}. Expected JSON object like {{\"key\": \"value\"}}"
                    }
            
            from gira.mcp.ticket_tools import create_ticket as create_ticket_impl
            result = create_ticket_impl(
                title=title,
                description=description,
                priority=priority,
                type=type,
                assignee=assignee,
                epic=epic,
                parent=parent,
                labels=validated_labels,
                story_points=validated_story_points,
                status=status,
                custom_fields=validated_custom_fields,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in create_ticket: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "create_ticket"
            }

    # Add new ticket management tools from GCM-715
    
    # Update Operations
    @mcp.tool()
    def update_ticket(
        ticket_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        type: Optional[str] = None,
        assignee: Optional[str] = None,
        epic: Optional[str] = None,
        parent: Optional[str] = None,
        labels: Optional[str] = None,
        add_labels: Optional[str] = None,
        remove_labels: Optional[str] = None,
        story_points: Optional[str] = None,
        custom_fields: Optional[str] = None,
    ) -> dict:
        """Update an existing ticket's fields."""
        try:
            # Validate array parameters (now coming as strings from Claude Desktop)
            validated_labels = None
            if labels is not None and labels.strip():
                validated_labels = coerce_array_parameter(labels, 'labels')
            
            validated_add_labels = None
            if add_labels is not None and add_labels.strip():
                validated_add_labels = coerce_array_parameter(add_labels, 'add_labels')
            
            validated_remove_labels = None
            if remove_labels is not None and remove_labels.strip():
                validated_remove_labels = coerce_array_parameter(remove_labels, 'remove_labels')
            
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_story_points = None
            if story_points is not None and story_points.strip():
                validated_story_points = coerce_integer_parameter(story_points, 'story_points', min_value=0, max_value=100)
            
            # Validate custom_fields if provided
            validated_custom_fields = None
            if custom_fields is not None and custom_fields.strip():
                try:
                    import json
                    validated_custom_fields = json.loads(custom_fields)
                    if not isinstance(validated_custom_fields, dict):
                        raise ValueError("custom_fields must be a JSON object")
                except (json.JSONDecodeError, ValueError) as e:
                    return {
                        "success": False,
                        "error": f"Invalid custom_fields format: {e}. Expected JSON object like {{\"key\": \"value\"}}"
                    }
            
            from gira.mcp.ticket_tools import update_ticket as update_ticket_impl
            result = update_ticket_impl(
                ticket_id=ticket_id,
                title=title,
                description=description,
                priority=priority,
                type=type,
                assignee=assignee,
                epic=epic,
                parent=parent,
                labels=validated_labels,
                add_labels=validated_add_labels,
                remove_labels=validated_remove_labels,
                story_points=validated_story_points,
                custom_fields=validated_custom_fields,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in update_ticket: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "update_ticket"
            }

    @mcp.tool()
    def move_ticket(
        ticket_id: str,
        status: str,
        comment: Optional[str] = None,
        use_git: Optional[str] = None,
    ) -> dict:
        """Move a ticket to a different status/swimlane."""
        try:
            # Parse boolean parameter
            parsed_use_git = parse_optional_boolean(use_git) if use_git is not None else None
            
            from gira.mcp.ticket_tools import move_ticket as move_ticket_impl
            result = move_ticket_impl(
                ticket_id=ticket_id,
                status=status,
                comment=comment,
                use_git=parsed_use_git,
            )
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in move_ticket: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "move_ticket"
            }

    @mcp.tool()
    def assign_ticket(
        ticket_id: str,
        assignee: str,
    ) -> dict:
        """Assign a ticket to someone."""
        try:
            from gira.mcp.ticket_tools import assign_ticket as assign_ticket_impl
            result = assign_ticket_impl(
                ticket_id=ticket_id,
                assignee=assignee,
            )
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in assign_ticket: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "assign_ticket"
            }

    # Comment Operations
    @mcp.tool()
    def add_comment(
        ticket_id: str,
        content: str,
        mentions: Optional[str] = None,
    ) -> dict:
        """Add a comment to a ticket."""
        try:
            # Validate array parameters (now coming as strings from Claude Desktop)
            validated_mentions = None
            if mentions is not None and mentions.strip():
                validated_mentions = coerce_array_parameter(mentions, 'mentions')
            
            from gira.mcp.ticket_tools import add_comment as add_comment_impl
            result = add_comment_impl(
                ticket_id=ticket_id,
                content=content,
                mentions=validated_mentions,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in add_comment: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "add_comment"
            }

    @mcp.tool()
    def list_comments(
        ticket_id: str,
        limit: Optional[str] = None,
    ) -> dict:
        """List comments for a ticket."""
        try:
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.ticket_tools import list_comments as list_comments_impl
            result = list_comments_impl(
                ticket_id=ticket_id,
                limit=validated_limit,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in list_comments: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "list_comments"
            }

    # Advanced Queries
    @mcp.tool()
    def search_tickets(
        query: str,
        limit: Optional[str] = "20",
        include_archived: bool = False,
    ) -> dict:
        """Search tickets using full-text search."""
        try:
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.ticket_tools import search_tickets as search_tickets_impl
            result = search_tickets_impl(
                query=query,
                limit=validated_limit,
                include_archived=include_archived,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in search_tickets: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "search_tickets"
            }

    @mcp.tool()
    def filter_tickets(
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        priority: Optional[str] = None,
        type: Optional[str] = None,
        epic: Optional[str] = None,
        labels: Optional[str] = None,
        labels_all: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        updated_after: Optional[str] = None,
        updated_before: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> dict:
        """Advanced filtering of tickets with multiple criteria."""
        try:
            # Validate and coerce parameters
            validated_params = {}
            
            # Array parameters (now coming as strings from Claude Desktop)
            if status is not None and status.strip():
                validated_params['status'] = coerce_array_parameter(status, 'status')
            if assignee is not None and assignee.strip():
                validated_params['assignee'] = coerce_array_parameter(assignee, 'assignee')
            if priority is not None and priority.strip():
                validated_params['priority'] = coerce_array_parameter(priority, 'priority')
            if type is not None and type.strip():
                validated_params['type'] = coerce_array_parameter(type, 'type')
            if epic is not None and epic.strip():
                validated_params['epic'] = coerce_array_parameter(epic, 'epic')
            if labels is not None and labels.strip():
                validated_params['labels'] = coerce_array_parameter(labels, 'labels')
            if labels_all is not None and labels_all.strip():
                validated_params['labels_all'] = coerce_array_parameter(labels_all, 'labels_all')
            
            # String parameters (pass through)
            if created_after is not None:
                validated_params['created_after'] = created_after
            if created_before is not None:
                validated_params['created_before'] = created_before
            if updated_after is not None:
                validated_params['updated_after'] = updated_after
            if updated_before is not None:
                validated_params['updated_before'] = updated_before
            
            # Integer parameters (now coming as strings from Claude Desktop)
            if limit is not None and limit.strip():
                validated_params['limit'] = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.ticket_tools import filter_tickets as filter_tickets_impl
            result = filter_tickets_impl(**validated_params)
            return result.model_dump()
            
        except ParameterValidationError as e:
            error_msg = get_helpful_error_message(e)
            logger.warning(f"Parameter validation error in filter_tickets: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool": "filter_tickets",
                "validation_error": True
            }
        except Exception as e:
            logger.error(f"Error in filter_tickets: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "filter_tickets"
            }

    @mcp.tool()
    def get_board_state(
        include_counts: bool = True,
        include_tickets: bool = False,
    ) -> dict:
        """Get current board state visualization."""
        try:
            from gira.mcp.ticket_tools import get_board_state as get_board_state_impl
            result = get_board_state_impl(
                include_counts=include_counts,
                include_tickets=include_tickets,
            )
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in get_board_state: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_board_state"
            }

    # Bulk Operations
    @mcp.tool()
    def bulk_update(
        ticket_ids: List[str],
        title: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        add_labels: Optional[list] = None,
        remove_labels: Optional[list] = None,
        epic: Optional[str] = None,
    ) -> dict:
        """Update multiple tickets with the same changes."""
        try:
            # Validate and coerce parameters
            validated_params = {}
            
            # Required array parameter
            validated_params['ticket_ids'] = coerce_array_parameter(ticket_ids, 'ticket_ids', allow_empty=False)
            
            # Optional string parameters (pass through)
            if title is not None:
                validated_params['title'] = title
            if status is not None:
                validated_params['status'] = status
            if priority is not None:
                validated_params['priority'] = priority
            if assignee is not None:
                validated_params['assignee'] = assignee
            if epic is not None:
                validated_params['epic'] = epic
            
            # Optional array parameters
            if add_labels is not None:
                validated_params['add_labels'] = coerce_array_parameter(add_labels, 'add_labels')
            if remove_labels is not None:
                validated_params['remove_labels'] = coerce_array_parameter(remove_labels, 'remove_labels')
            
            from gira.mcp.ticket_tools import bulk_update as bulk_update_impl
            result = bulk_update_impl(**validated_params)
            return result.model_dump()
            
        except ParameterValidationError as e:
            error_msg = get_helpful_error_message(e)
            logger.warning(f"Parameter validation error in bulk_update: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool": "bulk_update",
                "validation_error": True
            }
        except Exception as e:
            logger.error(f"Error in bulk_update: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "bulk_update"
            }

    @mcp.tool()
    def archive_tickets(
        ticket_ids: Optional[str] = None,
        status: Optional[str] = None,
        older_than_days: Optional[str] = None,
        dry_run: Optional[str] = None,
        use_git: Optional[str] = None,
    ) -> dict:
        """Archive completed tickets."""
        try:
            # Validate and coerce parameters
            validated_params = {}
            
            # Array parameters
            if ticket_ids is not None and ticket_ids.strip():
                validated_params['ticket_ids'] = coerce_array_parameter(ticket_ids, 'ticket_ids', allow_empty=False)
            if status is not None and status.strip():
                validated_params['status'] = coerce_array_parameter(status, 'status')
            
            # Integer parameters
            if older_than_days is not None and older_than_days.strip():
                validated_params['older_than_days'] = coerce_integer_parameter(older_than_days, 'older_than_days', min_value=0)
            
            # Boolean parameters
            if dry_run is not None and dry_run.strip():
                validated_params['dry_run'] = coerce_boolean_parameter(dry_run, 'dry_run')
            else:
                validated_params['dry_run'] = False
                
            # Optional boolean parameter for git operations
            if use_git is not None and use_git.strip():
                validated_params['use_git'] = parse_optional_boolean(use_git)
            
            from gira.mcp.ticket_tools import archive_tickets as archive_tickets_impl
            result = archive_tickets_impl(**validated_params)
            return result.model_dump()
            
        except ParameterValidationError as e:
            error_msg = get_helpful_error_message(e)
            logger.warning(f"Parameter validation error in archive_tickets: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool": "archive_tickets",
                "validation_error": True
            }
        except Exception as e:
            logger.error(f"Error in archive_tickets: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "archive_tickets"
            }

    # Epic Management Tools
    @mcp.tool()
    def list_epics(
        status: Optional[str] = None,
        owner: Optional[str] = None,
        labels: Optional[List[str]] = None,
        limit: Optional[str] = None,
    ) -> dict:
        """List epics with optional filtering."""
        try:
            # Validate array parameters
            validated_labels = None
            if labels is not None:
                validated_labels = coerce_array_parameter(labels, 'labels')
            
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.epic_tools import list_epics as list_epics_impl
            result = list_epics_impl(
                status=status,
                owner=owner,
                labels=validated_labels,
                limit=validated_limit,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in list_epics: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "list_epics"
            }

    @mcp.tool()
    def get_epic(epic_id: str) -> dict:
        """Get detailed information about a specific epic."""
        try:
            from gira.mcp.epic_tools import get_epic as get_epic_impl
            result = get_epic_impl(epic_id=epic_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in get_epic: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_epic"
            }

    @mcp.tool()
    def create_epic(
        title: str,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        labels: Optional[str] = None,
        status: Optional[str] = "draft",
    ) -> dict:
        """Create a new epic."""
        try:
            # Validate array parameters (now coming as strings from Claude Desktop)
            validated_labels = None
            if labels is not None and labels.strip():
                validated_labels = coerce_array_parameter(labels, 'labels')
            
            from gira.mcp.epic_tools import create_epic as create_epic_impl
            result = create_epic_impl(
                title=title,
                description=description,
                owner=owner,
                labels=validated_labels,
                status=status,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in create_epic: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "create_epic"
            }

    @mcp.tool()
    def update_epic(
        epic_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        status: Optional[str] = None,
        labels: Optional[List[str]] = None,
        add_labels: Optional[list] = None,
        remove_labels: Optional[list] = None,
    ) -> dict:
        """Update an existing epic."""
        try:
            # Validate array parameters
            validated_labels = None
            if labels is not None:
                validated_labels = coerce_array_parameter(labels, 'labels')
            
            validated_add_labels = None
            if add_labels is not None:
                validated_add_labels = coerce_array_parameter(add_labels, 'add_labels')
            
            validated_remove_labels = None
            if remove_labels is not None:
                validated_remove_labels = coerce_array_parameter(remove_labels, 'remove_labels')
            
            from gira.mcp.epic_tools import update_epic as update_epic_impl
            result = update_epic_impl(
                epic_id=epic_id,
                title=title,
                description=description,
                owner=owner,
                status=status,
                labels=validated_labels,
                add_labels=validated_add_labels,
                remove_labels=validated_remove_labels,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in update_epic: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "update_epic"
            }

    @mcp.tool()
    def add_tickets_to_epic(
        epic_id: str,
        ticket_ids: List[str],
    ) -> dict:
        """Add tickets to an epic."""
        try:
            # Validate array parameters
            validated_ticket_ids = coerce_array_parameter(ticket_ids, 'ticket_ids', allow_empty=False)
            
            from gira.mcp.epic_tools import add_tickets_to_epic as add_tickets_to_epic_impl
            result = add_tickets_to_epic_impl(
                epic_id=epic_id,
                ticket_ids=validated_ticket_ids,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in add_tickets_to_epic: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "add_tickets_to_epic"
            }

    @mcp.tool()
    def remove_tickets_from_epic(
        epic_id: str,
        ticket_ids: List[str],
    ) -> dict:
        """Remove tickets from an epic."""
        try:
            # Validate array parameters
            validated_ticket_ids = coerce_array_parameter(ticket_ids, 'ticket_ids', allow_empty=False)
            
            from gira.mcp.epic_tools import remove_tickets_from_epic as remove_tickets_from_epic_impl
            result = remove_tickets_from_epic_impl(
                epic_id=epic_id,
                ticket_ids=validated_ticket_ids,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in remove_tickets_from_epic: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "remove_tickets_from_epic"
            }

    @mcp.tool()
    def get_epic_tickets(
        epic_id: str,
        status: Optional[str] = None,
        limit: Optional[str] = None,
        include_archived: Optional[str] = None,
    ) -> dict:
        """Get all tickets in an epic."""
        try:
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            # Validate boolean parameters
            validated_include_archived = True  # Default to True for historical context
            if include_archived is not None and include_archived.strip():
                validated_include_archived = coerce_boolean_parameter(include_archived, 'include_archived')
            
            from gira.mcp.epic_tools import get_epic_tickets as get_epic_tickets_impl
            result = get_epic_tickets_impl(
                epic_id=epic_id,
                status=status,
                limit=validated_limit,
                include_archived=validated_include_archived,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in get_epic_tickets: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_epic_tickets"
            }

    # Sprint Management Tools
    @mcp.tool()
    def list_sprints(
        status: Optional[str] = None,
        name: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> dict:
        """List sprints with optional filtering."""
        try:
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.sprint_tools import list_sprints as list_sprints_impl
            result = list_sprints_impl(
                status=status,
                name=name,
                limit=validated_limit,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in list_sprints: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "list_sprints"
            }

    @mcp.tool()
    def get_sprint(sprint_id: str) -> dict:
        """Get detailed information about a specific sprint."""
        try:
            from gira.mcp.sprint_tools import get_sprint as get_sprint_impl
            result = get_sprint_impl(sprint_id=sprint_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in get_sprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_sprint"
            }

    @mcp.tool()
    def create_sprint(
        name: str,
        goal: Optional[str] = None,
        duration_days: int = 14,
        start_date: Optional[str] = None,
    ) -> dict:
        """Create a new sprint."""
        try:
            # Validate integer parameters
            validated_duration_days = coerce_integer_parameter(duration_days, 'duration_days', min_value=1, max_value=30)
            
            from gira.mcp.sprint_tools import create_sprint as create_sprint_impl
            result = create_sprint_impl(
                name=name,
                goal=goal,
                duration_days=validated_duration_days,
                start_date=start_date,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in create_sprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "create_sprint"
            }

    @mcp.tool()
    def start_sprint(sprint_id: str) -> dict:
        """Start a planned sprint."""
        try:
            from gira.mcp.sprint_tools import start_sprint as start_sprint_impl
            result = start_sprint_impl(sprint_id=sprint_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in start_sprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "start_sprint"
            }

    @mcp.tool()
    def complete_sprint(sprint_id: str) -> dict:
        """Complete an active sprint."""
        try:
            from gira.mcp.sprint_tools import complete_sprint as complete_sprint_impl
            result = complete_sprint_impl(sprint_id=sprint_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in complete_sprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "complete_sprint"
            }

    @mcp.tool()
    def add_tickets_to_sprint(
        sprint_id: str,
        ticket_ids: List[str],
    ) -> dict:
        """Add tickets to a sprint."""
        try:
            # Validate array parameters
            validated_ticket_ids = coerce_array_parameter(ticket_ids, 'ticket_ids', allow_empty=False)
            
            from gira.mcp.sprint_tools import add_tickets_to_sprint as add_tickets_to_sprint_impl
            result = add_tickets_to_sprint_impl(
                sprint_id=sprint_id,
                ticket_ids=validated_ticket_ids,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in add_tickets_to_sprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "add_tickets_to_sprint"
            }

    @mcp.tool()
    def remove_tickets_from_sprint(
        sprint_id: str,
        ticket_ids: List[str],
    ) -> dict:
        """Remove tickets from a sprint."""
        try:
            # Validate array parameters
            validated_ticket_ids = coerce_array_parameter(ticket_ids, 'ticket_ids', allow_empty=False)
            
            from gira.mcp.sprint_tools import remove_tickets_from_sprint as remove_tickets_from_sprint_impl
            result = remove_tickets_from_sprint_impl(
                sprint_id=sprint_id,
                ticket_ids=validated_ticket_ids,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in remove_tickets_from_sprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "remove_tickets_from_sprint"
            }

    @mcp.tool()
    def get_sprint_tickets(
        sprint_id: str,
        status: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> dict:
        """Get all tickets in a sprint."""
        try:
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.sprint_tools import get_sprint_tickets as get_sprint_tickets_impl
            result = get_sprint_tickets_impl(
                sprint_id=sprint_id,
                status=status,
                limit=validated_limit,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in get_sprint_tickets: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_sprint_tickets"
            }

    @mcp.tool()
    def get_sprint_metrics(sprint_id: str) -> dict:
        """Get detailed metrics for a sprint."""
        try:
            from gira.mcp.sprint_tools import get_sprint_metrics as get_sprint_metrics_impl
            result = get_sprint_metrics_impl(sprint_id=sprint_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in get_sprint_metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_sprint_metrics"
            }

    # Board and Visualization Tools
    @mcp.tool()
    def get_enhanced_board_state(
        include_counts: Optional[str] = None,
        include_tickets: Optional[str] = None,
        include_epic_context: Optional[str] = None,
        include_sprint_context: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> dict:
        """Get enhanced board state with epic and sprint context."""
        try:
            # Validate boolean parameters with defaults
            validated_include_counts = True
            if include_counts is not None and include_counts.strip():
                validated_include_counts = coerce_boolean_parameter(include_counts, 'include_counts')
            
            validated_include_tickets = False
            if include_tickets is not None and include_tickets.strip():
                validated_include_tickets = coerce_boolean_parameter(include_tickets, 'include_tickets')
            
            validated_include_epic_context = True
            if include_epic_context is not None and include_epic_context.strip():
                validated_include_epic_context = coerce_boolean_parameter(include_epic_context, 'include_epic_context')
            
            validated_include_sprint_context = True
            if include_sprint_context is not None and include_sprint_context.strip():
                validated_include_sprint_context = coerce_boolean_parameter(include_sprint_context, 'include_sprint_context')
            
            # Validate array parameters
            validated_status_filter = None
            if status_filter is not None and status_filter.strip():
                validated_status_filter = coerce_array_parameter(status_filter, 'status_filter')
            
            from gira.mcp.board_tools import get_enhanced_board_state as get_enhanced_board_state_impl
            result = get_enhanced_board_state_impl(
                include_counts=validated_include_counts,
                include_tickets=validated_include_tickets,
                include_epic_context=validated_include_epic_context,
                include_sprint_context=validated_include_sprint_context,
                status_filter=validated_status_filter,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in get_enhanced_board_state: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_enhanced_board_state"
            }

    @mcp.tool()
    def get_swimlane_tickets(
        status: str,
        group_by_epic: bool = True,
        limit: Optional[str] = None,
    ) -> dict:
        """Get tickets by status/swimlane with epic grouping."""
        try:
            # Validate integer parameters (now coming as strings from Claude Desktop)
            validated_limit = None
            if limit is not None and limit.strip():
                validated_limit = coerce_integer_parameter(limit, 'limit', min_value=1, max_value=1000)
            
            from gira.mcp.board_tools import get_swimlane_tickets as get_swimlane_tickets_impl
            result = get_swimlane_tickets_impl(
                status=status,
                group_by_epic=group_by_epic,
                limit=validated_limit,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in get_swimlane_tickets: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_swimlane_tickets"
            }

    @mcp.tool()
    def move_tickets_bulk(
        ticket_ids: List[str],
        target_status: str,
        comment: Optional[str] = None,
    ) -> dict:
        """Move multiple tickets between swimlanes/statuses."""
        try:
            # Validate array parameters
            validated_ticket_ids = coerce_array_parameter(ticket_ids, 'ticket_ids', allow_empty=False)
            
            from gira.mcp.board_tools import move_tickets_bulk as move_tickets_bulk_impl
            result = move_tickets_bulk_impl(
                ticket_ids=validated_ticket_ids,
                target_status=target_status,
                comment=comment,
            )
            return result.model_dump()
        except ParameterValidationError as e:
            return get_helpful_error_message(e.field, e.value, e.expected_type)
        except Exception as e:
            logger.error(f"Error in move_tickets_bulk: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "move_tickets_bulk"
            }

    # =====================================
    # PROJECT MANAGEMENT TOOLS
    # =====================================

    @mcp.tool()
    def list_projects() -> dict:
        """List all registered Gira projects with their status."""
        try:
            from gira.mcp.project_tools import list_projects as list_projects_impl
            result = list_projects_impl()
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in list_projects: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "list_projects"
            }

    @mcp.tool()
    def add_project(
        name: Optional[str] = None,
        path: Optional[str] = None
    ) -> dict:
        """Add a new Gira project to the registry."""
        try:
            from gira.mcp.project_tools import add_project as add_project_impl
            result = add_project_impl(name=name, path=path)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in add_project: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "add_project"
            }

    @mcp.tool()
    def switch_project(
        name: Optional[str] = None
    ) -> dict:
        """Switch to a different registered Gira project."""
        try:
            from gira.mcp.project_tools import switch_project as switch_project_impl
            result = switch_project_impl(name=name)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in switch_project: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "switch_project"
            }

    @mcp.tool()
    def remove_project(
        name: Optional[str] = None
    ) -> dict:
        """Remove a project from the registry."""
        try:
            from gira.mcp.project_tools import remove_project as remove_project_impl
            result = remove_project_impl(name=name)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in remove_project: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "remove_project"
            }

    @mcp.tool()
    def discover_projects(
        search_paths: Optional[str] = None
    ) -> dict:
        """Discover Gira projects in specified directories."""
        try:
            from gira.mcp.project_tools import discover_projects as discover_projects_impl
            result = discover_projects_impl(search_paths=search_paths)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in discover_projects: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "discover_projects"
            }

    @mcp.tool()
    def get_active_project() -> dict:
        """Get information about the currently active project."""
        try:
            from gira.mcp.project_tools import get_active_project as get_active_project_impl
            result = get_active_project_impl()
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error in get_active_project: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "get_active_project"
            }

    logger.info("MCP server initialization complete - registered 36 tools (12 ticket + 7 epic + 8 sprint + 3 board + 6 project)")
    return mcp




def main() -> None:
    """Main entry point for the Gira MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="Gira MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default=None,
        help="Transport mode (overrides config)"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host for HTTP/SSE transport (overrides config)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for HTTP/SSE transport (overrides config)"
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        default=None,
        help="Working directory (overrides config)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enable dry-run mode"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Disable dry-run mode"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Get configuration and apply command-line overrides
    config = get_config()

    if args.transport:
        config.transport = args.transport
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port
    if args.working_dir:
        from pathlib import Path
        config.working_directory = Path(args.working_dir)
    if args.dry_run:
        config.dry_run = True
    if args.no_dry_run:
        config.dry_run = False
    if args.debug:
        config.enable_debug = True

    try:
        # Run server directly with FastMCP's run method
        mcp = create_mcp_server()
        
        if config.transport == "stdio":
            logger.info("Starting MCP server with stdio transport")
            # FastMCP's run method is synchronous and handles asyncio internally
            mcp.run(transport="stdio")
        elif config.transport == "http":
            logger.info(f"Starting MCP server with HTTP transport on {config.host}:{config.port}")
            mcp.run(transport="http", host=config.host, port=config.port)
        elif config.transport == "sse":
            logger.info(f"Starting MCP server with SSE transport on {config.host}:{config.port}")
            mcp.run(transport="sse", host=config.host, port=config.port)
        else:
            logger.error(f"Unsupported transport: {config.transport}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
