"""SavedQuery model for storing reusable query expressions."""

from typing import Optional

from pydantic import Field, field_validator

from gira.models.base import TimestampedModel


class SavedQuery(TimestampedModel):
    """Represents a saved query expression for reuse."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$",
        description="Unique name for the saved query (alphanumeric, dash, underscore)"
    )
    query: str = Field(
        ...,
        min_length=1,
        description="The GQL query expression"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional description of what the query returns"
    )
    entity_type: str = Field(
        default="ticket",
        description="The entity type this query targets (ticket, epic, sprint, comment)"
    )
    author: str = Field(
        ...,
        description="Email or username of the query creator"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is valid and doesn't conflict with reserved words."""
        reserved_words = {"list", "save", "delete", "run", "help", "version"}
        if v.lower() in reserved_words:
            raise ValueError(f"'{v}' is a reserved word and cannot be used as a query name")
        return v

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        """Ensure entity type is valid."""
        valid_types = {"ticket", "epic", "sprint", "comment"}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid entity type: {v}. Must be one of: {', '.join(valid_types)}")
        return v.lower()

    def get_display_name(self) -> str:
        """Get the display name with @ prefix."""
        return f"@{self.name}"