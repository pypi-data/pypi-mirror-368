"""Unified output formatting system for Gira.

This module provides a centralized way to format output in various formats
(table, json, yaml, csv, tsv) consistently across all commands.
"""

import csv
import io
import json
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Union

import typer
from rich.syntax import Syntax

try:
    import yaml
except ImportError:
    yaml = None

from rich.table import Table

from gira.utils.console import console


class OutputFormat(str, Enum):
    """Supported output formats."""
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    TSV = "tsv"
    TEXT = "text"  # For show commands
    IDS = "ids"    # For query command


def should_use_highlighting(no_color: bool = False, color: bool = False, check_config: bool = True) -> bool:
    """Determine if syntax highlighting should be used for JSON output.
    
    By default, returns False (no highlighting) for better compatibility
    with AI agents and programmatic usage. Users must explicitly enable
    highlighting with --color or GIRA_COLOR=1 environment variable.
    
    Priority order:
    1. Explicit --no-color flag (always disables)
    2. Explicit --color flag (always enables)
    3. GIRA_COLOR environment variable
    4. Configuration setting (if check_config is True)
    5. Default to False
    """
    # Explicit --no-color always wins
    if no_color:
        return False

    # Explicit --color enables highlighting
    if color:
        return True

    # Check for explicit environment variable to enable color
    if os.environ.get('GIRA_COLOR', '').lower() in ('1', 'true', 'yes'):
        return True

    # Check configuration if requested
    if check_config:
        try:
            from gira.utils.config_utils import load_config
            from gira.utils.project import get_project_root

            # Try to get project root, but don't fail if not in a gira project
            root = get_project_root()
            if root:
                config = load_config(root)
                if config.get('output.json_highlighting', False):
                    return True
        except:
            # If we can't load config, just continue
            pass

    # Default to no highlighting for safety and AI agent compatibility
    return False


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format(self, data: Any, **kwargs) -> str:
        """Format the data for output."""
        pass

    @abstractmethod
    def print(self, data: Any, **kwargs) -> None:
        """Print the formatted data."""
        pass


class JSONFormatter(OutputFormatter):
    """JSON output formatter."""

    def format(self, data: Any, **kwargs) -> str:
        """Format data as JSON."""
        indent = kwargs.get('indent', 2)
        jsonpath_filter = kwargs.get('jsonpath_filter')

        # Handle Pydantic models
        if hasattr(data, 'model_dump'):
            data = data.model_dump(mode='json')
        elif isinstance(data, list) and data and hasattr(data[0], 'model_dump'):
            data = [item.model_dump(mode='json') for item in data]

        # Apply JSONPath filter if provided
        if jsonpath_filter:
            from gira.utils.jsonpath_filter import apply_jsonpath_filter
            try:
                data = apply_jsonpath_filter(data, jsonpath_filter)
            except ValueError as e:
                console.print(f"[red]JSONPath Error:[/red] {e}")
                raise typer.Exit(1)

        return json.dumps(data, indent=indent, default=str)

    def print(self, data: Any, **kwargs) -> None:
        """Print JSON data."""
        jsonpath_filter = kwargs.get('jsonpath_filter')
        indent = kwargs.get('indent', 2)
        compact = kwargs.get('compact', False)
        no_color = kwargs.get('no_color', False)
        color = kwargs.get('color', False)
        theme = kwargs.get('theme', 'monokai')

        # Handle Pydantic models
        if hasattr(data, 'model_dump'):
            data = data.model_dump(mode='json')
        elif isinstance(data, list) and data and hasattr(data[0], 'model_dump'):
            data = [item.model_dump(mode='json') for item in data]

        # Apply JSONPath filter if provided
        if jsonpath_filter:
            from gira.utils.jsonpath_filter import apply_jsonpath_filter
            try:
                data = apply_jsonpath_filter(data, jsonpath_filter)
            except ValueError as e:
                console.print(f"[red]JSONPath Error:[/red] {e}")
                raise typer.Exit(1)

        # Generate JSON string
        if compact:
            json_str = json.dumps(data, ensure_ascii=True, separators=(',', ':'), default=str)
        else:
            json_str = json.dumps(data, indent=indent, ensure_ascii=True, default=str)

        # Determine if we should use syntax highlighting
        use_highlighting = should_use_highlighting(no_color, color)

        if use_highlighting:
            # Get theme from kwargs or config
            if theme == 'monokai':  # Default value
                try:
                    from gira.utils.config_utils import load_config
                    from gira.utils.project import get_project_root

                    root = get_project_root()
                    if root:
                        config = load_config(root)
                        theme = config.get('output.json_theme', 'monokai')
                except:
                    pass

            # Use Rich's Syntax highlighting for JSON
            syntax = Syntax(json_str, "json", theme=theme, line_numbers=False)
            console.print(syntax)
        else:
            # Use plain print to avoid ANSI codes in JSON output
            print(json_str)


class YAMLFormatter(OutputFormatter):
    """YAML output formatter."""

    def format(self, data: Any, **kwargs) -> str:
        """Format data as YAML."""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML output. Install with: pip install pyyaml")

        # Handle Pydantic models
        if hasattr(data, 'model_dump'):
            data = data.model_dump(mode='json')
        elif isinstance(data, list) and data and hasattr(data[0], 'model_dump'):
            data = [item.model_dump(mode='json') for item in data]

        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def print(self, data: Any, **kwargs) -> None:
        """Print YAML data."""
        print(self.format(data, **kwargs))


class CSVFormatter(OutputFormatter):
    """CSV output formatter."""

    def format(self, data: Any, **kwargs) -> str:
        """Format data as CSV."""
        delimiter = kwargs.get('delimiter', ',')

        # Convert single item to list
        if not isinstance(data, list):
            data = [data]

        # Handle Pydantic models
        if data and hasattr(data[0], 'model_dump'):
            data = [item.model_dump(mode='json') for item in data]

        # Handle empty data
        if not data:
            return ""

        # Get headers from first item
        headers = list(data[0].keys()) if isinstance(data[0], dict) else []

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()

        for item in data:
            # Flatten nested structures to strings
            flattened = {}
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    flattened[key] = json.dumps(value)
                else:
                    flattened[key] = value
            writer.writerow(flattened)

        return output.getvalue()

    def print(self, data: Any, **kwargs) -> None:
        """Print CSV data."""
        print(self.format(data, **kwargs), end='')


class TSVFormatter(CSVFormatter):
    """TSV (Tab-Separated Values) output formatter."""

    def format(self, data: Any, **kwargs) -> str:
        """Format data as TSV."""
        kwargs['delimiter'] = '\t'
        return super().format(data, **kwargs)


class TableFormatter(OutputFormatter):
    """Rich table output formatter."""

    def format(self, data: Any, **kwargs) -> str:
        """Format data as a table (returns string representation)."""
        table = self._create_table(data, **kwargs)

        # Use console to capture the output
        with console.capture() as capture:
            console.print(table)
        return capture.get()

    def print(self, data: Any, **kwargs) -> None:
        """Print table data."""
        table = self._create_table(data, **kwargs)
        console.print(table)

    def _create_table(self, data: Any, **kwargs) -> Table:
        """Create a Rich table from the data."""
        title = kwargs.get('title')
        columns = kwargs.get('columns', [])

        # Convert single item to list
        if not isinstance(data, list):
            data = [data]

        # Handle Pydantic models
        if data and hasattr(data[0], 'model_dump'):
            data = [item.model_dump(mode='json') for item in data]

        # Handle empty data
        if not data:
            table = Table(title=title, show_header=True, header_style="bold cyan")
            table.add_column("No Data", style="dim")
            table.add_row("No items to display")
            return table

        # Auto-detect columns if not provided
        if not columns and isinstance(data[0], dict):
            columns = list(data[0].keys())

        # Create table
        table = Table(title=title, show_header=True, header_style="bold cyan")

        # Add columns
        for col in columns:
            # Customize column styles based on common field names
            style = None
            if col in ['id', 'ID']:
                style = "cyan"
            elif col in ['status', 'Status']:
                style = "yellow"
            elif col in ['priority', 'Priority']:
                style = "magenta"
            elif col in ['type', 'Type']:
                style = "green"

            table.add_column(col.replace('_', ' ').title(), style=style)

        # Add rows
        for item in data:
            row = []
            for col in columns:
                value = item.get(col, "") if isinstance(item, dict) else getattr(item, col, "")

                # Format specific value types
                if isinstance(value, bool):
                    value = "✓" if value else "✗"
                elif isinstance(value, (list, dict)):
                    value = json.dumps(value)
                elif value is None:
                    value = "-"

                row.append(str(value))

            table.add_row(*row)

        return table


class TextFormatter(OutputFormatter):
    """Text output formatter for detailed views."""

    def format(self, data: Any, **kwargs) -> str:
        """Format data as text."""
        # This is mainly used by show commands which have custom formatting
        # The actual formatting is done by the command itself
        return str(data)

    def print(self, data: Any, **kwargs) -> None:
        """Print text data."""
        # Most show commands handle their own printing
        # This is here for consistency
        console.print(data)


class IDsFormatter(OutputFormatter):
    """IDs-only output formatter."""

    def format(self, data: Any, **kwargs) -> str:
        """Format data as a list of IDs."""
        # Convert single item to list
        if not isinstance(data, list):
            data = [data]

        # Extract IDs
        ids = []
        for item in data:
            if hasattr(item, 'id'):
                ids.append(item.id)
            elif isinstance(item, dict) and 'id' in item:
                ids.append(item['id'])

        return '\n'.join(ids)

    def print(self, data: Any, **kwargs) -> None:
        """Print IDs."""
        print(self.format(data, **kwargs))


# Registry of formatters
FORMATTERS: Dict[OutputFormat, OutputFormatter] = {
    OutputFormat.JSON: JSONFormatter(),
    OutputFormat.YAML: YAMLFormatter(),
    OutputFormat.CSV: CSVFormatter(),
    OutputFormat.TSV: TSVFormatter(),
    OutputFormat.TABLE: TableFormatter(),
    OutputFormat.TEXT: TextFormatter(),
    OutputFormat.IDS: IDsFormatter(),
}


def format_output(
    data: Any,
    format: Union[OutputFormat, str],
    **kwargs
) -> str:
    """Format data in the specified format.
    
    Args:
        data: The data to format
        format: The output format
        **kwargs: Additional options passed to the formatter
        
    Returns:
        Formatted string
    """
    if isinstance(format, str):
        format = OutputFormat(format.lower())

    formatter = FORMATTERS.get(format)
    if not formatter:
        raise ValueError(f"Unsupported format: {format}")

    return formatter.format(data, **kwargs)


def print_output(
    data: Any,
    format: Union[OutputFormat, str],
    **kwargs
) -> None:
    """Print data in the specified format.
    
    Args:
        data: The data to print
        format: The output format
        **kwargs: Additional options passed to the formatter
    """
    if isinstance(format, str):
        format = OutputFormat(format.lower())

    formatter = FORMATTERS.get(format)
    if not formatter:
        raise ValueError(f"Unsupported format: {format}")

    formatter.print(data, **kwargs)


def get_default_format(command_type: str = "list") -> OutputFormat:
    """Get the default format for a command type.
    
    Args:
        command_type: Type of command (list, show, etc.)
        
    Returns:
        Default output format
    """
    if command_type == "list":
        return OutputFormat.TABLE
    elif command_type == "show":
        return OutputFormat.TEXT
    else:
        return OutputFormat.TABLE


def add_format_option(default: Union[OutputFormat, str] = OutputFormat.TABLE):
    """Typer option factory for adding --format option to commands.
    
    Usage:
        format: OutputFormat = add_format_option()
        format: OutputFormat = add_format_option(OutputFormat.JSON)
    """
    import typer

    if isinstance(default, str):
        default = OutputFormat(default.lower())

    return typer.Option(
        default.value,
        "--format",
        "-f",
        help="Output format",
        case_sensitive=False
    )


def add_color_option():
    """Typer option factory for adding --color option to commands.
    
    Usage:
        color: bool = add_color_option()
    """
    import typer

    return typer.Option(
        False,
        "--color",
        help="Enable syntax highlighting for JSON output (default: no color for AI compatibility)"
    )


def add_no_color_option():
    """Typer option factory for adding --no-color option to commands.
    
    Usage:
        no_color: bool = add_no_color_option()
    """
    import typer

    return typer.Option(
        False,
        "--no-color",
        help="Explicitly disable syntax highlighting (default is already no color)"
    )


def get_color_kwargs(color: bool = False, no_color: bool = False) -> Dict[str, Any]:
    """Get keyword arguments for color options to pass to print_output.
    
    Args:
        color: Whether to enable color
        no_color: Whether to disable color
        
    Returns:
        Dictionary with color-related kwargs
    """
    return {
        'color': color,
        'no_color': no_color
    }
