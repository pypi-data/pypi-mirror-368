"""Editor-specific implementation handlers."""

import json
import os
from abc import ABC, abstractmethod
from typing import Any

from mcpcommander.schemas.config_schema import EditorConfig, ServerConfig
from mcpcommander.utils.errors import EditorError, FilePermissionError
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


class EditorHandler(ABC):
    """Abstract base class for editor-specific handlers."""

    def __init__(self, editor_config: EditorConfig):
        self.editor_config = editor_config
        self.config_path = editor_config.expanded_path
        self.jsonpath = editor_config.jsonpath

    @abstractmethod
    def add_server(self, server_name: str, server_config: ServerConfig) -> None:
        """Add server to editor configuration."""
        pass

    @abstractmethod
    def remove_server(self, server_name: str) -> None:
        """Remove server from editor configuration."""
        pass

    @abstractmethod
    def list_servers(self) -> dict[str, Any]:
        """List configured servers."""
        pass

    def server_exists(self, server_name: str) -> bool:
        """Check if server exists in configuration."""
        servers = self.list_servers()
        return server_name in servers

    def get_status(self) -> dict[str, Any]:
        """Get editor configuration status."""
        return {
            "config_path": str(self.config_path),
            "exists": self.config_path.exists(),
            "readable": self.config_path.exists() and os.access(self.config_path, os.R_OK),
            "writable": self.config_path.parent.exists()
            and os.access(self.config_path.parent, os.W_OK),
            "server_count": len(self.list_servers()),
        }

    def _load_editor_config(self) -> dict[str, Any]:
        """Load editor configuration file."""
        try:
            if not self.config_path.exists():
                logger.debug(f"Config file does not exist: {self.config_path}")
                return {}

            with open(self.config_path, encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logger.debug(f"Config file is empty: {self.config_path}")
                    return {}
                config_data: dict[str, Any] = json.loads(content)
                return config_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.config_path}: {e}")
            raise EditorError(f"Invalid JSON in configuration file: {e}") from e
        except PermissionError as e:
            logger.error(f"Permission denied reading {self.config_path}: {e}")
            raise FilePermissionError(f"Permission denied reading configuration file: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise EditorError(f"Failed to load configuration: {e}") from e

    def _save_editor_config(self, config: dict[str, Any]) -> None:
        """Save editor configuration file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write configuration with proper formatting
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                f.write("\n")  # Add trailing newline

            logger.debug(f"Configuration saved to {self.config_path}")

        except PermissionError as e:
            logger.error(f"Permission denied writing to {self.config_path}: {e}")
            raise FilePermissionError(
                f"Permission denied writing to configuration file: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_path}: {e}")
            raise EditorError(f"Failed to save configuration: {e}") from e

    def _get_mcp_servers_section(self, config: dict[str, Any]) -> dict[str, Any]:
        """Get MCP servers section using jsonpath."""
        if self.jsonpath == "mcpServers":
            mcp_servers: dict[str, Any] = config.get("mcpServers", {})
            return mcp_servers

        # Handle nested jsonpath (e.g., "config.mcpServers")
        keys = self.jsonpath.split(".")
        current = config
        for key in keys:
            current = current.get(key, {})
            if not isinstance(current, dict):
                return {}
        return current

    def _set_mcp_servers_section(self, config: dict[str, Any], servers: dict[str, Any]) -> None:
        """Set MCP servers section using jsonpath."""
        if self.jsonpath == "mcpServers":
            config["mcpServers"] = servers
            return

        # Handle nested jsonpath
        keys = self.jsonpath.split(".")
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = servers


class ClaudeCodeHandler(EditorHandler):
    """Handler for Claude Code CLI configuration."""

    def add_server(self, server_name: str, server_config: ServerConfig) -> None:
        """Add server to Claude Code configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        servers[server_name] = server_config.dict()
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Added server '{server_name}' to Claude Code")

    def remove_server(self, server_name: str) -> None:
        """Remove server from Claude Code configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        if server_name not in servers:
            raise EditorError(f"Server '{server_name}' not found in Claude Code configuration")

        del servers[server_name]
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Removed server '{server_name}' from Claude Code")

    def list_servers(self) -> dict[str, Any]:
        """List servers configured in Claude Code."""
        config = self._load_editor_config()
        return self._get_mcp_servers_section(config)


class ClaudeDesktopHandler(EditorHandler):
    """Handler for Claude Desktop configuration."""

    def add_server(self, server_name: str, server_config: ServerConfig) -> None:
        """Add server to Claude Desktop configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        servers[server_name] = server_config.dict()
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Added server '{server_name}' to Claude Desktop")

    def remove_server(self, server_name: str) -> None:
        """Remove server from Claude Desktop configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        if server_name not in servers:
            raise EditorError(f"Server '{server_name}' not found in Claude Desktop configuration")

        del servers[server_name]
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Removed server '{server_name}' from Claude Desktop")

    def list_servers(self) -> dict[str, Any]:
        """List servers configured in Claude Desktop."""
        config = self._load_editor_config()
        return self._get_mcp_servers_section(config)


class CursorHandler(EditorHandler):
    """Handler for Cursor configuration."""

    def add_server(self, server_name: str, server_config: ServerConfig) -> None:
        """Add server to Cursor configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        servers[server_name] = server_config.dict()
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Added server '{server_name}' to Cursor")

    def remove_server(self, server_name: str) -> None:
        """Remove server from Cursor configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        if server_name not in servers:
            raise EditorError(f"Server '{server_name}' not found in Cursor configuration")

        del servers[server_name]
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Removed server '{server_name}' from Cursor")

    def list_servers(self) -> dict[str, Any]:
        """List servers configured in Cursor."""
        config = self._load_editor_config()
        return self._get_mcp_servers_section(config)


class GenericHandler(EditorHandler):
    """Generic handler for unknown editors with JSON-based MCP configurations."""

    def add_server(self, server_name: str, server_config: ServerConfig) -> None:
        """Add server to generic configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        servers[server_name] = server_config.dict()
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Added server '{server_name}' to generic configuration")

    def remove_server(self, server_name: str) -> None:
        """Remove server from generic configuration."""
        config = self._load_editor_config()
        servers = self._get_mcp_servers_section(config)

        if server_name not in servers:
            raise EditorError(f"Server '{server_name}' not found in configuration")

        del servers[server_name]
        self._set_mcp_servers_section(config, servers)
        self._save_editor_config(config)

        logger.info(f"Removed server '{server_name}' from generic configuration")

    def list_servers(self) -> dict[str, Any]:
        """List servers configured in generic configuration."""
        config = self._load_editor_config()
        return self._get_mcp_servers_section(config)


class EditorHandlerFactory:
    """Factory for creating editor-specific handlers."""

    _handlers: dict[str, type[EditorHandler]] = {
        "claude-code": ClaudeCodeHandler,
        "claude-desktop": ClaudeDesktopHandler,
        "cursor": CursorHandler,
        "vscode": GenericHandler,  # VS Code uses generic JSON format
        "vscode-custom": GenericHandler,  # Custom VS Code configurations
        "claude-cli": ClaudeCodeHandler,  # Use same format as Claude Code
    }

    @classmethod
    def get_handler(cls, editor_name: str, editor_config: EditorConfig) -> EditorHandler:
        """Get handler instance for specified editor."""
        handler_class: type[EditorHandler] | None = cls._handlers.get(editor_name.lower())
        if not handler_class:
            # Use GenericHandler for unknown editors
            # (it works for most JSON-based MCP configurations)
            logger.debug(f"Using GenericHandler for unknown editor: {editor_name}")
            handler_class = GenericHandler
        return handler_class(editor_config)

    @classmethod
    def get_supported_editors(cls) -> list[str]:
        """Get list of supported editor names."""
        return list(cls._handlers.keys())
