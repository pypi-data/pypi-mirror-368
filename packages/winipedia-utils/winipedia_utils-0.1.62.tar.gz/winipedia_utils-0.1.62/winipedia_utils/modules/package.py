"""Package utilities for introspection and manipulation.

This module provides comprehensive utility functions for working with Python packages,
including package discovery, creation, traversal, and module extraction. It handles
both regular packages and namespace packages, offering tools for filesystem operations
and module imports related to package structures.

The utilities support both static package analysis and dynamic package manipulation,
making them suitable for code generation, testing frameworks, and package management.
"""

import os
import pkgutil
import sys
from collections.abc import Generator, Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

from winipedia_utils.git.gitignore.gitignore import (
    load_gitignore,
    walk_os_skipping_gitignore_patterns,
)
from winipedia_utils.logging.logger import get_logger

logger = get_logger(__name__)


def get_src_package() -> ModuleType:
    """Identify and return the main source package of the project.

    Discovers the main source package by finding all top-level packages
    and filtering out the test package. This is useful for automatically
    determining the package that contains the actual implementation code.

    Returns:
        The main source package as a module object

    Raises:
        StopIteration: If no source package can be found or
                       if only the test package exists

    """
    from winipedia_utils.testing.convention import TESTS_PACKAGE_NAME

    packages = find_packages_as_modules(depth=0)
    return next(p for p in packages if p.__name__ != TESTS_PACKAGE_NAME)


def make_dir_with_init_file(path: str | Path) -> None:
    """Create a directory and initialize it as a Python package.

    Creates the specified directory (including any necessary parent directories)
    and adds __init__.py files to make it a proper Python package. Optionally
    writes custom content to the __init__.py file.

    Args:
        path: The directory path to create and initialize as a package

    Note:
        If the directory already exists, it will not be modified, but __init__.py
        files will still be added if missing.

    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    make_init_modules_for_package(path)


def module_is_package(obj: ModuleType) -> bool:
    """Determine if a module object represents a package.

    Checks if the given module object is a package by looking for the __path__
    attribute, which is only present in package modules.

    Args:
        obj: The module object to check

    Returns:
        True if the module is a package, False otherwise

    Note:
        This works for both regular packages and namespace packages.

    """
    return hasattr(obj, "__path__")


def package_name_to_path(package_name: str | Path | ModuleType) -> Path:
    """Convert a Python package import name to its filesystem path.

    Transforms a Python package name (with dots) into the corresponding
    directory path by replacing dots with the appropriate directory separator
    for the current operating system.

    Args:
        package_name: A Python package name to convert
                      or a Path object or a ModuleType object

    Returns:
        A Path object representing the filesystem path to the package

    Example:
        package_name_to_path("package.subpackage") -> Path("package/subpackage")

    """
    if isinstance(package_name, ModuleType):
        package_name = package_name.__name__
    elif isinstance(package_name, Path):
        package_name = package_name.as_posix()
    return Path(package_name.replace(".", os.sep))


def get_modules_and_packages_from_package(
    package: ModuleType,
) -> tuple[list[ModuleType], list[ModuleType]]:
    """Extract all direct subpackages and modules from a package.

    Discovers and imports all direct child modules and subpackages within
    the given package. Returns them as separate lists.

    Args:
        package: The package module to extract subpackages and modules from

    Returns:
        A tuple containing (list of subpackages, list of modules)

    Note:
        Only includes direct children, not recursive descendants.
        All discovered modules and packages are imported during this process.

    """
    packages: list[ModuleType] = []
    modules: list[ModuleType] = []
    for _, name, is_pkg in pkgutil.iter_modules(
        package.__path__, prefix=package.__name__ + "."
    ):
        mod = import_module(name)
        if is_pkg:
            packages.append(mod)
        else:
            modules.append(mod)

    # make consistent order
    packages.sort(key=lambda p: p.__name__)
    modules.sort(key=lambda m: m.__name__)

    return packages, modules


def find_packages(
    *,
    depth: int | None = None,
    include_namespace_packages: bool = False,
    where: str = ".",
    exclude: Iterable[str] | None = None,
    include: Iterable[str] = ("*",),
) -> list[str]:
    """Discover Python packages in the specified directory.

    Finds all Python packages in the given directory, with options to filter
    by depth, include/exclude patterns, and namespace packages. This is a wrapper
    around setuptools' find_packages and find_namespace_packages functions with
    additional filtering capabilities.

    Args:
        depth: Optional maximum depth of package nesting to include (None for unlimited)
        include_namespace_packages: Whether to include namespace packages
        where: Directory to search for packages (default: current directory)
        exclude: Patterns of package names to exclude
        include: Patterns of package names to include

    Returns:
        A list of package names as strings

    Example:
        find_packages(depth=1) might return ["package1", "package2"]

    """
    if exclude is None:
        exclude = load_gitignore()
        exclude = [
            p.replace("/", ".").removesuffix(".") for p in exclude if p.endswith("/")
        ]
    if include_namespace_packages:
        package_names = _find_namespace_packages(
            where=where, exclude=exclude, include=include
        )
    else:
        package_names = _find_packages(where=where, exclude=exclude, include=include)

    # Convert to list of strings explicitly
    package_names_list: list[str] = list(map(str, package_names))

    if depth is not None:
        package_names_list = [p for p in package_names_list if p.count(".") <= depth]

    return package_names_list


def find_packages_as_modules(
    *,
    depth: int | None = None,
    include_namespace_packages: bool = False,
    where: str = ".",
    exclude: Iterable[str] | None = None,
    include: Iterable[str] = ("*",),
) -> list[ModuleType]:
    """Discover and import Python packages in the specified directory.

    Similar to find_packages, but imports and returns the actual module objects
    instead of just the package names.

    Args:
        depth: Optional maximum depth of package nesting to include (None for unlimited)
        include_namespace_packages: Whether to include namespace packages
        where: Directory to search for packages (default: current directory)
        exclude: Patterns of package names to exclude
        include: Patterns of package names to include

    Returns:
        A list of imported package module objects

    Note:
        All discovered packages are imported during this process.

    """
    package_names = find_packages(
        depth=depth,
        include_namespace_packages=include_namespace_packages,
        where=where,
        exclude=exclude,
        include=include,
    )
    return [import_module(package_name) for package_name in package_names]


def walk_package(
    package: ModuleType,
) -> Generator[tuple[ModuleType, list[ModuleType]], None, None]:
    """Recursively walk through a package and all its subpackages.

    Performs a depth-first traversal of the package hierarchy, yielding each
    package along with its direct module children.

    Args:
        package: The root package module to start walking from

    Yields:
        Tuples of (package, list of modules in package)

    Note:
        All packages and modules are imported during this process.
        The traversal is depth-first, so subpackages are fully processed
        before moving to siblings.

    """
    subpackages, submodules = get_modules_and_packages_from_package(package)
    yield package, submodules
    for subpackage in subpackages:
        yield from walk_package(subpackage)


def make_init_modules_for_package(path: str | Path | ModuleType) -> None:
    """Create __init__.py files in all subdirectories of a package.

    Ensures that all subdirectories of the given package have __init__.py files,
    effectively converting them into proper Python packages. Skips directories
    that match patterns in .gitignore.

    Args:
        path: The package path or module object to process

    Note:
        Does not modify directories that already have __init__.py files.
        Uses the default content for __init__.py files
        from get_default_init_module_content.

    """
    from winipedia_utils.modules.module import to_path

    path = to_path(path, is_package=True)

    for root, _dirs, files in walk_os_skipping_gitignore_patterns(path):
        if "__init__.py" in files:
            continue
        make_init_module(root)


def make_init_module(path: str | Path) -> None:
    """Create an __init__.py file in the specified directory.

    Creates an __init__.py file with default content in the given directory,
    making it a proper Python package.

    Args:
        path: The directory path where the __init__.py file should be created

    Note:
        If the path already points to an __init__.py file, that file will be
        overwritten with the default content.
        Creates parent directories if they don't exist.

    """
    from winipedia_utils.modules.module import get_default_init_module_content, to_path

    path = to_path(path, is_package=True)

    # if __init__.py not in path add it
    if path.name != "__init__.py":
        path = path / "__init__.py"

    content = get_default_init_module_content()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def copy_package(
    src_package: ModuleType,
    dst: str | Path | ModuleType,
    *,
    with_file_content: bool = True,
) -> None:
    """Copy a package to a different destination.

    Takes a ModuleType of package and a destination package name and then copies
    the package to the destination. If with_file_content is True, it copies the
    content of the files, otherwise it just creates the files.

    Args:
        src_package (ModuleType): The package to copy
        dst (str | Path): destination package name as a
                          Path with / or as a str with dots
        with_file_content (bool, optional): copies the content of the files.

    """
    from winipedia_utils.modules.module import (
        create_module,
        get_isolated_obj_name,
        get_module_content_as_str,
        to_path,
    )

    src_path = to_path(src_package, is_package=True)
    dst_path = to_path(dst, is_package=True) / get_isolated_obj_name(src_package)
    for package, modules in walk_package(src_package):
        # we need to make right path from the package to the dst
        # so that if we have a package package.package2.package3
        # and dst is a path like package4/package5/package6
        # we get the right path which is package4/package5/package6/package3
        package_path = to_path(package, is_package=True)
        dst_package_path = dst_path / package_path.relative_to(src_path)
        create_module(dst_package_path, is_package=True)
        for module in modules:
            module_name = get_isolated_obj_name(module)
            module_path = dst_package_path / module_name
            create_module(module_path, is_package=False)
            if with_file_content:
                module_path.write_text(get_module_content_as_str(module))


def get_main_package() -> ModuleType:
    """Gets the main package of the executing code.

    Even when this package is installed as a module.
    """
    from winipedia_utils.modules.module import to_module_name

    main = sys.modules.get("__main__")
    if main is None:
        msg = "No __main__ module found"
        raise ValueError(msg)

    package_name = getattr(main, "__package__", None)
    if package_name:
        package_name = package_name.split(".")[0]
        return import_module(package_name)

    file_name = getattr(main, "__file__", None)
    if file_name:
        package_name = to_module_name(file_name)
        package_name = package_name.split(".")[0]
        return import_module(package_name)

    msg = "Not able to determine the main package"
    raise ValueError(msg)
