"""CLI command examples for verbose help output."""

import sys

from colorama import Fore, Style, init

# Initialize colorama
init()


def get_command_examples() -> dict[str, list[str]]:
    """Get examples for each CLI command."""
    return {
        "add": [
            'mcp add my-server "npx @modelcontextprotocol/server-filesystem /Users/user"',
            'mcp add api-server \'{"transport": {"type": "http", "host": "localhost", "port": 3000}}\' claude-code',
            'mcp add ws-server "ws://localhost:8080/mcp" vscode',
            'mcp add brave-search "npx -y @modelcontextprotocol/server-brave-search" --config custom.json',
        ],
        "add-all": [
            'mcp add-all global-server "npx @modelcontextprotocol/server-filesystem /tmp"',
            'mcp add-all api-gateway \'{"transport": {"type": "http", "host": "api.example.com", "port": 443}}\'',
            'mcp add-all realtime-ws "ws://realtime.example.com/mcp"',
        ],
        "remove": [
            "mcp remove my-server",
            "mcp remove old-server claude-code",
            "mcp remove test-api vscode",
        ],
        "list": ["mcp list", "mcp list claude-code", "mcp list vscode --verbose"],
        "status": ["mcp status", "mcp status --config custom.json", "mcp status --verbose"],
        "discover": ["mcp discover", "mcp discover --verbose"],
        "editors": ["mcp editors", "mcp editors --config custom.json"],
        "add-editor": [
            'mcp add-editor windsurf "~/.codeium/windsurf/mcp_config.json" --jsonpath mcpServers',
            'mcp add-editor sublime "~/Library/Application Support/Sublime Text/mcp.json" -j servers',
            'mcp add-editor custom-ide "/path/to/config.json"',
        ],
        "remove-editor": [
            "mcp remove-editor windsurf",
            "mcp remove-editor old-editor --config custom.json",
        ],
        "examples": ["mcp examples", "mcp examples --verbose"],
        "version": ["mcp version"],
    }


def should_show_examples() -> bool:
    """Check if we should show examples based on command line args."""
    return "--help" in sys.argv and ("--verbose" in sys.argv or "-v" in sys.argv)


def print_command_examples(command_name: str) -> None:
    """Print examples for a specific command."""
    examples = get_command_examples()
    command_examples = examples.get(command_name, [])

    if not command_examples:
        return

    print(f"\n{Fore.CYAN}💡 Examples:{Style.RESET_ALL}")
    for example in command_examples:
        print(f"{Fore.GREEN}  {example}{Style.RESET_ALL}")
    print()


def add_examples_to_help(command_name: str) -> None:
    """Add examples to help output if --verbose is used with --help."""
    if should_show_examples():
        print_command_examples(command_name)


class ExampleRichHelpFormatter:
    """Custom help formatter that adds examples when --verbose is used."""

    @staticmethod
    def add_examples_to_command(command_name: str) -> None:
        """Add examples after help is shown."""
        if should_show_examples():
            # Small delay to ensure help is shown first
            import time

            time.sleep(0.1)
            print_command_examples(command_name)
