import atexit
import os
import tempfile
import time
from collections import defaultdict
from collections.abc import Callable, Iterator
from enum import Enum
from functools import wraps
from typing import Any, TextIO

try:
    from loky import as_completed, get_reusable_executor
except ImportError:
    as_completed = None
    get_reusable_executor = None

import numpy as np

# Global variable to hold the reference to the log file
_log_file: TextIO | None = None
_logger: Any = None

# Dictionary to track function statistics
_function_stats: dict[str, list[float]] = defaultdict(list)

# Dictionary to track loop iteration statistics
_loop_stats: dict[Any, dict[str, Any]] = defaultdict(lambda: {"times": [], "iterations": 0})

_checkpoint_stats: dict[str, dict[str, Any]] = defaultdict(
    lambda: {"times": [], "last_checkpoint": None}
)


class Color(Enum):
    """ANSI escape codes for colors."""

    RESET = "\033[0m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    PURPLE = "\033[95m"
    DULL = "\033[37m"  # Dull white/gray color
    ORANGE = "\033[38;5;214m"


def log_message_with_color(message: str, color: Color) -> None:
    """Logs a simple message to the temp log file with a specific color."""
    colored_message = f"{color.value}{message}{Color.RESET.value}"
    _log_raw_message(colored_message)


def setup_log_file_and_logger(
    path: str | None = None, logger: Any = None, setup_independent_logging: bool = False
) -> tuple[TextIO | None, Any]:
    """Sets up the log file if it hasn't been set up already and prints its location."""
    global _log_file
    global _logger
    if setup_independent_logging:
        if _log_file is None:
            if path is None:
                _log_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".log")
            else:
                _log_file = open(path, "w+", encoding="utf-8")

            if _log_file is not None:
                print(f"{Color.CYAN.value}Log file created at: {_log_file.name}{Color.RESET.value}")
            atexit.register(close_log)

    if _logger is None:
        _logger = logger

    if _log_file is None and _logger is None:
        print(
            f"{Color.RED.value}No log file or logger set up!, run setup_log_file_and_logger first with setup_independent_logging or logger arguments.{Color.RESET.value}"
        )

    return _log_file, _logger


def _log_raw_message(message: str, end: str = "\n") -> None:
    log_file, logger = setup_log_file_and_logger()
    if log_file is not None:
        log_file.write(f"{message}{end}")
        log_file.flush()

    if logger is not None:
        logger.info(message)


def log_message(message: str) -> None:
    """Logs a simple message to the temp log file."""
    log_message_with_color(message, Color.BLUE)


def log_list_elements(elements: list[Any]) -> None:
    """Logs all elements in a list to the temp log file."""
    log_message_with_color("Logging list elements:", Color.GREEN)
    for element in elements:
        log_message_with_color(f"- {element}", Color.BLUE)


def log_timed_loop(
    iterable: Any,
    ignore_instant_iterations: bool = True,
    threshold: float = 0.001,
    loop_id: Any | None = None,
    loop_name: str | None = None,
    yield_statistics: bool = False,
) -> Iterator[Any]:
    """Logs the time taken for each iteration in a loop, calculates ETA if possible, and yields each element."""

    total_items = len(iterable) if hasattr(iterable, "__len__") else None
    start_time = time.time()
    loop_identifier = loop_id or id(iterable)  # Unique identifier for the loop

    loop_name_str = f"({loop_name}) " if loop_name else ""

    running_statistics = {
        "loop_id": loop_identifier,
        "loop_name": loop_name,
        "total_items": total_items,
        "start_time": start_time,
        "instant_items": 0,
        "completed_items": 0,
        "current_iteration": 0,
        "total_elapsed_time": 0.0,
        "average_time_per_item": None,
        "remaining_items": total_items,
        "eta": None,
    }

    for i, item in enumerate(iterable):
        running_statistics["current_iteration"] = i

        iter_start_time = time.time()
        _log_raw_message(
            f"{Color.BLUE.value}{loop_name_str}Iteration {i + 1}: Started processing {Color.GRAY.value}{item}{Color.RESET.value}"
        )

        if yield_statistics:
            yield item, running_statistics
        else:
            yield item  # Yield the current item for the loop to use

        iter_end_time = time.time()
        iter_elapsed_time = iter_end_time - iter_start_time
        _log_raw_message(
            f"{Color.GREEN.value}{loop_name_str}Iteration {i + 1}: Finished processing {Color.GRAY.value}{item} {Color.YELLOW.value}in {iter_elapsed_time:.2f} seconds{Color.RESET.value}"
        )

        if ignore_instant_iterations and iter_elapsed_time < threshold:
            running_statistics["instant_items"] += 1
            continue

        # Store iteration time
        _loop_stats[loop_identifier]["times"].append(iter_elapsed_time)
        _loop_stats[loop_identifier]["iterations"] += 1

        # Calculate and log ETA if the total length is known
        if total_items is not None:
            completed_items_count = (
                i + 1 - (running_statistics["instant_items"] if ignore_instant_iterations else 0)
            )
            total_elapsed_time = iter_end_time - start_time
            average_time_per_item = (
                total_elapsed_time / completed_items_count if completed_items_count > 0 else 0
            )
            remaining_items = (
                total_items - completed_items_count - running_statistics["instant_items"]
            )
            eta = remaining_items * average_time_per_item

            running_statistics["completed_items"] = completed_items_count
            running_statistics["total_elapsed_time"] = total_elapsed_time
            running_statistics["average_time_per_item"] = average_time_per_item
            running_statistics["remaining_items"] = remaining_items
            running_statistics["eta"] = eta
            _log_raw_message(
                f"{Color.YELLOW.value}{loop_name_str}Iteration {i + 1}: Estimated time remaining: {Color.YELLOW.value}{eta:.2f} seconds ({remaining_items} iterations remaining, Average time per item: {average_time_per_item:.2f} [s]){Color.RESET.value}"
            )

    # Log loop statistics
    times_list = _loop_stats[loop_identifier]["times"]
    if times_list:
        average_iter_time = np.mean(times_list)
        iterations_per_sec = 1 / average_iter_time if average_iter_time > 0 else float("inf")
        total_iterations = _loop_stats[loop_identifier]["iterations"]
        _log_raw_message(
            f"{Color.DULL.value}{loop_name_str}Loop ID {loop_identifier}: Average time per iteration: {average_iter_time:.2f} seconds ({iterations_per_sec:.2f} iterations per second). Total iterations: {total_iterations}.{Color.RESET.value}"
        )


def log_timed_function(
    ignore_instant_returns: bool, threshold: float = 0.001
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory that logs the timing of a function call and tracks statistics.
    - ignore_instant_returns: If True, ignores instant returns for counting time.
    - threshold: The time threshold below which the return is considered instant (default 1 millisecond).
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _log_raw_message(
                f"{Color.BLUE.value}Function {func.__name__} started with args: {Color.GRAY.value}{args}{Color.CYAN.value} and kwargs: {Color.GRAY.value}{kwargs}{Color.RESET.value}"
            )

            start_time = time.time()
            try:
                result = func(*args, **kwargs)  # Run the actual function with its arguments
            except Exception as e:
                elapsed_time = time.time() - start_time

                # Store function execution time even for exceptions
                _function_stats[func.__name__].append(elapsed_time)

                _log_raw_message(
                    f"{Color.RED.value}Function {func.__name__} failed with exception {Color.YELLOW.value}in {elapsed_time:.2f} seconds: {str(e)}{Color.RESET.value}"
                )

                # Calculate statistics
                avg_time = np.mean(_function_stats[func.__name__])
                std_dev_time = (
                    np.std(_function_stats[func.__name__])
                    if len(_function_stats[func.__name__]) > 1
                    else 0.0
                )
                num_calls = len(_function_stats[func.__name__])
                _log_raw_message(
                    f"{Color.DULL.value}Function {func.__name__}: Avg time: {avg_time:.2f} seconds, Std dev: {std_dev_time:.2f}, Calls: {num_calls}{Color.RESET.value}"
                )

                raise  # Re-raise the exception

            elapsed_time = time.time() - start_time

            # If ignoring instant returns and the time is below the threshold, skip logging
            if ignore_instant_returns and elapsed_time < threshold:
                return result

            # Store function execution time
            _function_stats[func.__name__].append(elapsed_time)

            _log_raw_message(
                f"{Color.GREEN.value}Function {func.__name__} finished {Color.YELLOW.value}in {elapsed_time:.2f} seconds{Color.RESET.value}"
            )

            # Calculate statistics
            avg_time = np.mean(_function_stats[func.__name__])
            std_dev_time = (
                np.std(_function_stats[func.__name__])
                if len(_function_stats[func.__name__]) > 1
                else 0.0
            )
            num_calls = len(_function_stats[func.__name__])
            _log_raw_message(
                f"{Color.DULL.value}Function {func.__name__}: Avg time: {avg_time:.2f} seconds, Std dev: {std_dev_time:.2f}, Calls: {num_calls}{Color.RESET.value}"
            )

            return result

        return wrapper

    return decorator


def log_checkpoint(checkpoint_id: str, message_on_reach: str | None = None) -> None:
    """
    Logs a checkpoint with a unique identifier, tracks the time since the last checkpoint,
    and records relevant statistics for analysis.

    Parameters:
    - checkpoint_id (str): Unique identifier for the checkpoint.
    - message_on_reach (str, optional): Custom message to log each time the checkpoint is reached.
    """
    if checkpoint_id is None:
        raise TypeError("checkpoint_id cannot be None")

    log_file, _ = setup_log_file_and_logger()
    current_time = time.time()

    # Log custom message if provided
    if message_on_reach:
        _log_raw_message(
            f"{Color.CYAN.value}Checkpoint {checkpoint_id}: {message_on_reach}{Color.RESET.value}"
        )

    # Get the last checkpoint time if it exists
    last_time = _checkpoint_stats[checkpoint_id]["last_checkpoint"]
    if last_time is not None:
        # Calculate elapsed time since the last checkpoint
        elapsed_time = current_time - last_time
        times_list = _checkpoint_stats[checkpoint_id]["times"]
        if isinstance(times_list, list):
            times_list.append(elapsed_time)
        _log_raw_message(
            f"{Color.PURPLE.value}Checkpoint {checkpoint_id}: Elapsed time since last checkpoint: {elapsed_time:.2f} seconds{Color.RESET.value}"
        )
    else:
        _log_raw_message(
            f"{Color.PURPLE.value}Checkpoint {checkpoint_id}: Initial checkpoint recorded{Color.RESET.value}"
        )

    # Update the last checkpoint time to the current time
    _checkpoint_stats[checkpoint_id]["last_checkpoint"] = current_time

    # Calculate average time between checkpoints for this ID
    times_list = _checkpoint_stats[checkpoint_id]["times"]
    if times_list and isinstance(times_list, list):
        avg_time = np.mean(times_list)
        std_dev_time = np.std(times_list) if len(times_list) > 1 else 0.0
        num_checks = len(times_list)
        _log_raw_message(
            f"{Color.DULL.value}Checkpoint {checkpoint_id}: Avg time: {avg_time:.2f} seconds, Std dev: {std_dev_time:.2f}, Total checks: {num_checks}{Color.RESET.value}"
        )


def timed_func(func: Callable[..., Any], item: Any, **kwargs: Any) -> tuple[Any, float, Any]:
    """
    Wraps the user function to measure execution time.
    """
    iter_start_time = time.time()
    result = func(item, **kwargs)
    iter_elapsed_time = time.time() - iter_start_time
    return result, iter_elapsed_time, item


def log_timed_parallel_loop(
    iterable: Any,
    func: Callable[..., Any],
    func_kwargs: dict[str, Any],
    n_jobs: int = 1,
    loop_name: str | None = None,
    ignore_instant_iterations: bool = True,
    threshold: float = 0.001,
    raise_exceptions: bool = False,
) -> tuple[list[Any], list[dict[str, Any]]]:
    """
    Runs a function over an iterable in parallel, logs timing statistics.

    Parameters:
    - iterable: The iterable to process.
    - func: The function to apply to each item in the iterable.
    - n_jobs: Number of parallel jobs to run.
    - loop_name: Name of the loop for logging purposes.
    - ignore_instant_iterations: Whether to ignore iterations that take less than the threshold time.
    - threshold: The time threshold to consider an iteration as 'instant'.
    - **kwargs: Additional keyword arguments to pass to func.
    """
    total_items = len(iterable) if hasattr(iterable, "__len__") else None
    loop_name_str = f"({loop_name}) " if loop_name else ""
    start_time = time.time()
    instant_items = 0
    completed_items = 0
    exception_items = 0

    # Prepare for collecting timings and results
    elapsed_times = []
    results = []
    errors = []

    if as_completed is None or get_reusable_executor is None:
        raise ImportError(
            "loky is required for parallel processing. Install it with: pip install loky"
        )

    with get_reusable_executor(max_workers=n_jobs) as executor:
        # Submit all tasks
        futures = {
            executor.submit(timed_func, func, item, **func_kwargs): item for item in iterable
        }

        for future in as_completed(futures):
            item = futures[future]
            try:
                result, iter_elapsed_time, item = future.result()

            except KeyboardInterrupt:
                raise

            except Exception as exc:
                _log_raw_message(
                    f"{Color.RED.value}{loop_name_str}Exception for {item}: {exc}{Color.RESET.value}"
                )
                if raise_exceptions:
                    # Stop the loop if an exception occurs
                    for f in futures:
                        f.cancel()
                    # Optionally shut down the executor
                    executor.shutdown(wait=False)
                    raise

                else:
                    errors.append(
                        {
                            "error": exc,
                            "item": item,
                            "func_kwargs": func_kwargs,
                        }
                    )

                exception_items += 1
                continue

            if ignore_instant_iterations and iter_elapsed_time < threshold:
                instant_items += 1
                continue

            completed_items += 1
            elapsed_times.append(iter_elapsed_time)
            results.append(result)

            # Log the completion of the task
            _log_raw_message(
                f"{Color.GREEN.value}{loop_name_str}Finished processing {Color.GRAY.value}{item} {Color.YELLOW.value}in {iter_elapsed_time:.2f} seconds{Color.RESET.value}"
            )

            # Calculate and log ETA if the total length is known
            if total_items is not None and completed_items > 0:
                total_elapsed_time = time.time() - start_time
                average_time_per_item = total_elapsed_time / completed_items
                remaining_items = total_items - completed_items - instant_items - exception_items
                eta = remaining_items * average_time_per_item
                _log_raw_message(
                    f"{Color.YELLOW.value}{loop_name_str}Estimated time remaining: {eta:.2f} seconds ({remaining_items} items remaining, Average time per item: {average_time_per_item:.2f} s){Color.RESET.value}"
                )

    # Log loop statistics
    if elapsed_times:
        average_iter_time = np.mean(elapsed_times)
        iterations_per_sec = 1 / average_iter_time if average_iter_time > 0 else float("inf")
    else:
        average_iter_time = 0
        iterations_per_sec = float("inf")
    total_iterations = len(elapsed_times)
    _log_raw_message(
        f"{Color.DULL.value}{loop_name_str}Parallel loop completed: Average time per iteration: {average_iter_time:.2f} seconds ({iterations_per_sec:.2f} iterations per second). Total iterations: {total_iterations}.{Color.RESET.value}"
    )

    return results, errors


def close_log() -> None:
    """Closes the log file if it's open."""
    global _log_file
    if _log_file:
        _log_file.close()
        _log_file = None


def read_log() -> str:
    """Reads and returns the content of the log file."""
    log_file, _ = setup_log_file_and_logger()
    if log_file is None:
        return ""
    with open(log_file.name, encoding="utf-8") as file:
        return file.read()


def cleanup_log() -> None:
    """Cleans up (removes) the temp log file."""
    global _log_file
    if _log_file:
        try:
            os.remove(_log_file.name)
        except FileNotFoundError:
            pass  # File already removed, which is fine
        _log_file = None
