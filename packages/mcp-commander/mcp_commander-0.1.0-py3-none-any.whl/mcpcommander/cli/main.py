"""Modern CLI interface using typer."""

import os
import sys
from pathlib import Path

import typer
from colorama import Fore, Style, init
from rich import box
from rich.console import Console
from rich.table import Table

from mcpcommander import __version__
from mcpcommander.core.manager import MCPManager
from mcpcommander.utils.cli_examples import print_command_examples, should_show_examples
from mcpcommander.utils.errors import MCPCommanderError
from mcpcommander.utils.logger import configure_debug_logging, get_logger

# Initialize colorama and rich with proper Windows support
init(autoreset=True, convert=True, strip=False)

# Set console encoding for Windows
if os.name == "nt":  # Windows
    try:
        # Try to set UTF-8 encoding for better Unicode support
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        # Fall back to default encoding if UTF-8 fails
        pass


# Cross-platform Unicode support
def get_unicode_chars() -> dict[str, str]:
    """Get appropriate Unicode characters based on platform and encoding support."""
    # Try to detect if Unicode is supported
    try:
        # Test if we can encode Unicode characters
        test_chars = {"checkmark": "✅", "cross": "❌", "line": "═"}
        for char in test_chars.values():
            char.encode(sys.stdout.encoding or "utf-8")
        return {"checkmark": "✅", "cross": "❌", "line": "═", "stop": "⏹️"}
    except (UnicodeEncodeError, LookupError, AttributeError):
        # Fall back to ASCII alternatives
        return {"checkmark": "[OK]", "cross": "[ERROR]", "line": "-", "stop": "[STOP]"}


UNICODE_CHARS = get_unicode_chars()

app = typer.Typer(help="MCP Commander - Cross-platform MCP server management", add_completion=False)
# Create console with cross-platform encoding support
console = Console(legacy_windows=True, force_terminal=True)
logger = get_logger(__name__)


def help_callback(ctx: typer.Context, param: typer.CallbackParam, value: bool) -> None:
    """Custom help callback that shows examples when verbose is used."""
    if not value:
        return

    # Get command name from context
    command_name = ctx.info_name

    # Show default help
    print(ctx.get_help())

    # Show examples if --verbose is also provided
    if should_show_examples() and command_name:
        print_command_examples(command_name)

    raise typer.Exit()


@app.command()
def add(
    server_name: str = typer.Argument(..., help="Name of the server"),
    server_config: str = typer.Argument(..., help="Server configuration (JSON or command path)"),
    editor: str | None = typer.Argument(None, help="Specific editor to add server to"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Add MCP server to editors."""
    if verbose:
        configure_debug_logging()

    try:
        manager = MCPManager(config)
        result = manager.add_server(server_name, server_config, editor)

        if not result["failed"]:
            # All successful
            target = editor or "all configured editors"
            print(
                f"{Fore.GREEN}✅ Successfully added server '{server_name}' to {target}{Style.RESET_ALL}"
            )
        else:
            # Some failures - details already printed by manager
            raise typer.Exit(1)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in add command")
        raise typer.Exit(1) from e


@app.command("add-all")
def add_all(
    server_name: str = typer.Argument(..., help="Name of the server"),
    server_config: str = typer.Argument(..., help="Server configuration (JSON or command path)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Add MCP server to ALL discovered MCP configurations on the system."""
    if verbose:
        configure_debug_logging()

    try:
        manager = MCPManager()
        result = manager.add_server_to_all_discovered(server_name, server_config)

        if result["discovered_count"] == 0:
            print(
                f"\n{Fore.YELLOW}💡 Tip: Install Claude Desktop or Claude Code CLI to get started with MCP{Style.RESET_ALL}"
            )
            raise typer.Exit(0)

        if not result["failed"]:
            # All successful
            print(
                f"\n{Fore.GREEN}🎉 Successfully added '{server_name}' to all {result['discovered_count']} MCP configuration(s)!{Style.RESET_ALL}"
            )
        elif result["successful"]:
            # Partial success
            print(
                f"\n{Fore.YELLOW}⚠️  Added '{server_name}' to {len(result['successful'])}/{result['discovered_count']} configuration(s){Style.RESET_ALL}"
            )
            raise typer.Exit(1)
        else:
            # All failed
            raise typer.Exit(1)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in add-all command")
        raise typer.Exit(1) from e


@app.command()
def remove(
    server_name: str = typer.Argument(..., help="Name of the server to remove"),
    editor: str | None = typer.Argument(None, help="Specific editor to remove server from"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Remove MCP server from editors."""
    if verbose:
        configure_debug_logging()

    try:
        manager = MCPManager(config)
        result = manager.remove_server(server_name, editor)

        if not result["failed"]:
            # All successful
            target = editor or "all configured editors"
            print(
                f"{Fore.GREEN}✅ Successfully removed server '{server_name}' from {target}{Style.RESET_ALL}"
            )
        else:
            # Some failures - details already printed by manager
            raise typer.Exit(1)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in remove command")
        raise typer.Exit(1) from e


@app.command()
def list(
    editor: str | None = typer.Argument(None, help="Specific editor to list servers for"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """List configured MCP servers."""
    if verbose:
        configure_debug_logging()

    try:
        manager = MCPManager(config)
        servers = manager.list_servers(editor)

        if not any(servers.values()):
            if editor:
                print(f"{Fore.YELLOW}No servers configured for {editor}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No servers configured{Style.RESET_ALL}")
            return

        # Create rich table
        table = Table(title="Configured MCP Servers", box=box.ROUNDED)
        table.add_column("Editor", style="cyan", no_wrap=True)
        table.add_column("Server Name", style="magenta")
        table.add_column("Transport", style="yellow", no_wrap=True)
        table.add_column("Command/URL", style="green")
        table.add_column("Details", style="blue")

        for editor_name, editor_servers in servers.items():
            if not editor_servers:
                table.add_row(editor_name.upper(), "[dim]No servers[/dim]", "", "", "")
                continue

            for i, (server_name, server_config) in enumerate(editor_servers.items()):
                editor_display = editor_name.upper() if i == 0 else ""

                # Determine transport type and display info
                if "transport" in server_config:
                    transport_info = server_config["transport"]
                    transport_type = transport_info.get("type", "unknown").upper()

                    if transport_type == "HTTP":
                        command_url = f"http://{transport_info.get('host')}:{transport_info.get('port')}{transport_info.get('path', '/mcp')}"
                        details = f"Host: {transport_info.get('host')}"
                    elif transport_type == "WEBSOCKET":
                        command_url = transport_info.get("url", "")
                        details = "Headers" if transport_info.get("headers") else ""
                    elif transport_type == "SSE":
                        command_url = transport_info.get("url", "")
                        details = "Headers" if transport_info.get("headers") else ""
                    else:
                        command_url = str(transport_info)
                        details = ""
                else:
                    # Legacy STDIO format
                    transport_type = "STDIO"
                    command_url = server_config.get("command", "")
                    args = server_config.get("args", [])
                    details = " ".join(args) if args else ""

                table.add_row(editor_display, server_name, transport_type, command_url, details)

        console.print(table)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in list command")
        raise typer.Exit(1) from e


@app.command()
def status(
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Show status of all editor configurations."""
    if verbose:
        configure_debug_logging()

    try:
        manager = MCPManager(config)
        status_info = manager.status()

        print(f"{Fore.CYAN}📊 MCP Commander Status{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 30}{Style.RESET_ALL}")
        print(f"Configuration: {status_info['config_path']}")
        print()

        # Create status table
        table = Table(title="Editor Configurations", box=box.ROUNDED)
        table.add_column("Editor", style="cyan")
        table.add_column("Config Path", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Servers", style="magenta", justify="center")

        for editor_name, editor_status in status_info["editors"].items():
            if "error" in editor_status:
                status = f"[red]Error: {editor_status['error']}[/red]"
                servers = "N/A"
                config_path = editor_status.get("config_path", "Unknown")
            else:
                exists = editor_status.get("exists", False)
                readable = editor_status.get("readable", False)
                writable = editor_status.get("writable", False)

                if exists and readable:
                    status = "[green]✅ Available[/green]"
                elif exists and not readable:
                    status = "[yellow]⚠️  Permission Issue[/yellow]"
                elif not exists and writable:
                    status = "[blue]📁 Ready to Create[/blue]"
                else:
                    status = "[red]❌ Not Available[/red]"

                servers = str(editor_status.get("server_count", 0))
                config_path = editor_status.get("config_path", "")

            table.add_row(editor_name.upper(), config_path, status, servers)

        console.print(table)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in status command")
        raise typer.Exit(1) from e


@app.command()
def discover(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Discover all MCP configurations on the system."""
    if verbose:
        configure_debug_logging()

    try:
        manager = MCPManager()
        manager.print_discovery_report()

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in discover command")
        raise typer.Exit(1) from e


@app.command()
def editors(
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """List available editors in configuration."""
    try:
        manager = MCPManager(config)
        available_editors = manager.get_available_editors()

        print(f"{Fore.CYAN}📝 Available Editors:{Style.RESET_ALL}")
        for editor in available_editors:
            print(f"  - {editor}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        raise typer.Exit(1) from None


@app.command("add-editor")
def add_editor(
    name: str = typer.Argument(..., help="Name of the editor (e.g., 'vscode-custom')"),
    config_path: str = typer.Argument(..., help="Path to the editor's MCP configuration file"),
    jsonpath: str = typer.Option(
        "mcpServers", "--jsonpath", "-j", help="JSONPath to MCP servers section"
    ),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Add support for a new editor."""
    if verbose:
        configure_debug_logging()

    try:
        from mcpcommander.schemas.config_schema import EditorConfig

        manager = MCPManager(config)

        # Create new editor configuration
        editor_config = EditorConfig(config_path=config_path, jsonpath=jsonpath)

        # Add to configuration
        manager.config_manager.add_editor(name, editor_config)

        print(f"{Fore.GREEN}✅ Successfully added editor '{name}'{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Config Path: {config_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   JSON Path: {jsonpath}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}💡 You can now use '{name}' with other commands:{Style.RESET_ALL}")
        print(f'{Fore.WHITE}   mcp add server-name "command" {name}{Style.RESET_ALL}')
        print(f"{Fore.WHITE}   mcp list {name}{Style.RESET_ALL}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in add-editor command")
        raise typer.Exit(1) from e


@app.command("remove-editor")
def remove_editor(
    name: str = typer.Argument(..., help="Name of the editor to remove"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Remove support for an editor."""
    if verbose:
        configure_debug_logging()

    try:
        manager = MCPManager(config)

        # Check if editor exists
        available_editors = manager.get_available_editors()
        if name not in available_editors:
            print(f"{Fore.RED}❌ Editor '{name}' not found{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}   Available editors: {', '.join(available_editors)}{Style.RESET_ALL}"
            )
            raise typer.Exit(1)

        # Remove editor
        manager.config_manager.remove_editor(name)

        print(f"{Fore.GREEN}✅ Successfully removed editor '{name}'{Style.RESET_ALL}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose:
            logger.exception("Unexpected error in remove-editor command")
        raise typer.Exit(1) from e


@app.command()
def examples(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed examples"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Show examples of MCP server configuration formats."""
    from mcpcommander.utils.config_parser import print_transport_examples

    try:
        print_transport_examples()

        if verbose:
            print(f"\n{Fore.CYAN}💡 Usage Examples:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  # Add STDIO server (traditional):{Style.RESET_ALL}")
            print(
                f'{Fore.GREEN}  mcp add my-server "npx @modelcontextprotocol/server-filesystem /Users/user"{Style.RESET_ALL}'
            )
            print()
            print(f"{Fore.WHITE}  # Add HTTP transport server:{Style.RESET_ALL}")
            http_config = '{"transport": {"type": "http", "host": "localhost", "port": 3000}}'
            print(f"{Fore.GREEN}  mcp add api-server '{http_config}'{Style.RESET_ALL}")
            print()
            print(f"{Fore.WHITE}  # Add WebSocket server:{Style.RESET_ALL}")
            ws_config = '{"transport": {"type": "websocket", "url": "ws://localhost:8080/mcp"}}'
            print(f"{Fore.GREEN}  mcp add ws-server '{ws_config}'{Style.RESET_ALL}")
            print()
            print(f"{Fore.WHITE}  # Quick URL format (auto-detects transport):{Style.RESET_ALL}")
            print(
                f'{Fore.GREEN}  mcp add sse-server "https://example.com/mcp/stream"{Style.RESET_ALL}'
            )

    except Exception as e:
        print(f"{Fore.RED}{UNICODE_CHARS['cross']} Error showing examples: {e}{Style.RESET_ALL}")
        raise typer.Exit(1) from e


@app.command()
def version(
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Show version information."""
    print(f"MCP Commander version {__version__}")


def main() -> None:
    """Entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        print(
            f"\n{Fore.YELLOW}{UNICODE_CHARS['stop']} Operation cancelled by user{Style.RESET_ALL}"
        )
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"{Fore.RED}{UNICODE_CHARS['cross']} Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
