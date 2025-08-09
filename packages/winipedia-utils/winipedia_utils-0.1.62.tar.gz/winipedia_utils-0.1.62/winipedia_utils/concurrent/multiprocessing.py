"""Multiprocessing utilities for concurrent execution.

This module provides functions for parallel processing using both multiprocessing
and multithreading approaches. It includes utilities for handling timeouts,
managing process pools, and organizing parallel execution of functions.

Returns:
    Various utility functions for concurrent processing.

"""

import multiprocessing
from collections.abc import Callable, Iterable
from functools import wraps
from multiprocessing.pool import Pool
from typing import Any

from winipedia_utils.logging.logger import get_logger

logger = get_logger(__name__)


def cancel_on_timeout(seconds: float, message: str) -> Callable[..., Any]:
    """Cancel a function execution if it exceeds a specified timeout.

    Creates a wrapper that executes the decorated function in a separate process
    and terminates it if execution time exceeds the specified timeout.

    Args:
        seconds: Maximum execution time in seconds before timeout
        message: Error message to include in the raised TimeoutError

    Returns:
        A decorator function that wraps the target function with timeout functionality

    Raises:
        multiprocessing.TimeoutError: When function execution exceeds the timeout

    Note:
        Only works with functions that are pickle-able.
        This means it may not work as a decorator.
        Instaed you should use it as a wrapper function.
        Like this:
        my_func = cancel_on_timeout(seconds=2, message="Test timeout")(my_func)

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            with Pool(processes=1) as pool:
                async_result = pool.apply_async(func, args, kwargs)
                try:
                    return async_result.get(timeout=seconds)
                except multiprocessing.TimeoutError:
                    logger.warning(
                        "%s -> Execution exceeded %s seconds: %s",
                        func.__name__,
                        seconds,
                        message,
                    )
                    raise
                finally:
                    pool.terminate()  # Ensure the worker process is killed
                    pool.join()  # Wait for cleanup

        return wrapper

    return decorator


def multiprocess_loop(
    process_function: Callable[..., Any],
    process_args: Iterable[Iterable[Any]],
    process_args_static: Iterable[Any] | None = None,
    deepcopy_static_args: Iterable[Any] | None = None,
    process_args_len: int = 1,
) -> list[Any]:
    """Process a loop using multiprocessing Pool for parallel execution.

    Executes the given process_function with the provided arguments in parallel using
    multiprocessing Pool, which is suitable for CPU-bound tasks.

    Args:
        process_function: Function that processes the given process_args
        process_args: List of args to be processed by the process_function
                    e.g. [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        process_args_static: Optional constant arguments passed to each function call
        deepcopy_static_args: Optional arguments that should be
                              deep-copied for each process
        process_args_len: Optional length of process_args
                          If not provided, it will ot be taken into account
                          when calculating the max number of processes.

    Returns:
        List of results from the process_function executions

    Note:
        Pool is used for CPU-bound tasks as it bypasses
        Python's GIL by creating separate processes.
        Multiprocessing is not safe for mutable objects unlike ThreadPoolExecutor.
        When debugging, if ConnectionErrors occur, set max_processes to 1.
        Also given functions must be pickle-able.

    """
    from winipedia_utils.concurrent.concurrent import concurrent_loop

    return concurrent_loop(
        threading=False,
        process_function=process_function,
        process_args=process_args,
        process_args_static=process_args_static,
        deepcopy_static_args=deepcopy_static_args,
        process_args_len=process_args_len,
    )
