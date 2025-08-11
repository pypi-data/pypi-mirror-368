"""Logging configuration for winipedia_utils.

This module provides a standardized logging configuration dictionary that can be
used with Python's logging.config.dictConfig() to set up consistent logging
across the application. The configuration includes formatters, handlers, and
logger settings for different components.
"""

# This dictionary can be passed directly to logging.config.dictConfig().
# It sets up a single console handler that prints **all** log levels
# (DEBUG, INFO, WARNING, ERROR and CRITICAL) using one consistent format.

from typing import Any

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,  # Mandatory schema version for dictConfig
    "disable_existing_loggers": False,  # Keep any loggers already created elsewhere
    # ---------------------------- #
    #  Define a single formatter   #
    # ---------------------------- #
    "formatters": {
        "standard": {  # You can reference this formatter by name
            "format": (
                "%(asctime)s | "  # • %(asctime)s human-readable timestamp
                "%(levelname)-8s | "  # • %(asctime)s human-readable timestamp
                "%(filename)s:"  # • %(filename)s source file where the call was made
                "%(lineno)d | "  # • %(lineno)d line number in that file
                "%(message)s"  # • %(message)s the log message itself
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",  # Override default timestamp style
        },
    },
    # --------------------------- #
    #  Define the console output  #
    # --------------------------- #
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",  # Send logs to sys.stderr
            "level": "DEBUG",  # Capture *everything* ≥ DEBUG
            "formatter": "standard",  # Use the formatter above
            "stream": "ext://sys.stdout",  # Emit to stdout instead of stderr
        },
    },
    # ------------------------------------------------------- #
    #  Attach the handler to either the root logger or named  #
    #  loggers. Below we set up the root so every message in  #
    #  your application uses this setup automatically.        #
    # ------------------------------------------------------- #
    "root": {
        "level": "DEBUG",  # Accept all levels from DEBUG upward
        "handlers": ["console"],  # Pipe them through the console handler
    },
    # ------------------------------------------------------- #
    #  Optionally, tweak individual libraries if they are     #
    #  too noisy. For example, silence urllib3 INFO chatter.   #
    # ------------------------------------------------------- #
    "loggers": {
        "urllib3": {
            "level": "WARNING",  # Raise urllib3's threshold to WARNING
            "handlers": ["console"],
            "propagate": False,  # Prevent double-logging to the root
        },
    },
}
