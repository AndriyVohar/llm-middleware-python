"""Logging configuration for the application."""
import logging
import sys
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Set specific levels for libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_token_usage(logger: logging.Logger, usage: dict[str, Any] | None, context: str = "") -> None:
    """Log token usage information.

    Args:
        logger: Logger instance
        usage: Usage dictionary with token counts
        context: Additional context for the log message
    """
    if not usage:
        return

    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    prefix = f"{context} - " if context else ""
    logger.info(
        f"{prefix}Token usage: prompt={prompt_tokens}, "
        f"completion={completion_tokens}, total={total_tokens}"
    )


