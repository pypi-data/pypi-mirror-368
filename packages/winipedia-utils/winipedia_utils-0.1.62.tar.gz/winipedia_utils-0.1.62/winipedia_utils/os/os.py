"""OS utilities for finding commands and paths.

This module provides utility functions for working with the operating system,
including finding the path to commands and managing environment variables.
These utilities help with system-level operations and configuration.
"""

import shutil
import subprocess  # nosec: B404
from pathlib import Path
from typing import Any


def which_with_raise(cmd: str, *, raise_error: bool = True) -> str | None:
    """Give the path to the given command.

    Args:
        cmd: The command to find
        raise_error: Whether to raise an error if the command is not found

    Returns:
        The path to the command

    Raises:
        FileNotFoundError: If the command is not found

    """
    path = shutil.which(cmd)
    if path is None:
        msg = f"Command {cmd} not found"
        if raise_error:
            raise FileNotFoundError(msg)
    return path


def run_subprocess(
    args: list[str | Path],
    *,
    input_: str | bytes | None = None,
    capture_output: bool = True,
    timeout: int | None = None,
    check: bool = True,
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Run a subprocess.

    Args:
        args: The arguments to pass to the subprocess
        input_: The input to pass to the subprocess
        capture_output: Whether to capture the output of the subprocess
        timeout: The timeout for the subprocess
        check: to raise an exception if the subprocess returns a non-zero exit code
        kwargs: Any other arguments to pass to subprocess.run()

    """
    return subprocess.run(  # noqa: S603  # nosec: B603
        args,
        check=check,
        input=input_,
        capture_output=capture_output,
        timeout=timeout,
        **kwargs,
    )
