"""Keyring utilities for secure storage and retrieval of secrets.

This module provides utility functions for working with keyring,
including getting and creating secrets and fernets.
These utilities help with secure storage and retrieval of secrets.
"""

from base64 import b64decode, b64encode
from collections.abc import Callable

import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_or_create_fernet(service_name: str, username: str) -> tuple[Fernet, bytes]:
    """Get the app secret using keyring.

    If it does not exist, create it with a Fernet.
    """
    return get_or_create_key(
        service_name, username, Fernet, lambda: Fernet.generate_key()
    )


def get_or_create_aes_gcm(service_name: str, username: str) -> tuple[AESGCM, bytes]:
    """Get the app secret using keyring.

    If it does not exist, create it with a AESGCM.
    """
    return get_or_create_key(
        service_name, username, AESGCM, lambda: AESGCM.generate_key(bit_length=256)
    )


def get_or_create_key[T](
    service_name: str,
    username: str,
    key_class: Callable[[bytes], T],
    generate_key_func: Callable[..., bytes],
) -> tuple[T, bytes]:
    """Get the app secret using keyring.

    If it does not exist, create it with the generate_func.
    """
    key = get_key_as_str(service_name, username, key_class)
    if key is None:
        binary_key = generate_key_func()
        key = b64encode(binary_key).decode("ascii")
        modified_service_name = make_service_name(service_name, key_class)
        keyring.set_password(modified_service_name, username, key)

    binary_key = b64decode(key)
    return key_class(binary_key), binary_key


def get_key_as_str[T](
    service_name: str, username: str, key_class: Callable[[bytes], T]
) -> str | None:
    """Get the app secret using keyring.

    If it does not exist, create it with the generate_func.
    """
    service_name = make_service_name(service_name, key_class)
    return keyring.get_password(service_name, username)


def make_service_name[T](service_name: str, key_class: Callable[[bytes], T]) -> str:
    """Make a service name from a service name and a key class."""
    return f"{service_name}_{key_class.__name__}"
