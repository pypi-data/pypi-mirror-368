"""Class utilities for introspection and manipulation.

This module provides utility functions for working with Python classes,
including extracting methods from classes and finding classes within modules.
These utilities are particularly useful for reflection, testing,
and dynamic code generation.
"""

import inspect
from collections.abc import Callable
from importlib import import_module
from types import ModuleType
from typing import Any

from winipedia_utils.modules.function import is_func


def get_all_methods_from_cls(
    class_: type, *, exclude_parent_methods: bool = False
) -> list[Callable[..., Any]]:
    """Get all methods from a class.

    Retrieves all methods (functions or methods) from a class. Can optionally
    exclude methods inherited from parent classes.

    Args:
        class_: The class to extract methods from
        exclude_parent_methods: If True, only include methods defined in this class,
        excluding those inherited from parent classes
    Returns:
        A list of callable methods from the class

    """
    from winipedia_utils.modules.module import get_def_line, get_module_of_obj

    methods = [
        (method, name) for name, method in inspect.getmembers(class_) if is_func(method)
    ]

    if exclude_parent_methods:
        methods = [
            (method, name)
            for method, name in methods
            if get_module_of_obj(method).__name__ == class_.__module__
            and name in class_.__dict__
        ]

    only_methods = [method for method, _name in methods]
    # sort by definition order
    return sorted(only_methods, key=get_def_line)


def get_all_cls_from_module(module: ModuleType | str) -> list[type]:
    """Get all classes defined in a module.

    Retrieves all class objects that are defined directly in the specified module,
    excluding imported classes.

    Args:
        module: The module to extract classes from

    Returns:
        A list of class types defined in the module

    """
    from winipedia_utils.modules.module import get_def_line, get_module_of_obj

    if isinstance(module, str):
        module = import_module(module)

    # necessary for bindings packages like AESGCM from cryptography._rust backend
    default = ModuleType("default")
    classes = [
        obj
        for _, obj in inspect.getmembers(module, inspect.isclass)
        if get_module_of_obj(obj, default).__name__ == module.__name__
    ]
    # sort by definition order
    return sorted(classes, key=get_def_line)


def get_all_subclasses(cls: type) -> list[type]:
    """Get all subclasses of a class.

    Retrieves all classes that are subclasses of the specified class.
    Also returns subclasses of subclasses (recursive).

    Args:
        cls: The class to find subclasses of

    Returns:
        A list of subclasses of the given class

    """
    subclasses_set = set(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses_set.update(get_all_subclasses(subclass))
    return list(subclasses_set)


def get_all_nonabstract_subclasses(cls: type) -> list[type]:
    """Get all non-abstract subclasses of a class.

    Retrieves all classes that are subclasses of the specified class,
    excluding abstract classes. Also returns subclasses of subclasses
    (recursive).

    Args:
        cls: The class to find subclasses of

    Returns:
        A list of non-abstract subclasses of the given class

    """
    return [
        subclass
        for subclass in get_all_subclasses(cls)
        if not inspect.isabstract(subclass)
    ]
