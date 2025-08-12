"""
Blame output JSON schema documentation and utilities.

This module provides the schema definition and validation utilities for the
JSON output of the 'gira blame' command. The schema ensures consistent,
machine-readable output that can be reliably consumed by tools and AI agents.

Schema Version: 1.0
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from gira.models.ticket import TicketStatus, TicketType


class BlameLineRange(BaseModel):
    """Line range specification."""
    start: int = Field(..., ge=1, description="Starting line number (1-based)")
    end: int = Field(..., ge=1, description="Ending line number (1-based)")
    
    model_config = ConfigDict(extra="forbid")
    
    @field_validator('end')
    @classmethod
    def end_must_be_gte_start(cls, v: int, info) -> int:
        """Ensure end >= start."""
        if 'start' in info.data and v < info.data['start']:
            raise ValueError('end must be >= start')
        return v


class BlameTicketInfo(BaseModel):
    """Information about a ticket found in blame results."""
    title: str = Field(..., min_length=1, description="Ticket title")
    status: TicketStatus = Field(..., description="Current ticket status")
    type: TicketType = Field(..., description="Ticket type")
    lines_affected: List[List[int]] = Field(..., description="List of [start, end] line ranges")
    total_lines: int = Field(..., ge=0, description="Total number of lines affected")
    last_modified: Optional[datetime] = Field(None, description="Last modification timestamp")
    commits: List[str] = Field(..., description="List of commit SHAs")
    
    model_config = ConfigDict(extra="forbid", use_enum_values=True)
    
    @field_validator('lines_affected')
    @classmethod
    def validate_line_ranges(cls, v: List[List[int]]) -> List[List[int]]:
        """Validate line range format."""
        for range_pair in v:
            if len(range_pair) != 2:
                raise ValueError('Each line range must be [start, end]')
            if range_pair[0] < 1 or range_pair[1] < 1:
                raise ValueError('Line numbers must be >= 1')
            if range_pair[0] > range_pair[1]:
                raise ValueError('Start line must be <= end line')
        return v
    
    @field_validator('commits')
    @classmethod
    def validate_commits(cls, v: List[str]) -> List[str]:
        """Validate commit SHAs (accepts both short 7+ and full 40 char SHAs)."""
        import re
        sha_pattern = re.compile(r'^[0-9a-f]{7,40}$', re.IGNORECASE)
        for commit in v:
            if not sha_pattern.match(commit):
                raise ValueError(f'Invalid commit SHA: {commit}')
        return v


class BlameFileResult(BaseModel):
    """Blame results for a single file."""
    file: str = Field(..., min_length=1, description="Path to the analyzed file")
    range: Optional[BlameLineRange] = Field(None, description="Optional line range filter")
    tickets: Dict[str, BlameTicketInfo] = Field(default_factory=dict, description="Tickets keyed by ID")
    
    model_config = ConfigDict(extra="forbid")
    
    @field_validator('tickets')
    @classmethod
    def validate_ticket_ids(cls, v: Dict[str, BlameTicketInfo]) -> Dict[str, BlameTicketInfo]:
        """Validate ticket ID format."""
        import re
        ticket_pattern = re.compile(r'^[A-Z]+-\d+$')
        for ticket_id in v.keys():
            if not ticket_pattern.match(ticket_id):
                raise ValueError(f'Invalid ticket ID format: {ticket_id}')
        return v


class BlameSummary(BaseModel):
    """Summary statistics for blame results."""
    total_files: int = Field(..., ge=0, description="Number of files analyzed")
    unique_tickets: List[str] = Field(..., description="All unique ticket IDs found")
    ticket_count: int = Field(..., ge=0, description="Count of unique tickets")
    
    model_config = ConfigDict(extra="forbid")
    
    @field_validator('unique_tickets')
    @classmethod
    def validate_unique_tickets(cls, v: List[str], info) -> List[str]:
        """Ensure ticket count matches unique tickets length."""
        if 'ticket_count' in info.data and len(v) != info.data['ticket_count']:
            raise ValueError('ticket_count must match length of unique_tickets')
        return v


class BlameOutput(BaseModel):
    """Complete blame command JSON output structure."""
    files: List[BlameFileResult] = Field(..., description="Analyzed files with ticket information")
    summary: BlameSummary = Field(..., description="Aggregate statistics")
    
    model_config = ConfigDict(extra="forbid")


# Schema documentation as a string for inclusion in help text
BLAME_JSON_SCHEMA_DOC = """
Blame JSON Output Schema
========================

The JSON output follows a structured schema designed for reliable parsing:

{
  "files": [
    {
      "file": "src/example.py",
      "range": {                    // Optional: only present if -L was used
        "start": 10,
        "end": 20
      },
      "tickets": {
        "GCM-123": {
          "title": "Implement new feature",
          "status": "done",
          "type": "feature",
          "lines_affected": [[10, 15], [18, 20]],
          "total_lines": 8,
          "last_modified": "2025-01-20T10:30:00",
          "commits": ["abc1234", "def4567"]
        }
      }
    }
  ],
  "summary": {
    "total_files": 1,
    "unique_tickets": ["GCM-123"],
    "ticket_count": 1
  }
}

Field Descriptions:
- files: Array of analyzed files with their ticket information
- file: Path to the analyzed file
- range: Optional line range if -L option was used
- tickets: Map of ticket IDs to their detailed information
- lines_affected: Array of [start, end] line ranges
- last_modified: ISO 8601 timestamp or null
- commits: Array of commit SHAs that reference the ticket
- summary: Aggregate statistics across all files
"""


def get_example_output() -> BlameOutput:
    """
    Get an example of valid blame output as a Pydantic model.
    
    This can be used for testing or documentation purposes.
    """
    return BlameOutput(
        files=[
            BlameFileResult(
                file="src/gira/commands/ticket/blame.py",
                tickets={
                    "GCM-572": BlameTicketInfo(
                        title="Implement blame CLI command",
                        status=TicketStatus.DONE,
                        type=TicketType.FEATURE,
                        lines_affected=[[1, 50], [100, 150]],
                        total_lines=101,
                        last_modified=datetime.fromisoformat("2025-01-21T14:30:00"),
                        commits=["a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0", "1234567890abcdef1234567890abcdef12345678"]
                    ),
                    "GCM-573": BlameTicketInfo(
                        title="Add unit tests for blame",
                        status=TicketStatus.DONE,
                        type=TicketType.SUBTASK,
                        lines_affected=[[51, 99]],
                        total_lines=49,
                        last_modified=datetime.fromisoformat("2025-01-21T16:00:00"),
                        commits=["fedcba0987654321fedcba0987654321fedcba09"]
                    )
                }
            )
        ],
        summary=BlameSummary(
            total_files=1,
            unique_tickets=["GCM-572", "GCM-573"],
            ticket_count=2
        )
    )


def validate_blame_output(data: Dict[str, Any]) -> bool:
    """
    Validate blame output using Pydantic model.
    
    Returns True if data conforms to the schema, False otherwise.
    """
    try:
        BlameOutput(**data)
        return True
    except Exception:
        return False


def generate_json_schema() -> Dict[str, Any]:
    """
    Generate JSON Schema from the Pydantic model.
    
    This can replace the manually maintained JSON schema file.
    """
    return BlameOutput.model_json_schema()