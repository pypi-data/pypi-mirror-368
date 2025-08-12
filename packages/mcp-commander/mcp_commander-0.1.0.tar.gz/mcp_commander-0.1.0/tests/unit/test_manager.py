"""Unit tests for MCPManager class."""

from unittest.mock import Mock, patch

import pytest

from mcpcommander.core.manager import MCPManager
from mcpcommander.utils.config_parser import ServerConfigParser
from mcpcommander.utils.errors import EditorError, ValidationError


class TestMCPManager:
    """Test MCPManager functionality."""

    def test_init_creates_manager(self, mock_config_file):
        """Test MCPManager initialization."""
        manager = MCPManager(mock_config_file)
        assert manager is not None
        assert manager.config_manager is not None
        assert manager.editor_factory is not None

    def test_parse_server_config_simple_command(self, mcp_manager):
        """Test parsing simple command string."""
        config = ServerConfigParser.parse_server_config("test-command")
        assert config.command == "test-command"

    def test_parse_server_config_json_string(self, mcp_manager):
        """Test parsing JSON string configuration."""
        json_config = '{"command": "test", "args": ["arg1", "arg2"]}'
        config = ServerConfigParser.parse_server_config(json_config)
        assert config.command == "test"
        assert config.args == ["arg1", "arg2"]

    def test_parse_server_config_dict(self, mcp_manager):
        """Test parsing dictionary configuration."""
        dict_config = {"command": "test", "args": ["arg1"]}
        config = ServerConfigParser.parse_server_config(dict_config)
        assert config.command == "test"
        assert config.args == ["arg1"]

    def test_parse_server_config_invalid_json(self, mcp_manager):
        """Test parsing invalid JSON raises error."""
        with pytest.raises(ValidationError, match="Invalid JSON"):
            ServerConfigParser.parse_server_config('{"invalid": json}')

    def test_get_target_editors_specific(self, mcp_manager):
        """Test getting specific editor."""
        editors = mcp_manager._get_target_editors("claude-code")
        assert editors == ["claude-code"]

    def test_get_target_editors_all(self, mcp_manager):
        """Test getting all editors."""
        editors = mcp_manager._get_target_editors(None)
        assert isinstance(editors, list)
        assert len(editors) >= 2  # Based on sample config

    def test_get_target_editors_unknown(self, mcp_manager):
        """Test getting unknown editor raises error."""
        with pytest.raises(EditorError, match="Unknown editor"):
            mcp_manager._get_target_editors("unknown-editor")

    @patch("mcpcommander.core.manager.MCPDiscovery")
    def test_discover_mcp_configs(self, mock_discovery, mcp_manager):
        """Test MCP configuration discovery."""
        mock_discovery_instance = Mock()
        mock_discovery.return_value = mock_discovery_instance
        mock_discovery_instance.discover_all_mcp_configs.return_value = {
            "claude-code": Mock(),
            "cursor": Mock(),
        }

        # Create a new manager to test discovery
        manager = MCPManager()
        result = manager.discover_mcp_configs()

        assert len(result) == 2
        assert "claude-code" in result
        assert "cursor" in result


class TestMCPManagerOperations:
    """Test MCPManager operations with mocked handlers."""

    @patch("mcpcommander.core.manager.EditorHandlerFactory.get_handler")
    def test_add_server_success(self, mock_get_handler, mcp_manager):
        """Test successful server addition."""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler

        result = mcp_manager.add_server("test-server", "test-command", "claude-code")

        assert result["server_name"] == "test-server"
        assert result["successful"] == ["claude-code"]
        assert result["failed"] == []
        mock_handler.add_server.assert_called_once()

    @patch("mcpcommander.core.manager.EditorHandlerFactory.get_handler")
    def test_remove_server_success(self, mock_get_handler, mcp_manager):
        """Test successful server removal."""
        mock_handler = Mock()
        mock_handler.server_exists.return_value = True
        mock_get_handler.return_value = mock_handler

        result = mcp_manager.remove_server("test-server", "claude-code")

        assert result["server_name"] == "test-server"
        assert result["successful"] == ["claude-code"]
        assert result["failed"] == []
        mock_handler.remove_server.assert_called_once_with("test-server")

    @patch("mcpcommander.core.manager.EditorHandlerFactory.get_handler")
    def test_list_servers_success(self, mock_get_handler, mcp_manager):
        """Test successful server listing."""
        mock_handler = Mock()
        mock_handler.list_servers.return_value = {"test-server": {"command": "test"}}
        mock_get_handler.return_value = mock_handler

        result = mcp_manager.list_servers("claude-code")

        assert "claude-code" in result
        assert result["claude-code"]["test-server"]["command"] == "test"
        mock_handler.list_servers.assert_called_once()


class TestAddServerToAllDiscovered:
    """Test the new add_server_to_all_discovered functionality."""

    @patch("mcpcommander.core.manager.MCPDiscovery")
    @patch("mcpcommander.core.manager.EditorHandlerFactory.get_handler")
    def test_add_server_to_all_discovered_success(self, mock_get_handler, mock_discovery_class):
        """Test successful addition to all discovered configurations."""
        # Setup discovery mock
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.discover_all_mcp_configs.return_value = {
            "claude-code": Mock(config_path="/path/to/claude.json"),
            "cursor": Mock(config_path="/path/to/cursor.json"),
        }

        # Setup handler mock
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler

        # Test
        manager = MCPManager()
        result = manager.add_server_to_all_discovered("test-server", "test-command")

        assert result["server_name"] == "test-server"
        assert result["discovered_count"] == 2
        assert len(result["successful"]) == 2
        assert len(result["failed"]) == 0
        assert "claude-code" in result["successful"]
        assert "cursor" in result["successful"]

    @patch("mcpcommander.core.manager.MCPDiscovery")
    def test_add_server_to_all_discovered_no_configs(self, mock_discovery_class):
        """Test behavior when no configurations are discovered."""
        # Setup discovery mock
        mock_discovery = Mock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.discover_all_mcp_configs.return_value = {}

        # Test
        manager = MCPManager()
        result = manager.add_server_to_all_discovered("test-server", "test-command")

        assert result["server_name"] == "test-server"
        assert result["discovered_count"] == 0
        assert len(result["successful"]) == 0
        assert len(result["failed"]) == 0
