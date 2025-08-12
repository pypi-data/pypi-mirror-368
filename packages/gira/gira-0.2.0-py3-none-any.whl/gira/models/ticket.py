"""Ticket model and related enums."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import Field, field_validator

from gira.models.base import TimestampedModel

if TYPE_CHECKING:
    from gira.models.comment import Comment


class TicketStatus(str, Enum):
    """Valid ticket statuses that map to swimlanes."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TicketPriority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKER = "blocker"


class TicketType(str, Enum):
    """Types of tickets."""
    STORY = "story"
    TASK = "task"
    BUG = "bug"
    EPIC = "epic"
    FEATURE = "feature"
    SUBTASK = "subtask"


class Ticket(TimestampedModel):
    """Represents a work item in Gira."""

    # Core fields
    id: str = Field(
        ...,
        pattern=r"^[A-Z]{2,4}-\d+$",
        description="Ticket ID in format PREFIX-NUMBER (e.g., GIRA-123)"
    )
    uuid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Internal UUID for merge conflict detection (never displayed to users)"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Brief summary of the ticket"
    )
    description: str = Field(
        default="",
        description="Detailed description in Markdown format"
    )

    # Status and workflow
    status: str = Field(
        default="todo",
        description="Current status/swimlane of the ticket"
    )

    # Categorization
    type: TicketType = Field(
        default=TicketType.TASK,
        description="Type of ticket"
    )
    priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM,
        description="Priority level"
    )
    labels: List[str] = Field(
        default_factory=list,
        description="Tags for categorization"
    )

    # People
    assignee: Optional[str] = Field(
        default=None,
        description="Email or username of assignee"
    )
    reporter: str = Field(
        ...,
        description="Email or username of ticket creator"
    )

    # Relationships
    epic_id: Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{2,4}-\d+$",
        description="Parent epic ID"
    )
    parent_id: Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{2,4}-\d+$",
        description="Parent ticket ID for subtasks"
    )
    sprint_id: Optional[str] = Field(
        default=None,
        description="Associated sprint ID"
    )

    # Dependencies
    blocked_by: List[str] = Field(
        default_factory=list,
        description="IDs of tickets blocking this one"
    )
    blocks: List[str] = Field(
        default_factory=list,
        description="IDs of tickets blocked by this one"
    )

    # Comments
    comments: List["Comment"] = Field(
        default_factory=list,
        description="List of comments on this ticket"
    )

    # Metadata counts (populated from separate files)
    attachment_count: int = Field(
        default=0,
        description="Number of attachments"
    )
    comment_count: int = Field(
        default=0,
        description="Number of comments"
    )

    # Optional fields
    due_date: Optional[datetime] = Field(
        default=None,
        description="Target completion date"
    )
    story_points: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Estimated effort"
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Custom order within status column (0 means unordered)"
    )
    
    # Custom fields
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom field values defined by project configuration"
    )

    @field_validator("id", "epic_id", "parent_id", mode="before")
    @classmethod
    def uppercase_id(cls, v: Optional[str]) -> Optional[str]:
        """Ensure IDs are uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("labels")
    @classmethod
    def lowercase_labels(cls, v: List[str]) -> List[str]:
        """Ensure labels are lowercase for consistency."""
        return [label.lower().strip() for label in v]

    @field_validator("blocked_by", "blocks")
    @classmethod
    def validate_dependencies(cls, v: List[str]) -> List[str]:
        """Ensure dependency IDs are in correct format."""
        pattern = r"^[A-Z]{2,4}-\d+$"
        import re
        validated = []
        for dep_id in v:
            dep_id = dep_id.upper()
            if re.match(pattern, dep_id):
                validated.append(dep_id)
            else:
                raise ValueError(f"Invalid dependency ID format: {dep_id}")
        return validated

    def get_directory_name(self) -> str:
        """Get the directory name for this ticket."""
        return self.id.lower().replace("-", "_")

    def is_subtask(self) -> bool:
        """Check if this ticket is a subtask."""
        return self.parent_id is not None

    def is_in_epic(self) -> bool:
        """Check if this ticket belongs to an epic."""
        return self.epic_id is not None

    def is_blocked(self) -> bool:
        """Check if this ticket is blocked by others."""
        return len(self.blocked_by) > 0

    def is_blocking_others(self) -> bool:
        """Check if this ticket blocks others."""
        return len(self.blocks) > 0
