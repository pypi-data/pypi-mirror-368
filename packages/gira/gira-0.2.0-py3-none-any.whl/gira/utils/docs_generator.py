"""Documentation generation utilities for Gira."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from gira.utils.console import console


def run_gira_describe(command: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Execute gira describe command and return JSON output.

    Args:
        command: Optional command path to describe (e.g., ['ticket', 'create'])

    Returns:
        Parsed JSON output from gira describe

    Raises:
        subprocess.CalledProcessError: If gira describe fails
        json.JSONDecodeError: If output is not valid JSON
    """
    cmd = ["gira", "describe"]
    if command:
        cmd.extend(command)

    # Run the command and capture output
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )

    # Parse and return JSON output
    return json.loads(result.stdout)


def parse_command_schema(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse command schema and extract relevant information.

    Args:
        schema: JSON schema from gira describe

    Returns:
        List of parsed command information
    """
    commands = []

    def extract_command(cmd: Dict[str, Any], parent_name: str = "") -> None:
        """Recursively extract command information."""
        full_name = f"{parent_name} {cmd['name']}".strip() if parent_name else cmd['name']

        if cmd['type'] == 'command':
            # Extract command details
            command_info = {
                'name': full_name,
                'description': cmd.get('description', ''),
                'group': cmd.get('group', 'Other Commands'),
                'arguments': cmd.get('arguments', []),
                'options': cmd.get('options', []),
                'examples': cmd.get('command_examples', [])
            }
            commands.append(command_info)

        elif cmd['type'] == 'group':
            # Process nested commands
            for subcmd in cmd.get('commands', []):
                extract_command(subcmd, full_name)

    # Handle top-level application
    if schema['type'] == 'application':
        # Process all top-level commands
        for cmd in schema.get('commands', []):
            extract_command(cmd)
    else:
        # Single command
        extract_command(schema)

    return commands


def get_jinja_env() -> Environment:
    """Get configured Jinja2 environment."""
    # Try to use PackageLoader for installed package
    try:
        env = Environment(
            loader=PackageLoader('gira', 'templates'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
    except Exception:
        # Fallback to FileSystemLoader for development
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

    # Add custom filter to clean up empty lines
    def cleanup_empty_lines(text):
        """Remove excessive empty lines from text."""
        if not text:
            return text
        # Split into lines, remove empty lines that are surrounded by empty lines
        lines = text.split('\n')
        cleaned = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()
            # Keep the line if it's not empty, or if previous line wasn't empty
            if not is_empty or not prev_empty:
                cleaned.append(line)
            prev_empty = is_empty

        return '\n'.join(cleaned)

    env.filters['cleanup_empty_lines'] = cleanup_empty_lines
    return env


def format_command_docs(commands: List[Dict[str, Any]], template_name: str = "cli_reference.md.j2") -> str:
    """
    Format command information using Jinja2 templates.

    Args:
        commands: List of parsed command information
        template_name: Name of the template to use

    Returns:
        Formatted Markdown content
    """
    env = get_jinja_env()
    template = env.get_template(template_name)
    content = template.render(commands=commands)
    # Apply cleanup filter to the entire output
    return env.filters['cleanup_empty_lines'](content)


def format_single_command(command: Dict[str, Any], template_name: str = "command.md.j2") -> str:
    """
    Format a single command using Jinja2 template.

    Args:
        command: Command information dict
        template_name: Name of the template to use

    Returns:
        Formatted Markdown content
    """
    env = get_jinja_env()
    template = env.get_template(template_name)
    content = template.render(command=command)
    # Apply cleanup filter to the entire output
    return env.filters['cleanup_empty_lines'](content)


def generate_cli_docs(output_path: Path, command: Optional[List[str]] = None,
                     template_name: str = "cli_reference.md.j2") -> None:
    """
    Generate CLI documentation.

    Args:
        output_path: Where to write the documentation
        command: Optional specific command to document
        template_name: Template to use
    """
    schema = run_gira_describe(command)
    commands = parse_command_schema(schema)

    # If single command and using command template, format differently
    if len(commands) == 1 and template_name == "command.md.j2":
        content = format_single_command(commands[0], template_name)
    else:
        content = format_command_docs(commands, template_name)

    # Write the content
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')


def generate_agent_docs(output_path: Path, context: Dict[str, Any],
                       template_name: Optional[str] = None) -> None:
    """
    Generate AI agent documentation.

    Args:
        output_path: Where to write the documentation
        context: Project context dictionary
        template_name: Specific template to use (optional)
    """
    env = get_jinja_env()

    if template_name:
        # Generate specific agent doc
        template = env.get_template(f"agents/{template_name}")
        content = template.render(**context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
    else:
        # Generate all agent docs
        agent_templates = [
            ("claude.md.j2", "CLAUDE.md"),
            ("gemini.md.j2", "GEMINI.md"),
            ("general.md.j2", "AI_AGENT_GUIDE.md"),
            ("tools.md.j2", "GIRA_TOOLS_REFERENCE.md"),
            ("codex.md.j2", "AGENTS.md")
        ]

        for template_file, output_name in agent_templates:
            template = env.get_template(f"agents/{template_file}")
            content = template.render(**context)

            if output_path.is_dir():
                file_path = output_path / output_name
            else:
                # If output is a file, use parent dir
                file_path = output_path.parent / output_name

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            console.print(f"Generated: {file_path}")


def generate_workflow_docs(output_path: Path, context: Dict[str, Any],
                          template_name: Optional[str] = None) -> None:
    """
    Generate workflow documentation.

    Args:
        output_path: Where to write the documentation
        context: Project context dictionary
        template_name: Specific template to use (optional)
    """
    env = get_jinja_env()

    # Determine which template to use based on workflow type
    workflow_type = context.get("workflow_type", "custom")

    if template_name:
        template_file = f"workflow/{template_name}"
    elif workflow_type == "kanban":
        template_file = "workflow/kanban.md.j2"
    elif workflow_type == "scrum":
        template_file = "workflow/scrum.md.j2"
    else:
        template_file = "workflow/custom.md.j2"

    template = env.get_template(template_file)
    content = template.render(**context)

    output_file = output_path / "WORKFLOW.md" if output_path.is_dir() else output_path

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding='utf-8')
    console.print(f"Generated workflow documentation: {output_file}")


def generate_all_docs(output_dir: Path, context: Dict[str, Any]) -> None:
    """
    Generate all documentation types.

    Args:
        output_dir: Directory where to write all documentation
        context: Project context dictionary
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print("Generating CLI documentation...")
    # Generate CLI docs
    generate_cli_docs(output_dir / "CLI_REFERENCE.md")

    console.print("Generating agent documentation...")
    # Generate agent docs
    generate_agent_docs(output_dir, context)

    console.print("Generating workflow documentation...")
    # Generate workflow docs
    generate_workflow_docs(output_dir, context)

    console.print(f"\nAll documentation generated in: {output_dir}")

