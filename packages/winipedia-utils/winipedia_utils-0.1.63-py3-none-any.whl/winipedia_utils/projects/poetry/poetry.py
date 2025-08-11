"""Project utilities for introspection and manipulation.

This module provides utility functions for working with Python projects
"""

import sys

from winipedia_utils.consts import _DEV_DEPENDENCIES
from winipedia_utils.logging.logger import get_logger
from winipedia_utils.os.os import run_subprocess, which_with_raise

logger = get_logger(__name__)


POETRY_PATH = which_with_raise("poetry", raise_error=False) or "poetry"

POETRY_RUN_ARGS = [POETRY_PATH, "run"]

POETRY_ADD_ARGS = [POETRY_PATH, "add"]

POETRY_ADD_DEV_ARGS = [*POETRY_ADD_ARGS, "--group", "dev"]

POETRY_RUN_PYTHON_ARGS = [*POETRY_RUN_ARGS, sys.executable]

POETRY_RUN_RUFF_ARGS = [*POETRY_RUN_ARGS, "ruff"]


def _install_dev_dependencies() -> None:
    """Install winipedia_utils dev dependencies as dev dependencies."""
    logger.info("Adding dev dependencies: %s", _DEV_DEPENDENCIES)
    run_subprocess([*POETRY_ADD_DEV_ARGS, *_DEV_DEPENDENCIES], check=True)
