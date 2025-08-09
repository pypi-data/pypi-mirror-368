"""Mixin utilities for class composition and behavior extension.

This module provides metaclasses and mixins that facilitate class composition
through the mixin pattern. It includes utilities for:
- Automatic method logging with performance tracking
- Abstract class implementation enforcement with type checking
- Combined metaclasses that merge multiple behaviors

These utilities help create robust class hierarchies with proper implementation
enforcement and built-in logging capabilities.
"""

from winipedia_utils.logging.logger import get_logger
from winipedia_utils.oop.mixins.meta import ABCLoggingMeta, StrictABCLoggingMeta

logger = get_logger(__name__)


class StrictABCLoggingMixin(metaclass=StrictABCLoggingMeta):
    """mixin class that provides implementation, logging, and ABC functionality.

    This mixin can be used as a base class for other mixins that need:
    - Abstract method declaration (from ABC)
    - Implementation enforcement (from ImplementationMeta)
    - Automatic method logging (from LoggingMeta)

    Subclasses must set __abstract__ = False when they provide concrete implementations.
    """


class ABCLoggingMixin(metaclass=ABCLoggingMeta):
    """Mixin class that provides automatic method logging with performance tracking.

    This mixin can be used as a base class for other mixins that need:
    - Automatic method logging (from LoggingMeta)

    """
