"""Core MCP server management functionality."""

from pathlib import Path
from typing import Any

from colorama import Fore, Style, init

from mcpcommander.core.config import ConfigManager
from mcpcommander.core.editor_handlers import EditorHandlerFactory
from mcpcommander.schemas.config_schema import EditorConfig
from mcpcommander.utils.config_parser import ServerConfigParser
from mcpcommander.utils.discovery import MCPDiscovery
from mcpcommander.utils.errors import ConfigurationError, EditorError
from mcpcommander.utils.logger import get_logger

# Initialize colorama
init()

logger = get_logger(__name__)


class MCPManager:
    """Main class for managing MCP servers across different editors."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize MCP Manager with configuration."""
        self.config_manager = ConfigManager(config_path)
        self.editor_factory = EditorHandlerFactory()
        self.discovery = MCPDiscovery()
        logger.info("MCPManager initialized")

    def add_server(
        self,
        server_name: str,
        server_config: str | dict[str, Any],
        editor_name: str | None = None,
    ) -> dict[str, Any]:
        """Add a server to specified editors or all editors."""
        try:
            # Parse and validate server configuration
            validated_config = ServerConfigParser.parse_server_config(server_config)

            # Get target editors
            target_editors = self._get_target_editors(editor_name)

            results = {}
            successful = []
            failed = []

            # Add server to each target editor
            for editor in target_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor)
                    handler = self.editor_factory.get_handler(editor, editor_config)
                    handler.add_server(server_name, validated_config)

                    successful.append(editor)
                    results[editor] = {"status": "success", "message": "Added successfully"}
                    logger.info(f"Added server '{server_name}' to {editor}")

                except Exception as e:
                    failed.append(editor)
                    results[editor] = {"status": "error", "message": str(e)}
                    logger.error(f"Failed to add server '{server_name}' to {editor}: {e}")

            # Print summary
            self._print_operation_summary("ADD", server_name, successful, failed)

            return {
                "server_name": server_name,
                "successful": successful,
                "failed": failed,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Failed to add server '{server_name}': {e}")
            raise ConfigurationError(f"Failed to add server '{server_name}': {e}") from e

    def add_server_to_all_discovered(
        self, server_name: str, server_config: str | dict[str, Any]
    ) -> dict[str, Any]:
        """Add a server to ALL discovered MCP configurations on the system."""
        logger.info(f"Adding server '{server_name}' to all discovered MCP configurations")

        try:
            # Discover all MCP configurations
            discovered = self.discovery.discover_all_mcp_configs()

            if not discovered:
                print(
                    f"{Fore.YELLOW}⚠️  No MCP configurations found on this system{Style.RESET_ALL}"
                )
                return {
                    "server_name": server_name,
                    "successful": [],
                    "failed": [],
                    "results": {},
                    "discovered_count": 0,
                }

            print(
                f"{Fore.CYAN}🔍 Discovered {len(discovered)} MCP configuration(s){Style.RESET_ALL}"
            )

            # Parse and validate server configuration
            validated_config = ServerConfigParser.parse_server_config(server_config)

            results = {}
            successful = []
            failed = []

            # Add server to each discovered configuration
            for editor_name, editor_config in discovered.items():
                try:
                    handler = self.editor_factory.get_handler(editor_name, editor_config)
                    handler.add_server(server_name, validated_config)

                    successful.append(editor_name)
                    results[editor_name] = {
                        "status": "success",
                        "message": "Added successfully",
                        "config_path": editor_config.config_path,
                    }
                    logger.info(f"Added server '{server_name}' to {editor_name}")

                except Exception as e:
                    failed.append(editor_name)
                    results[editor_name] = {
                        "status": "error",
                        "message": str(e),
                        "config_path": editor_config.config_path,
                    }
                    logger.error(f"Failed to add server '{server_name}' to {editor_name}: {e}")

            # Print detailed summary
            self._print_discovery_operation_summary("ADD", server_name, successful, failed, results)

            return {
                "server_name": server_name,
                "successful": successful,
                "failed": failed,
                "results": results,
                "discovered_count": len(discovered),
            }

        except Exception as e:
            logger.error(f"Failed to add server '{server_name}' to all configurations: {e}")
            raise ConfigurationError(f"Failed to add server to all configurations: {e}") from e

    def remove_server(self, server_name: str, editor_name: str | None = None) -> dict[str, Any]:
        """Remove a server from specified editors or all editors."""
        try:
            # Get target editors
            target_editors = self._get_target_editors(editor_name)

            results = {}
            successful = []
            failed = []

            # Remove server from each target editor
            for editor in target_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor)
                    handler = self.editor_factory.get_handler(editor, editor_config)

                    # Check if server exists
                    if not handler.server_exists(server_name):
                        failed.append(editor)
                        results[editor] = {
                            "status": "error",
                            "message": f"Server '{server_name}' not found",
                        }
                        continue

                    handler.remove_server(server_name)
                    successful.append(editor)
                    results[editor] = {"status": "success", "message": "Removed successfully"}
                    logger.info(f"Removed server '{server_name}' from {editor}")

                except Exception as e:
                    failed.append(editor)
                    results[editor] = {"status": "error", "message": str(e)}
                    logger.error(f"Failed to remove server '{server_name}' from {editor}: {e}")

            # Print summary
            self._print_operation_summary("REMOVE", server_name, successful, failed)

            return {
                "server_name": server_name,
                "successful": successful,
                "failed": failed,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Failed to remove server '{server_name}': {e}")
            raise ConfigurationError(f"Failed to remove server '{server_name}': {e}") from e

    def list_servers(self, editor_name: str | None = None) -> dict[str, dict[str, Any]]:
        """List servers configured in specified editors or all editors."""
        try:
            target_editors = self._get_target_editors(editor_name)

            all_servers = {}

            for editor in target_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor)
                    handler = self.editor_factory.get_handler(editor, editor_config)
                    servers = handler.list_servers()
                    all_servers[editor] = servers

                except Exception as e:
                    logger.error(f"Failed to list servers for {editor}: {e}")
                    all_servers[editor] = {}

            return all_servers

        except Exception as e:
            logger.error(f"Failed to list servers: {e}")
            raise ConfigurationError(f"Failed to list servers: {e}") from e

    def status(self) -> dict[str, Any]:
        """Get status of all editor configurations."""
        try:
            editors_status = {}
            available_editors = self.config_manager.get_available_editors()

            for editor_name in available_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor_name)
                    handler = self.editor_factory.get_handler(editor_name, editor_config)
                    editors_status[editor_name] = handler.get_status()

                except Exception as e:
                    logger.error(f"Failed to get status for {editor_name}: {e}")
                    editors_status[editor_name] = {
                        "error": str(e),
                        "config_path": (
                            editor_config.config_path if "editor_config" in locals() else "unknown"
                        ),
                    }

            return {"config_path": str(self.config_manager.config_path), "editors": editors_status}

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            raise ConfigurationError(f"Failed to get status: {e}") from e

    def discover_mcp_configs(self) -> dict[str, EditorConfig]:
        """Discover all MCP configurations on the system."""
        return self.discovery.discover_all_mcp_configs()

    def print_discovery_report(self) -> None:
        """Print discovery report of all MCP configurations."""
        discovered = self.discover_mcp_configs()
        self.discovery.print_discovery_report(discovered)

    def get_available_editors(self) -> list[str]:
        """Get list of available editor names."""
        return self.config_manager.get_available_editors()

    def _get_target_editors(self, editor_name: str | None) -> list[str]:
        """Get list of target editors for operation."""
        if editor_name:
            available_editors = self.config_manager.get_available_editors()
            if editor_name not in available_editors:
                raise EditorError(
                    f"Unknown editor: {editor_name}",
                    f"Available editors: {', '.join(available_editors)}",
                )
            return [editor_name]
        return self.config_manager.get_available_editors()

    def _print_operation_summary(
        self, operation: str, server_name: str, successful: list[str], failed: list[str]
    ) -> None:
        """Print colorized operation summary."""
        total = len(successful) + len(failed)

        if successful and not failed:
            print(
                f"{Fore.GREEN}✅ {operation} '{server_name}': Success on all {total} editor(s){Style.RESET_ALL}"
            )
        elif not successful and failed:
            print(
                f"{Fore.RED}❌ {operation} '{server_name}': Failed on all {total} editor(s){Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.YELLOW}⚠️  {operation} '{server_name}': Partial success ({len(successful)}/{total}){Style.RESET_ALL}"
            )

        if successful:
            print(f"{Fore.GREEN}   ✅ Successful: {', '.join(successful)}{Style.RESET_ALL}")
        if failed:
            print(f"{Fore.RED}   ❌ Failed: {', '.join(failed)}{Style.RESET_ALL}")

    def _print_discovery_operation_summary(
        self,
        operation: str,
        server_name: str,
        successful: list[str],
        failed: list[str],
        results: dict[str, Any],
    ) -> None:
        """Print detailed discovery operation summary."""
        total = len(successful) + len(failed)

        print(f"\n{Fore.CYAN}📊 {operation} Operation Summary{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 40}{Style.RESET_ALL}")

        if successful and not failed:
            print(
                f"{Fore.GREEN}✅ SUCCESS: Added '{server_name}' to all {total} discovered configuration(s){Style.RESET_ALL}"
            )
        elif not successful and failed:
            print(
                f"{Fore.RED}❌ FAILED: Could not add '{server_name}' to any configuration{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.YELLOW}⚠️  PARTIAL: Added '{server_name}' to {len(successful)}/{total} configuration(s){Style.RESET_ALL}"
            )

        # Print detailed results
        for editor_name in successful + failed:
            result = results[editor_name]
            status_color = Fore.GREEN if result["status"] == "success" else Fore.RED
            status_icon = "✅" if result["status"] == "success" else "❌"

            print(
                f"{status_color}   {status_icon} {editor_name.upper():<15} {result['config_path']}{Style.RESET_ALL}"
            )
            if result["status"] == "error":
                print(f"{Fore.RED}      Error: {result['message']}{Style.RESET_ALL}")

        if successful:
            print(
                f"\n{Fore.GREEN}🎉 Server '{server_name}' is now available in {len(successful)} MCP configuration(s){Style.RESET_ALL}"
            )
