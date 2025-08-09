"""Iterating utilities for handling iterables.

This module provides utility functions for working with iterables,
including getting the length of an iterable with a default value.
These utilities help with iterable operations and manipulations.
"""

from collections.abc import Iterable
from typing import Any


def get_len_with_default(iterable: Iterable[Any], default: int | None = None) -> int:
    """Get the length of an iterable with a default value.

    Args:
        iterable: Iterable to get the length of
        default: Default value to return if the iterable is empty

    Returns:
        Length of the iterable or the default value if the iterable is empty

    """
    try:
        return len(iterable)  # type: ignore[arg-type]
    except TypeError as e:
        if default is None:
            msg = "Can't get length of iterable and no default value provided"
            raise TypeError(msg) from e
        return default
