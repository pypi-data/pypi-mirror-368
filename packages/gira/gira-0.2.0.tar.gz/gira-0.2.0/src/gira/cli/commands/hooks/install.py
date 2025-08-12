"""Install Git hooks for Gira integration."""

from typing import List, Optional

import typer
from gira.utils.console import console
from rich.prompt import Confirm

from gira.utils.git_utils import is_git_repository
from gira.utils.project import ensure_gira_project

def install(
    hooks: Optional[List[str]] = typer.Option(
        None,
        "--hook",
        "-h",
        help="Specific hooks to install (can be used multiple times). If not specified, installs all available hooks."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing hooks without prompting"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be installed without actually installing"),
) -> None:
    """Install Git hooks for Gira integration.
    
    This command sets up Git hooks to enhance your workflow:
    - commit-msg: Validates commit messages contain ticket IDs
    - prepare-commit-msg: Adds ticket ID template to commit messages
    
    Examples:
        # Install all available hooks
        gira hooks install
        
        # Install specific hooks
        gira hooks install --hook commit-msg --hook prepare-commit-msg
        
        # Preview what would be installed
        gira hooks install --dry-run
        
        # Force overwrite existing hooks
        gira hooks install --force
    """
    root = ensure_gira_project()
    
    # Check if we're in a git repository
    if not is_git_repository():
        console.print("[red]Error:[/red] Not in a Git repository. Initialize Git first with 'git init'.")
        raise typer.Exit(1)
    
    # Available hooks
    available_hooks = {
        "commit-msg": _get_commit_msg_hook_content,
        "prepare-commit-msg": _get_prepare_commit_msg_hook_content,
    }
    
    # Determine which hooks to install
    if hooks:
        # Validate requested hooks
        invalid_hooks = [h for h in hooks if h not in available_hooks]
        if invalid_hooks:
            console.print(f"[red]Error:[/red] Unknown hooks: {', '.join(invalid_hooks)}")
            console.print(f"Available hooks: {', '.join(available_hooks.keys())}")
            raise typer.Exit(1)
        hooks_to_install = hooks
    else:
        hooks_to_install = list(available_hooks.keys())
    
    # Git hooks directory
    git_dir = root / ".git"
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    installed_count = 0
    skipped_count = 0
    
    for hook_name in hooks_to_install:
        hook_path = hooks_dir / hook_name
        
        if dry_run:
            if hook_path.exists():
                console.print(f"[yellow]Would overwrite:[/yellow] {hook_name}")
            else:
                console.print(f"[green]Would install:[/green] {hook_name}")
            continue
        
        # Check if hook already exists
        if hook_path.exists() and not force:
            if not Confirm.ask(f"Hook '{hook_name}' already exists. Overwrite?", default=False):
                console.print(f"[yellow]Skipped:[/yellow] {hook_name}")
                skipped_count += 1
                continue
        
        # Back up existing hook if it exists
        if hook_path.exists():
            backup_path = hook_path.with_suffix(f"{hook_path.suffix}.backup")
            hook_path.rename(backup_path)
            console.print(f"[dim]Backed up existing hook to {backup_path.name}[/dim]")
        
        # Write the hook content
        hook_content = available_hooks[hook_name]()
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)  # Make executable
        
        console.print(f"[green]✓[/green] Installed {hook_name} hook")
        installed_count += 1
    
    if not dry_run:
        if installed_count > 0:
            console.print(f"\n[green]Successfully installed {installed_count} hook(s)[/green]")
            if skipped_count > 0:
                console.print(f"[yellow]Skipped {skipped_count} existing hook(s)[/yellow]")
            
            console.print("\n[dim]The hooks will automatically run during Git operations.[/dim]")
            console.print("[dim]To configure hook behavior, see: gira config set hooks.*[/dim]")
        else:
            console.print("[yellow]No hooks were installed[/yellow]")


def _get_commit_msg_hook_content() -> str:
    """Get the content for the commit-msg hook."""
    return '''#!/usr/bin/env python3
"""Gira commit-msg hook to validate commit messages."""

import json
import re
import sys
from pathlib import Path

def load_config():
    """Load Gira project configuration."""
    # Find .gira directory
    current = Path.cwd()
    while current != current.parent:
        gira_dir = current / ".gira"
        if gira_dir.exists():
            config_file = gira_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            break
        current = current.parent
    return {}

def main():
    """Validate commit message contains a Gira ticket ID."""
    commit_msg_file = sys.argv[1]
    
    # Read the commit message
    with open(commit_msg_file, 'r') as f:
        commit_msg = f.read()
    
    # Skip merge commits and fixup commits
    if commit_msg.startswith(('Merge', 'fixup!', 'squash!')):
        sys.exit(0)
    
    # Load configuration
    config = load_config()
    
    # Check if hook is enabled
    if not config.get('hooks_commit_msg_enabled', True):
        sys.exit(0)
    
    # Get ticket prefix
    ticket_prefix = config.get('ticket_id_prefix', '[A-Z]{2,4}')
    
    # Check if commit message contains a ticket ID
    patterns = [
        rf'\\b{ticket_prefix}-\\d+\\b',  # Basic ticket ID pattern
    ]
    
    # In strict mode, check for conventional commit format
    strict_mode = config.get('hooks_commit_msg_strict', False)
    if strict_mode:
        allowed_types = config.get('hooks_allowed_commit_types', 
                                  ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore'])
        types_pattern = '|'.join(allowed_types)
        
        # Check if message follows conventional format
        conventional_pattern = rf'^({types_pattern})\\({ticket_prefix}-\\d+\\):'
        if not re.match(conventional_pattern, commit_msg):
            print(f"❌ Commit message must follow conventional format: type({ticket_prefix}-XXX): description")
            print(f"   Allowed types: {', '.join(allowed_types)}")
            print(f"   Example: feat({ticket_prefix}-123): add new feature")
            print("")
            print("   Use 'git commit --no-verify' to bypass this check")
            sys.exit(1)
        sys.exit(0)
    
    # Non-strict mode: just check for ticket ID anywhere
    has_ticket_id = False
    for pattern in patterns:
        if re.search(pattern, commit_msg, re.IGNORECASE):
            has_ticket_id = True
            break
    
    if not has_ticket_id:
        print(f"❌ Commit message must include a Gira ticket ID ({ticket_prefix}-XXX)")
        print("   Examples:")
        print(f"   - feat({ticket_prefix}-123): add new feature")
        print(f"   - fix: resolve issue\\n\\nGira: {ticket_prefix}-123")
        print(f"   - [{ticket_prefix}-123] Update documentation")
        print("")
        print("   Use 'git commit --no-verify' to bypass this check")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
'''


def _get_prepare_commit_msg_hook_content() -> str:
    """Get the content for the prepare-commit-msg hook."""
    return '''#!/usr/bin/env python3
"""Gira prepare-commit-msg hook to add ticket ID template."""

import json
import re
import sys
from pathlib import Path

def load_config():
    """Load Gira project configuration."""
    # Find .gira directory
    current = Path.cwd()
    while current != current.parent:
        gira_dir = current / ".gira"
        if gira_dir.exists():
            config_file = gira_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            break
        current = current.parent
    return {}

def main():
    """Add ticket ID template to commit message if not present."""
    commit_msg_file = sys.argv[1]
    commit_type = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # Skip for merge commits, squash, or when using -m flag
    if commit_type in ["merge", "squash"] or (commit_type == "message"):
        sys.exit(0)
    
    # Load configuration
    config = load_config()
    
    # Check if hook is enabled
    if not config.get('hooks_prepare_commit_msg_enabled', True):
        sys.exit(0)
    
    # Read the current commit message
    with open(commit_msg_file, 'r') as f:
        content = f.read()
    
    # Get ticket prefix
    ticket_prefix = config.get('ticket_id_prefix', '[A-Z]{2,4}')
    
    # Check if it already has a ticket ID
    if re.search(rf'\\b{ticket_prefix}-\\d+\\b', content):
        sys.exit(0)
    
    # Check if we should extract from branch
    if not config.get('hooks_auto_ticket_from_branch', True):
        sys.exit(0)
    
    # Try to extract ticket ID from branch name
    try:
        import subprocess
        branch = subprocess.check_output(
            ['git', 'symbolic-ref', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Look for ticket ID in branch name (e.g., feature/GCM-123-description)
        match = re.search(rf'\\b({ticket_prefix}-\\d+)\\b', branch)
        if match:
            ticket_id = match.group(1)
            
            # If the message is empty or just comments, add a template
            lines = content.split('\\n')
            non_comment_lines = [l for l in lines if not l.startswith('#')]
            
            if not any(non_comment_lines):
                # Add template with ticket ID
                template = f"""feat({ticket_id}): 

# Gira: {ticket_id}
"""
                new_content = template + content
                with open(commit_msg_file, 'w') as f:
                    f.write(new_content)
    except:
        # If anything fails, just continue without modification
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()
'''