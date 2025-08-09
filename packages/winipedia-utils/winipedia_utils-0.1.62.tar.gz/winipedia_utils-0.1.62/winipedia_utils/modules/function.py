"""Function utilities for introspection and manipulation.

This module provides utility functions for working with Python functions,
including extracting functions from modules and manipulating function objects.
These utilities are particularly useful for reflection, testing, and
dynamic code generation.
"""

import inspect
from collections.abc import Callable
from importlib import import_module
from types import ModuleType
from typing import Any


def is_func_or_method(obj: Any) -> bool:
    """Return True if *obj* is a function or method.

    This function checks if the given object is a function or method,
    including those defined in a class body.

    Args:
        obj: The object to check

    Returns:
        bool: True if the object is a function or method, False otherwise

    """
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def is_func(obj: Any) -> bool:
    """Return True if *obj* is a 'method-like' attribute as it appears in a class body.

    Accepts:


        • plain functions (instance methods)
        • staticmethod / classmethod descriptors
        • property descriptors (getter counts as method)
        • decorated functions that keep a __wrapped__ chain

    Returns:
        bool: True if the object is a method-like attribute, False otherwise

    """
    # plain function

    if is_func_or_method(obj):
        return True

    if isinstance(obj, (staticmethod, classmethod, property)):
        return True

    # unwrap any wrappers (@functools.wraps) and retest

    unwrapped = inspect.unwrap(obj)

    return is_func_or_method(unwrapped)


def get_all_functions_from_module(module: ModuleType | str) -> list[Callable[..., Any]]:
    """Get all functions defined in a module.

    Retrieves all function objects that are defined directly in the specified module,
    excluding imported functions.
    The functions are sorted by their line number in the module.

    Args:
        module: The module to extract functions from

    Returns:
        A list of callable functions defined in the module

    """
    from winipedia_utils.modules.module import get_def_line, get_module_of_obj

    if isinstance(module, str):
        module = import_module(module)
    funcs = [
        func
        for _name, func in inspect.getmembers(module, is_func)
        if get_module_of_obj(func).__name__ == module.__name__
    ]
    # sort by definition order
    return sorted(funcs, key=get_def_line)


def unwrap_method(method: Any) -> Callable[..., Any] | Any:
    """Unwrap a method to its underlying function.

    Args:
        method: The method to unwrap

    Returns:
        The underlying function of the method

    """
    if isinstance(method, (staticmethod, classmethod)):
        method = method.__func__
    if isinstance(method, property):
        method = method.fget
    return inspect.unwrap(method)
