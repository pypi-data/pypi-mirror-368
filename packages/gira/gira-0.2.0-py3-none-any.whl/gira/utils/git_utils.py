"""Git integration utilities for linking commits to tickets."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

from gira.utils.cache import cached_git_operation
from gira.utils.project import get_gira_root


@dataclass
class CommitInfo:
    """Information about a Git commit."""

    sha: str
    author: str
    date: datetime
    subject: str
    body: Optional[str] = None
    ticket_ids: List[str] = field(default_factory=list)

    @property
    def short_sha(self) -> str:
        """Return abbreviated SHA (7 characters)."""
        return self.sha[:7]

    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.short_sha} - {self.subject} ({self.author}, {self.date.strftime('%Y-%m-%d')})"


def extract_ticket_ids_from_message(
    message: str,
    patterns: Optional[List[str]] = None,
    project_root: Optional[Path] = None
) -> List[str]:
    """
    Extract ticket IDs from a commit message using configurable patterns.
    
    Args:
        message: The commit message to parse
        patterns: List of regex patterns to use. If None, uses default patterns.
        project_root: Project root to load prefix history. If None, uses current root.
        
    Returns:
        List of unique ticket IDs found in the message
    """
    if patterns is None:
        # Try to use prefix history for dynamic patterns
        if project_root is None:
            project_root = get_gira_root()

        if project_root:
            from gira.utils.prefix_history import PrefixHistory
            history = PrefixHistory(project_root)
            history_patterns = history.generate_regex_patterns()

            if history_patterns:
                patterns = history_patterns
            else:
                # Default patterns based on .gitmessage format
                patterns = [
                    r"^\w+\(([^)]+)\):",  # feat(GCM-123): style in subject
                    r"Gira:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Gira: GCM-123, GCM-456 in body
                    r"Ticket:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Ticket: GCM-123 in body
                    r"Closes:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Closes: GCM-123 in body
                    r"Fixes:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Fixes: GCM-123 in body
                ]
        else:
            # Default patterns if no project root
            patterns = [
                r"^\w+\(([^)]+)\):",  # feat(GCM-123): style in subject
                r"Gira:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Gira: GCM-123, GCM-456 in body
                r"Ticket:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Ticket: GCM-123 in body
                r"Closes:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Closes: GCM-123 in body
                r"Fixes:\s*([\w-]+(?:,\s*[\w-]+)*)",  # Fixes: GCM-123 in body
            ]

    ticket_ids: Set[str] = set()

    for pattern in patterns:
        try:
            regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            matches = regex.findall(message)

            for match in matches:
                # Handle comma-separated IDs (e.g., "GCM-123, GCM-456")
                if "," in match:
                    ids = [id.strip() for id in match.split(",")]
                    ticket_ids.update(ids)
                else:
                    ticket_ids.add(match.strip())
        except re.error:
            # Skip invalid regex patterns
            continue

    # Filter out empty strings and return sorted list
    return sorted([id for id in ticket_ids if id])


@cached_git_operation(ttl=60)  # Short TTL for git commands that might change frequently
def run_git_command(cmd: List[str], cwd: Optional[Path] = None) -> Optional[str]:
    """
    Run a git command and return the output.
    
    Args:
        cmd: Command arguments (e.g., ['git', 'log', '--oneline'])
        cwd: Working directory for the command
        
    Returns:
        Command output as string, or None if command failed
    """
    try:
        if cwd is None:
            cwd = get_gira_root() or Path.cwd()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def parse_commit_info(commit_data: str) -> Optional[CommitInfo]:
    """
    Parse git log output into CommitInfo object.
    
    Expected format (from git log --pretty=format):
    SHA|AUTHOR|DATE|SUBJECT
    BODY (if --pretty=format includes %b)
    """
    lines = commit_data.strip().split('\n')
    if not lines:
        return None

    # Parse the first line with commit metadata
    parts = lines[0].split('|', 3)
    if len(parts) < 4:
        return None

    sha, author, date_str, subject = parts

    try:
        # Parse the date
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        # Fallback for different date formats
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            date = datetime.now()

    # Get the body if present (remaining lines)
    body = '\n'.join(lines[1:]) if len(lines) > 1 else None

    # Extract ticket IDs from the full message
    full_message = subject
    if body:
        full_message += '\n' + body

    ticket_ids = extract_ticket_ids_from_message(full_message, project_root=get_gira_root())

    return CommitInfo(
        sha=sha,
        author=author,
        date=date,
        subject=subject,
        body=body,
        ticket_ids=ticket_ids
    )


@cached_git_operation()
def get_commits_for_ticket(
    ticket_id: str,
    limit: Optional[int] = None,
    patterns: Optional[List[str]] = None
) -> List[CommitInfo]:
    """
    Get all commits associated with a specific ticket.
    
    Args:
        ticket_id: The ticket ID to search for
        limit: Maximum number of commits to return
        patterns: Custom regex patterns for parsing ticket IDs
        
    Returns:
        List of CommitInfo objects sorted by date (newest first)
    """
    # Use git log with grep to efficiently find commits mentioning the ticket
    # Use -i for case-insensitive search
    cmd = [
        'git', 'log',
        f'--grep={ticket_id}',
        '-i',  # Case-insensitive
        '--all',
        '--pretty=format:%H|%an|%ad|%s%n%b',
        '--date=format:%Y-%m-%d %H:%M:%S %z',
        '--'
    ]

    if limit:
        cmd.insert(2, f'-{limit}')

    output = run_git_command(cmd)
    if not output:
        return []

    # Split by double newline to separate commits
    commit_blocks = output.split('\n\n')
    commits = []

    for block in commit_blocks:
        if not block.strip():
            continue

        commit = parse_commit_info(block)
        if commit:
            # Check if any of the commit's ticket IDs match (case-insensitive)
            ticket_id_upper = ticket_id.upper()
            for commit_ticket_id in commit.ticket_ids:
                if commit_ticket_id.upper() == ticket_id_upper:
                    commits.append(commit)
                    break

    # Sort by date, newest first
    commits.sort(key=lambda c: c.date, reverse=True)

    return commits


@cached_git_operation(ttl=300)  # 5 minutes for recent commits
def get_recent_commits(
    limit: int = 10,
    patterns: Optional[List[str]] = None
) -> List[CommitInfo]:
    """
    Get recent commits with ticket IDs.
    
    Args:
        limit: Maximum number of commits to return
        patterns: Custom regex patterns for parsing ticket IDs
        
    Returns:
        List of recent commits that reference tickets
    """
    cmd = [
        'git', 'log',
        f'-{limit}',
        '--pretty=format:%H|%an|%ad|%s%n%b',
        '--date=format:%Y-%m-%d %H:%M:%S %z',
        '--'
    ]

    output = run_git_command(cmd)
    if not output:
        return []

    commit_blocks = output.split('\n\n')
    commits = []

    for block in commit_blocks:
        if not block.strip():
            continue

        commit = parse_commit_info(block)
        if commit and commit.ticket_ids:  # Only include commits with ticket IDs
            commits.append(commit)

    return commits


def is_git_repository() -> bool:
    """Check if the current directory is inside a Git repository."""
    return run_git_command(['git', 'rev-parse', '--git-dir']) is not None


def get_current_head_sha() -> Optional[str]:
    """Get the current HEAD commit SHA."""
    result = run_git_command(['git', 'rev-parse', 'HEAD'])
    return result.strip() if result else None


def invalidate_git_caches() -> None:
    """
    Invalidate all git-related caches.
    
    This should be called after operations that modify git history,
    such as commits, rebases, or checkouts.
    """
    from gira.utils.cache import clear_git_cache
    clear_git_cache()

    # Also invalidate the specific function caches
    if hasattr(run_git_command, 'invalidate'):
        run_git_command.invalidate()
    if hasattr(get_commits_for_ticket, 'invalidate'):
        get_commits_for_ticket.invalidate()
    if hasattr(get_recent_commits, 'invalidate'):
        get_recent_commits.invalidate()
