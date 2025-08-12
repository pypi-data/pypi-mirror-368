"""Pytest configuration and fixtures."""

import json
from pathlib import Path

import pytest

from mcpcommander.core.config import ConfigManager
from mcpcommander.core.manager import MCPManager
from mcpcommander.schemas.config_schema import ServerConfig


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide temporary directory with sample config files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def sample_editor_config():
    """Provide sample editor configuration."""
    return {
        "claude-code": {"config_path": str(Path.home() / ".claude.json"), "jsonpath": "mcpServers"},
        "claude-desktop": {
            "config_path": str(
                Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
            ),
            "jsonpath": "mcpServers",
        },
    }


@pytest.fixture
def sample_server_config(tmp_path):
    """Provide sample server configuration."""
    return {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(tmp_path)],
    }


@pytest.fixture
def mock_config_file(temp_config_dir, sample_editor_config):
    """Provide mock configuration file."""
    config_file = temp_config_dir / "config.json"

    config_data = {"editors": sample_editor_config}

    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    return config_file


@pytest.fixture
def mock_editor_config_files(temp_config_dir):
    """Create mock editor configuration files."""
    # Claude Code config
    claude_config = temp_config_dir / ".claude.json"
    claude_config.write_text(
        json.dumps({"mcpServers": {"existing-server": {"command": "existing-command"}}}, indent=2)
    )

    # Claude Desktop config
    desktop_config = temp_config_dir / "claude_desktop_config.json"
    desktop_config.write_text(json.dumps({"mcpServers": {}}, indent=2))

    return {"claude-code": claude_config, "claude-desktop": desktop_config}


@pytest.fixture
def config_manager(mock_config_file):
    """Provide ConfigManager instance with test configuration."""
    return ConfigManager(mock_config_file)


@pytest.fixture
def mcp_manager(mock_config_file):
    """Provide MCPManager instance with test configuration."""
    return MCPManager(mock_config_file)


@pytest.fixture
def sample_server_config_object():
    """Provide ServerConfig instance."""
    return ServerConfig(
        command="npx", args=["-y", "@modelcontextprotocol/server-test"], env={"TEST_ENV": "value"}
    )
