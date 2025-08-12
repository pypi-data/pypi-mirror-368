"""Base model for all Gira entities."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class GiraModel(BaseModel):
    """Base model for all Gira entities with common configuration."""

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

    def to_json_dict(self) -> Dict[str, Any]:
        """Convert model to JSON-serializable dictionary."""
        return self.model_dump(mode="json", exclude_none=True)

    def to_pretty_json(self) -> str:
        """Convert model to pretty-printed JSON string."""
        return self.model_dump_json(indent=2, exclude_none=True)

    @classmethod
    def from_json_file(cls, file_path: str) -> "GiraModel":
        """Load model from JSON file."""
        import json
        from pathlib import Path

        data = json.loads(Path(file_path).read_text())
        return cls(**data)

    def save_to_json_file(self, file_path: str) -> None:
        """Save model to JSON file."""
        from pathlib import Path

        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(file_path).write_text(self.to_pretty_json())


class TimestampedModel(GiraModel):
    """Base model with created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def model_post_init(self, __context: Any) -> None:
        """Update the updated_at timestamp after initialization."""
        # This is called after the model is initialized
        # We'll use this in derived classes to update timestamps
