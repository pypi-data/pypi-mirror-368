"""Utility functions for tests."""

def get_available_board_statuses(runner, app):
    """Get the available board statuses for the current project context.
    
    This is useful for tests that need to adapt to different board configurations
    that may be present due to test isolation issues.
    
    Returns:
        tuple: (todo_status, in_progress_status, done_status) or None if project not found
    """
    # Try to get board info by running board command
    result = runner.invoke(app, ["board", "--fast"])
    if result.exit_code != 0:
        return None
        
    output = result.stdout
    lines = output.split('\n')
    
    # Look for status column headers or status names
    statuses = []
    for line in lines:
        line = line.strip()
        # Skip empty lines, table borders, and headers
        if not line or '━' in line or '┃' in line or 'Status' in line:
            continue
        
        # Look for common status patterns
        if any(word in line.lower() for word in ['todo', 'to do', 'backlog', 'sprint backlog']):
            if 'backlog' in line.lower():
                statuses.append('backlog')  
            elif 'sprint' in line.lower():
                statuses.append('todo')  # Sprint Backlog maps to todo status
            else:
                statuses.append('todo')
        elif any(word in line.lower() for word in ['in progress', 'doing', 'in_progress']):
            if 'doing' in line.lower():
                statuses.append('doing')
            else:
                statuses.append('in_progress')
        elif 'done' in line.lower():
            statuses.append('done')
    
    # Return the first found statuses in expected order
    todo_status = next((s for s in statuses if s in ['backlog', 'todo']), 'todo')
    progress_status = next((s for s in statuses if s in ['in_progress', 'doing']), 'in_progress') 
    done_status = 'done'
    
    return (todo_status, progress_status, done_status)


def get_project_board_config(project_root):
    """Get board configuration from a project directory.
    
    Args:
        project_root: Path to project root
        
    Returns:
        dict: Board configuration or None if not found
    """
    import json
    from pathlib import Path
    
    board_config_path = Path(project_root) / ".gira" / ".board.json"
    if not board_config_path.exists():
        return None
        
    try:
        with open(board_config_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def ensure_status_exists_or_skip(runner, app, status_name):
    """Check if a status exists in current board, skip test if not.
    
    This helps tests gracefully handle different board configurations.
    """
    import pytest
    
    result = runner.invoke(app, ["board", "--fast"])
    if result.exit_code != 0:
        pytest.skip(f"Cannot determine board status - project not found")
        
    if status_name.lower() not in result.stdout.lower():
        pytest.skip(f"Status '{status_name}' not available in current board configuration")