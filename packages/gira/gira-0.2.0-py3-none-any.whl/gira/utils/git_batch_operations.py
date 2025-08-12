"""Optimized batch git operations for performance improvements."""

import logging
import os
import re
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def parse_git_timestamp(timestamp_str: str) -> datetime:
    """Parse git timestamp string to datetime object.
    
    Args:
        timestamp_str: Git format timestamp like "2025-07-28 08:50:33 -0700"
        
    Returns:
        Timezone-aware datetime object in UTC
    """
    # Parse base datetime
    dt = datetime.strptime(timestamp_str[:19], "%Y-%m-%d %H:%M:%S")

    # Extract timezone offset
    tz_str = timestamp_str[20:].strip()
    if tz_str and len(tz_str) >= 5:
        try:
            sign = 1 if tz_str[0] == '+' else -1
            hours = int(tz_str[1:3])
            minutes = int(tz_str[3:5]) if len(tz_str) >= 5 else 0

            # Convert to UTC
            if sign == -1:
                dt = dt + timedelta(hours=hours, minutes=minutes)
            else:
                dt = dt - timedelta(hours=hours, minutes=minutes)
        except (ValueError, IndexError):
            pass

    return dt.replace(tzinfo=timezone.utc)


def extract_ticket_id_from_path(path: str) -> Optional[str]:
    """Extract ticket ID from file path.
    
    Args:
        path: File path like ".gira/board/todo/GCM-123.json"
        
    Returns:
        Ticket ID like "GCM-123" or None
    """
    match = re.search(r'([A-Z]{2,4}-\d+)\.json', path)
    return match.group(1) if match else None


def extract_status_from_path(path: str) -> Optional[str]:
    """Extract status from file path.
    
    Args:
        path: File path containing status directory
        
    Returns:
        Status string or None
    """
    # Match patterns like .gira/board/todo/ or .gira/board/in_progress/
    match = re.search(r'\.gira/board/([^/]+)/', path)
    if match:
        return match.group(1)

    # Handle backlog
    if '.gira/backlog/' in path:
        return 'backlog'

    # Handle archived
    if '.gira/archived/' in path:
        return 'archived'

    return None


def batch_get_ticket_histories(
    ticket_ids: List[str],
    gira_root: Path,
    since_date: Optional[datetime] = None,
    max_parallel: int = 4
) -> Dict[str, List[Dict[str, Any]]]:
    """Get git history for multiple tickets using optimized batch operations.
    
    This function uses a single git log command to fetch all ticket histories
    at once, then parses and groups the results by ticket ID.
    
    Args:
        ticket_ids: List of ticket IDs to fetch history for
        gira_root: Path to gira project root
        since_date: Optional date to limit history (for performance)
        max_parallel: Maximum parallel git operations for fallback
        
    Returns:
        Dictionary mapping ticket ID to list of history entries
    """
    if not ticket_ids:
        return {}

    # Change to gira root directory
    original_cwd = Path.cwd()
    histories: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    try:
        os.chdir(gira_root)

        # Build git log command for batch operation
        cmd = [
            "git", "log",
            "--all",  # Search all branches
            "--name-status",  # Show file operations
            "--format=COMMIT|%H|%ai|%an|%s",  # Custom format for parsing
        ]

        # Add date filter if provided
        if since_date:
            cmd.extend(["--since", since_date.strftime("%Y-%m-%d")])

        # Add path filter for JSON files
        cmd.extend(["--", "**/*.json"])

        logger.debug(f"Running batch git command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"Batch git log failed: {result.stderr}")
            # Fall back to parallel individual operations
            return _parallel_individual_git_logs(ticket_ids, gira_root, max_parallel)

        # Parse batch output
        current_commit = None
        relevant_ticket_ids = set(ticket_ids)

        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('COMMIT|'):
                # Parse commit header
                parts = line.split('|', 4)
                if len(parts) >= 5:
                    current_commit = {
                        'hash': parts[1],
                        'timestamp': parse_git_timestamp(parts[2]),
                        'author': parts[3],
                        'message': parts[4]
                    }
            elif current_commit and line[0] in 'RAMD':
                # Parse file operation
                if line.startswith('R'):  # Rename/move
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        old_path = parts[1]
                        new_path = parts[2]

                        # Check if this affects any of our tickets
                        ticket_id = None
                        for path in [old_path, new_path]:
                            tid = extract_ticket_id_from_path(path)
                            if tid and tid in relevant_ticket_ids:
                                ticket_id = tid
                                break

                        if ticket_id:
                            old_status = extract_status_from_path(old_path)
                            new_status = extract_status_from_path(new_path)

                            if old_status and new_status and old_status != new_status:
                                histories[ticket_id].append({
                                    'from_status': old_status,
                                    'to_status': new_status,
                                    'timestamp': current_commit['timestamp'],
                                    'commit': current_commit['hash'],
                                    'author': current_commit['author'],
                                    'message': current_commit['message']
                                })

                elif line.startswith('A'):  # Added
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        path = parts[1]
                        ticket_id = extract_ticket_id_from_path(path)

                        if ticket_id and ticket_id in relevant_ticket_ids:
                            status = extract_status_from_path(path)
                            if status:
                                histories[ticket_id].append({
                                    'from_status': None,
                                    'to_status': status,
                                    'timestamp': current_commit['timestamp'],
                                    'commit': current_commit['hash'],
                                    'author': current_commit['author'],
                                    'message': current_commit['message']
                                })

        # Sort histories by timestamp (oldest first) for each ticket
        for ticket_id in histories:
            histories[ticket_id].sort(key=lambda x: x['timestamp'])

        # Check for tickets with no history and try individual git log with --follow
        missing_tickets = set(ticket_ids) - set(histories.keys())
        if missing_tickets:
            logger.debug(f"Fetching individual histories for {len(missing_tickets)} tickets with --follow")
            follow_histories = _parallel_individual_git_logs(
                list(missing_tickets), gira_root, max_parallel, use_follow=True
            )
            histories.update(follow_histories)

        return dict(histories)

    finally:
        os.chdir(original_cwd)


def _parallel_individual_git_logs(
    ticket_ids: List[str],
    gira_root: Path,
    max_parallel: int = 4,
    use_follow: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """Fallback to parallel individual git log operations.
    
    This is used when batch operations fail or for tickets that need --follow.
    
    Args:
        ticket_ids: List of ticket IDs to process
        gira_root: Path to gira project root  
        max_parallel: Maximum concurrent git operations
        use_follow: Whether to use --follow flag
        
    Returns:
        Dictionary mapping ticket ID to history
    """
    histories = {}

    def get_single_ticket_history(ticket_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Get history for a single ticket."""
        cmd = [
            "git", "log", "--name-status",
            "--format=COMMIT|%H|%ai|%an|%s",
        ]

        if use_follow:
            cmd.append("--follow")

        cmd.extend(["--", f"**/{ticket_id}.json"])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=gira_root)

            if result.returncode != 0:
                # Try without wildcard
                cmd[-1] = f"{ticket_id}.json"
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=gira_root)

            history = []
            current_commit = None

            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line.startswith('COMMIT|'):
                    parts = line.split('|', 4)
                    if len(parts) >= 5:
                        current_commit = {
                            'hash': parts[1],
                            'timestamp': parse_git_timestamp(parts[2]),
                            'author': parts[3],
                            'message': parts[4]
                        }
                elif current_commit and line[0] in 'RAMD':
                    if line.startswith('R'):  # Rename/move
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            old_path = parts[1]
                            new_path = parts[2]

                            old_status = extract_status_from_path(old_path)
                            new_status = extract_status_from_path(new_path)

                            if old_status and new_status and old_status != new_status:
                                history.append({
                                    'from_status': old_status,
                                    'to_status': new_status,
                                    'timestamp': current_commit['timestamp'],
                                    'commit': current_commit['hash'],
                                    'author': current_commit['author'],
                                    'message': current_commit['message']
                                })
                    elif line.startswith('A'):  # Added
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            path = parts[1]
                            status = extract_status_from_path(path)
                            if status:
                                history.append({
                                    'from_status': None,
                                    'to_status': status,
                                    'timestamp': current_commit['timestamp'],
                                    'commit': current_commit['hash'],
                                    'author': current_commit['author'],
                                    'message': current_commit['message']
                                })

            # Sort by timestamp
            history.sort(key=lambda x: x['timestamp'])
            return ticket_id, history

        except Exception as e:
            logger.error(f"Error getting history for {ticket_id}: {e}")
            return ticket_id, []

    # Process tickets in parallel
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        future_to_ticket = {
            executor.submit(get_single_ticket_history, ticket_id): ticket_id
            for ticket_id in ticket_ids
        }

        for future in as_completed(future_to_ticket):
            ticket_id, history = future.result()
            if history:
                histories[ticket_id] = history

    return histories


def get_batch_ticket_histories_cached(
    ticket_ids: List[str],
    gira_root: Path,
    cache_instance=None,
    no_cache: bool = False,
    since_date: Optional[datetime] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Get ticket histories with caching support.
    
    This function checks cache first, then uses batch operations for
    missing tickets.
    
    Args:
        ticket_ids: List of ticket IDs
        gira_root: Path to gira root
        cache_instance: Optional cache instance to use
        no_cache: Bypass cache if True
        since_date: Optional date filter
        
    Returns:
        Dictionary mapping ticket ID to history
    """
    if no_cache or not cache_instance:
        # Direct batch fetch without cache
        return batch_get_ticket_histories(ticket_ids, gira_root, since_date)

    # Check cache first
    cached_histories = {}
    missing_tickets = []

    for ticket_id in ticket_ids:
        cached = cache_instance.get_history(ticket_id)
        if cached is not None:
            cached_histories[ticket_id] = cached
        else:
            missing_tickets.append(ticket_id)

    # Batch fetch missing tickets
    if missing_tickets:
        new_histories = batch_get_ticket_histories(missing_tickets, gira_root, since_date)

        # Cache new results
        for ticket_id, history in new_histories.items():
            if history:  # Only cache if we got history
                cache_instance.set_history(ticket_id, history)

        # Combine results
        cached_histories.update(new_histories)

    return cached_histories
