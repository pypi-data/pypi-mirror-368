"""Git integration utilities for finding ticket references."""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def find_ticket_references_in_commits(
    ticket_id: str,
    repo_path: Optional[Path] = None,
    limit: int = 50
) -> List[Dict[str, str]]:
    """Find commits that reference a ticket ID.
    
    Args:
        ticket_id: The ticket ID to search for
        repo_path: Path to git repository (defaults to current directory)
        limit: Maximum number of commits to return
        
    Returns:
        List of dicts with 'sha' and 'message' keys
    """
    if repo_path is None:
        repo_path = Path.cwd()

    try:
        # Search for ticket ID in commit messages
        result = subprocess.run(
            ["git", "log", f"--grep={ticket_id}", f"--max-count={limit}", "--pretty=format:%H|%s"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                sha, message = line.split('|', 1)
                commits.append({
                    'sha': sha,
                    'message': message
                })

        return commits

    except (subprocess.SubprocessError, FileNotFoundError):
        # Git not available or not a git repository
        return []
