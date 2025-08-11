"""Contains the pre-commit to run all hooks required by the winipedia_utils package.

This script is meant to be run by pre-commit (https://pre-commit.com/)
and should not be modified manually.
"""

import sys

from winipedia_utils.git.pre_commit import hooks
from winipedia_utils.logging.ansi import GREEN, RED, RESET
from winipedia_utils.logging.logger import get_logger
from winipedia_utils.modules.function import get_all_functions_from_module
from winipedia_utils.os.os import run_subprocess

logger = get_logger(__name__)


def _run_all_hooks() -> None:
    """Import all funcs defined in hooks.py and runs them."""
    hook_funcs = get_all_functions_from_module(hooks)

    exit_code = 0
    for hook_func in hook_funcs:
        subprocess_args = hook_func()
        result = run_subprocess(
            subprocess_args, check=False, capture_output=True, text=True
        )
        passed = result.returncode == 0

        log_method = logger.info
        passed_str = (f"{GREEN}PASSED" if passed else f"{RED}FAILED") + RESET
        if not passed:
            log_method = logger.error
            passed_str += f"\n{result.stdout}"
            exit_code = 1
        # make the dashes always the same lentgth by adjusting to len of hook name
        num_dashes = 50 - len(hook_func.__name__)
        log_method(
            "Hook %s -%s> %s",
            hook_func.__name__,
            "-" * num_dashes,
            passed_str,
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    _run_all_hooks()
