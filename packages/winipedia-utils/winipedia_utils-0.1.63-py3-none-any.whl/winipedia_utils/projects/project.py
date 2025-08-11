"""Utilities for working with Python projects."""

from types import ModuleType

from winipedia_utils.modules.module import create_module, to_path
from winipedia_utils.modules.package import get_src_package
from winipedia_utils.projects.poetry.config import get_poetry_package_name


def _create_project_root() -> None:
    """Create the project root."""
    src_package_name = get_poetry_package_name()
    create_module(src_package_name, is_package=True)
    _create_py_typed()


def _create_py_typed() -> None:
    """Create the py.typed file."""
    src_package_name = get_src_package().__name__
    py_typed_path = to_path(src_package_name, is_package=True) / "py.typed"
    py_typed_path.touch()


def make_name_from_package(
    package: ModuleType,
    split_on: str = "_",
    join_on: str = "-",
    *,
    capitalize: bool = True,
) -> str:
    """Make a name from a package.

    takes a package and makes a name from it that is readable by humans.

    Args:
        package (ModuleType): The package to make a name from
        split_on (str, optional): what to split the package name on. Defaults to "_".
        join_on (str, optional): what to join the package name with. Defaults to "-".
        capitalize (bool, optional): Whether to capitalize each part. Defaults to True.

    Returns:
        str: _description_
    """
    package_name = package.__name__.split(".")[-1]
    parts = package_name.split(split_on)
    if capitalize:
        parts = [part.capitalize() for part in parts]
    return join_on.join(parts)
