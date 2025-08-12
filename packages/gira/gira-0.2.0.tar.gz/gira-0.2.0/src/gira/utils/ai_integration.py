"""AI integration utilities for Gira."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class AIDocType(Enum):
    """Types of AI documentation files."""
    CLAUDE = "CLAUDE.md"
    GEMINI = "GEMINI.md"
    AGENTS = "AGENTS.md"
    AI = "AI.md"
    CURSOR = "CURSOR.md"
    COPILOT = "COPILOT.md"
    CUSTOM = "CUSTOM"


@dataclass
class AIDocFile:
    """Represents an AI documentation file."""
    path: Path
    doc_type: AIDocType
    exists: bool
    is_tracked: bool
    has_gira_section: bool
    content: Optional[str] = None


class AIDocumentationDetector:
    """Detects and analyzes AI documentation files in a project."""
    
    # Common AI documentation patterns
    AI_DOC_PATTERNS = [
        "CLAUDE.md",
        "GEMINI.md", 
        "AGENTS.md",
        "AI.md",
        "CURSOR.md",
        "COPILOT.md",
        ".ai/README.md",
        "docs/AI.md",
        "docs/CLAUDE.md",
    ]
    
    # Markers for Gira sections
    GIRA_START_MARKER = "<!-- GIRA-AI-INTEGRATION-START -->"
    GIRA_END_MARKER = "<!-- GIRA-AI-INTEGRATION-END -->"
    
    def __init__(self, project_root: Path):
        """Initialize detector with project root."""
        self.project_root = project_root
        
    def detect_ai_files(self) -> List[AIDocFile]:
        """Detect all AI documentation files in the project."""
        ai_files = []
        
        for pattern in self.AI_DOC_PATTERNS:
            file_path = self.project_root / pattern
            
            # Check if it's a directory pattern
            if "/" in pattern:
                # For patterns like .ai/README.md
                continue
                
            if file_path.exists():
                doc_type = self._get_doc_type(pattern)
                content = None
                has_gira = False
                
                try:
                    content = file_path.read_text()
                    has_gira = self._has_gira_section(content)
                except Exception:
                    pass
                    
                ai_files.append(AIDocFile(
                    path=file_path,
                    doc_type=doc_type,
                    exists=True,
                    is_tracked=self._is_git_tracked(file_path),
                    has_gira_section=has_gira,
                    content=content
                ))
                
        # Also check .ai directory
        ai_dir = self.project_root / ".ai"
        if ai_dir.exists() and ai_dir.is_dir():
            readme = ai_dir / "README.md"
            if readme.exists():
                try:
                    content = readme.read_text()
                    has_gira = self._has_gira_section(content)
                except Exception:
                    content = None
                    has_gira = False
                    
                ai_files.append(AIDocFile(
                    path=readme,
                    doc_type=AIDocType.CUSTOM,
                    exists=True,
                    is_tracked=self._is_git_tracked(readme),
                    has_gira_section=has_gira,
                    content=content
                ))
                
        return ai_files
        
    def _get_doc_type(self, filename: str) -> AIDocType:
        """Get the AI documentation type from filename."""
        filename_upper = filename.upper()
        for doc_type in AIDocType:
            if doc_type.value == filename_upper:
                return doc_type
        return AIDocType.CUSTOM
        
    def _is_git_tracked(self, file_path: Path) -> bool:
        """Check if a file is tracked by git."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(file_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
            
    def _has_gira_section(self, content: str) -> bool:
        """Check if content already has a Gira section."""
        return self.GIRA_START_MARKER in content and self.GIRA_END_MARKER in content
        
    def find_safe_insertion_point(self, content: str) -> Optional[int]:
        """Find a safe place to insert Gira documentation."""
        lines = content.split('\n')
        
        # Look for common section headers where we might insert
        insertion_patterns = [
            (r'^#+\s*Tools?\s*$', 'after'),  # After "Tools" section
            (r'^#+\s*Project\s+Tools?\s*$', 'after'),  # After "Project Tools"
            (r'^#+\s*Development\s+Tools?\s*$', 'after'),  # After "Development Tools"
            (r'^#+\s*Setup\s*$', 'after'),  # After "Setup" section
            (r'^#+\s*Getting\s+Started\s*$', 'after'),  # After "Getting Started"
            (r'^#+\s*Prerequisites?\s*$', 'after'),  # After "Prerequisites"
        ]
        
        for i, line in enumerate(lines):
            for pattern, position in insertion_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    if position == 'after':
                        # Find the end of this section (next header or end of file)
                        j = i + 1
                        while j < len(lines):
                            if re.match(r'^#+\s+', lines[j]):
                                # Found next section, insert before it
                                return sum(len(l) + 1 for l in lines[:j])
                            j += 1
                        # No next section, insert at end
                        return len(content)
                        
        # If no good insertion point found, suggest end of file
        return len(content)


class AIDocumentationGenerator:
    """Generates AI-friendly documentation for Gira."""
    
    @staticmethod
    def generate_gira_section(project_name: str, ticket_prefix: str) -> str:
        """Generate a Gira documentation section for AI files."""
        return f"""
{AIDocumentationDetector.GIRA_START_MARKER}
## Gira Project Management

This project uses Gira for issue tracking and project management.

### Quick Start for AI Assistants

1. **View project status**: `gira board`
2. **List tickets**: `gira ticket list`
3. **Show ticket details**: `gira ticket show <id>`
4. **Get AI-friendly context**: `gira describe`

### Key Commands

- **Tickets**: Create, update, move tickets through workflow stages
- **Epics**: Manage high-level features and group related tickets
- **Sprints**: Organize work into time-boxed iterations
- **Board**: Visualize project status and workflow

### Project Configuration

- Ticket Prefix: `{ticket_prefix}`
- Project Name: `{project_name}`
- Config Location: `.gira/config.json`

### AI Integration

For detailed AI integration docs, see:
- `.gira/docs/claude.md` - Claude-specific guide
- `.gira/docs/gemini.md` - Gemini integration guide
- `.gira/docs/ai-guide.md` - General AI usage patterns

Use `gira ai-help` for AI-optimized command examples.
{AIDocumentationDetector.GIRA_END_MARKER}"""

    @staticmethod
    def generate_ai_reference_section() -> str:
        """Generate a minimal reference section for existing AI docs."""
        return f"""
{AIDocumentationDetector.GIRA_START_MARKER}
## Project Management

This project uses Gira for issue tracking. Run `gira ai-help` for AI-specific commands and `gira describe` for project context.
{AIDocumentationDetector.GIRA_END_MARKER}"""

    @staticmethod
    def generate_companion_file(doc_type: AIDocType, project_name: str, ticket_prefix: str) -> str:
        """Generate a companion AI documentation file."""
        agent_name = doc_type.value.replace('.md', '')
        
        return f"""# {agent_name} Integration with Gira

This document provides {agent_name}-specific guidance for working with the Gira project management system in this repository.

## Overview

This project uses Gira for issue tracking and project management. As an AI assistant, you should be aware of the following commands and patterns.

## Key Commands for {agent_name}

### 1. Understanding Project State

```bash
# View the project board
gira board

# Get AI-friendly project context
gira describe --format json

# List all active tickets
gira ticket list --format json
```

### 2. Working with Tickets

```bash
# Show ticket details
gira ticket show {ticket_prefix}-123

# Create a new ticket
gira ticket create --title "Fix bug in parser" --type bug

# Update ticket status
gira ticket move {ticket_prefix}-123 in_progress

# Add a comment
gira comment add {ticket_prefix}-123 -m "Started investigation"
```

### 3. Structured Output

Always use `--format json` for machine-readable output:

```bash
gira ticket list --format json
gira epic show EPIC-001 --format json
gira sprint show --current --format json
```

## Project Details

- **Ticket Prefix**: `{ticket_prefix}`
- **Project Name**: `{project_name}`
- **Workflow**: Check `.gira/config.json` for workflow stages

## Best Practices for {agent_name}

1. Always check current ticket status before making changes
2. Use structured output (JSON) for parsing
3. Reference tickets by their full ID (e.g., `{ticket_prefix}-123`)
4. Run `gira ai-help` for more AI-specific examples

## Additional Resources

- Main AI documentation: See parent directory
- Gira AI guides: `.gira/docs/`
- Project board: Run `gira board`
"""


def create_backup(file_path: Path) -> Optional[Path]:
    """Create a backup of a file before modification."""
    if not file_path.exists():
        return None
        
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
    
    # Find a unique backup name
    counter = 1
    while backup_path.exists():
        backup_path = file_path.with_suffix(f"{file_path.suffix}.bak{counter}")
        counter += 1
        
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception:
        return None


def inject_gira_section(file_path: Path, content: str, insertion_point: int) -> str:
    """Inject Gira section into existing content at the specified point."""
    # Split content at insertion point
    before = content[:insertion_point]
    after = content[insertion_point:]
    
    # Ensure proper spacing
    if before and not before.endswith('\n\n'):
        if before.endswith('\n'):
            before += '\n'
        else:
            before += '\n\n'
            
    if after and not after.startswith('\n'):
        after = '\n' + after
        
    # Get project info for the section
    from gira.utils.config import load_config
    config = load_config()
    
    generator = AIDocumentationGenerator()
    gira_section = generator.generate_gira_section(
        project_name=config.get("project_name", "My Project"),
        ticket_prefix=config.get("ticket_id_prefix", "PROJ")
    )
    
    return before + gira_section + after