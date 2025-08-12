"""MCP configuration discovery utilities."""

import os
import platform
from pathlib import Path

from colorama import Fore, Style, init

from mcpcommander.schemas.config_schema import EditorConfig
from mcpcommander.utils.logger import get_logger

# Initialize colorama
init()

logger = get_logger(__name__)


class MCPDiscovery:
    """Discovers MCP configurations across the system."""

    def __init__(self) -> None:
        self.system = platform.system().lower()
        self.home = Path.home()

    def discover_all_mcp_configs(self) -> dict[str, EditorConfig]:
        """Discover all available MCP configurations on the system."""
        logger.info("Starting MCP configuration discovery")
        discovered = {}

        # Known MCP-compatible applications
        discovery_methods = [
            ("claude-code", self._discover_claude_code),
            ("claude-desktop", self._discover_claude_desktop),
            ("cursor", self._discover_cursor),
            ("vscode", self._discover_vscode),
            ("claude-cli", self._discover_claude_cli),
        ]

        for name, method in discovery_methods:
            try:
                config = method()
                if config:
                    discovered[name] = config
                    logger.info(f"Discovered {name} configuration at {config.config_path}")
            except Exception as e:
                logger.debug(f"Failed to discover {name}: {e}")

        logger.info(f"Discovery completed. Found {len(discovered)} MCP configurations")
        return discovered

    def _discover_claude_code(self) -> EditorConfig | None:
        """Discover Claude Code CLI configuration."""
        claude_config = self.home / ".claude.json"
        if claude_config.exists():
            return EditorConfig(config_path=str(claude_config), jsonpath="mcpServers")
        return None

    def _discover_claude_desktop(self) -> EditorConfig | None:
        """Discover Claude Desktop configuration."""
        if self.system == "darwin":  # macOS
            config_path = (
                self.home
                / "Library"
                / "Application Support"
                / "Claude"
                / "claude_desktop_config.json"
            )
        elif self.system == "windows":
            config_path = Path(os.getenv("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
        else:  # Linux
            config_path = self.home / ".config" / "Claude" / "claude_desktop_config.json"

        if config_path.exists():
            return EditorConfig(config_path=str(config_path), jsonpath="mcpServers")
        return None

    def _discover_cursor(self) -> EditorConfig | None:
        """Discover Cursor configuration."""
        if self.system == "darwin":  # macOS
            config_path = (
                self.home
                / "Library"
                / "Application Support"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "mcp.json"
            )
        elif self.system == "windows":
            config_path = (
                Path(os.getenv("APPDATA", "")) / "Cursor" / "User" / "globalStorage" / "mcp.json"
            )
        else:  # Linux
            config_path = self.home / ".config" / "Cursor" / "User" / "globalStorage" / "mcp.json"

        # Also check alternative Cursor locations
        alt_paths = [
            self.home / ".cursor" / "mcp.json",
            self.home / ".cursor" / "config.json",
        ]

        for path in [config_path] + alt_paths:
            if path.exists():
                return EditorConfig(config_path=str(path), jsonpath="mcpServers")
        return None

    def _discover_vscode(self) -> EditorConfig | None:
        """Discover VS Code configuration."""
        if self.system == "darwin":  # macOS
            # Try the specific MCP config file first
            mcp_config = (
                self.home / "Library" / "Application Support" / "Code" / "User" / "mcp.json"
            )
            if mcp_config.exists():
                return EditorConfig(config_path=str(mcp_config), jsonpath="servers")

            # Fallback to settings.json
            settings_config = (
                self.home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
            )
            if settings_config.exists():
                return EditorConfig(config_path=str(settings_config), jsonpath="mcp.servers")

        elif self.system == "windows":
            # Try MCP config file first
            mcp_config = Path(os.getenv("APPDATA", "")) / "Code" / "User" / "mcp.json"
            if mcp_config.exists():
                return EditorConfig(config_path=str(mcp_config), jsonpath="servers")

            # Fallback to settings.json
            settings_config = Path(os.getenv("APPDATA", "")) / "Code" / "User" / "settings.json"
            if settings_config.exists():
                return EditorConfig(config_path=str(settings_config), jsonpath="mcp.servers")

        else:  # Linux
            # Try MCP config file first
            mcp_config = self.home / ".config" / "Code" / "User" / "mcp.json"
            if mcp_config.exists():
                return EditorConfig(config_path=str(mcp_config), jsonpath="servers")

            # Fallback to settings.json
            settings_config = self.home / ".config" / "Code" / "User" / "settings.json"
            if settings_config.exists():
                return EditorConfig(config_path=str(settings_config), jsonpath="mcp.servers")

        return None

    def _discover_claude_cli(self) -> EditorConfig | None:
        """Discover Claude CLI configuration."""
        cli_config = self.home / ".clauderc.json"
        if cli_config.exists():
            return EditorConfig(config_path=str(cli_config), jsonpath="mcpServers")
        return None

    def print_discovery_report(self, discovered: dict[str, EditorConfig]) -> None:
        """Print colorized discovery report."""
        print(f"\n{Fore.CYAN}🔍 MCP Configuration Discovery Report{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}")

        if not discovered:
            print(f"{Fore.YELLOW}⚠️  No MCP configurations found on this system{Style.RESET_ALL}")
            print(
                f"{Fore.WHITE}   Consider installing Claude Desktop or Claude Code CLI{Style.RESET_ALL}"
            )
            return

        print(f"{Fore.GREEN}✅ Found {len(discovered)} MCP configuration(s):{Style.RESET_ALL}")

        for name, config in discovered.items():
            status = "✅" if config.expanded_path.exists() else "❌"
            color = Fore.GREEN if config.expanded_path.exists() else Fore.RED

            print(f"{color}   {status} {name.upper():<15} {config.config_path}{Style.RESET_ALL}")

        print(
            f"\n{Fore.CYAN}💡 Use 'mcp add-all <server_name> <config>' to install to all discovered configurations{Style.RESET_ALL}"
        )


def discover_mcp_configs() -> dict[str, EditorConfig]:
    """Convenience function to discover all MCP configurations."""
    discovery = MCPDiscovery()
    return discovery.discover_all_mcp_configs()


def print_discovery_report(discovered: dict[str, EditorConfig]) -> None:
    """Convenience function to print discovery report."""
    discovery = MCPDiscovery()
    discovery.print_discovery_report(discovered)
