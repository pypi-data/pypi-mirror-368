"""Custom exception classes for MCP Commander."""


class MCPCommanderError(Exception):
    """Base exception for MCP Commander errors."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


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


class ServerNotFoundError(MCPCommanderError):
    """Raised when a requested server is not found."""

    pass


class DiscoveryError(MCPCommanderError):
    """Raised when MCP configuration discovery fails."""

    pass
