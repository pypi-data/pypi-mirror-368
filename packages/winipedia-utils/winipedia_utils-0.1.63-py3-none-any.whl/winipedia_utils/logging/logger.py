"""Logger utilities for winipedia_utils.

This module provides functions for creating and configuring loggers
throughout the application. It applies the standardized logging configuration
defined in the config module to ensure consistent logging behavior.
"""

import logging
from logging.config import dictConfig

from winipedia_utils.logging.config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Args:
        name: The name for the logger, typically __name__ from the calling module

    Returns:
        A configured logger instance with the specified name

    """
    return logging.getLogger(name)
