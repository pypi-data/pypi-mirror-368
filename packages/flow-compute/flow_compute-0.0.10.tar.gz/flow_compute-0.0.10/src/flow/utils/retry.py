"""Simple retry utilities for Flow SDK."""

import logging
import time
from enum import Enum
from typing import Callable, Optional, Tuple, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryableErrorType(Enum):
    """Types of errors that can be retried."""

    NETWORK = "network"
    TIMEOUT = "timeout"
    SERVER = "server"
    RATE_LIMIT = "rate_limit"
    CONNECTION = "connection"


class ExponentialBackoffPolicy:
    """Exponential backoff retry policy."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        base_delay: Optional[float] = None,  # Alias for initial_delay
        retry_on: Optional[list] = None,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = base_delay or initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on = retry_on or []

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


def with_retry(
    policy: Optional[ExponentialBackoffPolicy] = None,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to add retry logic to a function.

    Can be used as:
    - @with_retry() - uses default policy
    - @with_retry(policy=my_policy) - uses custom policy
    """
    if policy is None:
        policy = ExponentialBackoffPolicy()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(1, policy.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < policy.max_attempts:
                        delay = policy.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt} failed: {e}. Retrying in {delay:.1f} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"All {policy.max_attempts} attempts failed")

            raise last_exception

        return wrapper

    return decorator


def retry_on_exception(
    exception_type: Type[Exception],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Create a retry decorator for specific exception types.

    Args:
        exception_type: Exception type to retry on
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for exponential delay

    Returns:
        Decorator function that adds retry logic
    """
    policy = ExponentialBackoffPolicy(
        max_attempts=max_attempts,
        initial_delay=delay,
        exponential_base=backoff,
    )

    return with_retry(policy=policy, retryable_exceptions=(exception_type,))
