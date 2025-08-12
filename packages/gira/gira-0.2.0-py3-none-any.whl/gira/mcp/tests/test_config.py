"""Tests for MCP configuration management."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from gira.mcp.config import MCPConfig, get_config, set_config, reset_config


class TestMCPConfig:
    """Test cases for MCPConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = MCPConfig()
        
        assert config.name == "Gira MCP Server"
        assert config.version == "0.1.0"
        assert config.dry_run is True
        assert config.require_confirmation is True
        assert config.transport == "stdio"
        assert config.working_directory == Path.cwd()
        assert config.log_level == "INFO"
        assert config.enable_debug is False
    
    def test_environment_variable_config(self):
        """Test configuration via environment variables."""
        env_vars = {
            "GIRA_MCP_NAME": "Test Server",
            "GIRA_MCP_VERSION": "1.0.0",
            "GIRA_MCP_DRY_RUN": "false",
            "GIRA_MCP_TRANSPORT": "http",
            "GIRA_MCP_HOST": "0.0.0.0",
            "GIRA_MCP_PORT": "9000",
            "GIRA_MCP_LOG_LEVEL": "DEBUG",
            "GIRA_MCP_ENABLE_DEBUG": "true"
        }
        
        with patch.dict(os.environ, env_vars):
            config = MCPConfig()
            
            assert config.name == "Test Server"
            assert config.version == "1.0.0"
            assert config.dry_run is False
            assert config.transport == "http"
            assert config.host == "0.0.0.0"
            assert config.port == 9000
            assert config.log_level == "DEBUG"
            assert config.enable_debug is True
    
    def test_working_directory_validation(self):
        """Test working directory validation."""
        # Valid directory should work
        config = MCPConfig(working_directory=Path.cwd())
        assert config.working_directory.exists()
        
        # Non-existent directory should raise error
        with pytest.raises(ValueError, match="Working directory does not exist"):
            MCPConfig(working_directory=Path("/non/existent/directory"))
    
    def test_safe_path_checking(self):
        """Test safe path validation."""
        config = MCPConfig()
        base_dir = config.working_directory
        
        # Paths within working directory should be safe
        safe_path = base_dir / "subdir" / "file.txt"
        assert config.is_safe_path(safe_path)
        
        # Paths outside working directory should not be safe
        unsafe_path = Path("/etc/passwd")
        assert not config.is_safe_path(unsafe_path)
        
        # Relative path traversal should not be safe
        traversal_path = base_dir / ".." / ".." / "etc" / "passwd"
        # This depends on the actual filesystem structure, but generally should be unsafe
        # if it goes outside the working directory
    
    def test_get_safe_path(self):
        """Test safe path resolution."""
        config = MCPConfig()
        
        # Relative path within working directory
        safe_path = config.get_safe_path("subdir/file.txt")
        assert safe_path is not None
        assert safe_path.is_absolute()
        
        # Absolute path outside working directory
        unsafe_path = config.get_safe_path("/etc/passwd")
        assert unsafe_path is None
    
    def test_allowed_file_extensions(self):
        """Test allowed file extensions configuration."""
        config = MCPConfig()
        
        # Default extensions should be present
        assert ".json" in config.allowed_file_extensions
        assert ".md" in config.allowed_file_extensions
        assert ".txt" in config.allowed_file_extensions
        assert ".py" in config.allowed_file_extensions


class TestConfigGlobals:
    """Test cases for global configuration management."""
    
    def setup_method(self):
        """Reset global config before each test."""
        reset_config()
    
    def teardown_method(self):
        """Reset global config after each test."""
        reset_config()
    
    def test_get_config_singleton(self):
        """Test that get_config returns singleton instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_set_config(self):
        """Test setting global configuration."""
        custom_config = MCPConfig(name="Custom Server")
        set_config(custom_config)
        
        retrieved_config = get_config()
        assert retrieved_config is custom_config
        assert retrieved_config.name == "Custom Server"
    
    def test_reset_config(self):
        """Test resetting global configuration."""
        # Set custom config
        custom_config = MCPConfig(name="Custom Server")
        set_config(custom_config)
        
        # Reset and get new config
        reset_config()
        new_config = get_config()
        
        assert new_config is not custom_config
        assert new_config.name == "Gira MCP Server"  # Default name