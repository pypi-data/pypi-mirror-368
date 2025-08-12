"""Configuration management for Gira MCP server."""

import os
from pathlib import Path
from typing import Optional, Dict

from pydantic import Field
from pydantic_settings import BaseSettings


class MCPConfig(BaseSettings):
    """Configuration for the Gira MCP server.
    
    Configuration can be provided via environment variables with the 
    GIRA_MCP_ prefix, or programmatically.
    """
    
    # Server metadata
    name: str = Field(default="Gira MCP Server", description="Server name")
    version: str = Field(default="0.2.0", description="Server version")
    description: str = Field(
        default="Model Context Protocol server for Gira project management",
        description="Server description"
    )
    
    # Working directory for Gira operations (legacy single-project mode)
    working_directory: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Working directory for Gira operations (legacy single-project mode)"
    )
    
    # Multi-project support
    projects: Dict[str, str] = Field(
        default_factory=dict,
        description="Registered Gira projects {name: path}"
    )
    active_project: Optional[str] = Field(
        default=None,
        description="Currently active project name"
    )
    
    # Safety settings
    dry_run: bool = Field(
        default=True,
        description="Enable dry-run mode (no actual changes made)"
    )
    require_confirmation: bool = Field(
        default=True,
        description="Require confirmation for destructive operations"
    )
    
    # Git integration settings
    auto_git_operations: bool = Field(
        default=True,
        description="Enable git operations for file moves/changes (git mv, git rm)"
    )
    
    # Transport settings
    transport: str = Field(
        default="stdio",
        description="Transport mode: stdio, http, or sse"
    )
    
    # HTTP transport settings (when transport="http")
    host: str = Field(default="localhost", description="HTTP server host")
    port: int = Field(default=8000, description="HTTP server port")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    enable_debug: bool = Field(default=False, description="Enable debug mode")
    
    # Security settings
    max_working_directory_depth: int = Field(
        default=10,
        description="Maximum depth for working directory traversal"
    )
    allowed_file_extensions: list[str] = Field(
        default_factory=lambda: [".json", ".md", ".txt", ".py"],
        description="Allowed file extensions for file operations"
    )
    
    # Enhanced security settings
    blocked_operations: list[str] = Field(
        default_factory=list,
        description="List of operations to block (e.g., 'ticket.archive', 'ticket.bulk_update')"
    )
    audit_enabled: bool = Field(
        default=True,
        description="Enable audit logging of all MCP operations"
    )
    verbose_logging: bool = Field(
        default=False,
        description="Enable verbose audit logging with parameter details"
    )
    max_input_length: int = Field(
        default=10000,
        description="Maximum length for string inputs"
    )
    max_list_length: int = Field(
        default=1000,
        description="Maximum length for list inputs"
    )
    
    class Config:
        env_prefix = "GIRA_MCP_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def model_post_init(self, __context) -> None:
        """Post-initialization validation and setup."""
        # Ensure working directory exists and is accessible
        if not self.working_directory.exists():
            raise ValueError(f"Working directory does not exist: {self.working_directory}")
        
        if not self.working_directory.is_dir():
            raise ValueError(f"Working directory is not a directory: {self.working_directory}")
        
        # Resolve to absolute path
        self.working_directory = self.working_directory.resolve()
    
    def is_safe_path(self, path: Path) -> bool:
        """Check if a path is safe to access within working directory constraints."""
        try:
            resolved_path = path.resolve()
            # Check if path is within working directory
            resolved_path.relative_to(self.working_directory)
            return True
        except (ValueError, OSError):
            return False
    
    def get_safe_path(self, path_str: str) -> Optional[Path]:
        """Get a safe path within the working directory, or None if unsafe."""
        try:
            path = Path(path_str)
            if not path.is_absolute():
                path = self.working_directory / path
            
            if self.is_safe_path(path):
                return path.resolve()
            return None
        except (ValueError, OSError):
            return None
    
    def get_active_project_path(self) -> Optional[Path]:
        """Get the path to the currently active project, or fallback to working_directory."""
        if self.active_project and self.active_project in self.projects:
            return Path(self.projects[self.active_project]).resolve()
        
        # Fallback to legacy working_directory behavior
        gira_dir = self.working_directory / '.gira'
        if gira_dir.exists() and gira_dir.is_dir():
            return self.working_directory.resolve()
        
        return None
    
    def add_project(self, name: str, path: str) -> bool:
        """Add a new project to the registry."""
        project_path = Path(path).resolve()
        gira_dir = project_path / '.gira'
        
        if not gira_dir.exists() or not gira_dir.is_dir():
            return False
        
        self.projects[name] = str(project_path)
        
        # Auto-activate first project if no active project is set
        if not self.active_project:
            self.active_project = name
            
        return True
    
    def remove_project(self, name: str) -> bool:
        """Remove a project from the registry."""
        if name not in self.projects:
            return False
        
        # If removing active project, clear active_project
        if self.active_project == name:
            self.active_project = None
            
        del self.projects[name]
        return True
    
    def switch_project(self, name: str) -> bool:
        """Switch to a different registered project."""
        if name not in self.projects:
            return False
        
        project_path = Path(self.projects[name])
        gira_dir = project_path / '.gira'
        
        if not gira_dir.exists() or not gira_dir.is_dir():
            return False
        
        self.active_project = name
        return True
    
    def list_projects(self) -> Dict[str, Dict[str, any]]:
        """List all registered projects with their status."""
        result = {}
        for name, path_str in self.projects.items():
            project_path = Path(path_str)
            gira_dir = project_path / '.gira'
            
            result[name] = {
                'path': path_str,
                'active': name == self.active_project,
                'valid': gira_dir.exists() and gira_dir.is_dir(),
                'exists': project_path.exists()
            }
        
        return result
    
    def should_use_git_operations(self) -> bool:
        """Determine if git operations should be used based on config and environment.
        
        Priority order:
        1. Environment variable (GIRA_AUTO_GIT_MV)
        2. MCP server configuration setting
        3. Default (True for AI-friendly behavior)
        
        Returns:
            Whether to use git operations for file moves/changes
        """
        # Check environment variable first (same as CLI for consistency)
        env_var = os.getenv("GIRA_AUTO_GIT_MV", "").lower()
        if env_var in ("true", "1", "yes", "on"):
            return True
        elif env_var in ("false", "0", "no", "off"):
            return False
        
        # Fall back to configuration setting
        return self.auto_git_operations
    
    def discover_projects(self, search_paths: Optional[list] = None) -> Dict[str, str]:
        """Discover Gira projects in specified paths."""
        if search_paths is None:
            search_paths = [str(Path.cwd()), str(Path.home())]
        
        discovered = {}
        
        for search_path in search_paths:
            try:
                path = Path(search_path)
                if not path.exists():
                    continue
                    
                # Check current directory
                gira_dir = path / '.gira'
                if gira_dir.exists() and gira_dir.is_dir():
                    project_name = path.name
                    discovered[project_name] = str(path.resolve())
                
                # Check subdirectories (up to 2 levels deep)
                if path.is_dir():
                    for subdir in path.iterdir():
                        if subdir.is_dir():
                            gira_dir = subdir / '.gira'
                            if gira_dir.exists() and gira_dir.is_dir():
                                project_name = subdir.name
                                discovered[project_name] = str(subdir.resolve())
                            
                            # Check one level deeper
                            for subsubdir in subdir.iterdir():
                                if subsubdir.is_dir():
                                    gira_dir = subsubdir / '.gira'
                                    if gira_dir.exists() and gira_dir.is_dir():
                                        project_name = f"{subdir.name}/{subsubdir.name}"
                                        discovered[project_name] = str(subsubdir.resolve())
                        
            except (OSError, PermissionError):
                continue
        
        return discovered


# Global configuration instance
_config: Optional[MCPConfig] = None


def get_config() -> MCPConfig:
    """Get the global MCP configuration instance."""
    global _config
    if _config is None:
        _config = MCPConfig()
    return _config


def set_config(config: MCPConfig) -> None:
    """Set the global MCP configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset the global configuration to None (will be reloaded on next access)."""
    global _config
    _config = None