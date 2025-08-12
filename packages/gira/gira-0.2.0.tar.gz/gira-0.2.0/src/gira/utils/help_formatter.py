"""Help text and example formatting utilities for Gira CLI commands."""

from dataclasses import dataclass
from typing import List, Optional

from rich.console import Console


@dataclass
class Example:
    """Represents a command example with description and command."""
    description: str
    command: str
    category: Optional[str] = None


class HelpFormatter:
    """Formats help text examples in a consistent, readable way."""

    def __init__(self, max_width: int = 70):
        """Initialize formatter with maximum line width.
        
        Args:
            max_width: Maximum line width for formatting (default 70 for 80-char terminals)
        """
        self.max_width = max_width
        self.console = Console(width=max_width, file=None)

    def format_examples(
        self,
        examples: List[Example],
        style: str = "simple"
    ) -> str:
        """Format a list of examples using the specified style.
        
        Args:
            examples: List of Example objects to format
            style: Formatting style ('simple', 'compact', 'grouped')
            
        Returns:
            Formatted examples string
        """
        if not examples:
            return ""

        if style == "simple":
            return self._format_simple_list(examples)
        elif style == "compact":
            return self._format_compact_table(examples)
        elif style == "grouped":
            return self._format_grouped(examples)
        else:
            raise ValueError(f"Unknown style: {style}")

    def _format_simple_list(self, examples: List[Example]) -> str:
        """Format examples as a simple indented list.
        
        This is the primary format - clean, scannable, terminal-friendly.
        """
        lines = ["", "Examples:", ""]  # Start with blank line and header

        for example in examples:
            # Add description line
            lines.append(f"  {example.description}")

            # Add command with $ prefix and proper wrapping
            command_line = f"  $ {example.command}"

            # Handle line wrapping for long commands
            if len(command_line) > self.max_width:
                wrapped_lines = self._wrap_command(command_line)
                lines.extend(wrapped_lines)
            else:
                lines.append(command_line)

            # Add blank line between examples
            lines.append("")

        return "\n".join(lines)

    def _format_compact_table(self, examples: List[Example]) -> str:
        """Format examples as a compact table with description | command format."""
        lines = ["", "Examples:"]

        # Calculate max description length for alignment (but not too wide)
        max_desc_len = min(25, max(len(ex.description) for ex in examples) if examples else 0)

        for example in examples:
            desc = example.description
            if len(desc) > max_desc_len:
                desc = desc[:max_desc_len-3] + "..."

            # Format as "Description │ command"
            command_part = f"$ {example.command}"
            line = f"  {desc:<{max_desc_len}} │ {command_part}"

            if len(line) > self.max_width:
                # If too long, fall back to simple format for this example
                lines.append(f"  {example.description}")
                wrapped_cmd = self._wrap_command(f"  $ {example.command}")
                lines.extend(wrapped_cmd)
                lines.append("")  # Add space after wrapped commands
            else:
                lines.append(line)

        lines.append("")  # Add blank line at end
        return "\n".join(lines)

    def _format_grouped(self, examples: List[Example]) -> str:
        """Format examples grouped by category."""
        if not examples:
            return ""

        # Group examples by category
        groups = {}
        for example in examples:
            category = example.category or "Examples"
            if category not in groups:
                groups[category] = []
            groups[category].append(example)

        lines = ["", "Examples:", ""]

        for category, group_examples in groups.items():
            if category != "Examples":  # Don't show category header for default
                lines.append(f"{category}:")

            for example in group_examples:
                lines.append(f"  $ {example.command}")

            lines.append("")  # Blank line between groups

        return "\n".join(lines)

    def _wrap_command(self, command_line: str) -> List[str]:
        """Wrap a long command line with proper indentation."""
        if len(command_line) <= self.max_width:
            return [command_line]

        lines = []
        current_line = command_line

        # Simple wrapping - break at spaces when possible
        while len(current_line) > self.max_width:
            # Find last space before max_width
            break_point = current_line.rfind(' ', 0, self.max_width)

            if break_point == -1:  # No space found, hard break
                break_point = self.max_width - 1

            lines.append(current_line[:break_point])
            # Continue on next line with proper indentation (4 spaces to align with $)
            current_line = "    " + current_line[break_point:].lstrip()

        if current_line.strip():  # Add remaining content
            lines.append(current_line)

        return lines

    def format_command_example(self, description: str, command: str) -> str:
        """Format a single command example.
        
        Args:
            description: Description of what the command does
            command: The command to execute
            
        Returns:
            Formatted example string
        """
        example = Example(description=description, command=command)
        return self.format_examples([example], style="simple")


# Convenience functions for common use
def format_examples_simple(examples: List[Example], max_width: int = 70) -> str:
    """Format examples using simple list style (recommended)."""
    formatter = HelpFormatter(max_width=max_width)
    return formatter.format_examples(examples, style="simple")


def format_examples_compact(examples: List[Example], max_width: int = 70) -> str:
    """Format examples using compact table style."""
    formatter = HelpFormatter(max_width=max_width)
    return formatter.format_examples(examples, style="compact")


def format_examples_grouped(examples: List[Example], max_width: int = 70) -> str:
    """Format examples using grouped style."""
    formatter = HelpFormatter(max_width=max_width)
    return formatter.format_examples(examples, style="grouped")


def create_example(description: str, command: str, category: Optional[str] = None) -> Example:
    """Helper function to create an Example object."""
    return Example(description=description, command=command, category=category)
