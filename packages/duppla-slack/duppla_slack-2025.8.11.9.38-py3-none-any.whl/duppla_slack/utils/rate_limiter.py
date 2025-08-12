import threading as t
import time
from collections.abc import Callable
from functools import wraps

import typing_extensions as ty

TIER_1 = (1, 60)
TIER_2 = (20, 60)
TIER_3 = (50, 60)
TIER_4 = (100, 60)
POST_MSG = (1, 1)
INCOMING_WEBHOOK = (1, 1)
EVENTS = (30_000, 60 * 60)
WORKFLOW_EVENT_TRIGGER = (10_000, 60 * 60)
WORKFLOW_WEBHOOK_TRIGGER = (10, 60)

_P = ty.ParamSpec("_P")
_R = ty.TypeVar("_R")


class RateLimiter:
    """Handles rate limiting per method."""

    def __init__(self, calls: int, period: float):
        """
        Args:
            calls (int): Allowed requests per period.
            period (int): Time period (seconds).
        """
        self.calls: int = calls
        self.period: float = period
        self.lock: t.Semaphore = t.Semaphore(calls)
        self.request_times: list[float] = []
        self.lock_time: t.Lock = t.Lock()

    def _clean_old_requests(self):
        """Removes expired request timestamps."""
        now = time.monotonic()
        with self.lock_time:
            self.request_times = [
                t for t in self.request_times if now - t < self.period
            ]

    def acquire(self):
        """Waits for a free slot before allowing execution."""
        while True:
            self._clean_old_requests()
            if len(self.request_times) < self.calls:
                with self.lock:
                    # Add new request timestamp
                    self.request_times.append(time.monotonic())
                return
            sleep_time = self.request_times[0] + self.period - time.monotonic()
            if sleep_time > 0:
                time.sleep(sleep_time)


def rate_limited(arg: tuple[int, float]):
    """
    Decorator to enforce rate limiting with threading.

    Args:
        calls (int): Allowed requests per period.
        period (float): Time period (seconds).
    """
    calls, period = arg
    limiter = RateLimiter(calls, period)

    def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
        @wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            # To store the function return value
            result_container: list[_R] = []
            # To store exceptions if they occur
            exception_container: list[Exception] = []
            # To signal when execution is done
            event = t.Event()

            def run():
                try:
                    result_container.append(func(*args, **kwargs))
                except Exception as e:
                    exception_container.append(e)
                finally:
                    event.set()  # Signal that the function has finished

            limiter.acquire()  # Enforce rate limit
            thread = t.Thread(target=run)
            thread.start()
            event.wait()  # Wait for the thread to finish

            if exception_container:
                raise exception_container[0]  # Re-raise any exception that occurred

            return result_container[0]  # Return the function result

        return wrapper

    return decorator
