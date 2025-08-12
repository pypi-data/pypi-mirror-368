"""JSON Schema definitions for Gira MCP server."""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class TicketStatus(str, Enum):
    """Valid ticket statuses in Gira."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    ARCHIVED = "archived"


class TicketType(str, Enum):
    """Valid ticket types in Gira."""
    FEATURE = "feature"
    BUG = "bug"
    TASK = "task"
    EPIC = "epic"
    STORY = "story"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"


class Priority(str, Enum):
    """Valid priority levels in Gira."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Base schemas for MCP tool parameters

class TicketIdentifier(BaseModel):
    """Schema for identifying a ticket."""
    ticket_id: str = Field(
        description="Ticket ID (e.g., 'GCM-123' or just '123')",
        examples=["GCM-123", "123"]
    )


class TicketFilter(BaseModel):
    """Schema for filtering tickets."""
    status: Optional[Union[TicketStatus, List[TicketStatus]]] = Field(
        default=None,
        description="Filter by ticket status"
    )
    type: Optional[Union[TicketType, List[TicketType]]] = Field(
        default=None,
        description="Filter by ticket type"
    )
    priority: Optional[Union[Priority, List[Priority]]] = Field(
        default=None,
        description="Filter by priority level"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="Filter by assignee email"
    )
    epic_id: Optional[str] = Field(
        default=None,
        description="Filter by epic ID"
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="Filter by labels (all must match)"
    )
    has_labels: Optional[List[str]] = Field(
        default=None,
        description="Filter by labels (any must match)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )


class TicketCreateParams(BaseModel):
    """Schema for creating a new ticket."""
    title: str = Field(
        description="Ticket title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Ticket description (Markdown supported)",
        max_length=10000
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate ticket title for security."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        
        # Remove null bytes and control characters
        cleaned = v.replace('\x00', '').replace('\r', '\n')
        
        if len(cleaned.strip()) == 0:
            raise ValueError("Title cannot be empty after cleaning")
            
        return cleaned.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate ticket description for security."""
        if v is None:
            return v
        
        # Remove null bytes and control characters  
        cleaned = v.replace('\x00', '').replace('\r', '\n')
        return cleaned
    
    type: TicketType = Field(
        default=TicketType.TASK,
        description="Ticket type"
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Ticket priority"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="Assignee email address"
    )
    epic_id: Optional[str] = Field(
        default=None,
        description="Epic ID if this ticket belongs to an epic"
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="List of labels to add to the ticket"
    )
    story_points: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Story points estimate"
    )


class TicketUpdateParams(BaseModel):
    """Schema for updating an existing ticket."""
    ticket_id: str = Field(
        description="Ticket ID to update"
    )
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New ticket title"
    )
    description: Optional[str] = Field(
        default=None,
        description="New ticket description"
    )
    status: Optional[TicketStatus] = Field(
        default=None,
        description="New ticket status"
    )
    type: Optional[TicketType] = Field(
        default=None,
        description="New ticket type"
    )
    priority: Optional[Priority] = Field(
        default=None,
        description="New ticket priority"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="New assignee email (use empty string to unassign)"
    )
    story_points: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Story points estimate"
    )


class CommentParams(BaseModel):
    """Schema for adding comments to tickets."""
    ticket_id: str = Field(
        description="Ticket ID to comment on"
    )
    content: str = Field(
        description="Comment content (Markdown supported)",
        min_length=1
    )


class EpicIdentifier(BaseModel):
    """Schema for identifying an epic."""
    epic_id: str = Field(
        description="Epic ID (e.g., 'EPIC-001')",
        examples=["EPIC-001"]
    )


class EpicCreateParams(BaseModel):
    """Schema for creating a new epic."""
    title: str = Field(
        description="Epic title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Epic description (Markdown supported)"
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="List of labels to add to the epic"
    )


class SprintIdentifier(BaseModel):
    """Schema for identifying a sprint."""
    sprint_id: str = Field(
        description="Sprint ID (e.g., 'SPRINT-2024-01')",
        examples=["SPRINT-2024-01"]
    )


# Response schemas

class TicketSummary(BaseModel):
    """Summary representation of a ticket."""
    id: str
    title: str
    status: TicketStatus
    type: TicketType
    priority: Priority
    assignee: Optional[str]
    epic_id: Optional[str]
    labels: List[str]
    story_points: Optional[int]
    created_at: str
    updated_at: str


class TicketDetail(TicketSummary):
    """Detailed representation of a ticket."""
    description: Optional[str]
    reporter: Optional[str]
    blocked_by: List[str]
    blocks: List[str]
    comment_count: int
    attachment_count: int
    custom_fields: Dict[str, Any]


class EpicSummary(BaseModel):
    """Summary representation of an epic."""
    id: str
    title: str
    status: str
    labels: List[str]
    ticket_count: int
    completed_tickets: int
    progress_percentage: float
    created_at: str
    updated_at: str


class SearchParams(BaseModel):
    """Schema for search operations."""
    query: str = Field(
        description="Search query string",
        min_length=1
    )
    entity_type: str = Field(
        default="ticket",
        description="Type of entity to search (ticket, epic, sprint)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results"
    )


# Epic Management Schemas

class EpicFilter(BaseModel):
    """Schema for filtering epics."""
    status: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Filter by epic status (draft, active, completed)"
    )
    owner: Optional[str] = Field(
        default=None,
        description="Filter by epic owner email"
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="Filter by labels (all must match)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of epics to return"
    )


class EpicCreateParams(BaseModel):
    """Schema for creating a new epic."""
    title: str = Field(
        description="Epic title",
        min_length=3,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Epic description (Markdown supported)",
        max_length=10000
    )
    owner: Optional[str] = Field(
        default=None,
        description="Epic owner email (defaults to current user)"
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="Epic labels"
    )
    status: Optional[str] = Field(
        default="draft",
        description="Initial epic status (draft, active, completed)"
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate epic title for security."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        
        # Remove null bytes and normalize line endings
        cleaned = v.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
        
        if len(cleaned.strip()) == 0:
            raise ValueError("Title cannot be empty after cleaning")
            
        return cleaned.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate epic description for security."""
        if v is None:
            return v
        
        # Remove null bytes and normalize line endings  
        cleaned = v.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
        return cleaned


class EpicUpdateParams(BaseModel):
    """Schema for updating an existing epic."""
    epic_id: str = Field(
        description="Epic ID to update"
    )
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=200,
        description="New epic title"
    )
    description: Optional[str] = Field(
        default=None,
        description="New epic description"
    )
    owner: Optional[str] = Field(
        default=None,
        description="New epic owner email"
    )
    status: Optional[str] = Field(
        default=None,
        description="New epic status (draft, active, completed)"
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="New labels (replaces existing)"
    )
    add_labels: Optional[List[str]] = Field(
        default=None,
        description="Labels to add"
    )
    remove_labels: Optional[List[str]] = Field(
        default=None,
        description="Labels to remove"
    )


class EpicTicketParams(BaseModel):
    """Schema for epic-ticket associations."""
    epic_id: str = Field(
        description="Epic ID"
    )
    ticket_ids: List[str] = Field(
        description="List of ticket IDs",
        max_length=100
    )


# Sprint Management Schemas

class SprintFilter(BaseModel):
    """Schema for filtering sprints."""
    status: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Filter by sprint status (planned, active, completed)"
    )
    name: Optional[str] = Field(
        default=None,
        description="Filter by sprint name (partial match)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of sprints to return"
    )


class SprintCreateParams(BaseModel):
    """Schema for creating a new sprint."""
    name: str = Field(
        description="Sprint name",
        min_length=1,
        max_length=100
    )
    goal: Optional[str] = Field(
        default=None,
        description="Sprint goal/objective",
        max_length=500
    )
    duration_days: int = Field(
        default=14,
        ge=1,
        le=30,
        description="Sprint duration in days"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Sprint start date (ISO format: YYYY-MM-DD)"
    )


class SprintUpdateParams(BaseModel):
    """Schema for updating a sprint."""
    sprint_id: str = Field(
        description="Sprint ID to update"
    )
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New sprint name"
    )
    goal: Optional[str] = Field(
        default=None,
        description="New sprint goal"
    )
    status: Optional[str] = Field(
        default=None,
        description="New sprint status (planned, active, completed)"
    )


class SprintTicketParams(BaseModel):
    """Schema for sprint-ticket associations."""
    sprint_id: str = Field(
        description="Sprint ID"
    )
    ticket_ids: List[str] = Field(
        description="List of ticket IDs",
        max_length=100
    )


# Response Schemas

class EpicSummary(BaseModel):
    """Summary representation of an epic."""
    id: str
    title: str
    status: str
    owner: str
    labels: List[str]
    ticket_count: int
    completed_tickets: int
    progress_percentage: float
    created_at: str
    updated_at: str


class EpicDetail(EpicSummary):
    """Detailed representation of an epic."""
    description: Optional[str]
    progress: Dict[str, Any]
    comment_count: int


class SprintSummary(BaseModel):
    """Summary representation of a sprint."""
    id: str
    name: str
    status: str
    goal: Optional[str]
    start_date: str
    end_date: str
    duration_days: int
    ticket_count: int
    completed_tickets: int
    progress_percentage: float
    created_at: str
    updated_at: str


class SprintDetail(SprintSummary):
    """Detailed representation of a sprint."""
    tickets: List[Dict[str, Any]]
    metrics: Dict[str, Any]


class MCPError(BaseModel):
    """Schema for MCP error responses (legacy compatibility)."""
    error: str = Field(description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class EnhancedMCPErrorResponse(BaseModel):
    """Enhanced MCP error response with comprehensive information."""
    error: str = Field(description="User-friendly error message")
    code: str = Field(description="Systematic error code")
    category: str = Field(description="Error category")
    severity: str = Field(description="Error severity level")
    timestamp: str = Field(description="Error timestamp")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracking")
    operation: Optional[str] = Field(default=None, description="Operation that caused the error")
    suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Suggestions for fixing the error")
    recovery_strategy: Optional[Dict[str, Any]] = Field(default=None, description="Recovery strategy information")
    debug_info: Optional[Dict[str, Any]] = Field(default=None, description="Debug information (debug mode only)")


class OperationResult(BaseModel):
    """Schema for operation results."""
    success: bool = Field(description="Whether the operation succeeded")
    message: str = Field(description="Result message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Result data")
    error: Optional[Union[Dict[str, Any], EnhancedMCPErrorResponse]] = Field(default=None, description="Error information if operation failed")
    dry_run: bool = Field(default=False, description="Whether this was a dry run")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracking")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    warnings: Optional[List[str]] = Field(default=None, description="Non-fatal warnings")


# Tool parameter schemas for FastMCP registration
TOOL_SCHEMAS = {
    "get_ticket": TicketIdentifier.model_json_schema(),
    "list_tickets": TicketFilter.model_json_schema(),
    "create_ticket": TicketCreateParams.model_json_schema(),
    "update_ticket": TicketUpdateParams.model_json_schema(),
    "add_comment": CommentParams.model_json_schema(),
    "get_epic": EpicIdentifier.model_json_schema(),
    "create_epic": EpicCreateParams.model_json_schema(),
    "search": SearchParams.model_json_schema(),
}