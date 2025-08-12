"""Project management tools for Gira MCP server."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from gira.mcp.schema import OperationResult
from gira.mcp.config import get_config, set_config
from gira.mcp.validation import (
    coerce_array_parameter,
    ParameterValidationError,
)

logger = logging.getLogger(__name__)


class ProjectInfo(BaseModel):
    """Information about a Gira project."""
    name: str
    path: str
    active: bool
    valid: bool
    exists: bool


class ProjectListResponse(BaseModel):
    """Response for listing projects."""
    projects: Dict[str, ProjectInfo]
    active_project: Optional[str]
    total_projects: int


class ProjectDiscoveryResponse(BaseModel):
    """Response for project discovery."""
    discovered_projects: Dict[str, str]
    total_discovered: int
    search_paths: List[str]


def list_projects() -> OperationResult:
    """List all registered Gira projects with their status.
    
    Returns information about all registered projects including:
    - Project name and path
    - Whether the project is currently active
    - Whether the project directory is valid (contains .gira folder)
    - Whether the project directory exists
    
    Returns:
        OperationResult: List of projects with their status information
    """
    try:
        config = get_config()
        projects_data = config.list_projects()
        
        # Convert to ProjectInfo objects
        projects = {}
        for name, info in projects_data.items():
            projects[name] = ProjectInfo(
                name=name,
                path=info['path'],
                active=info['active'],
                valid=info['valid'],
                exists=info['exists']
            )
        
        response = ProjectListResponse(
            projects=projects,
            active_project=config.active_project,
            total_projects=len(projects)
        )
        
        return OperationResult(
            success=True,
            message=f"Found {len(projects)} registered projects",
            data=response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return OperationResult(
            success=False,
            message=f"Failed to list projects: {str(e)}"
        )


def add_project(
    name: Optional[str] = None,
    path: Optional[str] = None
) -> OperationResult:
    """Add a new Gira project to the registry.
    
    Registers a new Gira project by name and path. The path must contain
    a valid .gira directory structure.
    
    Args:
        name: Unique name for the project
        path: Absolute or relative path to the project directory
        
    Returns:
        OperationResult: Result of adding the project
    """
    try:
        # Validate required parameters
        if not name or not name.strip():
            return OperationResult(
                success=False,
                message="Project name is required"
            )
            
        if not path or not path.strip():
            return OperationResult(
                success=False,
                message="Project path is required"
            )
        
        name = name.strip()
        path = path.strip()
        
        # Validate project path
        project_path = Path(path).resolve()
        if not project_path.exists():
            return OperationResult(
                success=False,
                message=f"Project path does not exist: {project_path}"
            )
            
        if not project_path.is_dir():
            return OperationResult(
                success=False,
                message=f"Project path is not a directory: {project_path}"
            )
        
        gira_dir = project_path / '.gira'
        if not gira_dir.exists() or not gira_dir.is_dir():
            return OperationResult(
                success=False,
                message=f"Invalid Gira project: {project_path} does not contain a .gira directory"
            )
        
        # Add project to configuration
        config = get_config()
        
        # Check if project name already exists
        if name in config.projects:
            return OperationResult(
                success=False,
                message=f"Project '{name}' already exists. Use a different name or remove the existing project first."
            )
        
        # Check if path is already registered
        for existing_name, existing_path in config.projects.items():
            if Path(existing_path).resolve() == project_path:
                return OperationResult(
                    success=False,
                    message=f"Project path is already registered as '{existing_name}'"
                )
        
        success = config.add_project(name, str(project_path))
        if not success:
            return OperationResult(
                success=False,
                message=f"Failed to add project '{name}'"
            )
        
        # If this is the first project, make it active
        if not config.active_project and len(config.projects) == 1:
            config.active_project = name
            
        return OperationResult(
            success=True,
            message=f"Successfully added project '{name}' at {project_path}",
            data={
                'name': name,
                'path': str(project_path),
                'active': config.active_project == name,
                'total_projects': len(config.projects)
            }
        )
        
    except Exception as e:
        logger.error(f"Error adding project: {e}")
        return OperationResult(
            success=False,
            message=f"Failed to add project: {str(e)}"
        )


def switch_project(
    name: Optional[str] = None
) -> OperationResult:
    """Switch to a different registered Gira project.
    
    Changes the active project context for all MCP operations.
    All subsequent ticket, epic, and sprint operations will
    work with the specified project.
    
    Args:
        name: Name of the project to switch to
        
    Returns:
        OperationResult: Result of switching projects
    """
    try:
        if not name or not name.strip():
            return OperationResult(
                success=False,
                message="Project name is required"
            )
            
        name = name.strip()
        config = get_config()
        
        if name not in config.projects:
            available = list(config.projects.keys())
            return OperationResult(
                success=False,
                message=f"Project '{name}' not found. Available projects: {available}"
            )
        
        success = config.switch_project(name)
        if not success:
            return OperationResult(
                success=False,
                message=f"Failed to switch to project '{name}'. Project directory may be invalid."
            )
        
        project_path = config.projects[name]
        return OperationResult(
            success=True,
            message=f"Successfully switched to project '{name}'",
            data={
                'active_project': name,
                'project_path': project_path,
                'total_projects': len(config.projects)
            }
        )
        
    except Exception as e:
        logger.error(f"Error switching project: {e}")
        return OperationResult(
            success=False,
            message=f"Failed to switch project: {str(e)}"
        )


def remove_project(
    name: Optional[str] = None
) -> OperationResult:
    """Remove a project from the registry.
    
    Removes a project from the MCP server registry. This does not
    delete the project files, only removes it from the server's
    project list. If removing the active project, no project
    will be active afterwards.
    
    Args:
        name: Name of the project to remove
        
    Returns:
        OperationResult: Result of removing the project
    """
    try:
        if not name or not name.strip():
            return OperationResult(
                success=False,
                message="Project name is required"
            )
            
        name = name.strip()
        config = get_config()
        
        if name not in config.projects:
            available = list(config.projects.keys())
            return OperationResult(
                success=False,
                message=f"Project '{name}' not found. Available projects: {available}"
            )
        
        project_path = config.projects[name]
        was_active = config.active_project == name
        
        success = config.remove_project(name)
        if not success:
            return OperationResult(
                success=False,
                message=f"Failed to remove project '{name}'"
            )
        
        message = f"Successfully removed project '{name}'"
        if was_active:
            message += " (was active project)"
            
        return OperationResult(
            success=True,
            message=message,
            data={
                'removed_project': name,
                'removed_path': project_path,
                'was_active': was_active,
                'active_project': config.active_project,
                'remaining_projects': len(config.projects)
            }
        )
        
    except Exception as e:
        logger.error(f"Error removing project: {e}")
        return OperationResult(
            success=False,
            message=f"Failed to remove project: {str(e)}"
        )


def discover_projects(
    search_paths: Optional[str] = None
) -> OperationResult:
    """Discover Gira projects in specified directories.
    
    Searches for Gira projects (directories containing .gira folders)
    in the specified paths. Useful for finding projects that haven't
    been registered yet.
    
    Args:
        search_paths: JSON array of paths to search, defaults to current directory and home
        
    Returns:
        OperationResult: List of discovered projects
    """
    try:
        config = get_config()
        
        # Parse search paths
        paths = None
        if search_paths and search_paths.strip():
            try:
                paths = coerce_array_parameter(search_paths, 'search_paths')
            except ParameterValidationError as e:
                return OperationResult(
                    success=False,
                    message=f"Invalid search_paths parameter: {str(e)}"
                )
        
        discovered = config.discover_projects(paths)
        
        # Filter out already registered projects
        new_projects = {}
        for name, path in discovered.items():
            path_obj = Path(path).resolve()
            already_registered = False
            
            for existing_path in config.projects.values():
                if Path(existing_path).resolve() == path_obj:
                    already_registered = True
                    break
                    
            if not already_registered:
                new_projects[name] = path
        
        search_paths_used = paths or [str(Path.cwd()), str(Path.home())]
        
        response = ProjectDiscoveryResponse(
            discovered_projects=new_projects,
            total_discovered=len(new_projects),
            search_paths=search_paths_used
        )
        
        if new_projects:
            message = f"Discovered {len(new_projects)} new Gira projects"
        else:
            message = "No new Gira projects found"
            
        return OperationResult(
            success=True,
            message=message,
            data=response.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Error discovering projects: {e}")
        return OperationResult(
            success=False,
            message=f"Failed to discover projects: {str(e)}"
        )


def get_active_project() -> OperationResult:
    """Get information about the currently active project.
    
    Returns details about the active project including its name,
    path, and validation status.
    
    Returns:
        OperationResult: Information about the active project
    """
    try:
        config = get_config()
        
        if not config.active_project:
            # Check if we have a legacy working directory setup
            gira_dir = config.working_directory / '.gira'
            if gira_dir.exists() and gira_dir.is_dir():
                return OperationResult(
                    success=True,
                    message="Using legacy single-project mode",
                    data={
                        'active_project': None,
                        'legacy_mode': True,
                        'working_directory': str(config.working_directory),
                        'total_projects': len(config.projects)
                    }
                )
            else:
                return OperationResult(
                    success=False,
                    message="No active project set and no legacy project found"
                )
        
        if config.active_project not in config.projects:
            return OperationResult(
                success=False,
                message=f"Active project '{config.active_project}' not found in registry"
            )
        
        project_path = config.projects[config.active_project]
        project_path_obj = Path(project_path)
        gira_dir = project_path_obj / '.gira'
        
        return OperationResult(
            success=True,
            message=f"Active project: {config.active_project}",
            data={
                'active_project': config.active_project,
                'project_path': project_path,
                'valid': gira_dir.exists() and gira_dir.is_dir(),
                'exists': project_path_obj.exists(),
                'legacy_mode': False,
                'total_projects': len(config.projects)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting active project: {e}")
        return OperationResult(
            success=False,
            message=f"Failed to get active project: {str(e)}"
        )