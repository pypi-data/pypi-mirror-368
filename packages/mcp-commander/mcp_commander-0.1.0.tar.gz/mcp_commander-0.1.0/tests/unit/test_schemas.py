"""Unit tests for Pydantic schemas."""

from pathlib import Path

import pytest

from mcpcommander.schemas.config_schema import EditorConfig, MCPCommanderConfig, ServerConfig


class TestServerConfig:
    """Test ServerConfig schema."""

    def test_valid_server_config_minimal(self):
        """Test valid minimal server configuration."""
        config = ServerConfig(command="test-command")
        assert config.command == "test-command"
        assert config.args is None
        assert config.env is None

    def test_valid_server_config_full(self):
        """Test valid full server configuration."""
        config = ServerConfig(
            command="test-command", args=["arg1", "arg2"], env={"VAR1": "value1", "VAR2": "value2"}
        )
        assert config.command == "test-command"
        assert config.args == ["arg1", "arg2"]
        assert config.env == {"VAR1": "value1", "VAR2": "value2"}

    def test_server_config_dict_excludes_none(self):
        """Test ServerConfig.dict() excludes None values."""
        config = ServerConfig(command="test-command")
        config_dict = config.dict()

        assert config_dict == {"command": "test-command"}
        assert "args" not in config_dict
        assert "env" not in config_dict

    def test_server_config_dict_includes_values(self):
        """Test ServerConfig.dict() includes non-None values."""
        config = ServerConfig(command="test-command", args=["arg1"], env={"VAR": "value"})
        config_dict = config.dict()

        assert config_dict == {"command": "test-command", "args": ["arg1"], "env": {"VAR": "value"}}

    def test_empty_command_validation(self):
        """Test empty command validation."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            ServerConfig(command="")

    def test_whitespace_command_validation(self):
        """Test whitespace-only command validation."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            ServerConfig(command="   ")

    def test_command_strip(self):
        """Test command whitespace stripping."""
        config = ServerConfig(command="  test-command  ")
        assert config.command == "test-command"


class TestEditorConfig:
    """Test EditorConfig schema."""

    def test_valid_editor_config_minimal(self):
        """Test valid minimal editor configuration."""
        config = EditorConfig(config_path="/path/to/config.json")
        assert config.config_path == "/path/to/config.json"
        assert config.jsonpath == "mcpServers"  # Default value

    def test_valid_editor_config_full(self):
        """Test valid full editor configuration."""
        config = EditorConfig(config_path="/path/to/config.json", jsonpath="custom.path")
        assert config.config_path == "/path/to/config.json"
        assert config.jsonpath == "custom.path"

    def test_expanded_path_property(self):
        """Test expanded_path property."""
        config = EditorConfig(config_path="~/config.json")
        expanded = config.expanded_path

        assert isinstance(expanded, Path)
        assert expanded.is_absolute()  # Cross-platform absolute path check
        assert "~" not in str(expanded)  # Should be expanded

    def test_empty_config_path_validation(self):
        """Test empty config path validation."""
        with pytest.raises(ValueError, match="Configuration path cannot be empty"):
            EditorConfig(config_path="")

    def test_whitespace_config_path_validation(self):
        """Test whitespace-only config path validation."""
        with pytest.raises(ValueError, match="Configuration path cannot be empty"):
            EditorConfig(config_path="   ")

    def test_config_path_strip(self):
        """Test config path whitespace stripping."""
        config = EditorConfig(config_path="  /path/to/config.json  ")
        assert config.config_path == "/path/to/config.json"


class TestMCPCommanderConfig:
    """Test MCPCommanderConfig schema."""

    def test_valid_commander_config(self):
        """Test valid MCP Commander configuration."""
        editors = {
            "claude-code": EditorConfig(config_path="/path/to/claude.json"),
            "cursor": EditorConfig(config_path="/path/to/cursor.json"),
        }

        config = MCPCommanderConfig(editors=editors)
        assert len(config.editors) == 2
        assert "claude-code" in config.editors
        assert "cursor" in config.editors

    def test_get_editor_names(self):
        """Test get_editor_names method."""
        editors = {
            "claude-code": EditorConfig(config_path="/path/to/claude.json"),
            "cursor": EditorConfig(config_path="/path/to/cursor.json"),
        }

        config = MCPCommanderConfig(editors=editors)
        names = config.get_editor_names()

        assert isinstance(names, list)
        assert len(names) == 2
        assert "claude-code" in names
        assert "cursor" in names

    def test_get_editor_config(self):
        """Test get_editor_config method."""
        editors = {"claude-code": EditorConfig(config_path="/path/to/claude.json")}

        config = MCPCommanderConfig(editors=editors)
        editor_config = config.get_editor_config("claude-code")

        assert isinstance(editor_config, EditorConfig)
        assert editor_config.config_path == "/path/to/claude.json"

    def test_get_unknown_editor_config(self):
        """Test get_editor_config with unknown editor."""
        editors = {"claude-code": EditorConfig(config_path="/path/to/claude.json")}

        config = MCPCommanderConfig(editors=editors)

        with pytest.raises(ValueError, match="Unknown editor"):
            config.get_editor_config("unknown-editor")

    def test_empty_editors_validation(self):
        """Test empty editors validation."""
        with pytest.raises(ValueError, match="At least one editor must be configured"):
            MCPCommanderConfig(editors={})
