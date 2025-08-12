"""Automatic documentation generation for MCP commands."""

import json
import logging
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from gira.mcp.help_system import help_registry, HelpFormatter
from gira.mcp.tools import tool_registry
from gira.mcp.schema import TOOL_SCHEMAS

logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """Generates comprehensive documentation for MCP commands."""
    
    def __init__(self):
        self.generated_at = datetime.now()
    
    def generate_full_documentation(self, format: str = "markdown") -> str:
        """
        Generate complete documentation for all MCP commands.
        
        Args:
            format: Output format (markdown, html, json)
            
        Returns:
            Generated documentation
        """
        if format == "markdown":
            return self._generate_markdown_docs()
        elif format == "html":
            return self._generate_html_docs()
        elif format == "json":
            return self._generate_json_docs()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_command_documentation(
        self,
        command_name: str,
        format: str = "markdown"
    ) -> Optional[str]:
        """
        Generate documentation for a specific command.
        
        Args:
            command_name: Command to document
            format: Output format
            
        Returns:
            Generated documentation or None if command not found
        """
        cmd_help = help_registry.get_command_help(command_name)
        if not cmd_help:
            return None
        
        if format == "markdown":
            return HelpFormatter.format_command_help(cmd_help, "detailed")
        elif format == "json":
            return json.dumps(self._command_to_dict(cmd_help), indent=2)
        else:
            return self._command_to_html(cmd_help)
    
    def generate_api_reference(self) -> Dict[str, Any]:
        """Generate API reference documentation."""
        reference = {
            "title": "Gira MCP Server API Reference",
            "version": "1.0.0",
            "generated_at": self.generated_at.isoformat(),
            "commands": {},
            "schemas": {},
            "categories": self._categorize_commands()
        }
        
        # Add command documentation
        for cmd_name in help_registry.list_commands():
            cmd_help = help_registry.get_command_help(cmd_name)
            if cmd_help:
                reference["commands"][cmd_name] = self._command_to_dict(cmd_help)
        
        # Add schema documentation
        for schema_name, schema_def in TOOL_SCHEMAS.items():
            reference["schemas"][schema_name] = schema_def
        
        return reference
    
    def generate_usage_guide(self) -> str:
        """Generate user-friendly usage guide."""
        guide_sections = [
            self._generate_introduction(),
            self._generate_getting_started(),
            self._generate_common_workflows(),
            self._generate_command_categories(),
            self._generate_troubleshooting(),
            self._generate_examples()
        ]
        
        return "\n\n".join(guide_sections)
    
    def _generate_markdown_docs(self) -> str:
        """Generate markdown documentation."""
        sections = [
            "# Gira MCP Server Documentation",
            "",
            f"*Generated on {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Overview",
            "",
            "The Gira MCP (Model Context Protocol) server provides AI agents with comprehensive project management capabilities.",
            "This documentation covers all available commands, their parameters, and usage examples.",
            "",
            "## Quick Start",
            "",
            "Use the `help` command to get information about any command:",
            "```json",
            '{"command": "help", "parameters": {"command": "create_ticket"}}',
            "```",
            "",
            "## Available Commands",
            ""
        ]
        
        # Add command documentation
        categories = self._categorize_commands()
        for category, commands in categories.items():
            sections.append(f"### {category}")
            sections.append("")
            
            for cmd_name in commands:
                cmd_help = help_registry.get_command_help(cmd_name)
                if cmd_help:
                    sections.append(f"#### {cmd_name}")
                    sections.append(cmd_help.description)
                    sections.append("")
                    
                    # Add parameter summary
                    if cmd_help.parameters:
                        sections.append("**Parameters:**")
                        for param in cmd_help.parameters:
                            required_marker = "✅" if param.required else "⚪"
                            sections.append(f"- {required_marker} `{param.name}` ({param.type_name}): {param.description}")
                        sections.append("")
                    
                    # Add usage example
                    if cmd_help.usage_examples:
                        sections.append("**Example:**")
                        sections.append("```json")
                        sections.append(json.dumps(cmd_help.usage_examples[0], indent=2))
                        sections.append("```")
                        sections.append("")
            
            sections.append("")
        
        return "\n".join(sections)
    
    def _generate_html_docs(self) -> str:
        """Generate HTML documentation."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Gira MCP Server Documentation</title>",
            "<style>",
            self._get_html_styles(),
            "</style>",
            "</head>",
            "<body>",
            "<h1>Gira MCP Server Documentation</h1>",
            f"<p><em>Generated on {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</em></p>",
            "<div class='toc'>",
            self._generate_table_of_contents(),
            "</div>",
            "<div class='commands'>",
        ]
        
        # Add command documentation in HTML
        categories = self._categorize_commands()
        for category, commands in categories.items():
            html_parts.append(f"<h2>{category}</h2>")
            
            for cmd_name in commands:
                cmd_help = help_registry.get_command_help(cmd_name)
                if cmd_help:
                    html_parts.append(self._command_to_html(cmd_help))
        
        html_parts.extend([
            "</div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _generate_json_docs(self) -> str:
        """Generate JSON documentation."""
        return json.dumps(self.generate_api_reference(), indent=2)
    
    def _command_to_dict(self, cmd_help) -> Dict[str, Any]:
        """Convert command help to dictionary."""
        return {
            "name": cmd_help.name,
            "description": cmd_help.description,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type_name,
                    "description": param.description,
                    "required": param.required,
                    "default": param.default_value,
                    "enum_values": param.enum_values,
                    "examples": [
                        {"value": ex.value, "description": ex.description}
                        for ex in param.examples
                    ],
                    "validation_rules": param.validation_rules,
                    "suggestions": param.suggestions
                }
                for param in cmd_help.parameters
            ],
            "usage_examples": cmd_help.usage_examples,
            "common_workflows": cmd_help.common_workflows,
            "related_commands": cmd_help.related_commands,
            "troubleshooting": cmd_help.troubleshooting
        }
    
    def _command_to_html(self, cmd_help) -> str:
        """Convert command help to HTML."""
        html_parts = [
            f"<div class='command' id='{cmd_help.name}'>",
            f"<h3>{cmd_help.name}</h3>",
            f"<p>{cmd_help.description}</p>"
        ]
        
        if cmd_help.parameters:
            html_parts.append("<h4>Parameters</h4>")
            html_parts.append("<table class='parameters'>")
            html_parts.append("<tr><th>Name</th><th>Type</th><th>Required</th><th>Description</th></tr>")
            
            for param in cmd_help.parameters:
                required = "Yes" if param.required else "No"
                html_parts.append(
                    f"<tr><td><code>{param.name}</code></td>"
                    f"<td>{param.type_name}</td>"
                    f"<td>{required}</td>"
                    f"<td>{param.description}</td></tr>"
                )
            
            html_parts.append("</table>")
        
        if cmd_help.usage_examples:
            html_parts.append("<h4>Example</h4>")
            html_parts.append("<pre><code>")
            html_parts.append(json.dumps(cmd_help.usage_examples[0], indent=2))
            html_parts.append("</code></pre>")
        
        html_parts.append("</div>")
        
        return "\n".join(html_parts)
    
    def _categorize_commands(self) -> Dict[str, List[str]]:
        """Categorize commands by functionality."""
        categories = {
            "Ticket Management": [],
            "Epic Management": [],
            "Sprint Management": [],
            "Board Operations": [],
            "Help & Documentation": [],
            "Utilities": []
        }
        
        for cmd_name in help_registry.list_commands():
            if any(word in cmd_name for word in ["ticket", "comment"]):
                categories["Ticket Management"].append(cmd_name)
            elif "epic" in cmd_name:
                categories["Epic Management"].append(cmd_name)
            elif "sprint" in cmd_name:
                categories["Sprint Management"].append(cmd_name)
            elif "board" in cmd_name:
                categories["Board Operations"].append(cmd_name)
            elif any(word in cmd_name for word in ["help", "validate", "search", "build"]):
                categories["Help & Documentation"].append(cmd_name)
            else:
                categories["Utilities"].append(cmd_name)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_introduction(self) -> str:
        """Generate introduction section."""
        return """# Gira MCP Server Usage Guide

The Gira MCP server enables AI agents to manage projects using the Gira project management system. 
This guide provides comprehensive information on using all available commands effectively.

## Key Features

- **Ticket Management**: Create, update, and track tickets
- **Epic Planning**: Organize work into epics for better project visibility  
- **Sprint Management**: Plan and execute work in time-boxed sprints
- **Board Visualization**: View project status across different workflows
- **Advanced Search**: Find tickets, epics, and sprints quickly
- **Interactive Help**: Get contextual help and parameter suggestions"""
    
    def _generate_getting_started(self) -> str:
        """Generate getting started section."""
        return """## Getting Started

### Basic Command Structure

All MCP commands follow this structure:
```json
{
  "command": "command_name",
  "parameters": {
    "parameter1": "value1",
    "parameter2": "value2"
  }
}
```

### Getting Help

Use the `help` command to learn about any command:
```json
{"command": "help", "parameters": {"command": "create_ticket"}}
```

### Your First Ticket

Create your first ticket:
```json
{
  "command": "create_ticket",
  "parameters": {
    "title": "My first ticket",
    "description": "This is a test ticket",
    "type": "task",
    "priority": "medium"
  }
}
```"""
    
    def _generate_common_workflows(self) -> str:
        """Generate common workflows section."""
        return """## Common Workflows

### Feature Development Workflow

1. **Create Epic**: Plan the feature scope
   ```json
   {"command": "create_epic", "parameters": {"title": "User Authentication", "description": "Complete auth system"}}
   ```

2. **Create Tickets**: Break down the work
   ```json
   {"command": "create_ticket", "parameters": {"title": "Login API", "epic_id": "EPIC-001"}}
   ```

3. **Track Progress**: Monitor development
   ```json
   {"command": "get_board", "parameters": {}}
   ```

### Bug Fix Workflow

1. **Create Bug Ticket**:
   ```json
   {"command": "create_ticket", "parameters": {"title": "Login fails", "type": "bug", "priority": "high"}}
   ```

2. **Assign and Track**:
   ```json
   {"command": "update_ticket", "parameters": {"ticket_id": "GCM-123", "assignee": "dev@company.com", "status": "in_progress"}}
   ```"""
    
    def _generate_command_categories(self) -> str:
        """Generate command categories section."""
        sections = ["## Command Categories"]
        
        categories = self._categorize_commands()
        for category, commands in categories.items():
            sections.append(f"\n### {category}")
            sections.append("")
            
            for cmd_name in commands:
                cmd_help = help_registry.get_command_help(cmd_name)
                if cmd_help:
                    sections.append(f"- **{cmd_name}**: {cmd_help.description}")
        
        return "\n".join(sections)
    
    def _generate_troubleshooting(self) -> str:
        """Generate troubleshooting section."""
        return """## Troubleshooting

### Common Issues

**"Ticket not found" errors**
- Check ticket ID format (use `list_tickets` to see available tickets)
- Ensure ticket exists and hasn't been deleted

**"Invalid parameter" errors**  
- Use `help` command to see required parameters
- Check parameter types and valid values
- Use `validate_command_parameters` to test before executing

**"Permission denied" errors**
- Ensure you're in a valid Gira project directory
- Check that the `.gira` directory exists

### Getting Help

- Use `help` for command documentation
- Use `search_commands` to find relevant commands
- Use `get_parameter_suggestions` for parameter help"""
    
    def _generate_examples(self) -> str:
        """Generate comprehensive examples section."""
        return """## Comprehensive Examples

### Project Setup

```json
// Create initial project structure
{"command": "create_epic", "parameters": {"title": "MVP Development", "description": "Core features for v1.0"}}

// Create sprint for work organization  
{"command": "create_sprint", "parameters": {"name": "Sprint 1", "goal": "Authentication features", "duration_days": 14}}
```

### Daily Operations

```json
// Check current work status
{"command": "get_board", "parameters": {}}

// Find my assigned tickets
{"command": "list_tickets", "parameters": {"assignee": "me@company.com", "status": ["todo", "in_progress"]}}

// Update progress
{"command": "update_ticket", "parameters": {"ticket_id": "GCM-123", "status": "review"}}
```

### Advanced Usage

```json
// Search across all content
{"command": "search", "parameters": {"query": "authentication bug", "limit": 10}}

// Bulk operations using filters
{"command": "list_tickets", "parameters": {"labels": ["critical"], "priority": "high", "limit": 50}}
```"""
    
    def _generate_table_of_contents(self) -> str:
        """Generate HTML table of contents."""
        toc_items = ["<h2>Table of Contents</h2>", "<ul>"]
        
        categories = self._categorize_commands()
        for category, commands in categories.items():
            toc_items.append(f"<li><a href='#{category.lower().replace(' ', '-')}'>{category}</a></li>")
        
        toc_items.append("</ul>")
        return "\n".join(toc_items)
    
    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML documentation."""
        return """
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #333; }
        .toc { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .command { border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 5px; }
        .parameters { width: 100%; border-collapse: collapse; margin: 10px 0; }
        .parameters th, .parameters td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .parameters th { background-color: #f2f2f2; }
        pre { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
        """


def generate_documentation_files(output_dir: Path, formats: List[str] = None):
    """
    Generate documentation files in multiple formats.
    
    Args:
        output_dir: Directory to write documentation files
        formats: List of formats to generate (markdown, html, json)
    """
    if formats is None:
        formats = ["markdown", "html", "json"]
    
    output_dir.mkdir(parents=True, exist_ok=True)
    generator = DocumentationGenerator()
    
    for format_type in formats:
        try:
            if format_type == "markdown":
                content = generator.generate_full_documentation("markdown")
                file_path = output_dir / "mcp-commands.md"
                
                # Also generate usage guide
                usage_guide = generator.generate_usage_guide()
                usage_path = output_dir / "usage-guide.md"
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                with open(usage_path, 'w') as f:
                    f.write(usage_guide)
                
                logger.info(f"Generated markdown documentation: {file_path}")
                logger.info(f"Generated usage guide: {usage_path}")
                
            elif format_type == "html":
                content = generator.generate_full_documentation("html")
                file_path = output_dir / "mcp-commands.html"
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                logger.info(f"Generated HTML documentation: {file_path}")
                
            elif format_type == "json":
                api_ref = generator.generate_api_reference()
                file_path = output_dir / "api-reference.json"
                
                with open(file_path, 'w') as f:
                    json.dump(api_ref, f, indent=2)
                
                logger.info(f"Generated JSON API reference: {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to generate {format_type} documentation: {e}")


def generate_command_specific_docs(command_name: str, output_dir: Path):
    """
    Generate documentation for a specific command.
    
    Args:
        command_name: Command to document
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generator = DocumentationGenerator()
    
    # Generate markdown documentation
    markdown_doc = generator.generate_command_documentation(command_name, "markdown")
    if markdown_doc:
        file_path = output_dir / f"{command_name}.md"
        with open(file_path, 'w') as f:
            f.write(markdown_doc)
        logger.info(f"Generated documentation for {command_name}: {file_path}")
    else:
        logger.warning(f"No documentation available for command: {command_name}")


# CLI integration for documentation generation
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python auto_documentation.py <output_dir> [formats...]")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    formats = sys.argv[2:] if len(sys.argv) > 2 else ["markdown", "html", "json"]
    
    generate_documentation_files(output_dir, formats)
    print(f"Documentation generated in {output_dir}")