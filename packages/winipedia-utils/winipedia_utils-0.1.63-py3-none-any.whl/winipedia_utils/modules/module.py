"""Module utilities for introspection and manipulation.

This module provides comprehensive utility functions for working with Python modules,
including path conversions, module creation, object importing, and content extraction.
It handles the complexities of Python's module system by providing a consistent API
for module operations across different contexts (packages vs. standalone modules).

The utilities support both runtime module manipulation and static analysis,
making them suitable for code generation, testing frameworks, and dynamic imports.
"""

import inspect
import os
import sys
import time
from collections.abc import Callable, Sequence
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, cast

from winipedia_utils.logging.logger import get_logger
from winipedia_utils.modules.class_ import (
    get_all_cls_from_module,
    get_all_methods_from_cls,
)
from winipedia_utils.modules.function import get_all_functions_from_module
from winipedia_utils.modules.package import (
    get_modules_and_packages_from_package,
    make_dir_with_init_file,
    module_is_package,
)

logger = get_logger(__name__)


def get_module_content_as_str(module: ModuleType) -> str:
    """Retrieve the complete source code of a module as a string.

    This function locates the physical file associated with the given module object
    and reads its entire content. It works for both regular modules and packages
    by determining the correct path using module_to_path.

    Args:
        module: The module object whose source code should be retrieved


    Returns:
        The complete source code of the module as a string

    """
    path = to_path(module, is_package=False)
    return path.read_text()


def to_module_name(path: str | Path | ModuleType) -> str:
    """Convert a filesystem path to a Python module import name.

    Transforms a file or directory path into the corresponding Python module name
    by making it relative to the current directory, removing the file extension,
    and replacing directory separators with dots.

    Args:
        path: a str that represents a path or a Path object or a ModuleType object
                or a str that represents a module name

    Returns:
        The Python module name corresponding to the path

    Example:
        path_to_module_name("src/package/module.py") -> "src.package.module"

    """
    if isinstance(path, ModuleType):
        return path.__name__
    if isinstance(path, Path):
        abs_path = path.resolve()
        rel_path = abs_path.relative_to(Path.cwd())
        if rel_path.suffix:
            rel_path = rel_path.with_suffix("")
        # return joined on . parts
        return ".".join(rel_path.parts)
    if path in (".", "./", ""):
        return ""
    # we get a str that can either be a dotted module name or a path
    # e.g. package/module.py or package/module or
    # package.module or just package/package2
    # or just package with nothing
    path = path.removesuffix(".py")
    if "." in path:
        # already a module name
        return path
    return to_module_name(Path(path))


def to_path(module_name: str | ModuleType | Path, *, is_package: bool) -> Path:
    """Convert a Python module import name to its filesystem path.

    Transforms a Python module name into the corresponding file path by replacing
    dots with directory separators and adding the .py extension. Uses the
    package_name_to_path function for the directory structure.

    Args:
        module_name: A Python module name to convert or Path or ModuleType
        is_package: Whether to return the path to the package directory
            without the .py extension

    Returns:
        A Path object representing the filesystem path to the module
        if is_package is True, returns the path to the package directory
        without the .py extension

    Example:
        module_name_to_path("src.package.module") -> Path("src/package/module.py")

    """
    module_name = to_module_name(module_name)
    path = Path(module_name.replace(".", os.sep))
    # for smth like pyinstaller we support frozen path
    if getattr(sys, "frozen", False):
        path = Path(getattr(sys, "_MEIPASS", "")) / path
    if is_package:
        return path
    return path.with_suffix(".py")


def create_module(
    module_name: str | Path | ModuleType, *, is_package: bool
) -> ModuleType:
    """Create a new Python module file and import it.

    Creates a new module file at the location specified by the module name,
    ensuring all necessary parent directories and __init__.py files exist.
    Optionally writes content to the module file and parent __init__.py files.
    Finally imports and returns the newly created module.

    Args:
        module_name: The fully qualified name of the module to create
        is_package: Whether to create a package instead of a module

    Returns:
        The imported module object representing the newly created module

    Note:
        Includes a small delay (0.1s) before importing to ensure filesystem operations
        are complete, preventing race conditions.

    """
    path = to_path(module_name, is_package=is_package)
    if path == Path():
        msg = f"Cannot create module {module_name=} because it is the current directory"
        logger.error(msg)
        raise ValueError(msg)

    make_dir_with_init_file(path if is_package else path.parent)
    # create the module file if not exists
    if not path.exists() and not is_package:
        path.write_text(get_default_module_content())

    module_name = to_module_name(path)
    # wait before importing the module
    time.sleep(0.1)
    return import_module(module_name)


def make_obj_importpath(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Create a fully qualified import path string for a Python object.

    Generates the import path that would be used to import the given object.
    Handles different types of objects (modules, classes, functions) appropriately.

    Args:
        obj: The object (module, class, or function) to create an import path for

    Returns:
        A string representing the fully qualified import path for the object

    Examples:
        For a module: "package.subpackage.module"
        For a class: "package.module.ClassName"
        For a function: "package.module.function_name"
        For a method: "package.module.ClassName.method_name"

    """
    if isinstance(obj, ModuleType):
        return obj.__name__
    module: str | None = get_module_of_obj(obj).__name__
    obj_name = get_qualname_of_obj(obj)
    if not module:
        return obj_name
    return module + "." + obj_name


def import_obj_from_importpath(
    importpath: str,
) -> Callable[..., Any] | type | ModuleType:
    """Import a Python object (module, class, or function) from its import path.

    Attempts to import the object specified by the given import path. First tries
    to import it as a module, and if that fails, attempts to import it as a class
    or function by splitting the path and using getattr.

    Args:
        importpath: The fully qualified import path of the object

    Returns:
        The imported object (module, class, or function)

    Raises:
        ImportError: If the module part of the path cannot be imported
        AttributeError: If the object is not found in the module

    """
    try:
        return import_module(importpath)
    except ImportError:
        # might be a class or function
        module_name, obj_name = importpath.rsplit(".", 1)
        module = import_module(module_name)
        obj: Callable[..., Any] | type | ModuleType = getattr(module, obj_name)
        return obj


def get_isolated_obj_name(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Extract the bare name of an object without its module prefix.

    Retrieves just the name part of an object, without any module path information.
    For modules, returns the last component of the module path.

    Args:
        obj: The object (module, class, or function) to get the name for

    Returns:
        The isolated name of the object without any module path

    Examples:
        For a module "package.subpackage.module": returns "module"
        For a class: returns the class name
        For a function: returns the function name

    """
    obj = get_unwrapped_obj(obj)
    if isinstance(obj, ModuleType):
        return obj.__name__.split(".")[-1]
    if isinstance(obj, type):
        return obj.__name__
    return get_qualname_of_obj(obj).split(".")[-1]


def get_objs_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> Sequence[Callable[..., Any] | type | ModuleType]:
    """Extract all contained objects from a container object.

    Retrieves all relevant objects contained within the given object, with behavior
    depending on the type of the container:
    - For modules: returns all functions and classes defined in the module
    - For packages: returns all submodules in the package
    - For classes: returns all methods defined directly in the class
    - For other objects: returns an empty list

    Args:
        obj: The container object to extract contained objects from

    Returns:
        A sequence of objects contained within the given container object

    """
    if isinstance(obj, ModuleType):
        if module_is_package(obj):
            return get_modules_and_packages_from_package(obj)[1]
        objs: list[Callable[..., Any] | type] = []
        objs.extend(get_all_functions_from_module(obj))
        objs.extend(get_all_cls_from_module(obj))
        return objs
    if isinstance(obj, type):
        return get_all_methods_from_cls(obj, exclude_parent_methods=True)
    return []


def execute_all_functions_from_module(module: ModuleType) -> list[Any]:
    """Execute all functions defined in a module with no arguments.

    Retrieves all functions defined in the module and calls each one with no arguments.
    Collects and returns the results of all function calls.

    Args:
        module: The module containing functions to execute

    Returns:
        A list containing the return values from all executed functions

    Note:
        Only executes functions defined directly in the module, not imported functions.
        All functions must accept being called with no arguments.

    """
    return [f() for f in get_all_functions_from_module(module)]


def get_default_init_module_content() -> str:
    """Generate standardized content for an __init__.py file.

    Creates a simple docstring for an __init__.py file based on its location,
    following the project's documentation conventions.

    Args:
        path: The path to the __init__.py file or its parent directory

    Returns:
        A string containing a properly formatted docstring for the __init__.py file

    """
    return '''"""__init__ module."""'''


def get_default_module_content() -> str:
    """Generate standardized content for a Python module file.

    Creates a simple docstring for a module file based on its name,
    following the project's documentation conventions.

    Returns:
        A string containing a properly formatted docstring for the module file

    """
    return '''"""module."""'''


def inside_frozen_bundle() -> bool:
    """Return True if the code is running inside a frozen bundle."""
    return getattr(sys, "frozen", False)


def get_def_line(obj: Any) -> int:
    """Return the line number where a method-like object is defined."""
    if isinstance(obj, property):
        obj = obj.fget
    unwrapped = inspect.unwrap(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)
    # getsourcelines does not work if in a pyinstaller bundle or something
    if inside_frozen_bundle():
        return 0
    return inspect.getsourcelines(unwrapped)[1]


def get_module_of_obj(obj: Any, default: ModuleType | None = None) -> ModuleType:
    """Return the module name where a method-like object is defined.

    Args:
        obj: Method-like object (funcs, method, property, staticmethod, classmethod...)
        default: Default module to return if the module cannot be determined

    Returns:
        The module name as a string, or None if module cannot be determined.

    """
    unwrapped = get_unwrapped_obj(obj)
    module = inspect.getmodule(unwrapped)
    if not module:
        msg = f"Could not determine module of {obj}"
        if default:
            return default
        raise ValueError(msg)
    return module


def get_qualname_of_obj(obj: Callable[..., Any] | type) -> str:
    """Return the name of a method-like object."""
    unwrapped = get_unwrapped_obj(obj)
    return cast("str", unwrapped.__qualname__)


def get_unwrapped_obj(obj: Any) -> Any:
    """Return the unwrapped version of a method-like object."""
    if isinstance(obj, property):
        obj = obj.fget  # get the getter function of the property
    return inspect.unwrap(obj)
