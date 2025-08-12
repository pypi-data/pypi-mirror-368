"""Epic model for grouping related tickets."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import EmailStr, Field, field_validator

from gira.models.base import TimestampedModel
from gira.models.comment import Comment


class EpicStatus(str, Enum):
    """Valid epic statuses."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class Epic(TimestampedModel):
    """Represents a collection of related tickets working towards a larger goal."""

    # Core fields
    id: str = Field(
        ...,
        pattern=r"^EPIC-\d+$",
        description="Epic ID in format EPIC-NNN (e.g., EPIC-123)"
    )
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Brief summary of the epic"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the epic goals and scope"
    )

    # Status and workflow
    status: EpicStatus = Field(
        default=EpicStatus.DRAFT,
        description="Current status of the epic"
    )

    # People
    owner: EmailStr = Field(
        ...,
        description="Email address of the epic owner"
    )

    # Planning
    target_date: Optional[date] = Field(
        default=None,
        description="Target completion date for the epic"
    )

    # Labels and categorization
    labels: List[str] = Field(
        default_factory=list,
        description="List of labels for categorizing and filtering epics"
    )

    # Relationships
    tickets: List[str] = Field(
        default_factory=list,
        description="List of ticket IDs that belong to this epic"
    )
    
    # Comments
    comments: List[Comment] = Field(
        default_factory=list,
        description="List of comments on this epic"
    )
    comment_count: int = Field(
        default=0,
        ge=0,
        description="Number of comments"
    )
    
    # Custom fields
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom field values defined by project configuration"
    )

    @field_validator("id", mode="before")
    @classmethod
    def uppercase_id(cls, v: str) -> str:
        """Ensure ID is uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("labels", mode="before")
    @classmethod
    def ensure_labels_list(cls, v) -> List[str]:
        """Ensure labels is always a list, even when missing from old data."""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Handle comma-separated string labels
            return [label.strip() for label in v.split(",") if label.strip()]
        return []

    @field_validator("tickets")
    @classmethod
    def validate_ticket_ids(cls, v: List[str]) -> List[str]:
        """Ensure ticket IDs are in correct format."""
        pattern = r"^[A-Z]{2,4}-\d+$"
        import re
        validated = []
        for ticket_id in v:
            ticket_id = ticket_id.upper()
            if re.match(pattern, ticket_id):
                validated.append(ticket_id)
            else:
                raise ValueError(f"Invalid ticket ID format: {ticket_id}")
        return validated

    def get_directory_name(self) -> str:
        """Get the directory name for this epic."""
        return self.id.lower().replace("-", "_")

    def is_active(self) -> bool:
        """Check if this epic is currently active."""
        return self.status == EpicStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if this epic is completed."""
        return self.status == EpicStatus.COMPLETED

    def add_ticket(self, ticket_id: str) -> None:
        """Add a ticket to this epic."""
        ticket_id = ticket_id.upper()
        if ticket_id not in self.tickets:
            self.tickets.append(ticket_id)

    def remove_ticket(self, ticket_id: str) -> None:
        """Remove a ticket from this epic."""
        ticket_id = ticket_id.upper()
        if ticket_id in self.tickets:
            self.tickets.remove(ticket_id)

    def ticket_count(self) -> int:
        """Get the number of tickets in this epic."""
        return len(self.tickets)
