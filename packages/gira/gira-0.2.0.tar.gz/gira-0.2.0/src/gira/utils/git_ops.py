"""Git operations utilities for Gira.

This module provides shared Git operations for file management,
ensuring consistent Git integration across all Gira commands.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Union

from gira.utils.config import load_config, save_config
from gira.utils.console import console


def is_file_tracked(file_path: Path, root: Path) -> bool:
    """Check if a file is tracked by git.
    
    Args:
        file_path: File path to check
        root: Project root path
        
    Returns:
        True if file is tracked, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(file_path)],
            capture_output=True,
            text=True,
            cwd=root,
        )
        return result.returncode == 0
    except Exception:
        return False


def should_use_git(
    root: Path,
    git_flag: Optional[bool] = None,
    operation: str = "move"
) -> bool:
    """Determine if git operations should be used based on flags, config, and repo state.
    
    Priority order:
    1. Command-line flag (--git/--no-git)
    2. Environment variable (GIRA_AUTO_GIT_MV)
    3. Config file setting (git.auto_stage_<operation>)
    4. Auto-detection (one-time check if .gira is tracked)
    
    For AI agents: Set GIRA_AUTO_GIT_MV=true to always use git operations.
    
    Args:
        root: Project root path
        git_flag: Explicit command-line flag
        operation: Type of operation ("move", "archive", "delete")
        
    Returns:
        Whether to use git operations
    """
    # 1. Command-line flag has highest priority
    if git_flag is not None:
        return git_flag

    # 2. Check environment variable (useful for AI agents)
    env_var = os.getenv("GIRA_AUTO_GIT_MV", "").lower()
    if env_var in ("true", "1", "yes", "on"):
        return True
    elif env_var in ("false", "0", "no", "off"):
        return False

    # 3. Check config file
    config = load_config()
    config_key = f"auto_stage_{operation}s"

    # Check nested format first (git.auto_stage_*)
    git_config = config.get("git", {})
    if isinstance(git_config, dict):
        auto_stage = git_config.get(config_key)
        if auto_stage is not None:
            return auto_stage

    # Check flat format (git.auto_stage_*)
    flat_key = f"git.{config_key}"
    if flat_key in config:
        return config[flat_key]

    # 4. One-time auto-detection
    try:
        # Check if we're in a git repository first
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            cwd=root,
        )

        # Check if the .gira directory is tracked by git
        gira_dir = root / ".gira"
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(gira_dir)],
            capture_output=True,
            text=True,
            cwd=root,
        )
        is_tracked = result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repo or git not available
        is_tracked = False

    # Save the result to the config for next time
    # Save in nested format
    if "git" not in config:
        config["git"] = {}
    config["git"][config_key] = is_tracked

    # Also save in flat format for compatibility
    flat_key = f"git.{config_key}"
    config[flat_key] = is_tracked

    try:
        save_config(config)
    except Exception:
        # If we can't save config, just continue
        pass

    return is_tracked


def git_move(
    source: Path,
    destination: Path,
    root: Path,
    silent: bool = False
) -> Tuple[bool, Optional[str]]:
    """Move a file using git mv.
    
    Args:
        source: Source file path
        destination: Destination file path
        root: Project root path
        silent: Whether to suppress warning messages
        
    Returns:
        Tuple of (success, error_message)
    """
    # Ensure destination directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Check if source file exists
    if not source.exists():
        return False, f"Source file not found: {source}"

    # Check if file is tracked, if not, add it first
    if not is_file_tracked(source, root):
        add_success, add_error = git_add(source, root, silent=True)
        if not add_success:
            if not silent:
                console.print(f"[yellow]Warning:[/yellow] Failed to add file to git: {add_error}")
            return False, f"Failed to add file to git: {add_error}"
        if not silent:
            console.print(f"[dim]Added {source.name} to git tracking[/dim]")

    try:
        result = subprocess.run(
            ["git", "mv", str(source), str(destination)],
            capture_output=True,
            text=True,
            check=True,
            cwd=root
        )

        # Check for warnings in stderr
        if result.stderr and "warning" not in result.stderr.lower() and not silent:
            console.print(f"[yellow]Warning:[/yellow] git mv reported: {result.stderr.strip()}")

        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else f"Command failed with exit code {e.returncode}"

        # Provide helpful context based on common failure reasons
        if not silent:
            if "not under version control" in error_msg.lower() or "fatal: not in a git repository" in error_msg.lower():
                # This should not happen anymore since we auto-add, but keep for safety
                console.print("[yellow]Warning:[/yellow] git mv failed - file tracking issue")
            elif "outside repository" in error_msg.lower():
                console.print("[yellow]Warning:[/yellow] Cannot use git mv - .gira directory is outside the git repository")
            elif "permission denied" in error_msg.lower():
                console.print("[yellow]Warning:[/yellow] Cannot use git mv - permission denied")
            else:
                console.print(f"[yellow]Warning:[/yellow] git mv failed: {error_msg}")

        return False, error_msg


def git_remove(
    file_path: Path,
    root: Path,
    silent: bool = False
) -> Tuple[bool, Optional[str]]:
    """Remove a file using git rm.
    
    Args:
        file_path: File path to remove
        root: Project root path
        silent: Whether to suppress warning messages
        
    Returns:
        Tuple of (success, error_message)
    """
    if not file_path.exists():
        return True, None  # Already removed

    try:
        result = subprocess.run(
            ["git", "rm", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=root
        )

        if result.stderr and "warning" not in result.stderr.lower() and not silent:
            console.print(f"[yellow]Warning:[/yellow] git rm reported: {result.stderr.strip()}")

        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else f"Command failed with exit code {e.returncode}"

        if not silent:
            if "not under version control" in error_msg.lower():
                console.print("[yellow]Warning:[/yellow] Cannot use git rm - file is not tracked by git")
            else:
                console.print(f"[yellow]Warning:[/yellow] git rm failed: {error_msg}")

        return False, error_msg


def git_add(
    file_path: Path,
    root: Path,
    silent: bool = False
) -> Tuple[bool, Optional[str]]:
    """Add a file to git staging.
    
    Args:
        file_path: File path to add
        root: Project root path
        silent: Whether to suppress warning messages
        
    Returns:
        Tuple of (success, error_message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    try:
        result = subprocess.run(
            ["git", "add", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=root
        )

        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else f"Command failed with exit code {e.returncode}"

        if not silent:
            console.print(f"[yellow]Warning:[/yellow] git add failed: {error_msg}")

        return False, error_msg


def move_with_git_fallback(
    source: Path,
    destination: Path,
    root: Path,
    use_git: bool = True,
    silent: bool = False
) -> Path:
    """Move a file with git mv, falling back to regular move if needed.
    
    Args:
        source: Source file path
        destination: Destination file path
        root: Project root path
        use_git: Whether to attempt git mv
        silent: Whether to suppress warning messages
        
    Returns:
        The destination path
    """
    if use_git:
        success, _ = git_move(source, destination, root, silent)
        if success:
            return destination

        # Fall back to regular move
        if not silent:
            console.print("[dim]Using regular file move instead[/dim]")

    # Regular move
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source != destination and source.exists():
        source.rename(destination)

    return destination


def remove_with_git_fallback(
    file_path: Path,
    root: Path,
    use_git: bool = True,
    silent: bool = False
) -> bool:
    """Remove a file with git rm, falling back to regular delete if needed.
    
    Args:
        file_path: File path to remove
        root: Project root path
        use_git: Whether to attempt git rm
        silent: Whether to suppress warning messages
        
    Returns:
        Whether the file was removed
    """
    if use_git:
        success, _ = git_remove(file_path, root, silent)
        if success:
            return True

        # Fall back to regular delete
        if not silent:
            console.print("[dim]Using regular file delete instead[/dim]")

    # Regular delete
    if file_path.exists():
        file_path.unlink()

    return True


def commit_changes(
    repo_path: Path,
    files: List[Union[str, Path]],
    message: str,
    silent: bool = False
) -> None:
    """Commit changes to git repository.
    
    Args:
        repo_path: Path to the repository root
        files: List of files to stage and commit (relative to repo root)
        message: Commit message
        silent: Whether to suppress output
        
    Raises:
        subprocess.CalledProcessError: If git commands fail
    """
    # Convert paths to strings
    file_paths = [str(f) for f in files]

    try:
        # Stage files
        result = subprocess.run(
            ["git", "add"] + file_paths,
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True,
        )

        if result.stderr and not silent:
            console.print(f"[yellow]Warning:[/yellow] git add: {result.stderr.strip()}")

        # Commit changes
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True,
        )

        if result.stderr and not silent:
            console.print(f"[yellow]Warning:[/yellow] git commit: {result.stderr.strip()}")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else f"Command failed with exit code {e.returncode}"
        if not silent:
            console.print(f"[red]Git operation failed:[/red] {error_msg}")
        raise
