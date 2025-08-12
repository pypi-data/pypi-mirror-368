"""Tests for MCP server functionality."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from gira.mcp.server import create_mcp_server, main
from gira.mcp.config import MCPConfig, set_config, reset_config


class TestMCPServer:
    """Test cases for MCP server creation and functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_config()
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_config()
    
    def test_create_mcp_server_default_config(self):
        """Test creating MCP server with default configuration."""
        server = create_mcp_server()
        
        assert server is not None
        # FastMCP server should have name and version attributes or similar
        # Note: Exact API depends on FastMCP implementation
    
    def test_create_mcp_server_custom_config(self):
        """Test creating MCP server with custom configuration."""
        custom_config = MCPConfig(
            name="Test MCP Server",
            version="1.0.0",
            dry_run=False,
            enable_debug=True
        )
        set_config(custom_config)
        
        server = create_mcp_server()
        assert server is not None
    
    def test_server_info_tool(self):
        """Test the built-in server info tool."""
        config = MCPConfig(
            name="Test Server",
            version="2.0.0",
            working_directory=Path.cwd(),
            dry_run=True,
            transport="stdio"
        )
        set_config(config)
        
        server = create_mcp_server()
        
        # Note: Testing the actual tool execution would require 
        # integration with FastMCP's testing framework
        # For now, we just verify the server is created successfully
        assert server is not None
    
    def test_health_check_tool(self):
        """Test the built-in health check tool."""
        config = MCPConfig(working_directory=Path.cwd())
        set_config(config)
        
        server = create_mcp_server()
        assert server is not None
        
        # The health check logic is embedded in the server creation
        # We verify it doesn't raise exceptions during server setup
    
    @patch('gira.mcp.server.create_mcp_server')
    @patch('asyncio.run')
    def test_main_with_stdio_transport(self, mock_asyncio_run, mock_create_server):
        """Test main function with stdio transport."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        
        with patch('sys.argv', ['gira-mcp', '--transport', 'stdio']):
            main()
        
        mock_create_server.assert_called_once()
        mock_asyncio_run.assert_called_once()
    
    @patch('gira.mcp.server.create_mcp_server')
    @patch('asyncio.run')
    def test_main_with_http_transport(self, mock_asyncio_run, mock_create_server):
        """Test main function with HTTP transport."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        
        with patch('sys.argv', ['gira-mcp', '--transport', 'http', '--host', '127.0.0.1', '--port', '8080']):
            main()
        
        mock_create_server.assert_called_once()
        mock_asyncio_run.assert_called_once()
    
    @patch('gira.mcp.server.create_mcp_server')
    @patch('asyncio.run')
    def test_main_with_custom_working_dir(self, mock_asyncio_run, mock_create_server):
        """Test main function with custom working directory."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        
        working_dir = str(Path.cwd())
        with patch('sys.argv', ['gira-mcp', '--working-dir', working_dir]):
            main()
        
        mock_create_server.assert_called_once()
        mock_asyncio_run.assert_called_once()
    
    @patch('gira.mcp.server.create_mcp_server')
    @patch('asyncio.run')
    def test_main_dry_run_flags(self, mock_asyncio_run, mock_create_server):
        """Test main function with dry-run flags."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        
        # Test --dry-run flag
        with patch('sys.argv', ['gira-mcp', '--dry-run']):
            main()
        
        # Test --no-dry-run flag
        with patch('sys.argv', ['gira-mcp', '--no-dry-run']):
            main()
        
        assert mock_create_server.call_count == 2
        assert mock_asyncio_run.call_count == 2
    
    @patch('gira.mcp.server.create_mcp_server')
    @patch('asyncio.run')
    def test_main_debug_flag(self, mock_asyncio_run, mock_create_server):
        """Test main function with debug flag."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        
        with patch('sys.argv', ['gira-mcp', '--debug']):
            main()
        
        mock_create_server.assert_called_once()
        mock_asyncio_run.assert_called_once()
    
    @patch('sys.exit')
    def test_main_invalid_transport(self, mock_exit):
        """Test main function with invalid transport."""
        with patch('sys.argv', ['gira-mcp', '--transport', 'invalid']):
            with patch('gira.mcp.config.get_config') as mock_get_config:
                mock_config = MagicMock()
                mock_config.transport = 'invalid'
                mock_get_config.return_value = mock_config
                
                main()
                
                mock_exit.assert_called_once_with(1)


class TestServerIntegration:
    """Integration tests for server functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_config()
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_config()
    
    @pytest.mark.asyncio
    async def test_server_startup_shutdown(self):
        """Test server can start up and shut down cleanly."""
        # This would be an integration test with actual FastMCP server
        # For now, just test that server creation doesn't fail
        
        config = MCPConfig(
            working_directory=Path.cwd(),
            transport="stdio"
        )
        set_config(config)
        
        server = create_mcp_server()
        assert server is not None
        
        # In a real integration test, we would:
        # 1. Start the server in a separate task
        # 2. Connect a test client
        # 3. Send test requests
        # 4. Verify responses
        # 5. Shut down cleanly
    
    def test_server_with_invalid_working_directory(self):
        """Test server handling of invalid working directory."""
        with pytest.raises(ValueError):
            MCPConfig(working_directory=Path("/non/existent/directory"))