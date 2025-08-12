"""Cross-platform path utilities for config and data directories."""

import os
import sys
from pathlib import Path

from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


def get_user_config_dir() -> Path:
    """Get the user configuration directory for mcpCommander.

    Platform-specific locations:
    - Windows: %APPDATA%/mcpCommander
    - macOS: ~/Library/Application Support/mcpCommander
    - Linux: ~/.config/mcpCommander

    Returns:
        Path to user config directory
    """
    app_name = "mcpCommander"

    if sys.platform == "win32":
        # Windows: %APPDATA%
        base_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~/AppData/Roaming")))
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        # Linux/Unix: ~/.config
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            base_dir = Path(config_home)
        else:
            base_dir = Path.home() / ".config"

    config_dir = base_dir / app_name

    # Ensure directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Using config directory: {config_dir}")

    return config_dir


def get_user_config_file() -> Path:
    """Get the user configuration file path."""
    return get_user_config_dir() / "config.json"


def get_legacy_config_paths() -> list[Path]:
    """Get potential legacy config file locations for migration.

    Returns:
        List of paths where config might have been stored previously
    """
    legacy_paths = [
        # Current working directory (most common legacy location)
        Path.cwd() / "config.json",
        # Project directory if different from cwd
        Path(__file__).parent.parent.parent.parent / "config.json",
    ]

    return [path for path in legacy_paths if path.exists()]


def migrate_legacy_config() -> Path | None:
    """Migrate legacy config file to user config directory.

    Returns:
        Path of migrated config file if migration occurred, None otherwise
    """
    user_config_file = get_user_config_file()

    # If user config already exists, no migration needed
    if user_config_file.exists():
        logger.debug("User config file already exists, no migration needed")
        return None

    # Find legacy config files
    legacy_configs = get_legacy_config_paths()
    if not legacy_configs:
        logger.debug("No legacy config files found")
        return None

    # Use the first found legacy config
    legacy_config = legacy_configs[0]
    logger.info(f"Migrating config from {legacy_config} to {user_config_file}")

    try:
        # Copy content to user config location
        content = legacy_config.read_text(encoding="utf-8")
        user_config_file.write_text(content, encoding="utf-8")

        logger.info(f"Successfully migrated config to {user_config_file}")
        return user_config_file

    except Exception as e:
        logger.error(f"Failed to migrate config file: {e}")
        return None


def ensure_user_config() -> Path:
    """Ensure user config file exists, creating from example or migrating if needed.

    Returns:
        Path to user config file
    """
    user_config_file = get_user_config_file()

    # Try to migrate legacy config first
    migrated = migrate_legacy_config()
    if migrated:
        return migrated

    # If no user config exists, create from example
    if not user_config_file.exists():
        # Try to find example config in the package
        example_paths = [
            # In repository
            Path(__file__).parent.parent.parent.parent / "config.example.json",
            # In installed package
            Path(__file__).parent.parent.parent / "config.example.json",
        ]

        example_config = None
        for example_path in example_paths:
            if example_path.exists():
                example_config = example_path
                break

        if example_config:
            logger.info(f"Creating user config from example: {example_config}")
            content = example_config.read_text(encoding="utf-8")
            user_config_file.write_text(content, encoding="utf-8")
        else:
            # Create minimal default config
            logger.info("Creating minimal default config")
            default_config = """{
  "editors": {
    "claude-code": {
      "config_path": "~/.claude.json",
      "jsonpath": "mcpServers"
    },
    "claude-desktop": {
      "config_path": "~/Library/Application Support/Claude/claude_desktop_config.json",
      "jsonpath": "mcpServers"
    },
    "cursor": {
      "config_path": "~/.cursor/mcp.json",
      "jsonpath": "mcpServers"
    }
  }
}"""
            user_config_file.write_text(default_config, encoding="utf-8")

    return user_config_file
