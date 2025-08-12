"""Utilities for managing comment attachments."""

from pathlib import Path
from typing import List, Optional, Tuple, Union

from gira.models.attachment import AttachmentPointer
from gira.models.comment import Comment
from gira.models.epic import Epic
from gira.models.ticket import Ticket


def get_comment_attachments_dir(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    gira_root: Path
) -> Path:
    """Get the directory path for comment attachments.
    
    Args:
        entity_type: Type of entity (ticket or epic)
        entity_id: Entity ID (e.g., GCM-123 or EPIC-001)
        comment_id: Comment ID
        gira_root: Root directory of Gira project
        
    Returns:
        Path to comment attachments directory
    """
    attachments_dir = gira_root / ".gira" / "attachments"

    if entity_type == "epic":
        return attachments_dir / "epics" / entity_id / "comments" / comment_id
    else:
        return attachments_dir / "tickets" / entity_id / "comments" / comment_id


def list_comment_attachments(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    gira_root: Path
) -> List[AttachmentPointer]:
    """List all attachments for a specific comment.
    
    Args:
        entity_type: Type of entity (ticket or epic)
        entity_id: Entity ID
        comment_id: Comment ID
        gira_root: Root directory of Gira project
        
    Returns:
        List of AttachmentPointer objects
    """
    attachments_dir = get_comment_attachments_dir(
        entity_type, entity_id, comment_id, gira_root
    )

    attachments = []
    if attachments_dir.exists():
        for pointer_file in attachments_dir.glob("*.yml"):
            try:
                attachment = AttachmentPointer.from_file(pointer_file)
                attachments.append(attachment)
            except Exception:
                # Skip invalid pointer files
                continue

    return attachments


def find_comment_in_entity(
    entity: Union[Ticket, Epic],
    comment_id: str
) -> Optional[Comment]:
    """Find a specific comment in a ticket or epic.
    
    Args:
        entity: Ticket or Epic object
        comment_id: Comment ID to find
        
    Returns:
        Comment object if found, None otherwise
    """
    if not entity.comments:
        return None

    for comment in entity.comments:
        if comment.id == comment_id:
            return comment

    return None


def update_comment_attachment_count(
    comment: Comment,
    entity_type: str,
    entity_id: str,
    gira_root: Path
) -> None:
    """Update the attachment count for a comment based on actual files.
    
    Args:
        comment: Comment object to update
        entity_type: Type of entity (ticket or epic)
        entity_id: Entity ID
        gira_root: Root directory of Gira project
    """
    attachments = list_comment_attachments(
        entity_type, entity_id, comment.id, gira_root
    )
    comment.attachment_count = len(attachments)

    # Update the attachments list with filenames
    comment.attachments = [
        att.get_pointer_filename() for att in attachments
    ]


def generate_comment_attachment_key(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    filename: str,
    timestamp: Optional[str] = None
) -> str:
    """Generate object key for comment attachment.
    
    Args:
        entity_type: Type of entity (ticket or epic)
        entity_id: Entity ID
        comment_id: Comment ID
        filename: Original filename
        timestamp: Optional timestamp string
        
    Returns:
        Generated object key for storage
    """
    from datetime import datetime, timezone

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Build path components
    if entity_type == "epic":
        return f"epics/{entity_id}/comments/{comment_id}/{timestamp}_{filename}"
    else:
        return f"tickets/{entity_id}/comments/{comment_id}/{timestamp}_{filename}"


def remove_comment_attachment(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    attachment_filename: str,
    gira_root: Path
) -> bool:
    """Remove an attachment pointer file from a comment.
    
    Args:
        entity_type: Type of entity (ticket or epic)
        entity_id: Entity ID
        comment_id: Comment ID
        attachment_filename: Filename of the attachment pointer
        gira_root: Root directory of Gira project
        
    Returns:
        True if removed successfully, False if not found
    """
    attachments_dir = get_comment_attachments_dir(
        entity_type, entity_id, comment_id, gira_root
    )

    pointer_path = attachments_dir / attachment_filename
    if pointer_path.exists():
        pointer_path.unlink()
        return True

    return False


def get_comment_attachment_stats(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    gira_root: Path
) -> Tuple[int, int]:
    """Get attachment statistics for a comment.
    
    Args:
        entity_type: Type of entity (ticket or epic)
        entity_id: Entity ID
        comment_id: Comment ID
        gira_root: Root directory of Gira project
        
    Returns:
        Tuple of (attachment_count, total_size_bytes)
    """
    attachments = list_comment_attachments(
        entity_type, entity_id, comment_id, gira_root
    )

    count = len(attachments)
    total_size = sum(att.size for att in attachments)

    return count, total_size


# Union already imported above
