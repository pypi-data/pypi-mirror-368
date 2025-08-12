"""MCP Commander - Cross-platform MCP server management tool."""

__version__ = "0.1.0"
__author__ = "Evandro Camargo"
__license__ = "Apache-2.0"
__description__ = "A command-line tool to manage MCP servers across different code editors"

from mcpcommander.core.manager import MCPManager
from mcpcommander.utils.errors import (
    ConfigurationError,
    EditorError,
    MCPCommanderError,
    ValidationError,
)

__all__ = [
    "MCPManager",
    "MCPCommanderError",
    "ConfigurationError",
    "EditorError",
    "ValidationError",
    "__version__",
]
