"""Stdin utilities for bulk operations."""

import json
import sys
from typing import Any, Dict, Iterator, List

from rich.progress import Progress, SpinnerColumn, TextColumn

from gira.utils.console import console


class StdinReader:
    """Handle reading and parsing stdin for bulk operations."""

    def __init__(self, stream=None):
        """Initialize stdin reader.
        
        Args:
            stream: Stream to read from (defaults to sys.stdin)
        """
        self.stream = stream or sys.stdin

    def is_available(self) -> bool:
        """Check if stdin has data available."""
        return not self.stream.isatty()

    def read_json_array(self) -> List[Dict[str, Any]]:
        """Read JSON array from stdin.
        
        Returns:
            List of dictionaries parsed from JSON
            
        Raises:
            ValueError: If input is not valid JSON array
        """
        try:
            content = self.stream.read().strip()
            if not content:
                return []

            data = json.loads(content)

            # Handle single object - wrap in array
            if isinstance(data, dict):
                return [data]

            # Must be an array
            if not isinstance(data, list):
                raise ValueError("Input must be a JSON array or single object")

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

    def read_json_lines(self) -> Iterator[Dict[str, Any]]:
        """Read JSON lines (JSONL) from stdin.
        
        Yields:
            Dictionary for each valid JSON line
            
        Raises:
            ValueError: If any line is not valid JSON
        """
        try:
            # Read all content first to handle CLI runner's stdin behavior
            content = self.stream.read()
            lines = content.strip().split('\n') if content else []

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    yield data
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_num}: {e}") from e
        except EOFError:
            # Handle EOFError from CLI runner
            return

    def read_lines(self) -> List[str]:
        """Read plain text lines from stdin.
        
        Returns:
            List of non-empty lines from stdin
        """
        try:
            # Read all content first to handle CLI runner's stdin behavior
            content = self.stream.read()
            if not content:
                return []

            # Return non-empty lines
            return [line.strip() for line in content.strip().split('\n') if line.strip()]
        except EOFError:
            # Handle EOFError from CLI runner
            return []


class BulkOperationResult:
    """Result of a bulk operation."""

    def __init__(self):
        self.successful: List[Dict[str, Any]] = []
        self.failed: List[Dict[str, Any]] = []
        self.total_count = 0

    def add_success(self, item: Dict[str, Any], result: Any = None):
        """Add successful operation result."""
        self.successful.append({
            "item": item,
            "result": result,
            "index": self.total_count
        })
        self.total_count += 1

    def add_failure(self, item: Dict[str, Any], error: str):
        """Add failed operation result."""
        self.failed.append({
            "item": item,
            "error": error,
            "index": self.total_count
        })
        self.total_count += 1

    @property
    def success_count(self) -> int:
        """Number of successful operations."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Number of failed operations."""
        return len(self.failed)

    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON output."""
        return {
            "summary": {
                "total": self.total_count,
                "successful": self.success_count,
                "failed": self.failure_count,
                "success_rate": round(self.success_rate, 2)
            },
            "successful": self.successful,
            "failed": self.failed
        }

    def print_summary(self, operation_name: str = "operation"):
        """Print a summary of the bulk operation results."""
        if self.total_count == 0:
            console.print(f"[yellow]No items processed for {operation_name}[/yellow]")
            return

        # Print summary
        console.print(f"\n📊 **{operation_name.title()} Summary**")
        console.print(f"Total: {self.total_count}")
        console.print(f"✅ Successful: [green]{self.success_count}[/green]")

        if self.failure_count > 0:
            console.print(f"❌ Failed: [red]{self.failure_count}[/red]")
            console.print(f"Success rate: [yellow]{self.success_rate:.1f}%[/yellow]")

            # Show first few failures
            console.print("\n**Failed Items:**")
            for i, failure in enumerate(self.failed[:3]):  # Show first 3
                console.print(f"  {i+1}. Index {failure['index']}: {failure['error']}")

            if len(self.failed) > 3:
                console.print(f"  ... and {len(self.failed) - 3} more failures")
        else:
            console.print(f"Success rate: [green]{self.success_rate:.1f}%[/green]")


def validate_bulk_items(items: List[Dict[str, Any]],
                       required_fields: List[str],
                       optional_fields: List[str] = None) -> List[str]:
    """Validate bulk operation items.
    
    Args:
        items: List of items to validate
        required_fields: Fields that must be present in each item
        optional_fields: Fields that are allowed but not required
        
    Returns:
        List of validation error messages
    """
    errors = []
    optional_fields = optional_fields or []
    all_allowed_fields = set(required_fields + optional_fields)

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"Item {i}: Must be a JSON object")
            continue

        # Check required fields
        missing_fields = []
        for field in required_fields:
            if field not in item:
                missing_fields.append(field)

        if missing_fields:
            errors.append(f"Item {i}: Missing required fields: {', '.join(missing_fields)}")

        # Check for unknown fields
        unknown_fields = set(item.keys()) - all_allowed_fields
        if unknown_fields:
            errors.append(f"Item {i}: Unknown fields: {', '.join(unknown_fields)}")

    return errors


def process_bulk_operation(items: List[Dict[str, Any]],
                          operation_func,
                          operation_name: str = "operation",
                          show_progress: bool = True) -> BulkOperationResult:
    """Process a bulk operation with progress tracking.
    
    Args:
        items: Items to process
        operation_func: Function to call for each item (should return result or raise exception)
        operation_name: Name of operation for progress display
        show_progress: Whether to show progress bar
        
    Returns:
        BulkOperationResult with success/failure details
    """
    result = BulkOperationResult()

    if not items:
        return result

    if show_progress and len(items) > 1:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Processing {operation_name}...", total=len(items))

            for item in items:
                try:
                    operation_result = operation_func(item)
                    result.add_success(item, operation_result)
                except Exception as e:
                    result.add_failure(item, str(e))

                progress.advance(task)
    else:
        # Process without progress bar
        for item in items:
            try:
                operation_result = operation_func(item)
                result.add_success(item, operation_result)
            except Exception as e:
                result.add_failure(item, str(e))

    return result
