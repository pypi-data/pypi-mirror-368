"""Concurrent processing utilities for parallel execution.

This module provides functions for concurrent processing using both multiprocessing
and multithreading approaches. It includes utilities for handling timeouts,
managing process pools, and organizing parallel execution of functions.

Returns:
    Various utility functions for concurrent processing.

"""

import multiprocessing
import os
import threading
from collections.abc import Callable, Generator, Iterable
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from functools import partial
from multiprocessing.pool import Pool
from typing import Any, cast

from tqdm import tqdm

from winipedia_utils.concurrent.multithreading import imap_unordered
from winipedia_utils.iterating.iterate import get_len_with_default
from winipedia_utils.logging.logger import get_logger

logger = get_logger(__name__)


def get_order_and_func_result(
    func_order_args: tuple[Any, ...],
) -> tuple[int, Any]:
    """Process function for imap with arguments unpacking.

    Helper function that gives back a function that can be used with imap_unordered
    to execute a function with arguments unpacking.

    Args:
        func_order_args: Tuple containing the function to be executed,
            the order index, and the arguments for the function

    Returns:
        A tuple containing the order index and the result of the function execution

    """
    function, order, *args = func_order_args
    return order, function(*args)


def generate_process_args(
    *,
    process_function: Callable[..., Any],
    process_args: Iterable[Iterable[Any]],
    process_args_static: Iterable[Any] | None = None,
    deepcopy_static_args: Iterable[Any] | None = None,
) -> Generator[tuple[Any, ...], None, None]:
    """Prepare arguments for multiprocessing or multithreading execution.

    Converts input arguments into a format suitable for parallel processing,
    organizing them for efficient unpacking during execution. The function:
    1. Prepends process func and order indices to arguments
    2. Handles static arguments (with optional deep copying)
    3. Restructures arguments into tuples for unpacking

    Args:
        process_function: Function to be executed
        process_args: Iterable of argument lists for each parallel call
        process_args_static: Optional constant arguments to add to each call
        deepcopy_static_args: Optional constant arguments that should be deep-copied

    Returns:
        A Genrator that yields one args tuple for each function call
        First is the process function
        Second item in the tuple is the order index
        Second item in the tuple is the function
        Rest of the items are the arguments for the function
        The length of the generator
    """
    process_args_static = (
        () if process_args_static is None else tuple(process_args_static)
    )
    deepcopy_static_args = (
        () if deepcopy_static_args is None else tuple(deepcopy_static_args)
    )
    for order, process_arg in enumerate(process_args):
        yield (
            process_function,
            order,
            *process_arg,
            *process_args_static,
            *(
                deepcopy(deepcopy_static_arg)
                for deepcopy_static_arg in deepcopy_static_args
            ),
        )


def get_multiprocess_results_with_tqdm(
    results: Iterable[Any],
    process_func: Callable[..., Any],
    process_args_len: int,
    *,
    threads: bool,
) -> list[Any]:
    """Get multiprocess results with tqdm progress tracking.

    Processes results from parallel execution with a progress bar and ensures
    they are returned in the original order.

    Args:
        results: Iterable of results from parallel execution
        process_func: Function that was executed in parallel
        process_args_len: Number of items to process in parallel
        threads: Whether threading (True) or multiprocessing (False) was used

    Returns:
        list[Any]: Results from parallel execution in original order

    """
    results = tqdm(
        results,
        total=process_args_len,
        desc=f"Multi{'threading' if threads else 'processing'} {process_func.__name__}",
        unit=f" {'threads' if threads else 'processes'}",
    )
    results_list = list(results)
    # results list is a tuple of (order, result),
    # so we need to sort it by order to get the original order
    results_list = sorted(results_list, key=lambda x: x[0])
    # now extract the results from the tuple
    return [result[1] for result in results_list]


def find_max_pools(
    *,
    threads: bool,
    process_args_len: int | None = None,
) -> int:
    """Find optimal number of worker processes or threads for parallel execution.

    Determines the maximum number of worker processes or threads based on system
    resources, active tasks, and the number of items to process.

    Args:
        threads: Whether to use threading (True) or multiprocessing (False)
        process_args_len: Number of items to process in parallel

    Returns:
        int: Maximum number of worker processes or threads to use

    """
    # use tee to find length of process_args
    cpu_count = os.cpu_count() or 1
    if threads:
        active_tasks = threading.active_count()
        max_tasks = cpu_count * 4
    else:
        active_tasks = len(multiprocessing.active_children())
        max_tasks = cpu_count

    available_tasks = max_tasks - active_tasks
    max_pools = (
        min(available_tasks, process_args_len) if process_args_len else available_tasks
    )
    max_pools = max(max_pools, 1)

    logger.info(
        "Multi%s with max_pools: %s",
        "threading" if threads else "processing",
        max_pools,
    )

    return max_pools


def concurrent_loop(  # noqa: PLR0913
    *,
    threading: bool,
    process_function: Callable[..., Any],
    process_args: Iterable[Iterable[Any]],
    process_args_static: Iterable[Any] | None = None,
    deepcopy_static_args: Iterable[Any] | None = None,
    process_args_len: int = 1,
) -> list[Any]:
    """Execute a function concurrently with multiple arguments using a pool executor.

    This function is a helper function for multiprocess_loop and multithread_loop.
    It is not meant to be used directly.

    Args:
        threading (bool):
            Whether to use threading (True) or multiprocessing (False)
        pool_executor (Pool | ThreadPoolExecutor):
            Pool executor to use for concurrent execution
        process_function (Callable[..., Any]):
            Function to be executed concurrently
        process_args (Iterable[Iterable[Any]]):
            Arguments for each process
        process_args_static (Iterable[Any] | None, optional):
            Static arguments to pass to each process. Defaults to None.
        deepcopy_static_args (Iterable[Any] | None, optional):
            Arguments that should be deep-copied for each process. Defaults to None.
        process_args_len (int | None, optional):
            Length of process_args. Defaults to None.

    Returns:
        list[Any]: Results from the process_function executions
    """
    process_args_len = get_len_with_default(process_args, process_args_len)
    process_args = generate_process_args(
        process_function=process_function,
        process_args=process_args,
        process_args_static=process_args_static,
        deepcopy_static_args=deepcopy_static_args,
    )
    max_workers = find_max_pools(threads=threading, process_args_len=process_args_len)
    pool_executor = (
        ThreadPoolExecutor(max_workers=max_workers)
        if threading
        else Pool(processes=max_workers)
    )
    with pool_executor as pool:
        map_func: Callable[[Callable[..., Any], Iterable[Any]], Any]

        if process_args_len == 1:
            map_func = map
        elif threading:
            pool = cast("ThreadPoolExecutor", pool)
            map_func = partial(imap_unordered, pool)
        else:
            pool = cast("Pool", pool)
            map_func = pool.imap_unordered

        results = map_func(get_order_and_func_result, process_args)

        return get_multiprocess_results_with_tqdm(
            results=results,
            process_func=process_function,
            process_args_len=process_args_len,
            threads=threading,
        )
