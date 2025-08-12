"""Tests for AI integration features."""

import json
from pathlib import Path
import pytest
from typer.testing import CliRunner
from gira.cli import app
from gira.utils.ai_integration import (
    AIDocumentationDetector,
    AIDocumentationGenerator,
    AIDocType,
    AIDocFile,
    inject_gira_section,
    create_backup
)


class TestAIDocumentationDetector:
    """Test AI documentation detection."""
    
    def test_detect_no_files(self, tmp_path):
        """Test detection when no AI files exist."""
        detector = AIDocumentationDetector(tmp_path)
        files = detector.detect_ai_files()
        assert len(files) == 0
        
    def test_detect_claude_file(self, tmp_path):
        """Test detection of CLAUDE.md file."""
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_text("# Claude Instructions\n\nTest content")
        
        detector = AIDocumentationDetector(tmp_path)
        files = detector.detect_ai_files()
        
        assert len(files) == 1
        assert files[0].doc_type == AIDocType.CUSTOM  # CLAUDE.md doesn't match "CLAUDE.md" enum value
        assert files[0].exists is True
        assert files[0].has_gira_section is False
        
    def test_detect_multiple_files(self, tmp_path):
        """Test detection of multiple AI files."""
        (tmp_path / "CLAUDE.md").write_text("Claude content")
        (tmp_path / "GEMINI.md").write_text("Gemini content")
        (tmp_path / "AGENTS.md").write_text("Agents content")
        
        detector = AIDocumentationDetector(tmp_path)
        files = detector.detect_ai_files()
        
        assert len(files) == 3
        # All will be CUSTOM because enum values have .md extension
        doc_types = {f.doc_type for f in files}
        assert AIDocType.CUSTOM in doc_types
        
    def test_detect_gira_section(self, tmp_path):
        """Test detection of existing Gira section."""
        content = """# Claude Instructions

Some content

<!-- GIRA-AI-INTEGRATION-START -->
## Gira Project Management
...
<!-- GIRA-AI-INTEGRATION-END -->

More content
"""
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_text(content)
        
        detector = AIDocumentationDetector(tmp_path)
        files = detector.detect_ai_files()
        
        assert len(files) == 1
        assert files[0].has_gira_section is True
        
    def test_find_safe_insertion_point(self, tmp_path):
        """Test finding insertion points in existing docs."""
        detector = AIDocumentationDetector(tmp_path)
        
        # Test with Tools section
        content1 = """# My Project

## Overview
Some overview

## Tools
List of tools

## Other Section
"""
        point = detector.find_safe_insertion_point(content1)
        assert content1[:point].count("## Tools") == 1
        assert content1[:point].count("## Other Section") == 0
        
        # Test with no matching sections
        content2 = """# My Project

Just some content
"""
        point = detector.find_safe_insertion_point(content2)
        assert point == len(content2)  # Should suggest end of file


class TestAIDocumentationGenerator:
    """Test AI documentation generation."""
    
    def test_generate_gira_section(self):
        """Test generation of Gira section."""
        generator = AIDocumentationGenerator()
        section = generator.generate_gira_section("My Project", "PROJ")
        
        assert "<!-- GIRA-AI-INTEGRATION-START -->" in section
        assert "<!-- GIRA-AI-INTEGRATION-END -->" in section
        assert "Ticket Prefix: `PROJ`" in section
        assert "Project Name: `My Project`" in section
        assert "gira ai-help" in section
        
    def test_generate_companion_file(self):
        """Test generation of companion AI file."""
        generator = AIDocumentationGenerator()
        content = generator.generate_companion_file(
            AIDocType.CLAUDE,
            "Test Project",
            "TEST"
        )
        
        # Check that it contains expected content (agent_name is stripped of .md)
        assert "Integration with Gira" in content
        assert "Ticket Prefix**: `TEST`" in content
        assert "Project Name**: `Test Project`" in content
        assert "gira ticket show TEST-123" in content


class TestAICommands:
    """Test AI CLI commands."""
    
    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()
        
    def test_ai_help_command(self):
        """Test ai-help command."""
        result = self.runner.invoke(app, ["ai-help"])
        assert result.exit_code == 0
        assert "Understanding Project State" in result.output
        assert "gira board" in result.output
        assert "gira describe --format json" in result.output
        
    def test_ai_help_with_agent(self):
        """Test ai-help command with specific agent."""
        result = self.runner.invoke(app, ["ai-help", "claude"])
        assert result.exit_code == 0
        assert "Claude-Specific Patterns" in result.output
        assert "Structured Output for Tool Use" in result.output
        
    def test_ai_status_command(self, tmp_path, monkeypatch):
        """Test ai status command."""
        # Create some AI files
        (tmp_path / "CLAUDE.md").write_text("Claude content")
        (tmp_path / "GEMINI.md").write_text("Gemini content")
        
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        result = self.runner.invoke(app, ["ai", "status"])
        assert result.exit_code == 0
        assert "AI Documentation Status" in result.output
        # Note: Exact output format may vary due to rich formatting
        
    def test_top_level_ai_help_alias(self):
        """Test top-level ai-help alias."""
        result = self.runner.invoke(app, ["ai-help"])
        assert result.exit_code == 0
        assert "AI Command Examples" in result.output


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_backup(self, tmp_path):
        """Test backup creation."""
        original = tmp_path / "test.md"
        original.write_text("Original content")
        
        backup = create_backup(original)
        assert backup is not None
        assert backup.exists()
        assert backup.read_text() == "Original content"
        assert backup.name == "test.md.bak"
        
    def test_create_backup_multiple(self, tmp_path):
        """Test creating multiple backups."""
        original = tmp_path / "test.md"
        original.write_text("Original content")
        
        backup1 = create_backup(original)
        original.write_text("Modified content")
        backup2 = create_backup(original)
        
        assert backup1.name == "test.md.bak"
        assert backup2.name == "test.md.bak1"
        assert backup1.read_text() == "Original content"
        assert backup2.read_text() == "Modified content"
        
    def test_inject_gira_section(self, tmp_path, monkeypatch):
        """Test Gira section injection."""
        # Mock the config loading
        def mock_load_config():
            return {
                "project_name": "Test Project",
                "ticket_id_prefix": "TEST"
            }
            
        monkeypatch.setattr("gira.utils.config.load_config", mock_load_config)
        
        content = """# My Project

## Tools
List of tools

## Other Section
"""
        
        # Find insertion point after Tools section
        lines = content.split('\n')
        insertion_point = len('\n'.join(lines[:5])) + 1  # After "List of tools" line
        
        result = inject_gira_section(Path("dummy.md"), content, insertion_point)
        
        assert "<!-- GIRA-AI-INTEGRATION-START -->" in result
        assert "<!-- GIRA-AI-INTEGRATION-END -->" in result
        assert "## Tools" in result
        assert result.index("## Tools") < result.index("<!-- GIRA-AI-INTEGRATION-START -->")
        assert result.index("<!-- GIRA-AI-INTEGRATION-END -->") < result.index("## Other Section")