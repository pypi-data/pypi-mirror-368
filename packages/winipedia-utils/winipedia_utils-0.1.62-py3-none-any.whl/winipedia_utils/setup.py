"""A script that can be called after you installed the package.

This script calls create tests, creates the pre-commit config, and
creates the pyproject.toml file and some other things to set up a project.
This package assumes you are using poetry and pre-commit.
This script is intended to be called once at the beginning of a project.
"""

from winipedia_utils.git.gitignore.gitignore import _add_package_patterns_to_gitignore
from winipedia_utils.git.pre_commit.config import (
    _add_package_hook_to_pre_commit_config,
    _pre_commit_install,
)
from winipedia_utils.git.pre_commit.run_hooks import _run_all_hooks
from winipedia_utils.logging.logger import get_logger
from winipedia_utils.projects.poetry.config import (
    _add_configurations_to_pyproject_toml,
)
from winipedia_utils.projects.poetry.poetry import (
    _install_dev_dependencies,
)
from winipedia_utils.projects.project import _create_project_root

logger = get_logger(__name__)


def _setup() -> None:
    """Set up the project."""
    # install winipedia_utils dev dependencies as dev
    _install_dev_dependencies()
    # create pre-commit config
    _add_package_hook_to_pre_commit_config()
    # install pre-commit
    _pre_commit_install()
    # add patterns to .gitignore
    _add_package_patterns_to_gitignore()
    # add tool.* configurations to pyproject.toml
    _add_configurations_to_pyproject_toml()
    # create the project root
    _create_project_root()
    # run pre-commit once, create tests is included here
    _run_all_hooks()
    logger.info("Setup complete!")


if __name__ == "__main__":
    _setup()
