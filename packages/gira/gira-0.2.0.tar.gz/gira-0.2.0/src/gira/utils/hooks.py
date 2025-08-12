"""Hook system for Gira extensibility.

Provides a simple, script-based hook system that allows users to run custom scripts
on Gira events like ticket creation, updates, moves, etc.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional, Any, List

from gira.utils.config import load_config
from gira.utils.console import console
from gira.utils.project import get_gira_root


class HookExecutor:
    """Executes hooks for Gira events."""
    
    def __init__(self):
        self.root = get_gira_root()
        if not self.root:
            raise ValueError("Not in a Gira project")
        self.hooks_dir = self.root / ".gira" / "hooks"
        self.config = load_config()
    
    def is_enabled(self) -> bool:
        """Check if hooks are enabled in configuration."""
        return self.config.get("hooks", {}).get("enabled", True)
    
    def get_timeout(self) -> int:
        """Get hook timeout in seconds."""
        return self.config.get("hooks", {}).get("timeout", 30)
    
    def get_hook_path(self, hook_name: str) -> Optional[Path]:
        """Get path to a hook script if it exists and is executable."""
        # Try common script extensions
        extensions = ['.sh', '.py', '.js', '.rb', '']
        
        for ext in extensions:
            hook_path = self.hooks_dir / f"{hook_name}{ext}"
            if hook_path.exists() and hook_path.is_file():
                # Check if file is executable
                if os.access(hook_path, os.X_OK):
                    return hook_path
        
        return None
    
    def prepare_environment(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare environment variables for hook execution."""
        env = os.environ.copy()
        
        # Add Gira-specific environment variables
        env.update({
            "GIRA_ROOT": str(self.root),
            "GIRA_HOOKS_DIR": str(self.hooks_dir)
        })
        
        # Add event-specific data with GIRA_ prefix
        for key, value in event_data.items():
            if value is not None:
                env_key = f"GIRA_{key.upper()}"
                env[env_key] = str(value)
        
        return env
    
    def execute_hook(self, hook_name: str, event_data: Dict[str, Any], silent: bool = False) -> bool:
        """Execute a hook if it exists.
        
        Args:
            hook_name: Name of the hook to execute (e.g., 'ticket-created')
            event_data: Dictionary of event data to pass as environment variables
            silent: Whether to suppress output messages
            
        Returns:
            True if hook executed successfully (or didn't exist), False if failed
        """
        if not self.is_enabled():
            return True
        
        hook_path = self.get_hook_path(hook_name)
        if not hook_path:
            return True  # No hook to execute, that's fine
        
        try:
            env = self.prepare_environment(event_data)
            timeout = self.get_timeout()
            
            if not silent:
                console.print(f"[dim]Running hook: {hook_name}[/dim]")
            
            start_time = time.time()
            result = subprocess.run(
                [str(hook_path)],
                env=env,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                if not silent and result.stdout:
                    console.print(f"[dim]Hook output: {result.stdout.strip()}[/dim]")
                return True
            else:
                if not silent:
                    console.print(f"[yellow]Hook {hook_name} failed with exit code {result.returncode}[/yellow]")
                    if result.stderr:
                        console.print(f"[yellow]Error: {result.stderr.strip()}[/yellow]")
                return False
                
        except subprocess.TimeoutExpired:
            if not silent:
                console.print(f"[red]Hook {hook_name} timed out after {timeout} seconds[/red]")
            return False
        except Exception as e:
            if not silent:
                console.print(f"[red]Hook {hook_name} failed: {e}[/red]")
            return False


# Global hook executor instance
_hook_executor = None


def get_hook_executor() -> HookExecutor:
    """Get the global hook executor instance."""
    global _hook_executor
    if _hook_executor is None:
        _hook_executor = HookExecutor()
    return _hook_executor


def execute_hook(hook_name: str, event_data: Dict[str, Any], silent: bool = False) -> bool:
    """Convenience function to execute a hook and deliver webhooks.
    
    Args:
        hook_name: Name of the hook to execute
        event_data: Event data to pass to the hook
        silent: Whether to suppress output
        
    Returns:
        True if successful or no hook exists, False if failed
    """
    # Execute local script hooks
    hook_success = True
    try:
        executor = get_hook_executor()
        hook_success = executor.execute_hook(hook_name, event_data, silent)
    except Exception:
        # If we can't get the executor (e.g., not in a Gira project), just continue
        pass
    
    # Execute webhooks for this event (non-blocking)
    # Note: Specific webhook calls with proper payloads are handled 
    # in individual command files using execute_webhook_for_* functions below
    
    return hook_success


# Common hook event data builders
def build_ticket_event_data(ticket) -> Dict[str, Any]:
    """Build event data dictionary for ticket events."""
    return {
        "ticket_id": ticket.id,
        "ticket_title": ticket.title,
        "ticket_description": ticket.description,
        "ticket_status": ticket.status,
        "ticket_type": ticket.type,
        "ticket_priority": ticket.priority,
        "ticket_assignee": ticket.assignee,
        "ticket_reporter": ticket.reporter,
        "ticket_epic_id": ticket.epic_id,
        "ticket_labels": ",".join(ticket.labels or []),
        "ticket_story_points": ticket.story_points,
        "ticket_created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "ticket_updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
    }


def build_ticket_move_event_data(ticket, old_status: str, new_status: str) -> Dict[str, Any]:
    """Build event data dictionary for ticket move events."""
    data = build_ticket_event_data(ticket)
    data.update({
        "old_status": old_status,
        "new_status": new_status,
    })
    return data


def build_sprint_event_data(sprint) -> Dict[str, Any]:
    """Build event data dictionary for sprint events."""
    return {
        "sprint_id": sprint.id,
        "sprint_name": sprint.name,
        "sprint_status": sprint.status,
        "sprint_start_date": sprint.start_date.isoformat() if sprint.start_date else None,
        "sprint_end_date": sprint.end_date.isoformat() if sprint.end_date else None,
        "sprint_tickets": ",".join(sprint.tickets or []),
    }


def build_epic_event_data(epic) -> Dict[str, Any]:
    """Build event data dictionary for epic events."""
    return {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "epic_description": epic.description,
        "epic_status": epic.status,
        "epic_assignee": epic.assignee,
        "epic_reporter": epic.reporter,
        "epic_labels": ",".join(epic.labels or []),
        "epic_created_at": epic.created_at.isoformat() if epic.created_at else None,
        "epic_updated_at": epic.updated_at.isoformat() if epic.updated_at else None,
    }


# Webhook integration functions

def execute_webhook_for_ticket_created(ticket, silent: bool = True) -> None:
    """Execute webhooks for ticket creation event."""
    try:
        from gira.utils.webhooks import deliver_webhook
        from gira.utils.webhook_events import build_ticket_webhook_payload
        
        payload = build_ticket_webhook_payload("ticket_created", ticket)
        deliver_webhook("ticket_created", payload, silent=silent)
    except Exception:
        # Webhook failures should not affect normal operation
        pass


def execute_webhook_for_ticket_updated(ticket, changes: Optional[Dict[str, Any]] = None, silent: bool = True) -> None:
    """Execute webhooks for ticket update event."""
    try:
        from gira.utils.webhooks import deliver_webhook
        from gira.utils.webhook_events import build_ticket_webhook_payload
        
        payload = build_ticket_webhook_payload("ticket_updated", ticket, changes)
        deliver_webhook("ticket_updated", payload, silent=silent)
    except Exception:
        # Webhook failures should not affect normal operation
        pass


def execute_webhook_for_ticket_moved(ticket, old_status: str, new_status: str, silent: bool = True) -> None:
    """Execute webhooks for ticket move event."""
    try:
        from gira.utils.webhooks import deliver_webhook
        from gira.utils.webhook_events import build_ticket_move_webhook_payload
        
        payload = build_ticket_move_webhook_payload(ticket, old_status, new_status)
        deliver_webhook("ticket_moved", payload, silent=silent)
    except Exception:
        # Webhook failures should not affect normal operation
        pass


def execute_webhook_for_sprint_created(sprint, silent: bool = True) -> None:
    """Execute webhooks for sprint creation event."""
    try:
        from gira.utils.webhooks import deliver_webhook
        from gira.utils.webhook_events import build_sprint_webhook_payload
        
        payload = build_sprint_webhook_payload("sprint_created", sprint)
        deliver_webhook("sprint_created", payload, silent=silent)
    except Exception:
        # Webhook failures should not affect normal operation
        pass


def execute_webhook_for_sprint_completed(sprint, silent: bool = True) -> None:
    """Execute webhooks for sprint completion event."""
    try:
        from gira.utils.webhooks import deliver_webhook
        from gira.utils.webhook_events import build_sprint_webhook_payload
        
        payload = build_sprint_webhook_payload("sprint_completed", sprint)
        deliver_webhook("sprint_completed", payload, silent=silent)
    except Exception:
        # Webhook failures should not affect normal operation
        pass


def execute_webhook_for_epic_created(epic, silent: bool = True) -> None:
    """Execute webhooks for epic creation event."""
    try:
        from gira.utils.webhooks import deliver_webhook
        from gira.utils.webhook_events import build_epic_webhook_payload
        
        payload = build_epic_webhook_payload("epic_created", epic)
        deliver_webhook("epic_created", payload, silent=silent)
    except Exception:
        # Webhook failures should not affect normal operation
        pass


def execute_webhook_for_epic_updated(epic, changes: Optional[Dict[str, Any]] = None, silent: bool = True) -> None:
    """Execute webhooks for epic update event."""
    try:
        from gira.utils.webhooks import deliver_webhook
        from gira.utils.webhook_events import build_epic_webhook_payload
        
        payload = build_epic_webhook_payload("epic_updated", epic, changes)
        deliver_webhook("epic_updated", payload, silent=silent)
    except Exception:
        # Webhook failures should not affect normal operation
        pass