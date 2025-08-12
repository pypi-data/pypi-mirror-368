"""Configuration models for Gira projects."""

import re
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from gira.models.base import GiraModel, TimestampedModel
from gira.models.attachment import StorageProvider
from gira.models.custom_fields import CustomFieldsConfig
from gira.models.working_hours import WorkingHoursConfig


class StorageConfig(BaseModel):
    """Configuration for attachment storage backends."""
    
    enabled: bool = Field(
        default=False,
        description="Enable attachment storage"
    )
    provider: Optional[StorageProvider] = Field(
        default=None,
        description="Storage provider (s3, gcs, azure, r2, b2)"
    )
    bucket: Optional[str] = Field(
        default=None,
        description="Storage bucket/container name"
    )
    region: Optional[str] = Field(
        default=None,
        description="Storage region (e.g., us-east-1)"
    )
    base_path: Optional[str] = Field(
        default=None,
        description="Base path in bucket for all attachments"
    )
    max_file_size_mb: int = Field(
        default=100,
        ge=1,
        le=5000,
        description="Maximum file size in megabytes"
    )
    allowed_extensions: List[str] = Field(
        default_factory=lambda: [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",  # Images
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",  # Documents
            ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml",  # Text
            ".zip", ".tar", ".gz", ".7z", ".rar",  # Archives
            ".mp4", ".avi", ".mov", ".webm",  # Videos
            ".mp3", ".wav", ".ogg",  # Audio
            ".log", ".dat", ".bin",  # Data files
        ],
        description="Allowed file extensions"
    )
    credential_source: str = Field(
        default="environment",
        pattern=r"^(environment|file|prompt)$",
        description="Where to load credentials from"
    )
    retention_days: Optional[int] = Field(
        default=None,
        ge=1,
        le=3650,  # 10 years max
        description="Default retention period in days"
    )
    
    @field_validator("provider", mode="before")
    @classmethod
    def validate_provider(cls, v: Any) -> Optional[StorageProvider]:
        """Validate and convert provider to enum."""
        if v is None:
            return None
        if isinstance(v, str):
            return StorageProvider.from_string(v)
        return v
    
    @field_validator("bucket")
    @classmethod
    def validate_bucket_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate bucket naming conventions."""
        if v is None:
            return None
            
        # Basic bucket name validation (works for most providers)
        if not v:
            raise ValueError("Bucket name cannot be empty")
        if len(v) < 3 or len(v) > 63:
            raise ValueError("Bucket name must be between 3 and 63 characters")
        if not re.match(r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$", v):
            raise ValueError(
                "Bucket name must start and end with lowercase letter or number, "
                "and can only contain lowercase letters, numbers, dots, and hyphens"
            )
        if ".." in v or ".-" in v or "-." in v:
            raise ValueError("Bucket name cannot contain .., .-, or -.")
            
        return v
    
    @field_validator("base_path")
    @classmethod
    def sanitize_base_path(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize base path."""
        if v is None:
            return None
            
        # Remove leading/trailing slashes
        v = v.strip("/")
        
        # Ensure valid path characters
        if not re.match(r"^[a-zA-Z0-9/_.-]*$", v):
            raise ValueError(
                "Base path can only contain letters, numbers, "
                "forward slashes, dots, hyphens, and underscores"
            )
            
        return v if v else None


class HooksConfig(BaseModel):
    """Configuration for the hook system."""
    
    enabled: bool = Field(
        default=True,
        description="Enable hook execution"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,  # Max 5 minutes
        description="Hook execution timeout in seconds"
    )
    silent: bool = Field(
        default=False,
        description="Suppress hook output messages"
    )
    on_failure: str = Field(
        default="warn",
        pattern=r"^(ignore|warn|fail)$",
        description="What to do when a hook fails: ignore, warn, or fail"
    )


class BlameConfig(BaseModel):
    """Configuration for the git blame feature."""
    
    ticket_patterns: List[str] = Field(
        default_factory=lambda: [
            r"^\w+\(([A-Z]{2,5}-\d+)\):",  # feat(GCM-123): style in subject
            r"(?:Gira|Ticket):\s*([A-Z]{2,5}-\d+(?:,\s*[A-Z]{2,5}-\d+)*)",  # Gira: GCM-123, GCM-456
            r"(?:Closes|Fixes|Resolves):\s*([A-Z]{2,5}-\d+)",  # Closes: GCM-123
            r"#([A-Z]{2,5}-\d+)",  # #GCM-123 anywhere in message
        ],
        description="Regex patterns to extract ticket IDs from commit messages for blame"
    )
    cache_enabled: bool = Field(
        default=True,
        description="Enable caching of blame results for performance"
    )
    history_depth: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of commits to analyze for historical blame"
    )
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "*.md",  # Exclude markdown files
            "test_*",  # Exclude test files
            "*.json",  # Exclude JSON files
            "*.yml",  # Exclude YAML files
            "*.yaml",
            "*.txt",  # Exclude text files
        ],
        description="File patterns to exclude from blame analysis"
    )
    cache_ttl_seconds: int = Field(
        default=900,  # 15 minutes
        ge=60,
        le=86400,  # Max 24 hours
        description="Cache time-to-live in seconds"
    )
    cache_max_size_mb: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum cache size in megabytes"
    )


class ProjectConfig(TimestampedModel):
    """Project-level configuration stored in .gira/config.json."""

    # Project identity
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Project name"
    )
    description: str = Field(
        default="",
        description="Project description"
    )
    ticket_id_prefix: str = Field(
        ...,
        pattern=r"^[A-Z]{2,4}$",
        description="Prefix for ticket IDs (e.g., GIRA)"
    )

    # Versioning
    gira_version: str = Field(
        default="0.2.0",
        description="Gira version used to create this project"
    )

    # Workflow configuration
    workflow_type: Optional[str] = Field(
        default=None,
        description="Workflow template used (scrum, kanban, etc.)"
    )
    statuses: List[str] = Field(
        default_factory=lambda: ["backlog", "todo", "in_progress", "review", "done"],
        description="Available ticket statuses"
    )
    priorities: List[str] = Field(
        default_factory=lambda: ["low", "medium", "high", "critical"],
        description="Available priority levels"
    )
    types: List[str] = Field(
        default_factory=lambda: ["story", "task", "bug", "epic"],
        description="Available ticket types"
    )

    # Behavior settings
    strict_workflow: bool = Field(
        default=False,
        description="Enforce workflow transitions"
    )
    auto_archive_after_days: Optional[int] = Field(
        default=None,
        ge=1,
        le=365,
        description="Archive completed tickets after N days"
    )
    skip_confirmations: bool = Field(
        default=False,
        description="Skip all confirmation prompts for this project"
    )

    # Default values
    default_priority: str = Field(
        default="medium",
        description="Default priority for new tickets"
    )
    default_type: str = Field(
        default="task",
        description="Default type for new tickets"
    )
    default_ticket_status: Optional[str] = Field(
        default=None,
        description="Default initial status for new tickets (e.g., 'backlog', 'todo')"
    )
    
    # Git integration
    commit_id_patterns: List[str] = Field(
        default_factory=lambda: [
            r"^\w+\(([^)]+)\):",  # feat(GCM-123): style
            r"Gira:\s*([\w-]+(?:,\s*[\w-]+)*)"  # Gira: GCM-123, GCM-456
        ],
        description="Regex patterns to extract ticket IDs from commit messages"
    )
    commit_scan_depth: int = Field(
        default=500,
        ge=1,
        le=10000,
        description="Maximum number of commits to scan for ticket references"
    )
    commit_cache_enabled: bool = Field(
        default=True,
        description="Enable caching of commit-to-ticket mappings"
    )
    
    # Git hooks configuration
    hooks_commit_msg_enabled: bool = Field(
        default=True,
        description="Enable commit message validation hook"
    )
    hooks_commit_msg_strict: bool = Field(
        default=False,
        description="Strict mode: require ticket ID in specific format (e.g., type(ID): message)"
    )
    hooks_prepare_commit_msg_enabled: bool = Field(
        default=True,
        description="Enable prepare-commit-msg hook to add ticket ID templates"
    )
    hooks_auto_ticket_from_branch: bool = Field(
        default=True,
        description="Automatically extract ticket ID from branch name"
    )
    hooks_allowed_commit_types: List[str] = Field(
        default_factory=lambda: ["feat", "fix", "docs", "style", "refactor", "test", "chore"],
        description="Allowed commit type prefixes for conventional commits"
    )
    
    # Blame feature configuration
    blame_config: BlameConfig = Field(
        default_factory=BlameConfig,
        description="Configuration for the git blame feature"
    )
    
    # Storage configuration
    storage: StorageConfig = Field(
        default_factory=StorageConfig,
        description="Configuration for attachment storage"
    )
    
    # Custom fields configuration
    custom_fields: CustomFieldsConfig = Field(
        default_factory=CustomFieldsConfig,
        description="Configuration for custom fields"
    )
    
    # Working hours configuration
    working_hours: Optional[WorkingHoursConfig] = Field(
        default=None,
        description="Configuration for working hours calculation"
    )
    
    # Hooks configuration
    hooks: HooksConfig = Field(
        default_factory=HooksConfig,
        description="Configuration for the hook system"
    )

    @field_validator("ticket_id_prefix", mode="before")
    @classmethod
    def uppercase_prefix(cls, v: str) -> str:
        """Ensure prefix is uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("statuses", "priorities", "types")
    @classmethod
    def lowercase_lists(cls, v: List[str]) -> List[str]:
        """Ensure list values are lowercase."""
        return [item.lower().strip() for item in v]

    @classmethod
    def generate_prefix_from_name(cls, project_name: str) -> str:
        """Generate a ticket ID prefix from project name."""
        # Remove special characters and split into words
        words = re.findall(r'[A-Za-z]+', project_name)

        if not words:
            return "PROJ"

        if len(words) == 1:
            # Single word: take up to 4 uppercase letters
            word = words[0].upper()
            return word[:4] if len(word) > 4 else word
        else:
            # Multiple words: take first letter of each word
            prefix = ''.join(word[0].upper() for word in words)
            # Limit to 4 characters
            return prefix[:4]


class UserInfo(GiraModel):
    """User information for the registry."""

    name: str = Field(..., description="User's display name")
    email: str = Field(..., description="User's email address")
    role: Optional[str] = Field(default=None, description="User's role in project")


class GiraConfig(GiraModel):
    """Global Gira configuration stored in ~/.gira/config.json."""

    # User settings
    default_user_name: Optional[str] = Field(
        default=None,
        description="Default name for commits and tickets"
    )
    default_user_email: Optional[str] = Field(
        default=None,
        description="Default email for commits and tickets"
    )

    # Display preferences
    use_emoji: bool = Field(
        default=False,
        description="Use emoji in CLI output"
    )
    color_enabled: bool = Field(
        default=True,
        description="Use colored output"
    )
    render_markdown: bool = Field(
        default=True,
        description="Render Markdown in descriptions"
    )

    # Editor
    editor: Optional[str] = Field(
        default=None,
        description="Preferred editor for long descriptions"
    )

    # AI agent settings
    ai_output_format: str = Field(
        default="json",
        pattern=r"^(json|table|markdown)$",
        description="Output format for AI agents"
    )
    
    # Interaction preferences
    skip_confirmations: bool = Field(
        default=False,
        description="Skip all confirmation prompts (can be overridden with --confirm)"
    )

    # Performance
    index_enabled: bool = Field(
        default=True,
        description="Use index files for performance"
    )

    # Recently used projects
    recent_projects: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Recently accessed project paths"
    )

    def add_recent_project(self, project_path: str) -> None:
        """Add a project to recent list, maintaining max size."""
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
        self.recent_projects.insert(0, project_path)
        self.recent_projects = self.recent_projects[:10]
