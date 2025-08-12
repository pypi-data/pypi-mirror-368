"""CSV utilities for import/export operations."""

import csv
import io
from typing import Any, Dict, List


class CSVReader:
    """Handle reading and parsing CSV for bulk operations."""

    def __init__(self, stream=None, delimiter: str = ','):
        """Initialize CSV reader.
        
        Args:
            stream: Stream to read from (defaults to sys.stdin)
            delimiter: CSV delimiter character
        """
        self.stream = stream
        self.delimiter = delimiter

    def read_csv_dicts(self) -> List[Dict[str, Any]]:
        """Read CSV and return as list of dictionaries.
        
        Returns:
            List of dictionaries parsed from CSV
            
        Raises:
            ValueError: If CSV is malformed
        """
        try:
            content = self.stream.read()
            if not content.strip():
                return []

            # Use StringIO to handle the content
            csv_file = io.StringIO(content)

            # Detect delimiter if not specified
            if self.delimiter == 'auto':
                sample = content[:1024]  # Use first 1KB as sample
                sniffer = csv.Sniffer()
                try:
                    detected_delimiter = sniffer.sniff(sample).delimiter
                    self.delimiter = detected_delimiter
                except csv.Error:
                    # Default to comma if detection fails
                    self.delimiter = ','

            # Reset to beginning
            csv_file.seek(0)

            # Read CSV with DictReader
            reader = csv.DictReader(
                csv_file,
                delimiter=self.delimiter,
                quoting=csv.QUOTE_MINIMAL,
                escapechar='\\',
                doublequote=True
            )

            items = []
            for row_num, row in enumerate(reader, 1):
                # Clean up the row - remove empty values
                cleaned_row = {k: v for k, v in row.items() if v}
                if cleaned_row:  # Only add non-empty rows
                    items.append(self._process_csv_row(cleaned_row, row_num))

            return items

        except csv.Error as e:
            raise ValueError(f"Invalid CSV: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading CSV: {e}") from e

    def _process_csv_row(self, row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """Process a single CSV row, converting types as needed.
        
        Args:
            row: Raw CSV row as string dict
            row_num: Row number for error reporting
            
        Returns:
            Processed row with appropriate types
        """
        processed = {}

        for key, value in row.items():
            if not value:  # Skip empty values
                continue

            # Handle special conversions
            if key == 'description':
                # Restore newlines from escape sequences
                processed[key] = value.replace('\\n', '\n').replace('\\r', '\r')
            elif key == 'labels':
                # Convert comma-separated string to list
                processed[key] = [label.strip() for label in value.split(',') if label.strip()]
            elif key in ['blocked_by', 'blocks']:
                # Convert comma-separated ticket IDs to list
                processed[key] = [id.strip() for id in value.split(',') if id.strip()]
            elif key == 'story_points':
                # Convert to integer
                try:
                    processed[key] = int(value)
                except ValueError:
                    raise ValueError(f"Row {row_num}: Invalid story_points value '{value}' - must be a number")
            elif key == 'priority' or key == 'type':
                # Normalize to lowercase
                processed[key] = value.lower()
            elif key == 'status':
                # Normalize to lowercase and handle spaces
                processed[key] = value.lower().replace(' ', '_')
            else:
                # Keep as string
                processed[key] = value

        return processed


def prepare_csv_field(value: Any) -> str:
    """Prepare a field value for CSV export.
    
    Args:
        value: Field value to prepare
        
    Returns:
        String representation suitable for CSV
    """
    if value is None:
        return ""
    elif isinstance(value, list):
        # Join lists with commas
        return ",".join(str(item) for item in value)
    elif isinstance(value, str):
        # Escape newlines in strings
        return value.replace('\n', '\\n').replace('\r', '\\r')
    else:
        return str(value)
