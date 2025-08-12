"""Unit tests for ConfigManager class."""

import json

import pytest

from mcpcommander.core.config import ConfigManager
from mcpcommander.schemas.config_schema import EditorConfig
from mcpcommander.utils.errors import ConfigurationError


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_init_with_config_path(self, mock_config_file):
        """Test ConfigManager initialization with config path."""
        manager = ConfigManager(mock_config_file)
        assert manager.config_path == mock_config_file.resolve()

    def test_init_without_config_path(self):
        """Test ConfigManager initialization without config path."""
        manager = ConfigManager()
        assert manager.config_path is not None

    def test_load_valid_config(self, config_manager):
        """Test loading valid configuration."""
        config = config_manager.config
        assert config is not None
        assert len(config.editors) >= 2
        assert "claude-code" in config.editors

    def test_get_available_editors(self, config_manager):
        """Test getting available editors."""
        editors = config_manager.get_available_editors()
        assert isinstance(editors, list)
        assert "claude-code" in editors
        assert "claude-desktop" in editors

    def test_get_editor_config(self, config_manager):
        """Test getting specific editor configuration."""
        editor_config = config_manager.get_editor_config("claude-code")
        assert isinstance(editor_config, EditorConfig)
        assert editor_config.jsonpath == "mcpServers"

    def test_get_unknown_editor_config(self, config_manager):
        """Test getting unknown editor configuration."""
        with pytest.raises(ValueError, match="Unknown editor"):
            config_manager.get_editor_config("unknown-editor")

    def test_create_default_config(self, tmp_path):
        """Test creating default configuration."""
        config_path = tmp_path / "new_config.json"
        manager = ConfigManager(config_path)

        # Access config property to trigger creation
        config = manager.config

        assert config is not None
        assert config_path.exists()
        assert len(config.editors) >= 3  # Should have at least claude-code, claude-desktop, cursor

    def test_reload_config(self, config_manager, mock_config_file):
        """Test configuration reloading."""
        # Get initial config
        initial_config = config_manager.config

        # Modify config file
        new_config = {
            "editors": {"test-editor": {"config_path": "/test/path", "jsonpath": "testPath"}}
        }

        with open(mock_config_file, "w") as f:
            json.dump(new_config, f)

        # Reload and verify
        config_manager.reload_config()
        reloaded_config = config_manager.config

        assert reloaded_config != initial_config
        assert "test-editor" in reloaded_config.editors
        assert len(reloaded_config.editors) == 1


class TestConfigManagerErrors:
    """Test ConfigManager error handling."""

    def test_invalid_json_config(self, tmp_path):
        """Test handling invalid JSON configuration."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{ invalid json }")

        manager = ConfigManager(config_file)
        with pytest.raises(ConfigurationError, match="Invalid JSON"):
            _ = manager.config

    def test_missing_editors_section(self, tmp_path):
        """Test handling missing editors section."""
        config_file = tmp_path / "no_editors.json"
        config_file.write_text('{"other": "data"}')

        manager = ConfigManager(config_file)
        with pytest.raises(ConfigurationError, match="validation failed"):
            _ = manager.config

    def test_empty_editors_section(self, tmp_path):
        """Test handling empty editors section."""
        config_file = tmp_path / "empty_editors.json"
        config_file.write_text('{"editors": {}}')

        manager = ConfigManager(config_file)
        with pytest.raises(ConfigurationError, match="validation failed"):
            _ = manager.config
