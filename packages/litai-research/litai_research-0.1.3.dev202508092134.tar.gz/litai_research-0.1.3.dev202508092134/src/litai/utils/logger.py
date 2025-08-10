"""Logging configuration for LitAI."""

import logging
from pathlib import Path
from typing import Any

import structlog


def setup_logging(debug: bool = False) -> None:
    """Configure structured logging."""
    log_level = logging.DEBUG if debug else logging.INFO

    # Create logs directory
    log_dir = Path.home() / ".litai" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure standard logging
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[
            logging.FileHandler(log_dir / "litai.log"),
        ],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
            if debug
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a configured logger instance."""
    return structlog.get_logger(name)
