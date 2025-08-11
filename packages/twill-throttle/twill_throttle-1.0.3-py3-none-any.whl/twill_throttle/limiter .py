import time
import threading
import asyncio
from collections import deque
from functools import wraps
from typing import Callable


class FuncPerMin:
    """
    Decorator that limits the number of times a function can be called per minute.
    This implementation is per-instance, meaning each decorated function instance
    has its own call counter and time tracking.

    Attributes:
        max_calls (int): Maximum number of allowed calls per minute.
        call_count (int): Current number of calls in the ongoing 60-second period.
        start_time (float): Timestamp (in seconds) of the first call in the current period.
    """

    def __init__(self, max_calls_per_minute: int):
        """
        Initialize the FuncPerMin instance.

        Args:
            max_calls_per_minute (int): Maximum number of allowed calls per minute.
        """
        self.max_calls = max_calls_per_minute
        self.call_count = 0
        self.start_time = time.perf_counter()

    def __call__(self, func: Callable):
        """
        Wrap the target function to enforce the rate limit.

        Args:
            func (Callable): The function to be decorated.

        Returns:
            Callable: The wrapped function with rate limiting applied.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapped function that applies the per-minute rate limit.
            If the limit is reached, waits until the next minute starts.
            """
            elapsed = time.perf_counter() - self.start_time

            # Reset if more than a minute passed
            if elapsed > 60:
                self.call_count = 0
                self.start_time = time.perf_counter()

            # Execute if under the limit
            if self.call_count < self.max_calls:
                self.call_count += 1
                return func(*args, **kwargs)

            # Limit reached — wait for the remaining time
            wait_time = 60 - elapsed
            print(f"[FuncPerMin] Limit of {self.max_calls}/min reached. Waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)

            # Reset and execute
            self.call_count = 1
            self.start_time = time.perf_counter()
            return func(*args, **kwargs)

        return wrapper


class SharedRateLimiter:
    """
    Decorator that limits the number of calls shared across multiple functions per minute.
    This version supports both synchronous and asynchronous functions.
    Uses a sliding window to track call times and ensure accuracy.

    Attributes:
        max_calls (int): Maximum number of allowed calls per minute.
        call_times (deque): Timestamps of previous calls, stored for rate calculation.
        lock (threading.Lock): Lock for thread-safe operations in synchronous functions.
        async_lock (asyncio.Lock): Lock for coroutine-safe operations in asynchronous functions.
    """

    def __init__(self, max_calls_per_minute: int):
        """
        Initialize the SharedRateLimiter instance.

        Args:
            max_calls_per_minute (int): Maximum number of allowed calls per minute.
        """
        self.max_calls = max_calls_per_minute
        self.call_times = deque()
        self.lock = threading.Lock()
        self.async_lock = asyncio.Lock()

    def _clean_old_calls(self):
        """
        Remove timestamps older than one minute from the call history.
        """
        one_minute_ago = time.time() - 60
        while self.call_times and self.call_times[0] <= one_minute_ago:
            self.call_times.popleft()

    def _can_call(self) -> bool:
        """
        Check if a new call can be made under the rate limit.

        Returns:
            bool: True if a call is allowed, False otherwise.
        """
        self._clean_old_calls()
        return len(self.call_times) < self.max_calls

    def _wait_time(self) -> float:
        """
        Calculate the time (in seconds) that must pass before another call is allowed.

        Returns:
            float: Number of seconds to wait before the next allowed call.
        """
        self._clean_old_calls()
        if len(self.call_times) < self.max_calls:
            return 0
        return 60 - (time.time() - self.call_times[0])

    def __call__(self, func: Callable):
        """
        Wrap the target function to enforce the shared rate limit.

        Args:
            func (Callable): The function to be decorated (sync or async).

        Returns:
            Callable: The wrapped function with shared rate limiting applied.
        """
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                """
                Asynchronous wrapped function that applies the shared rate limit.
                Waits if the limit is reached.
                """
                while True:
                    async with self.async_lock:
                        with self.lock:
                            if self._can_call():
                                self.call_times.append(time.time())
                                break
                    wait = self._wait_time()
                    if wait > 0:
                        await asyncio.sleep(wait)
                return await func(*args, **kwargs)
            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                """
                Synchronous wrapped function that applies the shared rate limit.
                Waits if the limit is reached.
                """
                while True:
                    with self.lock:
                        if self._can_call():
                            self.call_times.append(time.time())
                            break
                    wait = self._wait_time()
                    if wait > 0:
                        time.sleep(wait)
                return func(*args, **kwargs)
            return sync_wrapper





def main_test():
    # Example 1: FuncPerMin - Limits calls per minute for a specific function
    @FuncPerMin(max_calls_per_minute=3)
    def greet(name):
        """
        Example function that greets the given name.
        This function can only be called 3 times per minute.
        """
        print(f"Hello, {name}!")

    print("=== FuncPerMin Example ===")
    for i in range(5):
        greet(f"User {i + 1}")  # The last two calls will wait until the next minute window

    # Example 2: SharedRateLimiter - Limits calls across multiple functions (shared limit)
    shared_limiter = SharedRateLimiter(max_calls_per_minute=4)

    @shared_limiter
    def process_data(data):
        """
        Example synchronous function that processes data.
        Shared rate limit: All functions using 'shared_limiter' share the same call limit.
        """
        print(f"Processing data: {data}")

    @shared_limiter
    async def async_task(task_id):
        """
        Example asynchronous function that simulates a network or I/O task.
        Shared rate limit: All async and sync functions using 'shared_limiter' share the same limit.
        """
        print(f"Starting async task {task_id}...")
        await asyncio.sleep(0.5)
        print(f"Finished async task {task_id}.")

    async def main():
        print("\n=== SharedRateLimiter Example (Mixed sync/async) ===")
        # Call synchronous function
        process_data("File1")
        process_data("File2")

        # Call asynchronous function
        await asyncio.gather(
            async_task(1),
            async_task(2),
            async_task(3),
        )

    # Run async example
    asyncio.run(main())




if __name__ == "__main__":
    main_test()
