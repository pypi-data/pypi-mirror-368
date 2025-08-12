# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-08-11

### Added
- **Complete MCP Server Management System**: Cross-platform command-line tool for managing MCP (Model Context Protocol) servers
- **Multi-Transport Support**: Support for all MCP transport types:
  - STDIO servers (traditional command-based)
  - HTTP servers with host, port, and path configuration
  - WebSocket servers with URL and headers support
  - Server-Sent Events (SSE) with URL and headers support
- **Cross-Platform Configuration Management**:
  - Automatic user config directory detection (Windows: `%APPDATA%`, macOS: `~/Library/Application Support`, Linux: `~/.config`)
  - Legacy configuration migration from repository to user directories
  - Schema validation with Pydantic models
- **Editor Support**: Built-in support for multiple code editors:
  - Claude Code CLI (`~/.claude.json`)
  - Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)
  - Cursor (`~/Library/Application Support/Cursor/User/globalStorage/storage.json`)
  - VS Code with configurable paths and JSONPath support
  - Windsurf editor support
- **Modern CLI Interface**:
  - Built with Typer framework and Rich formatting
  - Contextual help system with `--help --verbose` showing practical examples
  - Colored output and progress indicators
  - Comprehensive error messages with suggestions
- **Advanced Server Discovery**: Automatic detection of existing MCP server configurations across all supported editors
- **Comprehensive Testing Suite**:
  - 43+ unit tests with 85%+ coverage requirement
  - Integration tests for cross-platform compatibility
  - End-to-end workflow testing
  - Mock frameworks for safe testing
- **Enterprise-Grade Development Infrastructure**:
  - Modern Python packaging with `pyproject.toml` (PEP 517/518/621)
  - Pre-commit hooks for code quality (15+ hooks including linting, formatting, security)
  - GitHub Actions CI/CD pipelines for testing and PyPI publishing
  - Comprehensive type hints with mypy validation
  - Structured logging with configurable levels
  - Cross-platform path handling and file operations
- **Developer Experience**:
  - Rich console output with tables and formatting
  - Detailed error messages with context and suggestions
  - Comprehensive API documentation with examples
  - Contributing guidelines and development setup

### Changed
- **Architecture**: Complete transformation from monolithic script to enterprise-grade Python package with proper module structure
- **Configuration Format**: Enhanced to support all transport types while maintaining backward compatibility
- **CLI Interface**: Upgraded from basic argparse to modern Typer framework with Rich formatting
- **Error Handling**: Centralized exception hierarchy with context-aware error messages
- **Testing**: Professional test suite replacing basic validation

### Technical Details
- **Python Support**: Requires Python 3.12+
- **Dependencies**: Minimal core dependencies (colorama, pydantic, typer, rich)
- **Packaging**: Modern setuptools with automated PyPI publishing via trusted publishing
- **Code Quality**: Black formatting, Ruff linting, MyPy type checking, Bandit security scanning
- **Development**: Pre-commit hooks, GitHub Actions, comprehensive test coverage

### Usage Examples
```bash
# Add server to all editors
mcp add my-server "npx @modelcontextprotocol/server-filesystem /tmp"

# Add HTTP server to specific editor
mcp add web-server '{"transport": {"type": "http", "host": "localhost", "port": 8080}}' claude-code

# List all configured servers
mcp list

# Remove server from specific editor
mcp remove my-server cursor

# Show detailed help with examples
mcp add --help --verbose
```

[Unreleased]: https://github.com/nmindz/mcp-commander/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nmindz/mcp-commander/releases/tag/v0.1.0
