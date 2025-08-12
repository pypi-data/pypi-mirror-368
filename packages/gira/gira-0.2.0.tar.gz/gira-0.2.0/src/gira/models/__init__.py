"""Pydantic models for Gira data structures."""

from gira.models.attachment import AttachmentPointer, StorageProvider
from gira.models.base import GiraModel
from gira.models.board import Board, Swimlane, WorkflowTransitions
from gira.models.comment import Comment
from gira.models.config import GiraConfig, ProjectConfig
from gira.models.epic import Epic, EpicStatus
from gira.models.saved_query import SavedQuery
from gira.models.sprint import Sprint, SprintStatus
from gira.models.team import Team, TeamMember
from gira.models.ticket import Ticket, TicketPriority, TicketStatus, TicketType

# Rebuild models to resolve forward references
Ticket.model_rebuild()

__all__ = [
    "GiraModel",
    "Ticket",
    "TicketStatus",
    "TicketPriority",
    "TicketType",
    "Epic",
    "EpicStatus",
    "Sprint",
    "SprintStatus",
    "Comment",
    "ProjectConfig",
    "GiraConfig",
    "Board",
    "Swimlane",
    "WorkflowTransitions",
    "Team",
    "TeamMember",
    "SavedQuery",
    "AttachmentPointer",
    "StorageProvider",
]
