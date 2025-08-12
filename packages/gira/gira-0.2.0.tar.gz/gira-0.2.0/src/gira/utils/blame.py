"""Git blame utilities for discovering tickets associated with file lines."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from gira.models.config import ProjectConfig
from gira.utils.cache import cached_blame_operation
from gira.utils.git_utils import extract_ticket_ids_from_message, run_git_command
from gira.utils.project import get_gira_root
from gira.utils.ticket_utils import find_ticket


@dataclass
class BlameLine:
    """Information about a single line from git blame."""

    line_number: int
    line_content: str
    commit_sha: str
    author: str
    author_email: str
    timestamp: datetime
    ticket_ids: List[str] = field(default_factory=list)
    is_context: bool = False  # True if this is a context line, not the blamed line

    @property
    def short_sha(self) -> str:
        """Return abbreviated SHA (7 characters)."""
        return self.commit_sha[:7]


@dataclass
class FileBlameResult:
    """Aggregated blame information for a file."""

    file_path: Path
    lines: List[BlameLine]
    tickets: Dict[str, TicketBlameInfo] = field(default_factory=dict)

    def get_lines_for_ticket(self, ticket_id: str) -> List[BlameLine]:
        """Get all lines associated with a specific ticket."""
        return [line for line in self.lines if ticket_id in line.ticket_ids and not line.is_context]

    def get_line_ranges_for_ticket(self, ticket_id: str) -> List[Tuple[int, int]]:
        """Get consolidated line ranges for a ticket."""
        lines_with_ticket = [line.line_number for line in self.lines if ticket_id in line.ticket_ids and not line.is_context]
        if not lines_with_ticket:
            return []

        # Consolidate consecutive lines into ranges
        ranges = []
        start = lines_with_ticket[0]
        end = start

        for line_num in lines_with_ticket[1:]:
            if line_num == end + 1:
                end = line_num
            else:
                ranges.append((start, end))
                start = end = line_num

        ranges.append((start, end))
        return ranges


@dataclass
class TicketBlameInfo:
    """Ticket-centric view of blame information."""

    ticket_id: str
    title: str
    status: str
    type: str
    lines_affected: List[Tuple[int, int]]  # Line ranges
    commits: Set[str] = field(default_factory=set)
    last_modified: Optional[datetime] = None

    def total_lines(self) -> int:
        """Calculate total number of lines affected by this ticket."""
        total = 0
        for start, end in self.lines_affected:
            total += (end - start + 1)
        return total


@dataclass
class HistoryEntry:
    """A single entry in the line history."""

    commit_sha: str
    author: str
    date: datetime
    message: str
    ticket_ids: List[str]
    diff_preview: Optional[str] = None

    @property
    def short_sha(self) -> str:
        """Return abbreviated SHA (7 characters)."""
        return self.commit_sha[:7]


@dataclass
class LineHistory:
    """Historical view of changes to specific lines."""

    file_path: Path
    line_range: Tuple[int, int]
    entries: List[HistoryEntry]
    tickets: Dict[str, TicketBlameInfo] = field(default_factory=dict)


def parse_blame_porcelain(output: str, patterns: Optional[List[str]] = None) -> List[BlameLine]:
    """
    Parse git blame --porcelain output into BlameLine objects.
    
    Args:
        output: Raw output from git blame --porcelain
        patterns: Optional list of regex patterns for ticket extraction
        
    Returns:
        List of BlameLine objects
    """
    lines = []
    current_block = {}
    line_number = 0
    # Cache commit information to reuse for subsequent lines from same commit
    commit_cache = {}

    for line in output.strip().split('\n'):
        if not line:
            continue

        # Start of a new blame block (SHA line_number original_line_number [group_lines])
        if re.match(r'^[0-9a-f]{40}\s+\d+\s+\d+', line):
            parts = line.split()
            sha = parts[0]
            current_block = {
                'sha': sha,
                'line_number': int(parts[1]),
                'original_line': int(parts[2])
            }
            line_number = current_block['line_number']
            
            # If we've seen this commit before, reuse cached info
            if sha in commit_cache:
                current_block.update(commit_cache[sha])

        # Author information
        elif line.startswith('author '):
            current_block['author'] = line[7:]
        elif line.startswith('author-mail '):
            current_block['author_email'] = line[12:].strip('<>')
        elif line.startswith('author-time '):
            current_block['timestamp'] = datetime.fromtimestamp(int(line[12:]))
        elif line.startswith('summary '):
            current_block['summary'] = line[8:]
            # Cache this commit's info for future lines
            commit_cache[current_block['sha']] = {
                'author': current_block.get('author', ''),
                'author_email': current_block.get('author_email', ''),
                'timestamp': current_block.get('timestamp', datetime.now()),
                'summary': current_block['summary']
            }

        # The actual line content (starts with tab)
        elif line.startswith('\t'):
            content = line[1:]  # Remove the tab

            # Extract ticket IDs from the commit summary (now available from cache too)
            ticket_ids = []
            if 'summary' in current_block:
                ticket_ids = extract_ticket_ids_from_message(current_block['summary'], patterns, project_root=get_gira_root())

            blame_line = BlameLine(
                line_number=line_number,
                line_content=content,
                commit_sha=current_block.get('sha', ''),
                author=current_block.get('author', ''),
                author_email=current_block.get('author_email', ''),
                timestamp=current_block.get('timestamp', datetime.now()),
                ticket_ids=ticket_ids
            )
            lines.append(blame_line)

    # Deduplicate lines - if multiple commits affected the same line number,
    # keep only the most recent one (git blame can show multiple entries for the same line)
    line_dict = {}
    for line in lines:
        line_num = line.line_number
        if line_num not in line_dict or line.timestamp > line_dict[line_num].timestamp:
            line_dict[line_num] = line
    
    # Return deduplicated lines sorted by line number
    return sorted(line_dict.values(), key=lambda x: x.line_number)


@cached_blame_operation()
def get_file_blame(
    file_path: Path,
    line_range: Optional[Tuple[int, int]] = None,
    patterns: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
    context: Optional[int] = None,
    no_cache: bool = False
) -> Optional[FileBlameResult]:
    """
    Get blame information for a file with ticket extraction.
    
    Args:
        file_path: Path to the file to blame
        line_range: Optional tuple of (start_line, end_line)
        patterns: Optional list of regex patterns for ticket extraction
        cwd: Working directory for git command
        context: Optional number of context lines to show around blamed lines
        
    Returns:
        FileBlameResult object or None if blame fails
    """
    if cwd is None:
        cwd = get_gira_root() or Path.cwd()

    # Load patterns from config if not provided
    if patterns is None and cwd:
        config_path = cwd / ".gira" / "config.json"
        if config_path.exists():
            try:
                config = ProjectConfig.from_json_file(str(config_path))
                patterns = config.blame_config.ticket_patterns
            except Exception:
                # Fall back to default patterns
                pass

    # Build git blame command
    cmd = ['git', 'blame', '--porcelain']

    # Add line range if specified
    if line_range:
        start, end = line_range
        cmd.extend(['-L', f'{start},{end}'])

    cmd.append(str(file_path))

    # Run git blame
    output = run_git_command(cmd, cwd=cwd)
    if not output:
        return None

    # Parse the blame output
    blame_lines = parse_blame_porcelain(output, patterns)

    # Add context lines if requested
    if context is not None and context > 0:
        blame_lines = _add_context_lines(blame_lines, file_path, context, line_range)

    # Create the result
    result = FileBlameResult(
        file_path=file_path,
        lines=blame_lines
    )

    # Aggregate ticket information
    _aggregate_ticket_info(result, cwd)

    return result


def _aggregate_ticket_info(result: FileBlameResult, cwd: Path) -> None:
    """
    Aggregate ticket information from blame lines.
    
    Args:
        result: FileBlameResult to populate with ticket info
        cwd: Working directory for ticket lookups
    """
    ticket_data: Dict[str, Dict] = {}

    # Collect ticket data from all lines (excluding context lines)
    for line in result.lines:
        if line.is_context:
            continue
        for ticket_id in line.ticket_ids:
            if ticket_id not in ticket_data:
                ticket_data[ticket_id] = {
                    'commits': set(),
                    'last_modified': None,
                    'lines': []
                }

            ticket_data[ticket_id]['commits'].add(line.commit_sha)
            ticket_data[ticket_id]['lines'].append(line.line_number)

            # Update last modified time
            if (ticket_data[ticket_id]['last_modified'] is None or
                line.timestamp > ticket_data[ticket_id]['last_modified']):
                ticket_data[ticket_id]['last_modified'] = line.timestamp

    # Create TicketBlameInfo objects
    for ticket_id, data in ticket_data.items():
        # Try to find the actual ticket for metadata
        ticket, _ = find_ticket(ticket_id, cwd, include_archived=True)

        # Get line ranges
        line_ranges = _consolidate_line_numbers(data['lines'])

        ticket_info = TicketBlameInfo(
            ticket_id=ticket_id,
            title=ticket.title if ticket else f"Unknown ticket {ticket_id}",
            status=ticket.status if ticket else "todo",
            type=ticket.type if ticket else "task",
            lines_affected=line_ranges,
            commits=data['commits'],
            last_modified=data['last_modified']
        )

        result.tickets[ticket_id] = ticket_info


def _consolidate_line_numbers(line_numbers: List[int]) -> List[Tuple[int, int]]:
    """
    Consolidate a list of line numbers into ranges.
    
    Args:
        line_numbers: List of line numbers
        
    Returns:
        List of (start, end) tuples representing ranges
    """
    if not line_numbers:
        return []

    # Sort and remove duplicates
    sorted_lines = sorted(set(line_numbers))

    ranges = []
    start = sorted_lines[0]
    end = start

    for line in sorted_lines[1:]:
        if line == end + 1:
            end = line
        else:
            ranges.append((start, end))
            start = end = line

    ranges.append((start, end))
    return ranges


def _read_file_lines(file_path: Path) -> List[str]:
    """
    Read all lines from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        List of lines (with line endings stripped)
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            return [line.rstrip('\n\r') for line in f]
    except Exception:
        return []


def _add_context_lines(
    blame_lines: List[BlameLine],
    file_path: Path,
    context: int,
    line_range: Optional[Tuple[int, int]] = None
) -> List[BlameLine]:
    """
    Add context lines around blamed lines.
    
    Args:
        blame_lines: Original blamed lines
        file_path: Path to the file
        context: Number of context lines to add
        line_range: Optional line range restriction
        
    Returns:
        List with blame lines and context lines
    """
    if context <= 0 or not blame_lines:
        return blame_lines

    # Read the full file
    file_lines = _read_file_lines(file_path)
    if not file_lines:
        return blame_lines

    # Create a set of blamed line numbers for quick lookup
    blamed_line_nums = {line.line_number for line in blame_lines}

    # Determine which lines to include as context
    context_line_nums = set()

    # If we have a line range, we need to also consider context lines outside the range
    if line_range:
        # Add context before the range
        for i in range(max(1, line_range[0] - context), line_range[0]):
            context_line_nums.add(i)

        # Add context after the range
        for i in range(line_range[1] + 1, min(len(file_lines) + 1, line_range[1] + context + 1)):
            context_line_nums.add(i)

    # Add context around each blamed line
    for line in blame_lines:
        line_num = line.line_number

        # Add context before
        for i in range(max(1, line_num - context), line_num):
            context_line_nums.add(i)

        # Add context after
        for i in range(line_num + 1, min(len(file_lines) + 1, line_num + context + 1)):
            context_line_nums.add(i)

    # Remove any line numbers that are already blamed
    context_line_nums -= blamed_line_nums

    # Create context line objects
    context_lines = []
    for line_num in context_line_nums:
        if 1 <= line_num <= len(file_lines):
            context_lines.append(BlameLine(
                line_number=line_num,
                line_content=file_lines[line_num - 1],
                commit_sha='',
                author='',
                author_email='',
                timestamp=datetime.min,
                ticket_ids=[],
                is_context=True
            ))

    # Merge and sort all lines
    all_lines = blame_lines + context_lines
    all_lines.sort(key=lambda x: x.line_number)

    return all_lines


def parse_line_range(line_spec: str) -> Optional[Tuple[int, int]]:
    """
    Parse a line range specification.
    
    Supports formats:
    - "10,20" -> lines 10 to 20
    - "10,+5" -> lines 10 to 15 (10 + 5)
    - "10" -> just line 10
    
    Args:
        line_spec: Line specification string
        
    Returns:
        Tuple of (start, end) or None if invalid
    """
    line_spec = line_spec.strip()

    # Single line number
    if re.match(r'^\d+$', line_spec):
        line_num = int(line_spec)
        return (line_num, line_num)

    # Range with comma
    if ',' in line_spec:
        parts = line_spec.split(',', 1)
        if len(parts) != 2:
            return None

        try:
            start = int(parts[0])

            # Handle +N format
            if parts[1].startswith('+'):
                count = int(parts[1][1:])
                return (start, start + count - 1)
            else:
                end = int(parts[1])
                return (start, end)
        except ValueError:
            return None

    return None


@cached_blame_operation()
def get_line_history(
    file_path: Path,
    line_range: Tuple[int, int],
    patterns: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
    max_entries: int = 50,
    no_cache: bool = False
) -> Optional[LineHistory]:
    """
    Get the historical changes to specific lines using git log -L.
    
    Args:
        file_path: Path to the file
        line_range: Tuple of (start, end) line numbers
        patterns: Optional list of regex patterns for ticket extraction
        cwd: Working directory for git command
        max_entries: Maximum number of history entries to return
        
    Returns:
        LineHistory object with all historical changes
    """
    if cwd is None:
        cwd = get_gira_root()

    # Format for git log -L
    start, end = line_range

    # Run git log -L command
    cmd = [
        'git', 'log', f'-L{start},{end}:{file_path}',
        '--pretty=format:COMMIT:%H%nAUTHOR:%an%nDATE:%ad%nMESSAGE:%s%nBODY:%b%nEND_COMMIT',
        '--date=iso',
        f'-{max_entries}'
    ]

    result = run_git_command(cmd, cwd=cwd)
    if result is None:
        return None

    # Parse the output
    entries = []
    tickets_map = {}
    lines = result.strip().split('\n')
    i = 0

    while i < len(lines):
        # Look for commit info
        if lines[i].startswith('COMMIT:'):
            commit_sha = lines[i][7:]
            i += 1

            # Parse author
            if i < len(lines) and lines[i].startswith('AUTHOR:'):
                author = lines[i][7:]
                i += 1
            else:
                author = ""

            # Parse date
            if i < len(lines) and lines[i].startswith('DATE:'):
                date_str = lines[i][5:]
                try:
                    date = datetime.fromisoformat(date_str.replace(' ', 'T'))
                except:
                    date = datetime.now()
                i += 1
            else:
                date = datetime.now()

            # Parse message
            if i < len(lines) and lines[i].startswith('MESSAGE:'):
                message = lines[i][8:]
                i += 1
            else:
                message = ""

            # Parse body (multi-line until END_COMMIT)
            body_lines = []
            while i < len(lines) and not lines[i].startswith('END_COMMIT'):
                if lines[i].startswith('BODY:'):
                    body_lines.append(lines[i][5:])
                else:
                    body_lines.append(lines[i])
                i += 1

            # Extract ticket IDs from message and body
            full_message = message + '\n' + '\n'.join(body_lines)
            ticket_ids = extract_ticket_ids_from_message(full_message, patterns, project_root=get_gira_root())

            # Skip to diff part
            diff_lines = []
            while i < len(lines) and not lines[i].startswith('COMMIT:') and not lines[i].startswith('diff --git'):
                i += 1

            # Capture diff preview (limited)
            if i < len(lines) and lines[i].startswith('diff --git'):
                diff_start = i
                while i < len(lines) and not lines[i].startswith('COMMIT:'):
                    diff_lines.append(lines[i])
                    i += 1
                    if len(diff_lines) > 20:  # Limit diff preview
                        diff_lines.append('...')
                        break

            # Create history entry
            entry = HistoryEntry(
                commit_sha=commit_sha,
                author=author,
                date=date,
                message=message,
                ticket_ids=ticket_ids,
                diff_preview='\n'.join(diff_lines) if diff_lines else None
            )
            entries.append(entry)

            # Collect ticket info
            for ticket_id in ticket_ids:
                if ticket_id not in tickets_map:
                    # Try to find ticket info
                    ticket, _ = find_ticket(ticket_id, cwd)
                    if ticket:
                        tickets_map[ticket_id] = TicketBlameInfo(
                            ticket_id=ticket_id,
                            title=ticket.title,
                            status=ticket.status,
                            type=ticket.type,
                            lines_affected=[line_range],
                            commits={commit_sha},
                            last_modified=date
                        )
                    else:
                        tickets_map[ticket_id] = TicketBlameInfo(
                            ticket_id=ticket_id,
                            title="[Ticket not found]",
                            status="unknown",
                            type="unknown",
                            lines_affected=[line_range],
                            commits={commit_sha},
                            last_modified=date
                        )
                else:
                    tickets_map[ticket_id].commits.add(commit_sha)
                    if date > tickets_map[ticket_id].last_modified:
                        tickets_map[ticket_id].last_modified = date
        else:
            i += 1

    return LineHistory(
        file_path=file_path,
        line_range=line_range,
        entries=entries,
        tickets=tickets_map
    )


def get_tickets_for_file(
    file_path: Path,
    line_range: Optional[Tuple[int, int]] = None,
    patterns: Optional[List[str]] = None,
    cwd: Optional[Path] = None
) -> List[str]:
    """
    Get a simple list of ticket IDs that have touched a file.
    
    Args:
        file_path: Path to the file
        line_range: Optional line range to restrict search
        patterns: Optional regex patterns for ticket extraction
        cwd: Working directory
        
    Returns:
        List of unique ticket IDs
    """
    result = get_file_blame(file_path, line_range, patterns, cwd)
    if not result:
        return []

    return sorted(result.tickets.keys())
