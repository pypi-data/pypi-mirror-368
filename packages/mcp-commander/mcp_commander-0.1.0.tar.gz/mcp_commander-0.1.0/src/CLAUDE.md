# Source Code Context - mcpCommander/src

## Source Code Architecture Overview

This directory will contain the modernized, enterprise-grade Python source code for the MCP Commander project, transformed from the current basic implementation to match the sophistication observed in the jira-mcp reference implementation.

## Current Source State vs Target

### Current Implementation Analysis
- **File**: `mcp_manager.py` (256 lines) - Monolithic implementation
- **Structure**: Single file with all functionality
- **Standards**: Basic Python with minimal error handling
- **Dependencies**: Standard library only (json, os, sys, argparse, pathlib)

### Target Architecture Transformation
```
src/
├── mcpcommander/                    # Main package directory
│   ├── __init__.py                  # Package initialization and version
│   ├── core/                        # Core business logic
│   │   ├── __init__.py
│   │   ├── manager.py               # Refactored MCPManager class
│   │   ├── config.py                # Configuration management
│   │   └── editor_handlers.py       # Editor-specific implementations
│   ├── cli/                         # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py                  # CLI implementation with typer
│   ├── utils/                       # Utility modules
│   │   ├── __init__.py
│   │   ├── logger.py                # Structured logging
│   │   ├── errors.py                # Custom exceptions
│   │   └── validators.py            # Input validation
│   ├── schemas/                     # Data validation schemas
│   │   ├── __init__.py
│   │   └── config_schema.py         # Pydantic models
│   └── py.typed                     # PEP 561 type information marker
```

## Architecture Transformation Plan

### Phase 1: Core Module Restructuring

#### 1. Package Initialization (`__init__.py`)
```python
"""MCP Commander - Cross-platform MCP server management tool."""

__version__ = "2.0.0"
__author__ = "Evandro Camargo"
__license__ = "Apache-2.0"

from mcpcommander.core.manager import MCPManager
from mcpcommander.utils.errors import (
    MCPCommanderError,
    ConfigurationError,
    EditorError,
    ValidationError
)

__all__ = [
    "MCPManager",
    "MCPCommanderError",
    "ConfigurationError",
    "EditorError",
    "ValidationError",
    "__version__"
]
```

#### 2. Core Manager (`core/manager.py`)
**Transformation**: mcp_manager.py → Modular, typed implementation

```python
"""Core MCP server management functionality."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from mcpcommander.core.config import ConfigManager
from mcpcommander.core.editor_handlers import EditorHandlerFactory
from mcpcommander.schemas.config_schema import ServerConfig, EditorConfig
from mcpcommander.utils.errors import ConfigurationError, EditorError
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)

class MCPManager:
    """Main class for managing MCP servers across different editors."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize MCP Manager with configuration."""
        self.config_manager = ConfigManager(config_path)
        self.editor_factory = EditorHandlerFactory()
        logger.info("MCPManager initialized")

    def add_server(
        self,
        server_name: str,
        server_config: Union[str, Dict[str, Any]],
        editor_name: Optional[str] = None
    ) -> None:
        """Add a server to specified editors or all editors."""
        try:
            # Parse and validate server configuration
            parsed_config = self._parse_server_config(server_config)
            validated_config = ServerConfig(**parsed_config)

            # Get target editors
            target_editors = self._get_target_editors(editor_name)

            # Add server to each target editor
            for editor in target_editors:
                handler = self.editor_factory.get_handler(editor)
                handler.add_server(server_name, validated_config)
                logger.info(f"Added server '{server_name}' to {editor}")

        except Exception as e:
            raise ConfigurationError(f"Failed to add server '{server_name}': {e}") from e

    def remove_server(
        self,
        server_name: str,
        editor_name: Optional[str] = None
    ) -> None:
        """Remove a server from specified editors or all editors."""
        # Implementation with proper error handling and logging
        pass

    def list_servers(self, editor_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List servers configured in specified editors or all editors."""
        # Implementation returning structured data
        pass

    def status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all editor configurations."""
        # Implementation returning comprehensive status
        pass

    def _parse_server_config(self, config: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Parse server configuration from string or dict."""
        if isinstance(config, str):
            if config.startswith('{'):
                import json
                return json.loads(config)
            return {"command": config}
        return config

    def _get_target_editors(self, editor_name: Optional[str]) -> List[str]:
        """Get list of target editors for operation."""
        if editor_name:
            if editor_name not in self.config_manager.get_available_editors():
                raise EditorError(f"Unknown editor: {editor_name}")
            return [editor_name]
        return self.config_manager.get_available_editors()
```

#### 3. Configuration Management (`core/config.py`)
**Purpose**: Centralized configuration handling with validation

```python
"""Configuration management for MCP Commander."""

import json
from pathlib import Path
from typing import Dict, Any, List

from mcpcommander.schemas.config_schema import MCPCommanderConfig
from mcpcommander.utils.errors import ConfigurationError
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)

class ConfigManager:
    """Manages MCP Commander configuration."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = self._resolve_config_path(config_path)
        self._config: Optional[MCPCommanderConfig] = None

    @property
    def config(self) -> MCPCommanderConfig:
        """Get validated configuration, loading if necessary."""
        if self._config is None:
            self._config = self._load_and_validate_config()
        return self._config

    def _resolve_config_path(self, config_path: Optional[Path]) -> Path:
        """Resolve configuration file path."""
        if config_path:
            return Path(config_path)

        # Look in standard locations
        script_dir = Path(__file__).parent.parent.parent.parent
        return script_dir / "config.json"

    def _load_and_validate_config(self) -> MCPCommanderConfig:
        """Load and validate configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                raw_config = json.load(f)

            # Validate with Pydantic
            config = MCPCommanderConfig(**raw_config)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config

        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")

    def get_available_editors(self) -> List[str]:
        """Get list of available editor names."""
        return list(self.config.editors.keys())

    def get_editor_config(self, editor_name: str) -> Dict[str, Any]:
        """Get configuration for specific editor."""
        if editor_name not in self.config.editors:
            raise ConfigurationError(f"Unknown editor: {editor_name}")
        return self.config.editors[editor_name].dict()
```

#### 4. Editor Handlers (`core/editor_handlers.py`)
**Purpose**: Editor-specific logic with strategy pattern

```python
"""Editor-specific implementation handlers."""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from mcpcommander.schemas.config_schema import ServerConfig, EditorConfig
from mcpcommander.utils.errors import EditorError
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)

class EditorHandler(ABC):
    """Abstract base class for editor-specific handlers."""

    def __init__(self, editor_config: EditorConfig):
        self.editor_config = editor_config
        self.config_path = Path(editor_config.config_path).expanduser()

    @abstractmethod
    def add_server(self, server_name: str, server_config: ServerConfig) -> None:
        """Add server to editor configuration."""
        pass

    @abstractmethod
    def remove_server(self, server_name: str) -> None:
        """Remove server from editor configuration."""
        pass

    @abstractmethod
    def list_servers(self) -> Dict[str, Any]:
        """List configured servers."""
        pass

    def _load_editor_config(self) -> Dict[str, Any]:
        """Load editor configuration file."""
        try:
            if not self.config_path.exists():
                return {}
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.config_path}: {e}")
            return {}

    def _save_editor_config(self, config: Dict[str, Any]) -> None:
        """Save editor configuration file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            raise EditorError(f"Failed to save configuration to {self.config_path}: {e}")

class ClaudeCodeHandler(EditorHandler):
    """Handler for Claude Code CLI configuration."""

    def add_server(self, server_name: str, server_config: ServerConfig) -> None:
        config = self._load_editor_config()

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"][server_name] = server_config.dict()
        self._save_editor_config(config)

    def remove_server(self, server_name: str) -> None:
        config = self._load_editor_config()
        servers = config.get("mcpServers", {})

        if server_name in servers:
            del servers[server_name]
            self._save_editor_config(config)
        else:
            raise EditorError(f"Server '{server_name}' not found")

    def list_servers(self) -> Dict[str, Any]:
        config = self._load_editor_config()
        return config.get("mcpServers", {})

# Similar implementations for ClaudeDesktopHandler, CursorHandler...

class EditorHandlerFactory:
    """Factory for creating editor-specific handlers."""

    _handlers = {
        "claude-code": ClaudeCodeHandler,
        "claude-desktop": ClaudeCodeHandler,  # Similar implementation
        "cursor": ClaudeCodeHandler,          # Similar implementation
    }

    @classmethod
    def get_handler(cls, editor_name: str, editor_config: EditorConfig) -> EditorHandler:
        """Get handler instance for specified editor."""
        handler_class = cls._handlers.get(editor_name)
        if not handler_class:
            raise EditorError(f"No handler available for editor: {editor_name}")
        return handler_class(editor_config)
```

### Phase 2: Modern Python Infrastructure

#### 1. Type System (`schemas/config_schema.py`)
**Purpose**: Pydantic models for configuration validation

```python
"""Pydantic schemas for configuration validation."""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator

class ServerConfig(BaseModel):
    """Schema for MCP server configuration."""

    command: str = Field(..., description="Command to execute the server")
    args: Optional[List[str]] = Field(None, description="Command arguments")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")

    @validator('command')
    def validate_command(cls, v):
        if not v or not v.strip():
            raise ValueError("Command cannot be empty")
        return v.strip()

class EditorConfig(BaseModel):
    """Schema for editor configuration."""

    config_path: str = Field(..., description="Path to editor configuration file")
    jsonpath: str = Field("mcpServers", description="JSON path to MCP servers section")

    @validator('config_path')
    def validate_config_path(cls, v):
        if not v or not v.strip():
            raise ValueError("Configuration path cannot be empty")
        return v.strip()

class MCPCommanderConfig(BaseModel):
    """Schema for main MCP Commander configuration."""

    editors: Dict[str, EditorConfig] = Field(..., description="Editor configurations")

    @validator('editors')
    def validate_editors(cls, v):
        if not v:
            raise ValueError("At least one editor must be configured")
        return v
```

#### 2. Error Handling (`utils/errors.py`)
**Purpose**: Centralized exception hierarchy

```python
"""Custom exception classes for MCP Commander."""

class MCPCommanderError(Exception):
    """Base exception for MCP Commander errors."""
    pass

class ConfigurationError(MCPCommanderError):
    """Raised when configuration is invalid or missing."""
    pass

class EditorError(MCPCommanderError):
    """Raised when editor-specific operations fail."""
    pass

class ValidationError(MCPCommanderError):
    """Raised when input validation fails."""
    pass

class FilePermissionError(MCPCommanderError):
    """Raised when file operations fail due to permissions."""
    pass
```

#### 3. Structured Logging (`utils/logger.py`)
**Purpose**: Consistent logging across the application

```python
"""Structured logging configuration for MCP Commander."""

import logging
import sys
from pathlib import Path
from typing import Optional

def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        setup_logging(logger)

    return logger

def setup_logging(logger: logging.Logger, level: str = "INFO") -> None:
    """Set up logging configuration."""

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set level
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate logs
    logger.propagate = False
```

#### 4. Modern CLI (`cli/main.py`)
**Purpose**: Typer-based CLI with rich formatting

```python
"""Modern CLI interface using typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from mcpcommander.core.manager import MCPManager
from mcpcommander.utils.errors import MCPCommanderError
from mcpcommander.utils.logger import get_logger

app = typer.Typer(help="MCP Commander - Cross-platform MCP server management")
console = Console()
logger = get_logger(__name__)

@app.command()
def add(
    server_name: str = typer.Argument(..., help="Name of the server"),
    server_config: str = typer.Argument(..., help="Server configuration (JSON or command path)"),
    editor: Optional[str] = typer.Argument(None, help="Specific editor to add server to"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path")
) -> None:
    """Add MCP server to editors."""
    try:
        manager = MCPManager(config)
        manager.add_server(server_name, server_config, editor)

        target = editor or "all editors"
        console.print(f"✅ Added server '{server_name}' to {target}", style="green")

    except MCPCommanderError as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)

@app.command()
def remove(
    server_name: str = typer.Argument(..., help="Name of the server to remove"),
    editor: Optional[str] = typer.Argument(None, help="Specific editor to remove server from"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path")
) -> None:
    """Remove MCP server from editors."""
    # Implementation with rich formatting
    pass

@app.command()
def list(
    editor: Optional[str] = typer.Argument(None, help="Specific editor to list servers for"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path")
) -> None:
    """List configured MCP servers."""
    try:
        manager = MCPManager(config)
        servers = manager.list_servers(editor)

        # Create rich table
        table = Table(title="Configured MCP Servers")
        table.add_column("Editor", style="cyan")
        table.add_column("Server Name", style="magenta")
        table.add_column("Command", style="green")

        for editor_name, editor_servers in servers.items():
            for server_name, server_config in editor_servers.items():
                table.add_row(editor_name, server_name, server_config.get("command", ""))

        console.print(table)

    except MCPCommanderError as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)

def main() -> None:
    """Entry point for the CLI application."""
    app()

if __name__ == "__main__":
    main()
```

## Development Standards and Patterns

### Type Hints and Documentation
```python
def add_server(
    self,
    server_name: str,
    server_config: Union[str, Dict[str, Any]],
    editor_name: Optional[str] = None
) -> None:
    """Add a server to specified editors or all editors.

    Args:
        server_name: Unique name for the server
        server_config: Server configuration (JSON string or dict)
        editor_name: Target editor name, or None for all editors

    Raises:
        ConfigurationError: If server configuration is invalid
        EditorError: If specified editor is unknown
    """
```

### Error Handling Patterns
```python
try:
    # Operation that might fail
    result = risky_operation()
except SpecificError as e:
    # Handle specific error with context
    logger.error(f"Specific operation failed: {e}")
    raise ConfigurationError(f"Failed to perform operation: {e}") from e
except Exception as e:
    # Handle unexpected errors
    logger.exception("Unexpected error occurred")
    raise MCPCommanderError(f"Unexpected error: {e}") from e
```

### Logging Standards
```python
logger.info("Starting operation", extra={"server_name": server_name})
logger.warning("Configuration issue detected", extra={"path": config_path})
logger.error("Operation failed", extra={"error": str(e)}, exc_info=True)
```

## Future Source Architecture Enhancements

### Advanced Features
1. **Plugin System**: Extensible architecture for custom editors
2. **Configuration Templates**: Pre-defined server configurations
3. **Migration Tools**: Automated configuration migration
4. **Backup/Restore**: Configuration backup and restoration
5. **Validation Engine**: Advanced configuration validation

### Performance Optimizations
1. **Lazy Loading**: Load editor configurations only when needed
2. **Caching**: Cache frequently accessed configurations
3. **Async Operations**: Asynchronous file operations for performance
4. **Batch Operations**: Efficient bulk operations

---

*Source architecture defined: 2025-08-11*
*Transformation from basic to enterprise-grade Python implementation*
*Based on jira-mcp architectural patterns and best practices*
