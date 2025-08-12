"""Structured logging configuration for MCP Commander."""

import logging
import sys


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
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set level
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate logs
    logger.propagate = False


def configure_debug_logging() -> None:
    """Configure debug-level logging for development."""
    root_logger = logging.getLogger("mcpcommander")
    setup_logging(root_logger, "DEBUG")
