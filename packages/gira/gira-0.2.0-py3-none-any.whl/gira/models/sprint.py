"""Sprint model for time-boxed development cycles."""

from datetime import date
from enum import Enum
from typing import Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from gira.models.base import TimestampedModel


class SprintStatus(str, Enum):
    """Sprint lifecycle states."""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


class Sprint(TimestampedModel):
    """Represents a time-boxed development iteration."""

    model_config = ConfigDict(
        # Allow future fields without breaking old versions
        extra="allow",
        # Use enum values instead of names in JSON
        use_enum_values=True,
        # Validate data on assignment
        validate_assignment=True,
        # Use field serializers
        ser_json_timedelta="float",
        # Populate models by field name or alias
        populate_by_name=True,
        # Better error messages
        str_strip_whitespace=True,
    )

    id: str = Field(
        ...,
        pattern=r"^SPRINT-\d{4}-\d{2}-\d{2}$",
        description="Sprint ID in format SPRINT-YYYY-MM-DD"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sprint name"
    )
    goal: Optional[str] = Field(
        default=None,
        description="Sprint goal/objective"
    )
    start_date: date = Field(
        ...,
        description="Sprint start date"
    )
    end_date: date = Field(
        ...,
        description="Sprint end date"
    )
    status: SprintStatus = Field(
        default=SprintStatus.PLANNED,
        description="Current sprint status"
    )
    tickets: List[str] = Field(
        default_factory=list,
        description="List of ticket IDs in this sprint"
    )
    retrospective: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Sprint retrospective with what_went_well, what_went_wrong, action_items"
    )

    @field_validator("id")
    @classmethod
    def validate_sprint_id(cls, v: str) -> str:
        """Ensure sprint ID follows SPRINT-YYYY-MM-DD format."""
        import re
        if not re.match(r"^SPRINT-\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Sprint ID must be in format SPRINT-YYYY-MM-DD")
        return v

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

    @field_validator("retrospective")
    @classmethod
    def validate_retrospective(cls, v: Optional[Dict[str, List[str]]]) -> Optional[Dict[str, List[str]]]:
        """Validate retrospective structure if provided."""
        if v is not None:
            required_keys = {"what_went_well", "what_went_wrong", "action_items"}
            if not all(key in v for key in required_keys):
                raise ValueError(f"Retrospective must contain keys: {required_keys}")
            for key in required_keys:
                if not isinstance(v[key], list):
                    raise ValueError(f"Retrospective '{key}' must be a list of strings")
                for item in v[key]:
                    if not isinstance(item, str):
                        raise ValueError(f"All items in retrospective '{key}' must be strings")
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "Sprint":
        """Ensure end date is after start date."""
        if self.end_date <= self.start_date:
            raise ValueError("Sprint end date must be after start date")
        return self

    @model_validator(mode="after")
    def validate_status_transitions(self) -> "Sprint":
        """Validate status transitions and retrospective requirements."""
        if self.status == SprintStatus.COMPLETED and not self.retrospective:
            # Retrospective is optional, but log a warning if completing without it
            pass  # Could add logging here if needed
        return self

