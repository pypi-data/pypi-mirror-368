"""Configuration management for MCP Commander."""

import json
from pathlib import Path

from mcpcommander.schemas.config_schema import EditorConfig, MCPCommanderConfig
from mcpcommander.utils.errors import ConfigurationError
from mcpcommander.utils.logger import get_logger
from mcpcommander.utils.paths import ensure_user_config

logger = get_logger(__name__)


class ConfigManager:
    """Manages MCP Commander configuration."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = self._resolve_config_path(config_path)
        self._config: MCPCommanderConfig | None = None

    @property
    def config(self) -> MCPCommanderConfig:
        """Get validated configuration, loading if necessary."""
        if self._config is None:
            self._config = self._load_and_validate_config()
        return self._config

    def reload_config(self) -> None:
        """Force reload of configuration."""
        self._config = None
        logger.info("Configuration reloaded")

    def _resolve_config_path(self, config_path: Path | None) -> Path:
        """Resolve configuration file path."""
        if config_path:
            return Path(config_path).resolve()

        # Use user config directory (cross-platform)
        user_config_path = ensure_user_config()
        logger.debug(f"Using user config at {user_config_path}")
        return user_config_path

    def _load_and_validate_config(self) -> MCPCommanderConfig:
        """Load and validate configuration file."""
        try:
            if not self.config_path.exists():
                # Create default configuration
                logger.info(f"Creating default configuration at {self.config_path}")
                return self._create_default_config()

            with open(self.config_path) as f:
                raw_config = json.load(f)

            # Validate with Pydantic
            config = MCPCommanderConfig(**raw_config)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config

        except FileNotFoundError as e:
            raise ConfigurationError(f"Configuration file not found: {self.config_path}") from e
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}") from e

    def _create_default_config(self) -> MCPCommanderConfig:
        """Create default configuration file."""
        home = Path.home()

        default_editors = {
            "claude-code": EditorConfig(
                config_path=str(home / ".claude.json"), jsonpath="mcpServers"
            ),
            "claude-desktop": EditorConfig(
                config_path=self._get_claude_desktop_path(), jsonpath="mcpServers"
            ),
            "cursor": EditorConfig(
                config_path=str(home / ".cursor" / "mcp.json"), jsonpath="mcpServers"
            ),
        }

        config = MCPCommanderConfig(editors=default_editors)

        # Save default config
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(
                    {
                        "editors": {
                            name: {"config_path": editor.config_path, "jsonpath": editor.jsonpath}
                            for name, editor in default_editors.items()
                        }
                    },
                    f,
                    indent=2,
                )
            logger.info(f"Default configuration saved to {self.config_path}")
        except Exception as e:
            logger.warning(f"Failed to save default config: {e}")

        return config

    def _get_claude_desktop_path(self) -> str:
        """Get platform-specific Claude Desktop path."""
        import platform

        system = platform.system().lower()
        home = Path.home()

        if system == "darwin":  # macOS
            return str(
                home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
            )
        elif system == "windows":
            import os

            appdata = os.getenv("APPDATA", str(home / "AppData" / "Roaming"))
            return str(Path(appdata) / "Claude" / "claude_desktop_config.json")
        else:  # Linux
            return str(home / ".config" / "Claude" / "claude_desktop_config.json")

    def get_available_editors(self) -> list[str]:
        """Get list of available editor names."""
        return self.config.get_editor_names()

    def get_editor_config(self, editor_name: str) -> EditorConfig:
        """Get configuration for specific editor."""
        return self.config.get_editor_config(editor_name)

    def add_editor(self, name: str, config: EditorConfig) -> None:
        """Add new editor configuration."""
        self.config.editors[name] = config
        self._save_config()
        logger.info(f"Added editor configuration: {name}")

    def remove_editor(self, name: str) -> None:
        """Remove editor configuration."""
        if name in self.config.editors:
            del self.config.editors[name]
            self._save_config()
            logger.info(f"Removed editor configuration: {name}")
        else:
            raise ConfigurationError(f"Editor not found: {name}")

    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config_data = {
                "editors": {
                    name: {"config_path": editor.config_path, "jsonpath": editor.jsonpath}
                    for name, editor in self.config.editors.items()
                }
            }

            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=2)

        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}") from e
