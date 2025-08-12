"""Team and user management models for Gira projects."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field, field_validator

from gira.models.base import GiraModel, TimestampedModel


class TeamMember(GiraModel):
    """Represents a team member in a Gira project."""

    email: str = Field(
        ...,
        description="Email address (primary identifier)"
    )
    name: str = Field(
        ...,
        description="Display name"
    )
    username: Optional[str] = Field(
        default=None,
        description="Username for mentions and shortcuts"
    )
    role: str = Field(
        default="developer",
        description="Role in the project"
    )
    active: bool = Field(
        default=True,
        description="Whether the member is active"
    )
    joined_at: datetime = Field(
        default_factory=datetime.now,
        description="When the member joined the team"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("role")
    @classmethod
    def lowercase_role(cls, v: str) -> str:
        """Ensure role is lowercase."""
        return v.lower().strip()

    @property
    def display_name(self) -> str:
        """Get display name for the member."""
        return self.name or self.username or self.email.split("@")[0]

    def matches(self, identifier: str) -> bool:
        """Check if identifier matches this member."""
        identifier_lower = identifier.lower()
        return any([
            self.email.lower() == identifier_lower,
            self.username and self.username.lower() == identifier_lower,
            identifier_lower.startswith("@") and
            self.username and self.username.lower() == identifier_lower[1:]
        ])


class Team(TimestampedModel):
    """Team configuration for a Gira project."""

    members: List[TeamMember] = Field(
        default_factory=list,
        description="List of team members"
    )
    aliases: Dict[str, str] = Field(
        default_factory=dict,
        description="Alias mappings to email addresses"
    )
    roles: List[str] = Field(
        default_factory=lambda: ["lead", "developer", "reviewer", "observer"],
        description="Available roles in the project"
    )
    allow_external_assignees: bool = Field(
        default=True,
        description="Allow assignments to non-team members"
    )

    def add_member(self, member: TeamMember) -> None:
        """Add a member to the team."""
        # Check if member already exists
        existing = self.find_member(member.email)
        if existing:
            raise ValueError(f"Member with email {member.email} already exists")

        self.members.append(member)
        self.updated_at = datetime.now()

    def remove_member(self, identifier: str) -> bool:
        """Remove a member by email, username, or alias."""
        member = self.find_member(identifier)
        if member:
            self.members.remove(member)
            # Remove any aliases pointing to this member
            self.aliases = {
                alias: email
                for alias, email in self.aliases.items()
                if email != member.email
            }
            self.updated_at = datetime.now()
            return True
        return False

    def find_member(self, identifier: str) -> Optional[TeamMember]:
        """Find a member by email, username, alias, or @mention."""
        if not identifier:
            return None

        # Check direct member match
        for member in self.members:
            if member.matches(identifier):
                return member

        # Check aliases
        identifier_lower = identifier.lower()
        if identifier_lower in self.aliases:
            email = self.aliases[identifier_lower]
            return self.find_member(email)

        # Check @mention format in aliases
        if identifier_lower.startswith("@"):
            mention_name = identifier_lower[1:]
            if mention_name in self.aliases:
                email = self.aliases[mention_name]
                return self.find_member(email)

        return None

    def is_valid_assignee(self, identifier: str) -> bool:
        """Check if identifier is a valid assignee."""
        if self.allow_external_assignees:
            return True
        return self.find_member(identifier) is not None

    def resolve_assignee(self, identifier: str) -> str:
        """Resolve an identifier to an email address."""
        member = self.find_member(identifier)
        if member:
            return member.email

        # If external assignees allowed and it looks like an email
        if self.allow_external_assignees and "@" in identifier:
            return identifier.lower().strip()

        # Return as-is if external allowed, otherwise raise
        if self.allow_external_assignees:
            return identifier

        raise ValueError(f"Unknown team member: {identifier}")

    def add_alias(self, alias: str, email: str) -> None:
        """Add an alias for a team member."""
        alias_lower = alias.lower().strip()

        # Ensure the email belongs to a team member
        member = self.find_member(email)
        if not member:
            raise ValueError(f"No team member found with email: {email}")

        # Check if alias already exists
        if alias_lower in self.aliases:
            raise ValueError(f"Alias '{alias}' already exists")

        self.aliases[alias_lower] = member.email
        self.updated_at = datetime.now()

    def remove_alias(self, alias: str) -> bool:
        """Remove an alias."""
        alias_lower = alias.lower().strip()
        if alias_lower in self.aliases:
            del self.aliases[alias_lower]
            self.updated_at = datetime.now()
            return True
        return False

    def get_active_members(self) -> List[TeamMember]:
        """Get list of active team members."""
        return [m for m in self.members if m.active]

    def get_members_by_role(self, role: str) -> List[TeamMember]:
        """Get members with a specific role."""
        role_lower = role.lower()
        return [m for m in self.members if m.role.lower() == role_lower]

    def to_display_list(self) -> List[Dict[str, str]]:
        """Convert team to a display-friendly list."""
        result = []
        for member in self.members:
            display = {
                "email": member.email,
                "name": member.name,
                "role": member.role,
                "status": "active" if member.active else "inactive"
            }
            if member.username:
                display["username"] = f"@{member.username}"

            # Find aliases for this member
            member_aliases = [
                f"@{alias}" for alias, email in self.aliases.items()
                if email == member.email
            ]
            if member_aliases:
                display["aliases"] = ", ".join(member_aliases)

            result.append(display)

        return result
