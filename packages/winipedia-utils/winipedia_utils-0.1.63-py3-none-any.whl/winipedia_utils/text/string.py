"""String manipulation utilities for text processing.

This module provides utility functions for working with strings, including
input handling, XML parsing, string truncation, and hashing operations.
These utilities simplify common string manipulation tasks throughout the application.
"""

import hashlib
import textwrap
from io import StringIO

from defusedxml import ElementTree as DefusedElementTree

from winipedia_utils.concurrent.multiprocessing import (
    cancel_on_timeout,
)
from winipedia_utils.logging.logger import get_logger

logger = get_logger(__name__)


def ask_for_input_with_timeout(prompt: str, timeout: int) -> str:
    """Request user input with a timeout constraint.

    Args:
        prompt: The text prompt to display to the user
        timeout: Maximum time in seconds to wait for input

    Returns:
        The user's input as a string

    Raises:
        TimeoutError: If the user doesn't provide input within the timeout period

    """

    @cancel_on_timeout(timeout, "Input not given within the timeout")
    def give_input() -> str:
        return input(prompt)

    user_input: str = give_input()

    return user_input


def find_xml_namespaces(xml: str | StringIO) -> dict[str, str]:
    """Extract namespace declarations from XML content.

    Args:
        xml: XML content as a string or StringIO object

    Returns:
        Dictionary mapping namespace prefixes to their URIs,
        excluding the default namespace

    """
    if not isinstance(xml, StringIO):
        xml = StringIO(xml)
    # Extract the namespaces from the root tag
    namespaces_: dict[str, str] = {}
    iter_ns = DefusedElementTree.iterparse(xml, events=["start-ns"])
    for _, namespace_data in iter_ns:
        prefix, uri = namespace_data
        namespaces_[str(prefix)] = str(uri)

    namespaces_.pop("", None)

    return namespaces_


def value_to_truncated_string(value: object, max_length: int) -> str:
    """Convert any value to a string and truncate if longer than max_length.

    Args:
        value: Any object to convert to string
        max_length: Maximum length of the resulting string

    Returns:
        Truncated string representation of the value

    """
    string = str(value)
    return textwrap.shorten(string, width=max_length, placeholder="...")


def get_reusable_hash(value: object) -> str:
    """Generate a consistent hash for any object.

    Creates a SHA-256 hash of the string representation of the given value.
    This hash is deterministic and can be used for caching or identification.

    Args:
        value: Any object to hash

    Returns:
        Hexadecimal string representation of the SHA-256 hash

    """
    value_str = str(value)
    return hashlib.sha256(value_str.encode("utf-8")).hexdigest()


def split_on_uppercase(string: str) -> list[str]:
    """Split a string on uppercase letters.

    Args:
        string: String to split

    Returns:
        List of substrings split on uppercase letters

    Example:
        split_on_uppercase("HelloWorld") -> ["Hello", "World"]

    """
    letters = list(string)
    parts = []
    current_part = ""
    for letter in letters:
        if letter.isupper() and current_part:
            parts.append(current_part)
            current_part = letter
        else:
            current_part += letter
    parts.append(current_part)
    return parts
