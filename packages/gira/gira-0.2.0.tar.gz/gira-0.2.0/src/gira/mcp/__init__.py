"""MCP (Model Context Protocol) server implementation for Gira.

This module provides a FastMCP-based server that enables AI agents to interact
with Gira's project management functionality through the Model Context Protocol.

The server provides tools for:
- Ticket management (create, update, list, search)
- Epic management 
- Sprint operations
- Project querying and reporting

Usage:
    # Run the server directly
    python -m gira.mcp.server
    
    # Or use the installed console script
    gira-mcp
    
    # With custom options
    gira-mcp --transport stdio --working-dir /path/to/project
"""

from .config import MCPConfig, get_config, set_config, reset_config
from .server import create_mcp_server, main
from .schema import (
    TicketStatus,
    TicketType,
    Priority,
    TicketIdentifier,
    TicketFilter,
    TicketCreateParams,
    TicketUpdateParams,
    OperationResult,
    MCPError,
)
from .tools import (
    MCPToolError,
    ValidationError,
    PermissionError,
    NotFoundError,
    tool_registry,
    register_tool,
    normalize_ticket_id,
    normalize_epic_id,
)

__all__ = [
    # Configuration
    "MCPConfig",
    "get_config",
    "set_config", 
    "reset_config",
    
    # Server
    "create_mcp_server",
    "main",
    
    # Schema types
    "TicketStatus",
    "TicketType", 
    "Priority",
    "TicketIdentifier",
    "TicketFilter",
    "TicketCreateParams",
    "TicketUpdateParams",
    "OperationResult",
    "MCPError",
    
    # Tools infrastructure
    "MCPToolError",
    "ValidationError",
    "PermissionError", 
    "NotFoundError",
    "tool_registry",
    "register_tool",
    "normalize_ticket_id",
    "normalize_epic_id",
]