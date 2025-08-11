"""Multithreading utilities for concurrent execution.

This module provides functions for parallel processing using thread pools.
It includes utilities for handling thread pools, managing futures, and organizing
parallel execution of I/O-bound tasks.
Base helper functions that serve threading and processing are located in the
multiprocessing module.

Returns:
    Various utility functions for multithreaded processing.

"""

from collections.abc import Callable, Generator, Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any


def get_future_results_as_completed(
    futures: Iterable[Future[Any]],
) -> Generator[Any, None, None]:
    """Get future results as they complete.

    Yields results from futures in the order they complete,
    not in the order they were submitted.

    Args:
        futures: List of Future objects to get results from

    Yields:
        The result of each completed future

    """
    for future in as_completed(futures):
        yield future.result()


def multithread_loop(
    process_function: Callable[..., Any],
    process_args: Iterable[Iterable[Any]],
    process_args_static: Iterable[Any] | None = None,
    process_args_len: int = 1,
) -> list[Any]:
    """Process a loop using ThreadPoolExecutor for parallel execution.

    Executes the given process_function with the provided arguments in parallel using
    ThreadPoolExecutor, which is suitable for I/O-bound tasks.

    Args:
        process_function: Function that processes the given process_args
        process_args: list of args to be processed by the process_function
                    e.g. [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        process_args_static: Optional constant arguments passed to each function call
        process_args_len: Optional length of process_args
                          If not provided, it will ot be taken into account
                          when calculating the max number of workers.

    Returns:
        List of results from the process_function executions

    Note:
        ThreadPoolExecutor is used for I/O-bound tasks, not for CPU-bound tasks.

    """
    from winipedia_utils.concurrent.concurrent import concurrent_loop

    return concurrent_loop(
        threading=True,
        process_function=process_function,
        process_args=process_args,
        process_args_static=process_args_static,
        process_args_len=process_args_len,
    )


def imap_unordered(
    executor: ThreadPoolExecutor,
    func: Callable[..., Any],
    iterable: Iterable[Any],
) -> Generator[Any, None, None]:
    """Apply a function to each item in an iterable in parallel.

    Args:
        executor: ThreadPoolExecutor to use for parallel execution
        func: Function to apply to each item in the iterable
        iterable: Iterable of items to apply the function to

    Yields:
        Results of applying the function to each item in the iterable

    """
    results = [executor.submit(func, item) for item in iterable]
    yield from get_future_results_as_completed(results)
