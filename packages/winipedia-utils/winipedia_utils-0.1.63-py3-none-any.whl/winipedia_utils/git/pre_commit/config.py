"""Has config utilities for pre-commit."""

from pathlib import Path
from typing import Any

import yaml

from winipedia_utils.logging.logger import get_logger
from winipedia_utils.os.os import run_subprocess
from winipedia_utils.projects.poetry.poetry import POETRY_RUN_ARGS

logger = get_logger(__name__)


def load_pre_commit_config() -> dict[str, Any]:
    """Load the pre-commit config."""
    path = Path(".pre-commit-config.yaml")
    if not path.exists():
        path.touch()
    return yaml.safe_load(path.read_text()) or {}


def dump_pre_commit_config(config: dict[str, Any]) -> None:
    """Dump the pre-commit config."""
    path = Path(".pre-commit-config.yaml")
    with path.open("w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


def _get_pre_commit_config_dict() -> dict[str, Any]:
    """Get the content for a pre-commit config file as a dictionary."""
    return {
        "repo": "local",
        "hooks": [
            {
                "id": "winipedia-utils",
                "name": "winipedia-utils",
                "entry": "python -m winipedia_utils.git.pre_commit.run_hooks",
                "language": "system",
                "always_run": True,
                "pass_filenames": False,
            }
        ],
    }


def _pre_commit_config_is_correct() -> bool:
    """Check if the pre-commit config is correct."""
    config = load_pre_commit_config()
    package_hook_config = _get_pre_commit_config_dict().get("hooks", [{}])[0]
    return bool(
        config.get("repos", [{}])[0].get("hooks", [{}])[0] == package_hook_config
    )


def _add_package_hook_to_pre_commit_config() -> None:
    """Add the winipedia-utils hook to the pre-commit config."""
    config = load_pre_commit_config()
    package_hook_config = _get_pre_commit_config_dict()
    # insert at the beginning of the list
    if not _pre_commit_config_is_correct():
        logger.info("Adding winipedia-utils hook to pre-commit config")
        config["repos"] = [package_hook_config, *config.get("repos", [])]
        dump_pre_commit_config(config)


def _pre_commit_install() -> None:
    """Install pre-commit."""
    logger.info("Running pre-commit install")
    run_subprocess([*POETRY_RUN_ARGS, "pre-commit", "install"], check=True)
