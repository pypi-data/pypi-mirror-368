"""Tests for MCP tools infrastructure."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from gira.mcp.tools import (
    MCPToolError,
    ValidationError,
    PermissionError,
    NotFoundError,
    require_confirmation,
    validate_working_directory,
    handle_errors,
    dry_run_safe,
    normalize_ticket_id,
    normalize_epic_id,
    ToolRegistry,
    register_tool,
    tool_registry
)
from gira.mcp.errors import ErrorCodes
from gira.mcp.config import MCPConfig, set_config, reset_config
from gira.mcp.schema import OperationResult


class TestMCPExceptions:
    """Test cases for MCP exception classes."""
    
    def test_mcp_tool_error_basic(self):
        """Test basic MCPToolError functionality."""
        error = MCPToolError("Test error")
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.code is None
        assert error.details == {}
        
        error_response = error.to_error_response()
        assert error_response.error == "Test error"
        assert error_response.code is None
        assert error_response.details == {}
    
    def test_mcp_tool_error_with_details(self):
        """Test MCPToolError with code and details."""
        details = {"field": "test_field", "value": "test_value"}
        error = MCPToolError("Test error", code="test_code", details=details)
        
        assert error.code == "test_code"
        assert error.details == details
        
        error_response = error.to_error_response()
        assert error_response.code == "test_code"
        assert error_response.details == details
    
    def test_validation_error(self):
        """Test ValidationError specialized exception."""
        error = ValidationError("Invalid input", field="ticket_id")
        
        assert error.code == ErrorCodes.VALIDATION_ERROR.value
        assert error.details["field"] == "ticket_id"
    
    def test_permission_error(self):
        """Test PermissionError specialized exception."""
        error = PermissionError("Access denied", operation="delete_ticket")
        
        assert error.code == ErrorCodes.PERMISSION_ERROR.value
        assert error.details["operation"] == "delete_ticket"
    
    def test_not_found_error(self):
        """Test NotFoundError specialized exception."""
        error = NotFoundError("Resource not found", resource_type="ticket", resource_id="GCM-123")
        
        assert error.code == ErrorCodes.NOT_FOUND.value
        assert error.details["resource_type"] == "ticket"
        assert error.details["resource_id"] == "GCM-123"


class TestDecorators:
    """Test cases for tool decorators."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_config()
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_config()
    
    def test_require_confirmation_decorator(self):
        """Test require_confirmation decorator."""
        @require_confirmation("test_operation")
        def test_function():
            return "success"
        
        # With confirmation required and dry run
        config = MCPConfig(require_confirmation=True, dry_run=True)
        set_config(config)
        
        result = test_function()
        assert isinstance(result, OperationResult)
        assert not result.success
        assert result.dry_run
    
    def test_validate_working_directory_decorator(self):
        """Test validate_working_directory decorator."""
        @validate_working_directory()
        def test_function(file_path=None):
            return f"Processing {file_path}"
        
        config = MCPConfig(working_directory=Path.cwd())
        set_config(config)
        
        # Valid path within working directory
        result = test_function(file_path="test.txt")
        assert "test.txt" in str(result)
        
        # Invalid path outside working directory
        with pytest.raises(PermissionError):
            test_function(file_path="/etc/passwd")
    
    def test_handle_errors_decorator(self):
        """Test handle_errors decorator."""
        @handle_errors()
        def test_function_success():
            return "success"
        
        @handle_errors()
        def test_function_file_not_found():
            raise FileNotFoundError("File not found")
        
        @handle_errors()
        def test_function_generic_error():
            raise RuntimeError("Generic error")
        
        # Successful execution
        result = test_function_success()
        assert result == "success"
        
        # FileNotFoundError conversion
        with pytest.raises(NotFoundError):
            test_function_file_not_found()
        
        # Generic error conversion
        with pytest.raises(MCPToolError) as exc_info:
            test_function_generic_error()
        assert exc_info.value.code == ErrorCodes.INTERNAL_ERROR_LEGACY.value
    
    def test_dry_run_safe_decorator(self):
        """Test dry_run_safe decorator."""
        @dry_run_safe
        def test_function(value):
            return f"Executed with {value}"
        
        # With dry run disabled
        config = MCPConfig(dry_run=False)
        set_config(config)
        
        result = test_function("test")
        assert result == "Executed with test"
        
        # With dry run enabled
        config.dry_run = True
        set_config(config)
        
        result = test_function("test")
        assert isinstance(result, OperationResult)
        assert result.success
        assert result.dry_run
        assert "test" in str(result.data)


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_normalize_ticket_id(self):
        """Test ticket ID normalization."""
        # Number only
        assert normalize_ticket_id("123") == "GCM-123"
        
        # Already formatted
        assert normalize_ticket_id("GCM-123") == "GCM-123"
        assert normalize_ticket_id("gcm-123") == "GCM-123"
        
        # Other prefix
        assert normalize_ticket_id("PROJ-456") == "PROJ-456"
        
        # Empty string
        with pytest.raises(ValidationError):
            normalize_ticket_id("")
    
    def test_normalize_epic_id(self):
        """Test epic ID normalization."""
        # Number only
        assert normalize_epic_id("1") == "EPIC-001"
        assert normalize_epic_id("12") == "EPIC-012"
        assert normalize_epic_id("123") == "EPIC-123"
        
        # Already formatted
        assert normalize_epic_id("EPIC-001") == "EPIC-001"
        assert normalize_epic_id("epic-001") == "EPIC-001"
        
        # Empty string
        with pytest.raises(ValidationError):
            normalize_epic_id("")


class TestToolRegistry:
    """Test cases for ToolRegistry."""
    
    def test_tool_registration(self):
        """Test basic tool registration."""
        registry = ToolRegistry()
        
        def test_tool():
            return "test"
        
        registry.register(
            name="test_tool",
            func=test_tool,
            description="Test tool",
            requires_confirmation=True,
            is_destructive=False
        )
        
        tool_info = registry.get_tool("test_tool")
        assert tool_info is not None
        assert tool_info["function"] == test_tool
        assert tool_info["description"] == "Test tool"
        assert tool_info["requires_confirmation"] is True
        assert tool_info["is_destructive"] is False
    
    def test_tool_registry_list(self):
        """Test listing all tools in registry."""
        registry = ToolRegistry()
        
        def tool1():
            pass
        
        def tool2():
            pass
        
        registry.register("tool1", tool1, "First tool")
        registry.register("tool2", tool2, "Second tool")
        
        all_tools = registry.list_tools()
        assert len(all_tools) == 2
        assert "tool1" in all_tools
        assert "tool2" in all_tools
    
    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        registry = ToolRegistry()
        
        tool_info = registry.get_tool("nonexistent")
        assert tool_info is None


class TestRegisterToolDecorator:
    """Test cases for register_tool decorator."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_config()
        # Clear the global registry
        tool_registry.tools.clear()
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_config()
        tool_registry.tools.clear()
    
    def test_register_tool_decorator_basic(self):
        """Test basic tool registration with decorator."""
        @register_tool(
            name="test_tool",
            description="Test tool for testing",
            requires_confirmation=False,
            is_destructive=False
        )
        def test_tool(value: str) -> str:
            return f"Processed: {value}"
        
        # Check that tool was registered
        tool_info = tool_registry.get_tool("test_tool")
        assert tool_info is not None
        assert tool_info["description"] == "Test tool for testing"
        
        # Check that function still works
        result = test_tool("hello")
        assert result == "Processed: hello"
    
    def test_register_tool_decorator_with_decorators(self):
        """Test tool registration with automatic decorator application."""
        config = MCPConfig(dry_run=True)
        set_config(config)
        
        @register_tool(
            name="destructive_tool",
            description="A destructive tool",
            requires_confirmation=True,
            is_destructive=True
        )
        def destructive_tool(value: str) -> str:
            return f"Destroyed: {value}"
        
        # Should return OperationResult due to dry_run_safe decorator
        result = destructive_tool("test")
        assert isinstance(result, OperationResult)
        assert result.dry_run