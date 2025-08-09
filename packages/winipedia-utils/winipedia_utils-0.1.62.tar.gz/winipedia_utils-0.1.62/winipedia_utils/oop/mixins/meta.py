"""Metaclass utilities for class behavior modification and enforcement.

This module provides metaclasses that can be used to
modify class behavior at creation time.
These metaclasses can be used individually or combined to create classes
with enhanced capabilities and stricter implementation requirements.

"""

import time
from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any, final

from winipedia_utils.logging.logger import get_logger
from winipedia_utils.modules.class_ import get_all_methods_from_cls
from winipedia_utils.modules.function import is_func, unwrap_method
from winipedia_utils.text.string import value_to_truncated_string

logger = get_logger(__name__)


class ABCLoggingMeta(ABCMeta):
    """Metaclass that automatically adds logging to class methods.

    Wraps non-magic methods with a logging decorator that tracks method calls,
    arguments, execution time, and return values. Includes rate limiting to
    prevent log flooding.
    """

    def __new__(
        mcs: type["ABCLoggingMeta"],
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, Any],
    ) -> "ABCLoggingMeta":
        """Create a new class with logging-wrapped methods.

        Args:
            mcs: The metaclass instance
            name: The name of the class being created
            bases: The base classes of the class being created
            dct: The attribute dictionary of the class being created

        Returns:
            A new class with logging functionality added to its methods

        """
        # Wrap all callables of the class with a logging wrapper

        for attr_name, attr_value in dct.items():
            if mcs.is_loggable_method(attr_value):
                if isinstance(attr_value, classmethod):
                    wrapped_method = mcs.wrap_with_logging(
                        func=attr_value.__func__, class_name=name, call_times={}
                    )
                    dct[attr_name] = classmethod(wrapped_method)
                elif isinstance(attr_value, staticmethod):
                    wrapped_method = mcs.wrap_with_logging(
                        func=attr_value.__func__, class_name=name, call_times={}
                    )
                    dct[attr_name] = staticmethod(wrapped_method)
                else:
                    dct[attr_name] = mcs.wrap_with_logging(
                        func=attr_value, class_name=name, call_times={}
                    )

        return super().__new__(mcs, name, bases, dct)

    @staticmethod
    def is_loggable_method(method: Callable[..., Any]) -> bool:
        """Determine if a method should have logging applied.

        Args:
            method: The method to check

        Returns:
            True if the method should be wrapped with logging, False otherwise

        """
        return (
            is_func(method)  # must be a method-like attribute
            and not method.__name__.startswith("__")  # must not be a magic method
        )

    @staticmethod
    def wrap_with_logging(
        func: Callable[..., Any],
        class_name: str,
        call_times: dict[str, float],
    ) -> Callable[..., Any]:
        """Wrap a function with logging functionality.

        Creates a wrapper that logs method calls, arguments, execution time,
        and return values. Includes rate limiting to prevent excessive logging.

        Args:
            func: The function to wrap with logging
            class_name: The name of the class containing the function
            call_times: Dictionary to track when methods were last called

        Returns:
            A wrapped function with logging capabilities

        """
        time_time = time.time  # Cache the time.time function for performance

        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            # call_times as a dictionary to store the call times of the function
            # we only log if the time since the last call is greater than the threshold
            # this is to avoid spamming the logs

            func_name = func.__name__

            threshold = 1

            last_call_time = call_times.get(func_name, 0)

            current_time = time_time()

            do_logging = (current_time - last_call_time) > threshold

            max_log_length = 20

            if do_logging:
                args_str = value_to_truncated_string(
                    value=args, max_length=max_log_length
                )

                kwargs_str = value_to_truncated_string(
                    value=kwargs, max_length=max_log_length
                )

                logger.info(
                    "%s - Calling %s with %s and %s",
                    class_name,
                    func_name,
                    args_str,
                    kwargs_str,
                )

            # Execute the function and return the result

            result = func(*args, **kwargs)

            if do_logging:
                duration = time_time() - current_time

                result_str = value_to_truncated_string(
                    value=result, max_length=max_log_length
                )

                logger.info(
                    "%s - %s finished with %s seconds -> returning %s",
                    class_name,
                    func_name,
                    duration,
                    result_str,
                )

            # save the call time for the next call

            call_times[func_name] = current_time

            return result

        return wrapper


class StrictABCMeta(ABCMeta):
    """Metaclass that enforces implementation.

    Ensures that concrete subclasses properly implement all required attributes
    and that their types match the expected types from type annotations.
    Additionally enforces that methods must be decorated with either @final or
    @abstractmethod to make design intentions explicit.
    """

    def __init__(
        cls: "StrictABCMeta",
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        /,
        **_kwargs: Any,
    ) -> None:
        """Initialize a class with implementation checking.

        Verifies that concrete classes (non-abstract) properly implement
        all required attributes with the correct types. Also checks that
        methods are properly decorated with @final or @abstractmethod.

        Args:
            cls: The class being initialized
            name: The name of the class
            bases: The base classes
            namespace: The attribute dictionary

        Raises:
            NotImplementedError: If the class doesn't define __abstract__
            ValueError: If a required attribute is not implemented
            TypeError: If an implemented attribute has the wrong type
            TypeError: If a method is neither final nor abstract

        """
        super().__init__(name, bases, namespace)

        # Check method decorators regardless of abstract status

        cls.check_method_decorators()

        if cls.is_abstract_cls():
            return

        cls.check_attrs_implemented()

    def is_abstract_cls(cls) -> bool:
        """Check if the class is abstract.

        Determines abstractness based on if any methods have @abstractmethod.

        Returns:
            True if the class is abstract, False otherwise

        """
        return any(cls.__abstractmethods__)

    def check_method_decorators(cls) -> None:
        """Check that all methods are properly decorated with @final or @abstractmethod.

        Verifies that all methods in the class are explicitly marked
        as either final or abstract to enforce design intentions.

        Raises:
            TypeError: If a method is neither final nor abstract

        """
        # Get all methods defined in this class (not inherited)

        for func in get_all_methods_from_cls(cls, exclude_parent_methods=True):
            # Check if the method is marked as final or abstract

            if not cls.is_final_method(func) and not cls.is_abstract_method(func):
                msg = (
                    f"Method {cls.__name__}.{func.__name__} must be decorated with "
                    f"@{final.__name__} or @{abstractmethod.__name__} "
                    f"to make design intentions explicit."
                )

                raise TypeError(msg)

    @staticmethod
    def is_final_method(method: Callable[..., Any]) -> bool:
        """Check if a method is marked as final.

        Args:
            method: The method to check

        Returns:
            True if the method is marked with @final, False otherwise

        """
        unwrapped_method = unwrap_method(method)
        return getattr(method, "__final__", False) or getattr(
            unwrapped_method, "__final__", False
        )

    @staticmethod
    def is_abstract_method(method: Callable[..., Any]) -> bool:
        """Check if a method is an abstract method.

        Args:
            method: The method to check

        Returns:
            True if the method is marked with @abstractmethod, False otherwise

        """
        return getattr(method, "__isabstractmethod__", False)

    def check_attrs_implemented(cls) -> None:
        """Check that all required attributes are implemented.

        Verifies that all attributes marked as NotImplemented in parent classes
        are properly implemented in this class, and that their types match
        the expected types from type annotations.

        Raises:
            ValueError: If a required attribute is not implemented

        """
        for attr in cls.attrs_to_implement():
            value = getattr(cls, attr, NotImplemented)

            if value is NotImplemented:
                msg = f"{attr=} must be implemented."

                raise ValueError(msg)

    def attrs_to_implement(cls) -> list[str]:
        """Find all attributes marked as NotImplemented in parent classes.

        Searches the class hierarchy for attributes that are set to NotImplemented,
        which indicates they must be implemented by concrete subclasses.

        Returns:
            List of attribute names that must be implemented

        """
        attrs = {
            attr
            for base_class in cls.__mro__
            for attr in dir(base_class)
            if getattr(base_class, attr, None) is NotImplemented
        }

        return list(attrs)


class StrictABCLoggingMeta(StrictABCMeta, ABCLoggingMeta):
    """Combined metaclass that merges implementation, logging, and ABC functionality.

    This metaclass combines the features of:
    - ImplementationMeta: Enforces implementation of required attributes
    - LoggingMeta: Adds automatic logging to methods
    - ABCMeta: Provides abstract base class functionality

    Use this metaclass when you need all three behaviors in a single class.
    """
