"""
Logging configuration
"""

import logging
import sys
from typing import Optional


def get_logger(
    name: str,
    level: int = logging.INFO,
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Get a logger with the specified name and configuration.

    Args:
        name: Name of the logger
        level: Logging level
        format: Log message format

    Returns:
        Configured logger instance with stdout/stderr handlers
    """
    logger = logging.getLogger(name)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(level)

    # Create formatters
    formatter = logging.Formatter(format)

    # Console handler for INFO and below (stdout)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    logger.addHandler(stdout_handler)

    # Console handler for WARNING and above (stderr)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.WARNING)
    logger.addHandler(stderr_handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger
