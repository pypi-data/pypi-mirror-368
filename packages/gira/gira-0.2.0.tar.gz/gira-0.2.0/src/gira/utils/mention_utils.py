"""Utilities for handling @ mentions in comments."""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from rich.text import Text

from gira.utils.team_utils import load_team


def find_mentions(content: str) -> List[str]:
    """
    Find all @ mentions in content.
    
    Args:
        content: Text content to search for mentions
        
    Returns:
        List of mentions found (without @ prefix)
    """
    # Match @username patterns (alphanumeric, underscore, hyphen)
    # Must be preceded by whitespace or start of string
    # Must be followed by whitespace, punctuation, or end of string
    pattern = r'(?:^|(?<=\s))@([a-zA-Z0-9_-]+)(?=\s|[.,!?;:]|$)'
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches


def resolve_mentions(content: str, project_root: Optional[Path] = None) -> List[Tuple[str, str]]:
    """
    Find and resolve @ mentions to team members.
    
    Args:
        content: Text content with potential mentions
        project_root: Project root path for loading team.json
        
    Returns:
        List of (mention, resolved_email) tuples
    """
    mentions = find_mentions(content)
    if not mentions:
        return []

    # Load team to resolve mentions
    team = load_team(project_root)
    if not team:
        return []

    resolved = []
    for mention in mentions:
        # Try to resolve the mention
        member = team.find_member(mention)
        if member:
            resolved.append((mention, member.email))
        else:
            # Also try with @ prefix in case it's stored that way
            member = team.find_member(f"@{mention}")
            if member:
                resolved.append((mention, member.email))

    return resolved


def format_content_with_mentions(content: str, project_root: Optional[Path] = None) -> Text:
    """
    Format content with highlighted @ mentions.
    
    Args:
        content: Text content with potential mentions
        project_root: Project root path for loading team.json
        
    Returns:
        Rich Text object with formatted mentions
    """
    # Load team to check valid mentions
    team = load_team(project_root)

    # Create a Rich Text object
    text = Text()

    # Pattern to find mentions with their positions
    pattern = r'(@[a-zA-Z0-9_-]+)'
    last_end = 0

    for match in re.finditer(pattern, content):
        # Add text before the mention
        text.append(content[last_end:match.start()])

        mention = match.group(1)
        mention_name = mention[1:]  # Remove @ prefix

        # Check if this is a valid team member mention
        is_valid = False
        if team:
            member = team.find_member(mention_name) or team.find_member(mention)
            is_valid = member is not None

        # Style the mention
        if is_valid:
            # Valid team member - highlight in cyan
            text.append(mention, style="bold cyan")
        else:
            # Unknown mention - keep as plain text but dimmed
            text.append(mention, style="dim")

        last_end = match.end()

    # Add remaining text
    text.append(content[last_end:])

    return text


def get_mentioned_members(content: str, project_root: Optional[Path] = None) -> List[str]:
    """
    Get list of team member emails mentioned in content.
    
    Args:
        content: Text content with potential mentions
        project_root: Project root path for loading team.json
        
    Returns:
        List of email addresses for mentioned team members
    """
    resolved = resolve_mentions(content, project_root)
    return [email for _, email in resolved]
