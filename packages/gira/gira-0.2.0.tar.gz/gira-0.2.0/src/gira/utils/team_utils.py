"""Utility functions for team management."""

import json
from pathlib import Path
from typing import Optional, Tuple

from gira.models.team import Team, TeamMember
from gira.utils.project import get_gira_root


def get_team_file_path(base_path: Optional[Path] = None) -> Path:
    """Get the path to the team.json file."""
    if base_path is None:
        base_path = get_gira_root()
    return base_path / ".gira" / "team.json"


def load_team(base_path: Optional[Path] = None) -> Optional[Team]:
    """Load team configuration from team.json."""
    team_file = get_team_file_path(base_path)

    if not team_file.exists():
        return None

    try:
        data = json.loads(team_file.read_text())
        return Team(**data)
    except Exception:
        # Return empty team on error
        return Team()


def save_team(team: Team, base_path: Optional[Path] = None) -> None:
    """Save team configuration to team.json."""
    team_file = get_team_file_path(base_path)
    team_file.parent.mkdir(parents=True, exist_ok=True)
    team_file.write_text(team.to_pretty_json())


def create_default_team(base_path: Optional[Path] = None) -> Team:
    """Create a default team configuration."""
    team = Team()

    # Try to add current user from git config
    # TODO: Implement when git_utils module is available
    # try:
    #     from gira.utils.git_utils import get_user_email, get_user_name
    #
    #     email = get_user_email()
    #     name = get_user_name()
    #
    #     if email:
    #         member = TeamMember(
    #             email=email,
    #             name=name or email.split("@")[0],
    #             role="developer"
    #         )
    #         team.add_member(member)
    # except Exception:
    #     pass

    return team


def find_assignee(identifier: str, base_path: Optional[Path] = None) -> Tuple[Optional[str], Optional[Team]]:
    """Find an assignee identifier and return resolved email.
    
    Returns:
        Tuple of (resolved_email, team) where team may be None if no team.json exists
    """
    if not identifier or identifier.lower() in ["none", "unassigned"]:
        return None, None

    team = load_team(base_path)
    if not team:
        # No team file, return identifier as-is if it looks like email
        if "@" in identifier:
            return identifier.lower().strip(), None
        return identifier, None

    try:
        resolved = team.resolve_assignee(identifier)
        return resolved, team
    except ValueError:
        # Not a valid team member and external assignees not allowed
        return None, team


def validate_assignee(identifier: str, base_path: Optional[Path] = None) -> bool:
    """Check if an identifier is a valid assignee."""
    if not identifier or identifier.lower() in ["none", "unassigned"]:
        return True

    team = load_team(base_path)
    if not team:
        # No team file means any assignee is valid
        return True

    return team.is_valid_assignee(identifier)


def add_team_member(
    email: str,
    name: str,
    username: Optional[str] = None,
    role: str = "developer",
    base_path: Optional[Path] = None
) -> TeamMember:
    """Add a new team member."""
    team = load_team(base_path) or create_default_team(base_path)

    member = TeamMember(
        email=email,
        name=name,
        username=username,
        role=role
    )

    team.add_member(member)
    save_team(team, base_path)

    return member


def remove_team_member(identifier: str, base_path: Optional[Path] = None) -> bool:
    """Remove a team member by identifier."""
    team = load_team(base_path)
    if not team:
        return False

    result = team.remove_member(identifier)
    if result:
        save_team(team, base_path)

    return result


def import_team_from_git_history(base_path: Optional[Path] = None) -> Team:
    """Import team members from git history."""
    team = load_team(base_path) or create_default_team(base_path)

    try:
        import subprocess

        # Get unique authors from git log
        result = subprocess.run(
            ["git", "log", "--pretty=format:%an|%ae"],
            capture_output=True,
            text=True,
            cwd=base_path or Path.cwd()
        )

        if result.returncode == 0:
            seen = set()
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    name, email = line.split("|", 1)
                    email = email.strip().lower()

                    if email and email not in seen:
                        seen.add(email)

                        # Check if member already exists
                        if not team.find_member(email):
                            try:
                                member = TeamMember(
                                    email=email,
                                    name=name.strip(),
                                    role="developer"
                                )
                                team.add_member(member)
                            except Exception:
                                pass

    except Exception:
        pass

    return team


def format_assignee_display(assignee: Optional[str], base_path: Optional[Path] = None) -> str:
    """Format assignee for display, showing name if available."""
    if not assignee:
        return "Unassigned"

    team = load_team(base_path)
    if team:
        member = team.find_member(assignee)
        if member:
            return member.display_name

    # Return email or identifier as-is
    return assignee
