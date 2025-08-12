"""Retry utilities with exponential backoff.

Following Dean/Ghemawat's approach to distributed systems reliability.
"""

import logging
import random
import time
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from flow.errors import NetworkError, TimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retriable_exceptions: tuple[type[Exception], ...] = (NetworkError, TimeoutError),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying operations with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd
        retriable_exceptions: Exceptions that trigger retry

    Example:
        @with_retry(max_attempts=5)
        def flaky_network_call():
            return requests.get("https://api.example.com")
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retriable_exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base**attempt), max_delay)

                    # Add jitter to prevent synchronized retries
                    if jitter:
                        delay *= 0.5 + random.random()

                    logger.debug(f"Retry {attempt + 1}/{max_attempts} after {delay:.1f}s: {e}")
                    time.sleep(delay)

            # Should never reach here
            raise last_exception

        return wrapper

    return decorator


class RetryableOperation:
    """Context manager for retryable operations with detailed control.

    Example:
        with RetryableOperation(max_attempts=5) as retry:
            while retry.should_retry():
                try:
                    result = do_something()
                    retry.success()
                    return result
                except NetworkError as e:
                    retry.failure(e)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

        self.attempt = 0
        self.succeeded = False
        self.last_exception = None
        self.total_delay = 0.0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.succeeded and self.last_exception:
            raise self.last_exception

    def should_retry(self) -> bool:
        """Check if we should attempt the operation."""
        return self.attempt < self.max_attempts and not self.succeeded

    def success(self):
        """Mark operation as successful."""
        self.succeeded = True

    def failure(self, exception: Exception):
        """Record failure and sleep if retrying."""
        self.last_exception = exception
        self.attempt += 1

        if self.attempt < self.max_attempts:
            delay = self._calculate_delay()
            logger.debug(
                f"Retry {self.attempt}/{self.max_attempts} after {delay:.1f}s: {exception}"
            )
            time.sleep(delay)
            self.total_delay += delay

    def _calculate_delay(self) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = min(
            self.initial_delay * (self.exponential_base ** (self.attempt - 1)), self.max_delay
        )

        if self.jitter:
            delay *= 0.5 + random.random()

        return delay


def retry_on_network_error(func: Callable[..., T]) -> Callable[..., T]:
    """Simple retry decorator for network operations."""
    return with_retry(
        max_attempts=3,
        initial_delay=1.0,
        retriable_exceptions=(NetworkError, ConnectionError, TimeoutError),
    )(func)


def retry_with_logging(
    logger, level: str = "warning"
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry decorator that logs attempts."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            with RetryableOperation() as retry:
                while retry.should_retry():
                    try:
                        result = func(*args, **kwargs)
                        retry.success()

                        if retry.attempt > 1:
                            getattr(logger, level)(
                                f"{func.__name__} succeeded after {retry.attempt} attempts "
                                f"({retry.total_delay:.1f}s total delay)"
                            )

                        return result
                    except Exception as e:
                        retry.failure(e)

                        if retry.attempt < retry.max_attempts:
                            getattr(logger, level)(
                                f"{func.__name__} attempt {retry.attempt} failed: {e}"
                            )
                        else:
                            logger.error(
                                f"{func.__name__} failed after {retry.attempt} attempts: {e}"
                            )
                            raise

        return wrapper

    return decorator
