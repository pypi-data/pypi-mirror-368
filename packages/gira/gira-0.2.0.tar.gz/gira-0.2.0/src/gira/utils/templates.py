"""Workflow and project templates for Gira."""

from typing import Optional

from gira.models.board import Board, Swimlane


def get_workflow_templates() -> dict[str, dict]:
    """Get available workflow templates with metadata."""
    return {
        "scrum": {
            "name": "Scrum",
            "description": "Sprint-based development with ceremonies",
            "statuses": ["Backlog", "Sprint Backlog", "In Progress", "Code Review", "Testing", "Done"],
        },
        "kanban": {
            "name": "Kanban",
            "description": "Continuous flow with WIP limits",
            "statuses": ["Backlog", "Ready", "In Progress", "Done"],
        },
        "support-desk": {
            "name": "Support Desk",
            "description": "Customer support workflow",
            "statuses": ["Triage", "In Progress", "Resolved", "Closed"],
        },
        "bug-tracking": {
            "name": "Bug Tracking",
            "description": "Bug lifecycle management",
            "statuses": ["New", "Confirmed", "In Progress", "Fixed", "Verified", "Closed"],
        },
        "minimal": {
            "name": "Minimal",
            "description": "Simple todo/done workflow",
            "statuses": ["Todo", "Doing", "Done"],
        },
        "custom": {
            "name": "Custom",
            "description": "Start from scratch with default board",
            "statuses": ["Todo", "In Progress", "Review", "Done"],
        },
    }


def create_board_from_template(template: str) -> Optional[Board]:
    """Create a board configuration from a template.
    
    Args:
        template: Template name (scrum, kanban, support-desk, bug-tracking, minimal, custom)
        
    Returns:
        Board configuration or None if template not found
    """
    if template == "scrum":
        return Board(
            swimlanes=[
                Swimlane(id="backlog", name="Backlog"),
                Swimlane(id="todo", name="Sprint Backlog"),
                Swimlane(id="in_progress", name="In Progress", limit=5),
                Swimlane(id="review", name="Code Review", limit=3),
                Swimlane(id="testing", name="Testing", limit=3),
                Swimlane(id="done", name="Done"),
            ],
            transitions={
                "backlog": ["todo", "in_progress"],  # Allow skipping sprint backlog
                "todo": ["in_progress", "backlog"],
                "in_progress": ["review", "testing", "todo", "backlog"],  # Allow skipping review
                "review": ["testing", "done", "in_progress"],  # Allow skipping testing for simple changes
                "testing": ["done", "in_progress", "review"],
                "done": ["backlog", "todo"],  # Allow reopening
            }
        )

    elif template == "kanban":
        return Board(
            swimlanes=[
                Swimlane(id="backlog", name="Backlog"),
                Swimlane(id="ready", name="Ready", limit=10),
                Swimlane(id="in_progress", name="In Progress", limit=3),
                Swimlane(id="done", name="Done"),
            ],
            transitions={
                "backlog": ["ready"],
                "ready": ["in_progress", "backlog"],
                "in_progress": ["done", "ready"],
                "done": ["backlog"],
            }
        )

    elif template == "support-desk":
        return Board(
            swimlanes=[
                Swimlane(id="triage", name="Triage"),
                Swimlane(id="in_progress", name="In Progress", limit=5),
                Swimlane(id="resolved", name="Resolved"),
                Swimlane(id="closed", name="Closed"),
            ],
            transitions={
                "triage": ["in_progress", "closed"],
                "in_progress": ["resolved", "triage"],
                "resolved": ["closed", "in_progress"],
                "closed": ["triage"],
            }
        )

    elif template == "bug-tracking":
        return Board(
            swimlanes=[
                Swimlane(id="new", name="New"),
                Swimlane(id="confirmed", name="Confirmed"),
                Swimlane(id="in_progress", name="In Progress", limit=5),
                Swimlane(id="fixed", name="Fixed"),
                Swimlane(id="verified", name="Verified"),
                Swimlane(id="closed", name="Closed"),
            ],
            transitions={
                "new": ["confirmed", "closed"],
                "confirmed": ["in_progress", "closed"],
                "in_progress": ["fixed", "confirmed"],
                "fixed": ["verified", "in_progress"],
                "verified": ["closed"],
                "closed": ["new"],
            }
        )

    elif template == "minimal":
        return Board(
            swimlanes=[
                Swimlane(id="todo", name="Todo"),
                Swimlane(id="doing", name="Doing", limit=3),
                Swimlane(id="done", name="Done"),
            ],
            transitions={
                "todo": ["doing", "done"],  # Allow direct completion for trivial tasks
                "doing": ["done", "todo"],
                "done": ["todo", "doing"],  # Allow reopening to any state
            }
        )

    elif template == "custom":
        # Return default board - let user configure as needed
        return Board.create_default(strict_workflow=False)

    return None


def get_workflow_config(workflow_type: str) -> dict:
    """Get configuration for a specific workflow type.
    
    Returns dictionary with workflow-specific settings.
    """
    configs = {
        "scrum": {
            "workflow_type": "scrum",
            "default_status": "backlog",
            "sprint_settings": {
                "duration_days": 14,
                "naming_pattern": "Sprint {number}",
                "auto_create": True,
            },
            "features": ["sprints", "velocity", "burndown"],
        },
        "kanban": {
            "workflow_type": "kanban",
            "default_status": "backlog",
            "features": ["wip_limits", "cycle_time", "cumulative_flow"],
            "board_columns": [
                {"status": "backlog", "name": "Backlog"},
                {"status": "ready", "name": "Ready", "wip_limit": 10},
                {"status": "in_progress", "name": "In Progress", "wip_limit": 3},
                {"status": "done", "name": "Done"}
            ],
        },
        "support-desk": {
            "workflow_type": "support-desk",
            "default_status": "triage",
            "features": ["sla_tracking", "priority_queue", "customer_fields"],
            "custom_fields": {
                "customer_email": {"type": "email", "required": True},
                "severity": {"type": "select", "options": ["low", "medium", "high", "critical"]},
                "sla_deadline": {"type": "datetime"},
            },
        },
        "bug-tracking": {
            "workflow_type": "bug-tracking",
            "default_status": "new",
            "features": ["severity", "reproducibility", "test_cases"],
            "custom_fields": {
                "severity": {"type": "select", "options": ["minor", "major", "critical", "blocker"]},
                "reproducible": {"type": "select", "options": ["always", "sometimes", "rarely", "unable"]},
                "affected_version": {"type": "string"},
                "fixed_version": {"type": "string"},
            },
        },
        "minimal": {
            "workflow_type": "minimal",
            "default_status": "todo",
            "features": [],
        },
        "custom": {
            "workflow_type": "custom",
            "default_status": "todo",
            "features": ["customizable"],
        },
    }

    return configs.get(workflow_type, configs["custom"])


def create_workflow_guide(workflow_type: str, project_name: str, ticket_prefix: str) -> str:
    """Generate a workflow-specific guide markdown file.
    
    Args:
        workflow_type: Type of workflow (scrum, kanban, etc.)
        project_name: Name of the project
        ticket_prefix: Ticket ID prefix
        
    Returns:
        Markdown content for the workflow guide
    """
    guides = {
        "scrum": f"""# Scrum Workflow Guide for {project_name}

## Overview
This project uses the Scrum workflow with sprint-based development cycles.

## Workflow States
1. **Backlog** - All tickets waiting to be worked on
2. **Sprint Backlog** - Tickets selected for the current sprint
3. **In Progress** - Actively being worked on (WIP limit: 5)
4. **Code Review** - Awaiting review (WIP limit: 3)
5. **Testing** - In QA/testing phase (WIP limit: 3)
6. **Done** - Completed tickets

## Common Commands

### Sprint Management
```bash
# Create a new sprint
gira sprint create "Sprint {{number}}" --duration 14

# Add tickets to sprint
gira ticket update {ticket_prefix}-1 {ticket_prefix}-2 --sprint SPRINT-ID

# View sprint progress
gira sprint show SPRINT-ID
```

### Daily Workflow
```bash
# Move ticket to in progress
gira ticket move {ticket_prefix}-1 "in progress"

# After completing work
gira ticket move {ticket_prefix}-1 review

# After review approval
gira ticket move {ticket_prefix}-1 testing

# After testing passes
gira ticket move {ticket_prefix}-1 done
```

## Best Practices
- Keep tickets small and focused (1-3 days of work)
- Update story points before sprint planning
- Move tickets through all stages (no skipping)
- Close sprint and conduct retrospective
""",

        "kanban": f"""# Kanban Workflow Guide for {project_name}

## Overview
This project uses Kanban for continuous flow development with WIP limits.

## Workflow States
1. **Backlog** - All tickets awaiting prioritization
2. **Ready** - Prioritized and ready to work (WIP limit: 10)
3. **In Progress** - Actively being worked on (WIP limit: 3)
4. **Done** - Completed tickets

## WIP Limits
- Ready: 10 tickets maximum
- In Progress: 3 tickets maximum

## Common Commands

### Managing Flow
```bash
# View board with WIP limits
gira board

# Move ticket when ready
gira ticket move {ticket_prefix}-1 ready

# Start work (check WIP limit first)
gira ticket move {ticket_prefix}-1 "in progress"

# Complete work
gira ticket move {ticket_prefix}-1 done
```

### Monitoring
```bash
# Check for bottlenecks
gira workflow stats

# View cycle time metrics
gira metrics cycle-time
```

## Best Practices
- Respect WIP limits - finish before starting new work
- Pull work when you have capacity
- Focus on flow, not utilization
- Monitor and adjust WIP limits based on team capacity
""",

        "support-desk": f"""# Support Desk Workflow Guide for {project_name}

## Overview
Customer support workflow with SLA tracking and priority management.

## Workflow States
1. **Triage** - New tickets awaiting assessment
2. **In Progress** - Being worked on (WIP limit: 5)
3. **Resolved** - Solution provided, awaiting confirmation
4. **Closed** - Ticket closed

## Common Commands

### Ticket Triage
```bash
# Create support ticket
gira ticket create "Customer issue" --type bug --priority high \\
  --custom customer_email=user@example.com --custom severity=high

# Assign and start work
gira ticket update {ticket_prefix}-1 --assignee @me
gira ticket move {ticket_prefix}-1 "in progress"
```

### Resolution Flow
```bash
# Mark as resolved
gira ticket move {ticket_prefix}-1 resolved
gira comment add {ticket_prefix}-1 # Add resolution details

# Close after confirmation
gira ticket move {ticket_prefix}-1 closed
```

## SLA Management
- Critical: 4 hours
- High: 1 business day
- Medium: 3 business days
- Low: 5 business days

## Best Practices
- Triage new tickets within 1 hour
- Set accurate severity levels
- Document resolution steps
- Follow up on resolved tickets
""",

        "bug-tracking": f"""# Bug Tracking Workflow Guide for {project_name}

## Overview
Comprehensive bug lifecycle management with verification steps.

## Workflow States
1. **New** - Newly reported bugs
2. **Confirmed** - Reproduced and confirmed
3. **In Progress** - Being fixed (WIP limit: 5)
4. **Fixed** - Fix implemented
5. **Verified** - Fix tested and confirmed
6. **Closed** - Bug resolved

## Common Commands

### Bug Reporting
```bash
# Create bug report
gira ticket create "Application crashes on login" --type bug \\
  --custom severity=major --custom reproducible=always \\
  --custom affected_version=1.2.3

# Confirm bug
gira ticket move {ticket_prefix}-1 confirmed
gira comment add {ticket_prefix}-1 # Add reproduction steps
```

### Fix Workflow
```bash
# Start fixing
gira ticket move {ticket_prefix}-1 "in progress"
gira ticket update {ticket_prefix}-1 --assignee @me

# Mark as fixed
gira ticket move {ticket_prefix}-1 fixed
gira ticket update {ticket_prefix}-1 --custom fixed_version=1.2.4

# Verify fix
gira ticket move {ticket_prefix}-1 verified

# Close bug
gira ticket move {ticket_prefix}-1 closed
```

## Severity Levels
- **Blocker**: System unusable, no workaround
- **Critical**: Major functionality broken
- **Major**: Significant impact, workaround exists
- **Minor**: Low impact, cosmetic issues

## Best Practices
- Always include reproduction steps
- Link related bugs
- Test fixes in multiple scenarios
- Document test cases for regression
""",

        "minimal": f"""# Minimal Workflow Guide for {project_name}

## Overview
Simple three-stage workflow for straightforward task management.

## Workflow States
1. **Todo** - Tasks to be done
2. **Doing** - Currently working on (WIP limit: 3)
3. **Done** - Completed tasks

## Common Commands

```bash
# Create a task
gira ticket create "Update documentation"

# Start work
gira ticket move {ticket_prefix}-1 doing

# Complete task
gira ticket move {ticket_prefix}-1 done

# View board
gira board
```

## Best Practices
- Keep tasks small and actionable
- Limit work in progress
- Review and archive done items regularly
""",

        "custom": f"""# Custom Workflow Guide for {project_name}

## Overview
This project uses a custom workflow. Customize this guide based on your team's process.

## Default Workflow States
1. **Todo** - Tasks to be done
2. **In Progress** - Currently being worked on
3. **Review** - Awaiting review
4. **Done** - Completed tasks

## Customization

### Modify Workflow States
```bash
# View current workflow
gira workflow config

# Add custom transitions
gira workflow transitions add todo blocked
gira workflow transitions add blocked "in progress"
```

### Add Custom Fields
Edit `.gira/config.json` to add custom fields for your workflow.

## Common Commands
```bash
# Basic ticket flow
gira ticket create "New task"
gira ticket move {ticket_prefix}-1 "in progress"
gira ticket move {ticket_prefix}-1 review
gira ticket move {ticket_prefix}-1 done
```

## Next Steps
1. Define your team's workflow states
2. Set up appropriate transitions
3. Configure any needed custom fields
4. Update this guide with your process
"""
    }

    return guides.get(workflow_type, guides["custom"])
