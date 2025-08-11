"""module contains functions that return the input for subprocess.run().

Each function is named after the hook it represents. The docstring of each function
describes the hook it represents. The function returns a list of strings that
represent the command to run. The first string is the command, and the following
strings are the arguments to the command. These funcs will be called by
run_hooks.py, which will pass the returned list to subprocess.run().
"""

from pathlib import Path

from winipedia_utils.projects.poetry.poetry import (
    POETRY_PATH,
    POETRY_RUN_ARGS,
    POETRY_RUN_PYTHON_ARGS,
    POETRY_RUN_RUFF_ARGS,
)


def _update_package_manager() -> list[str | Path]:
    """Update the package manager.

    This function returns the input for subprocess.run() to update the package
    manager.
    """
    return [POETRY_PATH, "self", "update"]


def _install_packages() -> list[str | Path]:
    """Install all dependencies.

    This function returns the input for subprocess.run() to install all dependencies.
    """
    return [POETRY_PATH, "install"]


def _update_packages() -> list[str | Path]:
    """Update all dependencies.

    This function returns the input for subprocess.run() to update all dependencies.
    """
    return [POETRY_PATH, "update"]


def _lock_dependencies() -> list[str | Path]:
    """Lock the dependencies.

    This function returns the input for subprocess.run() to lock the dependencies.
    """
    return [POETRY_PATH, "lock"]


def _check_configurations() -> list[str | Path]:
    """Check that poetry.lock and pyproject.toml is up to date.

    This function returns the input for subprocess.run() to check that poetry.lock
    is up to date.
    """
    return [POETRY_PATH, "check", "--strict"]


def _creating_tests() -> list[str | Path]:
    """Create all tests for the project.

    This function returns the input for subprocess.run() to create all tests.
    """
    return [*POETRY_RUN_PYTHON_ARGS, "-m", "winipedia_utils.testing.create_tests"]


def _linting() -> list[str | Path]:
    """Check the code.

    This function returns the input for subprocess.run() to lint the code.
    It autofixes all errors that can be autofixed with --fix.
    """
    return [*POETRY_RUN_RUFF_ARGS, "check", "--fix"]


def _formating() -> list[str | Path]:
    """Format the code.

    This function calls ruff format to format the code.
    """
    return [*POETRY_RUN_RUFF_ARGS, "format"]


def _type_checking() -> list[str | Path]:
    """Check the types.

    This function returns the input for subprocess.run() to check the static types.
    """
    return [*POETRY_RUN_ARGS, "mypy"]


def _security_checking() -> list[str | Path]:
    """Check the security of the code.

    This function returns the input for subprocess.run() to check the security of
    the code.
    """
    return [*POETRY_RUN_ARGS, "bandit", "-c", "pyproject.toml", "-r", "."]


def _testing() -> list[str | Path]:
    """Run the tests.

    This function returns the input for subprocess.run() to run all tests.
    """
    return [*POETRY_RUN_ARGS, "pytest"]
