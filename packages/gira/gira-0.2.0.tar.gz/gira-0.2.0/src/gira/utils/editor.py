"""Editor integration utilities for Gira."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def launch_editor(
    initial_content: str = "",
    suffix: str = ".md",
    instructions: Optional[str] = None,
    strip_comments: bool = True
) -> Optional[str]:
    """Launch the user's preferred editor to get multi-line input.
    
    Args:
        initial_content: Content to pre-populate the editor with
        suffix: File suffix for syntax highlighting (e.g., .md for markdown)
        instructions: Optional instructions to show at the top (as comments)
        strip_comments: Whether to strip lines starting with # from the result
        
    Returns:
        The content entered by the user, or None if cancelled/empty
    """
    # Get editor from environment
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "vi"))

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w+', suffix=suffix, delete=False) as tmp:
        # Write instructions if provided
        if instructions:
            for line in instructions.strip().split('\n'):
                tmp.write(f"# {line}\n")
            tmp.write("#\n")
            if initial_content:
                tmp.write("# Current content below:\n#\n")

        # Write initial content
        if initial_content:
            tmp.write(initial_content)

        tmp.flush()
        tmp_path = tmp.name

    try:
        # Launch editor
        try:
            subprocess.run([editor, tmp_path], check=True)
        except subprocess.CalledProcessError:
            # Editor was cancelled (e.g., :cq in vim)
            return None
        except FileNotFoundError:
            # Editor not found
            raise RuntimeError(
                f"Editor '{editor}' not found. "
                f"Please set the EDITOR environment variable to your preferred editor."
            )

        # Read content
        with open(tmp_path) as f:
            lines = f.readlines()

        # Process content
        if strip_comments and instructions:
            # Filter out comment lines
            content_lines = [
                line.rstrip() for line in lines
                if not line.strip().startswith('#')
            ]
        else:
            content_lines = [line.rstrip() for line in lines]

        content = '\n'.join(content_lines).strip()

        # Return None if empty
        return content if content else None

    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


def get_editor_name() -> str:
    """Get the name of the configured editor."""
    return os.environ.get("EDITOR", os.environ.get("VISUAL", "vi"))


def has_editor_configured() -> bool:
    """Check if an editor is configured in the environment."""
    return bool(os.environ.get("EDITOR") or os.environ.get("VISUAL"))
