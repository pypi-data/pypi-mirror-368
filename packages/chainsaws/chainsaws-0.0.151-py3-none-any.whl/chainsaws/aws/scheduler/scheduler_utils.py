"""Utility module for scheduling tasks using cron expressions.

This module provides utilities for scheduling and managing tasks using cron expressions
within a ThreadPool environment. It includes a context manager for task scheduling
and a thread pool manager implemented as a singleton.

Example:
    ```python
    from chainsaws.aws.scheduler import ScheduledTask, join

    # Schedule tasks to run at specific times
    with ScheduledTask('0 0 * * *') as do:
        do(daily_task)
        do(another_task)

    # Wait for all tasks to complete
    join()
    ```
"""

import traceback
import datetime
import logging
from typing import Any, Callable, Optional, TypeVar, List
from types import TracebackType
from concurrent.futures import ThreadPoolExecutor, Future
from croniter import croniter

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')


class SchedulerException(Exception):
    """Custom exception for scheduler-related errors."""
    pass


class ThreadPoolManager:
    """A singleton class managing thread pool execution.

    This class implements the Singleton pattern to manage a shared thread pool
    across the application. It handles task submission and result collection.

    Attributes:
        _instance: Singleton instance of ThreadPoolManager.
        _pool: ThreadPoolExecutor instance.
        _futures: List of Future objects for submitted tasks.
    """
    _instance: Optional['ThreadPoolManager'] = None
    _pool: Optional[ThreadPoolExecutor] = None
    _futures: List[Future] = []

    def __new__(cls) -> 'ThreadPoolManager':
        """Creates or returns the singleton instance of ThreadPoolManager.

        Returns:
            ThreadPoolManager: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._pool = ThreadPoolExecutor(max_workers=8)
            cls._futures = []
        return cls._instance

    def submit(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> Future:
        """Submits a task to the thread pool.

        Args:
            func: The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Future: A Future object representing the task.

        Raises:
            SchedulerException: If the thread pool is not initialized.
        """
        if not self._pool:
            raise SchedulerException("Thread pool is not initialized")
        future = self._pool.submit(func, *args, **kwargs)
        self._futures.append(future)
        return future

    def join(self) -> None:
        """Waits for all submitted tasks to complete.

        This method blocks until all submitted tasks are finished and handles
        any exceptions that occurred during task execution.

        Raises:
            SchedulerException: If any task fails during execution.
        """
        for future in self._futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Task execution failed: {str(e)}")
                raise SchedulerException(f"Task execution failed: {str(e)}")
        self._futures.clear()

    @property
    def active_tasks(self) -> int:
        """Returns the number of active tasks.

        Returns:
            int: Number of tasks currently being executed.
        """
        return len([f for f in self._futures if not f.done()])


def join() -> None:
    """Waits for all scheduled tasks to complete.

    This is a convenience function that delegates to ThreadPoolManager's join method.
    """
    ThreadPoolManager().join()


class ScheduledTask:
    """A context manager for scheduling tasks using cron expressions.

    This class provides a context manager interface for scheduling and executing
    tasks based on cron expressions.

    Attributes:
        cron_expression: The cron expression defining the schedule.
        _pool_manager: Instance of ThreadPoolManager for task execution.
    """

    def __init__(self, cron_expression: str):
        """Initializes a new ScheduledTask.

        Args:
            cron_expression: A cron expression defining when tasks should run.

        Raises:
            ValueError: If the cron expression is invalid.
        """
        try:
            croniter(cron_expression)
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {str(e)}")

        self.cron_expression = cron_expression
        self._pool_manager = ThreadPoolManager()

    def _should_execute(self) -> bool:
        """Determines if tasks should be executed based on the current time.

        Returns:
            bool: True if the schedule matches the current time, False otherwise.
        """
        now = datetime.datetime.now() + datetime.timedelta(seconds=5)
        iter = croniter(self.cron_expression, now)
        prev_schedule = iter.get_prev(datetime.datetime)

        return (prev_schedule.year == now.year and
                prev_schedule.month == now.month and
                prev_schedule.day == now.day and
                prev_schedule.hour == now.hour and
                prev_schedule.minute == now.minute)

    def __enter__(self) -> Callable[..., Future]:
        """Enters the context manager.

        Returns:
            Callable: A function that submits tasks to the thread pool if the
                     schedule matches, or a no-op function otherwise.
        """
        if not self._should_execute():
            def no_op(*args: Any, **kwargs: Any) -> Future:
                future: Future = Future()
                future.set_result(None)
                return future
            return no_op

        def run(*args: Any, **kwargs: Any) -> Future:
            return self._pool_manager.submit(*args, **kwargs)
        return run

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception],
                 exc_tb: Optional[TracebackType]) -> bool:
        """Exits the context manager.

        Args:
            exc_type: Type of the exception that occurred, if any.
            exc_val: The exception instance that occurred, if any.
            exc_tb: The traceback of the exception, if any.

        Returns:
            bool: True if the exception was handled, False otherwise.

        Raises:
            SchedulerException: If an error occurred during task execution.
        """
        if exc_type is not None:
            traceback_str = ''.join(
                traceback.format_exception(exc_type, exc_val, exc_tb))
            logger.error(f"Error during task execution: {traceback_str}")
            raise SchedulerException(
                f"Scheduler error: {str(exc_val)}\n{traceback_str}")
        return True


def generate_schedule_name(
    function_name: str,
    prefix: Optional[str] = None,
) -> str:
    """Generate unique schedule name."""
    name_parts = [part for part in [prefix, function_name] if part]
    return "-".join(name_parts)


if __name__ == '__main__':
    raise RuntimeError('This module cannot be run directly')
