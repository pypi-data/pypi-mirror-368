"""
Gather project context for documentation generation.

This module collects various project statistics, configuration, and state
information to provide rich context for documentation templates.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from gira.utils.project import get_gira_root


def get_project_stats() -> Dict[str, Any]:
    """Get project statistics including ticket counts, epics, etc."""
    stats = {
        "total_tickets": 0,
        "active_tickets": 0,
        "total_epics": 0,
        "active_epics": 0,
        "total_files": 0,
        "total_lines": 0,
    }

    try:
        # Get ticket statistics
        result = subprocess.run(
            ["gira", "ticket", "list", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        tickets = json.loads(result.stdout)
        stats["total_tickets"] = len(tickets)
        stats["active_tickets"] = sum(
            1 for t in tickets
            if t.get("status", "").lower() in ["in progress", "review"]
        )

        # Get epic statistics
        result = subprocess.run(
            ["gira", "epic", "list", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        epics = json.loads(result.stdout)
        stats["total_epics"] = len(epics)
        stats["active_epics"] = sum(
            1 for e in epics
            if e.get("status", "").lower() == "active"
        )

    except (subprocess.CalledProcessError, json.JSONDecodeError):
        # If commands fail, return partial stats
        pass

    # Try to get codebase statistics
    try:
        # Count Python files (adjust for your project)
        result = subprocess.run(
            ["find", ".", "-name", "*.py", "-type", "f"],
            capture_output=True,
            text=True,
            check=True
        )
        stats["total_files"] = len(result.stdout.strip().split('\n'))

        # Count lines (rough estimate)
        result = subprocess.run(
            ["find", ".", "-name", "*.py", "-type", "f", "-exec", "wc", "-l", "{}", "+"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split('\n')
        if lines and "total" in lines[-1]:
            stats["total_lines"] = int(lines[-1].split()[0])

    except (subprocess.CalledProcessError, ValueError):
        pass

    return stats


def get_current_sprint() -> Optional[Dict[str, Any]]:
    """Get information about the current active sprint."""
    try:
        result = subprocess.run(
            ["gira", "sprint", "current", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def get_active_epics() -> List[Dict[str, Any]]:
    """Get list of active epics with their details."""
    try:
        result = subprocess.run(
            ["gira", "epic", "list", "--status", "active", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        epics = json.loads(result.stdout)

        # Enrich with ticket counts
        for epic in epics:
            try:
                result = subprocess.run(
                    ["gira", "ticket", "list", "--epic", epic["id"], "--format", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                tickets = json.loads(result.stdout)
                epic["total_tickets"] = len(tickets)
                epic["completed_tickets"] = sum(
                    1 for t in tickets
                    if t.get("status", "").lower() == "done"
                )
            except Exception:
                epic["total_tickets"] = 0
                epic["completed_tickets"] = 0

        return epics
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def get_project_config() -> Dict[str, Any]:
    """Get project configuration from .gira/config.json."""
    config = {
        "project_name": "Gira Project",
        "project_description": "A Git-native project management tool",
        "ticket_prefix": "GIRA",
        "workflow_type": "kanban",
        "primary_language": "Python",
    }

    gira_root = get_gira_root()
    if gira_root:
        gira_config = gira_root / ".gira" / "config.json"
        if gira_config.exists():
            try:
                with open(gira_config) as f:
                    file_config = json.load(f)

                # Extract relevant config
                if "project" in file_config:
                    config["project_name"] = file_config["project"].get("name", config["project_name"])
                    config["project_description"] = file_config["project"].get("description", config["project_description"])

                if "ticket" in file_config:
                    config["ticket_prefix"] = file_config["ticket"].get("prefix", config["ticket_prefix"])

                if "workflow" in file_config:
                    config["workflow_type"] = file_config["workflow"].get("type", config["workflow_type"])

            except (json.JSONDecodeError, FileNotFoundError):
                pass

    return config


def get_test_commands() -> Dict[str, str]:
    """Detect and return test-related commands for the project."""
    commands = {
        "test_command": "pytest",
        "coverage_command": "pytest --cov=src --cov-report=html",
        "test_file_command": "pytest tests/test_specific.py",
        "lint_command": "ruff check src/",
        "format_command": "ruff format src/",
        "dev_install_command": "pip install -e '.[dev]'",
    }

    # Check for different test runners
    if Path("package.json").exists():
        commands["test_command"] = "npm test"
        commands["coverage_command"] = "npm run test:coverage"
        commands["lint_command"] = "npm run lint"
        commands["format_command"] = "npm run format"
        commands["dev_install_command"] = "npm install"

    elif Path("Cargo.toml").exists():
        commands["test_command"] = "cargo test"
        commands["coverage_command"] = "cargo tarpaulin"
        commands["lint_command"] = "cargo clippy"
        commands["format_command"] = "cargo fmt"
        commands["dev_install_command"] = "cargo build"

    return commands


def get_workflow_info() -> Dict[str, Any]:
    """Get workflow-specific information."""
    config = get_project_config()
    workflow_type = config.get("workflow_type", "kanban")

    info = {
        "workflow_type": workflow_type,
        "workflow_states": [],
        "workflow_description": "",
    }

    # Define default states based on workflow type
    if workflow_type == "kanban":
        info["workflow_states"] = [
            {"name": "Todo", "description": "Work not started"},
            {"name": "In Progress", "description": "Active work"},
            {"name": "Review", "description": "Awaiting review"},
            {"name": "Done", "description": "Completed work"},
        ]
        info["workflow_description"] = "Kanban workflow with continuous flow"
    elif workflow_type == "scrum":
        info["workflow_states"] = [
            {"name": "Backlog", "description": "Product backlog"},
            {"name": "Sprint Backlog", "description": "Sprint committed work"},
            {"name": "In Progress", "description": "Active development"},
            {"name": "Review", "description": "Code review"},
            {"name": "Testing", "description": "QA testing"},
            {"name": "Done", "description": "Sprint complete"},
        ]
        info["workflow_description"] = "Scrum workflow with fixed sprints"
    else:
        # Custom workflow - try to detect from board structure
        gira_root = get_gira_root()
        if gira_root:
            board_path = gira_root / ".gira" / "board"
            if board_path.exists():
                try:
                    states = [d.name.replace("_", " ").title() for d in board_path.iterdir() if d.is_dir()]
                    info["workflow_states"] = [
                        {"name": state, "description": f"Custom state: {state}"}
                        for state in states
                    ]
                    info["workflow_description"] = "Custom workflow tailored for this project"
                except Exception:
                    pass

    return info


def gather_project_context(doc_type: str = "all",
                         project_name: Optional[str] = None,
                         project_description: Optional[str] = None,
                         ticket_prefix: Optional[str] = None,
                         workflow_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Gather comprehensive project context for documentation generation.

    Args:
        doc_type: Type of documentation being generated
        project_name: Override project name
        project_description: Override project description
        ticket_prefix: Override ticket prefix
        workflow_type: Override workflow type

    Returns:
        Dictionary containing all project context
    """
    context = {
        "generation_date": datetime.now().strftime("%Y-%m-%d"),
        "gira_version": "0.1.0",  # TODO: Get from package
    }

    # Get basic project configuration
    config = get_project_config()

    # Apply overrides if provided
    if project_name:
        config["project_name"] = project_name
    if project_description:
        config["project_description"] = project_description
    if ticket_prefix:
        config["ticket_prefix"] = ticket_prefix
    if workflow_type:
        config["workflow_type"] = workflow_type

    context.update(config)

    # Try to get project statistics (may fail if not in a gira project)
    try:
        context["stats"] = get_project_stats()
    except Exception:
        context["stats"] = {
            "total_tickets": 0,
            "active_tickets": 0,
            "total_epics": 0,
            "active_epics": 0,
        }

    # Get test/development commands
    context.update(get_test_commands())

    # Try to get sprint information (if using Scrum)
    try:
        context["current_sprint"] = get_current_sprint()
    except Exception:
        context["current_sprint"] = None

    # Try to get active epics
    try:
        context["active_epics"] = get_active_epics()
    except Exception:
        context["active_epics"] = []

    # Get workflow information
    workflow_info = get_workflow_info()
    if workflow_type:
        workflow_info["workflow_type"] = workflow_type
    context.update(workflow_info)

    # Add doc-type specific context
    if doc_type == "agents":
        # Add agent-specific context
        context["next_sprint_number"] = "X"  # Placeholder
        context["coverage_target"] = "80%"

    elif doc_type == "workflow":
        # Add workflow-specific context
        if context["workflow_type"] == "scrum":
            context["sprint_duration"] = 14
            context["estimation_scale"] = ["1", "2", "3", "5", "8", "13", "21"]
        elif context["workflow_type"] == "kanban":
            context["wip_limits"] = {
                "in_progress": 3,
                "review": 5,
            }
            context["archive_after"] = 30

    return context

