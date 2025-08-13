"""
Logging utilities for ClaudeCraftsman.

Provides structured logging with correlation IDs and rich output.
"""

import logging
import sys
from collections.abc import MutableMapping
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from rich.logging import RichHandler

# Context variable for correlation ID
correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)

console = Console()


class LogConfig(BaseModel):
    """Logging configuration."""

    model_config = ConfigDict(extra="forbid")

    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = "%(message)s"
    log_file: Path | None = None
    rich_output: bool = True
    show_path: bool = False
    show_time: bool = True


def setup_logging(config: LogConfig) -> None:
    """Set up logging with the given configuration."""
    handlers: list[logging.Handler] = []

    if config.rich_output:
        # Rich handler for console output
        rich_handler = RichHandler(
            console=console,
            show_path=config.show_path,
            show_time=config.show_time,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
        )
        rich_handler.setFormatter(logging.Formatter(config.format))
        handlers.append(rich_handler)
    else:
        # Standard console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(config.format))
        handlers.append(console_handler)

    if config.log_file:
        # File handler
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.level),
        handlers=handlers,
        force=True,
    )


class CorrelationLoggerAdapter(logging.LoggerAdapter[logging.Logger]):
    """Logger adapter that includes correlation ID in log records."""

    def process(
        self, msg: object, kwargs: MutableMapping[str, Any]
    ) -> tuple[object, MutableMapping[str, Any]]:
        """Process log message to include correlation ID."""
        corr_id = correlation_id.get()
        if corr_id:
            return f"[{corr_id}] {msg}", kwargs
        return msg, kwargs


def get_logger(name: str) -> CorrelationLoggerAdapter:
    """Get a logger with correlation ID support."""
    logger = logging.getLogger(name)
    return CorrelationLoggerAdapter(logger, {})


def set_correlation_id(corr_id: str | None = None) -> str:
    """Set or generate a correlation ID for the current context."""
    if not corr_id:
        # Generate a correlation ID based on timestamp
        corr_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]

    correlation_id.set(corr_id)
    return corr_id


# Default logger for the package
logger = get_logger("claudecraftsman")
