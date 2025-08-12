"""Webhook event payload generation for Gira.

Provides standardized event payload generation for various Gira events
to be sent to external webhook endpoints.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from gira.utils.project import get_gira_root


def get_project_name() -> str:
    """Get the project name from git or directory name."""
    try:
        root = get_gira_root()
        if root:
            # Try to get project name from git remote
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract project name from git URL
                if "/" in url:
                    return url.split("/")[-1].replace(".git", "")
            
            # Fallback to directory name
            return root.name
    except Exception:
        pass
    
    return "gira-project"


def create_base_payload(event_type: str) -> Dict[str, Any]:
    """Create base webhook payload with standard metadata."""
    return {
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "gira",
        "project": get_project_name(),
        "data": {}
    }


def build_ticket_webhook_payload(event_type: str, ticket, changes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build webhook payload for ticket events.
    
    Args:
        event_type: Type of event (e.g., 'ticket_created', 'ticket_updated')
        ticket: Ticket model instance
        changes: Optional dictionary of changes for update events
        
    Returns:
        Complete webhook payload
    """
    payload = create_base_payload(event_type)
    
    # Build ticket data
    ticket_data = {
        "id": ticket.id,
        "uuid": ticket.uuid,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "type": ticket.type,
        "priority": ticket.priority,
        "labels": ticket.labels or [],
        "assignee": ticket.assignee,
        "reporter": ticket.reporter,
        "epic_id": ticket.epic_id,
        "parent_id": ticket.parent_id,
        "sprint_id": ticket.sprint_id,
        "story_points": ticket.story_points,
        "due_date": ticket.due_date.isoformat() if ticket.due_date else None,
        "created_at": ticket.created_at.isoformat() + "Z" if ticket.created_at else None,
        "updated_at": ticket.updated_at.isoformat() + "Z" if ticket.updated_at else None,
        "blocked_by": ticket.blocked_by or [],
        "blocks": ticket.blocks or [],
        "attachment_count": ticket.attachment_count,
        "comment_count": ticket.comment_count,
        "custom_fields": ticket.custom_fields or {}
    }
    
    payload["data"]["ticket"] = ticket_data
    
    # Add changes for update events
    if changes:
        payload["data"]["changes"] = changes
    
    return payload


def build_ticket_move_webhook_payload(ticket, old_status: str, new_status: str) -> Dict[str, Any]:
    """Build webhook payload for ticket move events."""
    payload = build_ticket_webhook_payload("ticket_moved", ticket)
    
    # Add move-specific data
    payload["data"]["changes"] = {
        "status": {
            "from": old_status,
            "to": new_status
        }
    }
    
    return payload


def build_sprint_webhook_payload(event_type: str, sprint, changes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build webhook payload for sprint events.
    
    Args:
        event_type: Type of event (e.g., 'sprint_created', 'sprint_completed')
        sprint: Sprint model instance
        changes: Optional dictionary of changes for update events
        
    Returns:
        Complete webhook payload
    """
    payload = create_base_payload(event_type)
    
    # Build sprint data
    sprint_data = {
        "id": sprint.id,
        "name": sprint.name,
        "status": sprint.status,
        "start_date": sprint.start_date.isoformat() if sprint.start_date else None,
        "end_date": sprint.end_date.isoformat() if sprint.end_date else None,
        "tickets": sprint.tickets or [],
        "created_at": sprint.created_at.isoformat() + "Z" if sprint.created_at else None,
        "updated_at": sprint.updated_at.isoformat() + "Z" if sprint.updated_at else None
    }
    
    payload["data"]["sprint"] = sprint_data
    
    # Add changes for update events
    if changes:
        payload["data"]["changes"] = changes
    
    return payload


def build_epic_webhook_payload(event_type: str, epic, changes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build webhook payload for epic events.
    
    Args:
        event_type: Type of event (e.g., 'epic_created', 'epic_updated')
        epic: Epic model instance
        changes: Optional dictionary of changes for update events
        
    Returns:
        Complete webhook payload
    """
    payload = create_base_payload(event_type)
    
    # Build epic data
    epic_data = {
        "id": epic.id,
        "title": epic.title,
        "description": epic.description,
        "status": epic.status,
        "assignee": epic.assignee,
        "reporter": epic.reporter,
        "labels": epic.labels or [],
        "due_date": epic.due_date.isoformat() if epic.due_date else None,
        "created_at": epic.created_at.isoformat() + "Z" if epic.created_at else None,
        "updated_at": epic.updated_at.isoformat() + "Z" if epic.updated_at else None,
        "custom_fields": epic.custom_fields or {}
    }
    
    payload["data"]["epic"] = epic_data
    
    # Add changes for update events
    if changes:
        payload["data"]["changes"] = changes
    
    return payload


def build_comment_webhook_payload(event_type: str, ticket, comment, user: Optional[str] = None) -> Dict[str, Any]:
    """Build webhook payload for comment events.
    
    Args:
        event_type: Type of event (e.g., 'comment_added')
        ticket: Ticket model instance
        comment: Comment content
        user: User who added the comment
        
    Returns:
        Complete webhook payload
    """
    payload = create_base_payload(event_type)
    
    # Add basic ticket info
    payload["data"]["ticket"] = {
        "id": ticket.id,
        "title": ticket.title,
        "status": ticket.status,
        "type": ticket.type,
        "priority": ticket.priority
    }
    
    # Add comment data
    payload["data"]["comment"] = {
        "content": comment,
        "author": user,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return payload


def build_attachment_webhook_payload(event_type: str, ticket, attachment_name: str, 
                                   attachment_size: Optional[int] = None,
                                   user: Optional[str] = None) -> Dict[str, Any]:
    """Build webhook payload for attachment events.
    
    Args:
        event_type: Type of event (e.g., 'attachment_added', 'attachment_removed')
        ticket: Ticket model instance
        attachment_name: Name of the attachment
        attachment_size: Size of the attachment in bytes
        user: User who performed the action
        
    Returns:
        Complete webhook payload
    """
    payload = create_base_payload(event_type)
    
    # Add basic ticket info
    payload["data"]["ticket"] = {
        "id": ticket.id,
        "title": ticket.title,
        "status": ticket.status,
        "type": ticket.type,
        "priority": ticket.priority
    }
    
    # Add attachment data
    payload["data"]["attachment"] = {
        "name": attachment_name,
        "size": attachment_size,
        "user": user,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return payload


def build_bulk_operation_webhook_payload(event_type: str, operation: str, 
                                       tickets: list, results: Dict[str, Any]) -> Dict[str, Any]:
    """Build webhook payload for bulk operations.
    
    Args:
        event_type: Type of event (e.g., 'bulk_update', 'bulk_move')
        operation: Type of bulk operation
        tickets: List of affected tickets
        results: Operation results
        
    Returns:
        Complete webhook payload
    """
    payload = create_base_payload(event_type)
    
    # Add operation data
    payload["data"]["bulk_operation"] = {
        "operation": operation,
        "ticket_count": len(tickets),
        "ticket_ids": [ticket.id for ticket in tickets],
        "results": results,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return payload


def build_project_webhook_payload(event_type: str, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Build webhook payload for project-level events.
    
    Args:
        event_type: Type of event (e.g., 'project_initialized', 'config_updated')
        action: Specific action performed
        details: Additional details about the action
        
    Returns:
        Complete webhook payload
    """
    payload = create_base_payload(event_type)
    
    # Add project action data
    payload["data"]["project_action"] = {
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return payload


# Template-specific payload builders for popular services

def build_slack_payload(base_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transform base payload into Slack-compatible format."""
    event_type = base_payload["event"]
    data = base_payload["data"]
    
    # Build Slack message
    if "ticket" in data:
        ticket = data["ticket"]
        
        if event_type == "ticket_created":
            text = f"🎫 New ticket created: *{ticket['title']}*"
            color = "good"
        elif event_type == "ticket_moved":
            changes = data.get("changes", {})
            status_change = changes.get("status", {})
            text = f"🔄 Ticket moved: *{ticket['title']}* from `{status_change.get('from', 'unknown')}` to `{status_change.get('to', 'unknown')}`"
            color = "warning"
        elif event_type == "ticket_updated":
            text = f"✏️ Ticket updated: *{ticket['title']}*"
            color = "#439FE0"
        else:
            text = f"📋 Ticket {event_type}: *{ticket['title']}*"
            color = "good"
        
        # Build attachment with ticket details
        fields = [
            {"title": "ID", "value": ticket["id"], "short": True},
            {"title": "Status", "value": ticket["status"], "short": True},
            {"title": "Type", "value": ticket["type"], "short": True},
            {"title": "Priority", "value": ticket["priority"], "short": True},
        ]
        
        if ticket["assignee"]:
            fields.append({"title": "Assignee", "value": ticket["assignee"], "short": True})
        
        return {
            "text": text,
            "attachments": [{
                "color": color,
                "fields": fields,
                "footer": "Gira",
                "ts": int(datetime.fromisoformat(base_payload["timestamp"].replace("Z", "+00:00")).timestamp())
            }]
        }
    
    # Default format for other events
    return {
        "text": f"🔔 Gira {event_type} event",
        "attachments": [{
            "color": "good",
            "text": f"Event: {event_type}\nProject: {base_payload['project']}",
            "footer": "Gira",
            "ts": int(datetime.fromisoformat(base_payload["timestamp"].replace("Z", "+00:00")).timestamp())
        }]
    }


def build_discord_payload(base_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transform base payload into Discord webhook format."""
    event_type = base_payload["event"]
    data = base_payload["data"]
    
    if "ticket" in data:
        ticket = data["ticket"]
        
        if event_type == "ticket_created":
            title = "🎫 New Ticket Created"
            color = 0x28a745  # Green
            description = f"**{ticket['title']}**\n{ticket['description'][:200]}{'...' if len(ticket['description']) > 200 else ''}"
        elif event_type == "ticket_moved":
            changes = data.get("changes", {})
            status_change = changes.get("status", {})
            title = "🔄 Ticket Moved"
            color = 0xffc107  # Yellow/Orange
            description = f"**{ticket['title']}**\nFrom `{status_change.get('from')}` to `{status_change.get('to')}`"
        elif event_type == "ticket_updated":
            title = "✏️ Ticket Updated"
            color = 0x17a2b8  # Blue
            description = f"**{ticket['title']}**"
        else:
            title = f"📋 Ticket {event_type.replace('_', ' ').title()}"
            color = 0x6c757d  # Gray
            description = f"**{ticket['title']}**"
        
        fields = [
            {"name": "ID", "value": ticket["id"], "inline": True},
            {"name": "Status", "value": ticket["status"], "inline": True},
            {"name": "Priority", "value": ticket["priority"], "inline": True},
        ]
        
        if ticket.get("assignee"):
            fields.append({"name": "Assignee", "value": ticket["assignee"], "inline": True})
        
        return {
            "embeds": [{
                "title": title,
                "description": description,
                "color": color,
                "fields": fields,
                "footer": {
                    "text": f"Gira • {base_payload['project']}"
                },
                "timestamp": base_payload["timestamp"]
            }]
        }
    
    # Default format for other events
    return {
        "embeds": [{
            "title": f"🔔 Gira {event_type.replace('_', ' ').title()}",
            "description": f"Event occurred in project: {base_payload['project']}",
            "color": 0x6c757d,
            "footer": {"text": "Gira"},
            "timestamp": base_payload["timestamp"]
        }]
    }


def apply_template(payload: Dict[str, Any], template: str) -> Dict[str, Any]:
    """Apply a service-specific template to transform the payload.
    
    Args:
        payload: Base webhook payload
        template: Template name (e.g., 'slack', 'discord')
        
    Returns:
        Transformed payload for the specific service
    """
    if template == "slack":
        return build_slack_payload(payload)
    elif template == "discord":
        return build_discord_payload(payload)
    else:
        # Return original payload for unknown templates
        return payload