"""Board and workflow models."""

from typing import Dict, List, Optional

from pydantic import Field, field_validator, model_validator

from gira.models.base import GiraModel


class Swimlane(GiraModel):
    """Represents a swimlane on the board."""

    id: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_-]*$",
        description="Unique identifier for the swimlane"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Display name for the swimlane"
    )
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="WIP limit for this swimlane"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of what this swimlane represents"
    )

    @field_validator("id")
    @classmethod
    def lowercase_id(cls, v: str) -> str:
        """Ensure swimlane ID is lowercase."""
        return v.lower()


class WorkflowTransitions(GiraModel):
    """Defines allowed transitions between swimlanes."""

    transitions: Dict[str, List[str]] = Field(
        ...,
        description="Map of swimlane ID to list of allowed target swimlane IDs"
    )

    def can_transition(self, from_swimlane: str, to_swimlane: str) -> bool:
        """Check if a transition is allowed."""
        from_swimlane = from_swimlane.lower()
        to_swimlane = to_swimlane.lower()

        allowed_targets = self.transitions.get(from_swimlane, [])
        return to_swimlane in allowed_targets

    def get_allowed_transitions(self, from_swimlane: str) -> List[str]:
        """Get list of allowed target swimlanes."""
        from_swimlane = from_swimlane.lower()
        return self.transitions.get(from_swimlane, [])


class Board(GiraModel):
    """Board configuration stored in .gira/.board.json."""

    swimlanes: List[Swimlane] = Field(
        ...,
        min_length=1,
        description="List of swimlanes on the board"
    )
    transitions: Dict[str, List[str]] = Field(
        ...,
        description="Allowed transitions between swimlanes"
    )

    @model_validator(mode="after")
    def validate_transitions(self) -> "Board":
        """Ensure all transition references are valid swimlanes."""
        swimlane_ids = {s.id for s in self.swimlanes}

        for from_id, to_ids in self.transitions.items():
            if from_id not in swimlane_ids:
                raise ValueError(f"Unknown swimlane in transitions: {from_id}")

            for to_id in to_ids:
                if to_id not in swimlane_ids:
                    raise ValueError(f"Unknown target swimlane: {to_id}")

        return self

    def get_swimlane_by_id(self, swimlane_id: str) -> Optional[Swimlane]:
        """Get swimlane by ID."""
        swimlane_id = swimlane_id.lower()
        for swimlane in self.swimlanes:
            if swimlane.id == swimlane_id:
                return swimlane
        return None

    def get_swimlane_by_status(self, status: str) -> Optional[Swimlane]:
        """Get swimlane by status (assumes 1:1 mapping in MVP)."""
        # In MVP, status directly maps to swimlane ID
        return self.get_swimlane_by_id(status)

    def can_transition(self, from_status: str, to_status: str) -> bool:
        """Check if a status transition is allowed."""
        from_status = from_status.lower()
        to_status = to_status.lower()

        allowed_targets = self.transitions.get(from_status, [])
        return to_status in allowed_targets

    def get_workflow_transitions(self) -> WorkflowTransitions:
        """Convert to WorkflowTransitions object."""
        return WorkflowTransitions(transitions=self.transitions)

    def get_valid_statuses(self) -> List[str]:
        """Get list of valid status IDs from swimlanes."""
        return [swimlane.id for swimlane in self.swimlanes]
    
    def is_valid_status(self, status: str) -> bool:
        """Check if a status is valid."""
        return status.lower() in [s.lower() for s in self.get_valid_statuses()]

    @classmethod
    def create_default(cls, strict_workflow: bool = False) -> "Board":
        """Create a default board configuration.
        
        Args:
            strict_workflow: If True, use traditional linear workflow.
                           If False, use more flexible transitions.
        """
        swimlanes = [
            Swimlane(id="backlog", name="Backlog"),
            Swimlane(id="todo", name="To Do"),
            Swimlane(id="in_progress", name="In Progress", limit=3),
            Swimlane(id="review", name="Review", limit=2),
            Swimlane(id="done", name="Done"),
        ]
        
        if strict_workflow:
            # Traditional linear workflow
            transitions = {
                "backlog": ["todo"],
                "todo": ["in_progress", "backlog"],
                "in_progress": ["review", "todo", "backlog"],
                "review": ["done", "in_progress"],
                "done": ["backlog"],  # Only allow reopening to backlog
            }
        else:
            # Flexible workflow that accommodates various team practices
            transitions = {
                "backlog": ["todo", "in_progress"],  # Can skip todo
                "todo": ["in_progress", "backlog"],
                "in_progress": ["review", "done", "todo", "backlog"],  # Can skip review
                "review": ["done", "in_progress", "todo"],  # Can go back to todo
                "done": ["backlog", "todo", "in_progress"],  # Direct reopening
            }
        
        return cls(swimlanes=swimlanes, transitions=transitions)
