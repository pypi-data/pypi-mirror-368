"""Cryptography utilities for secure data handling.

This module provides utility functions for working with cryptography,
including encryption and decryption using Fernet and AESGCM.
These utilities help with secure data handling.
"""

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

IV_LEN = 12


def encrypt_with_aes_gcm(
    aes_gcm: AESGCM, data: bytes, aad: bytes | None = None
) -> bytes:
    """Encrypt data using AESGCM."""
    iv = os.urandom(IV_LEN)
    encrypted = aes_gcm.encrypt(iv, data, aad)
    return iv + encrypted


def decrypt_with_aes_gcm(
    aes_gcm: AESGCM, data: bytes, aad: bytes | None = None
) -> bytes:
    """Decrypt data using AESGCM."""
    iv, encrypted = data[:IV_LEN], data[IV_LEN:]
    return aes_gcm.decrypt(iv, encrypted, aad)
