"""Tools related to timers and performance measurement."""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from time import perf_counter
from typing import TYPE_CHECKING, Any, Literal, Self

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Generator


def create_timer(**defaults) -> Callable:
    """A way to set defaults for a frequently used timer decorator."""

    def timer_decorator(func: Callable) -> Any:
        """Decorator to time the execution of a function."""

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            defaults["name"] = func.__name__
            with timer(**defaults):
                return func(*args, **kwargs)

        return wrapper

    return timer_decorator


def create_async_timer(**defaults) -> Callable:
    """Set defaults for an async timer decorator."""

    def timer_decorator(func: Callable) -> Any:
        """Decorator to time the execution of an async function."""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            """Async wrapper to time the execution of an async function."""
            defaults["name"] = func.__name__
            async with async_timer(**defaults):
                return await func(*args, **kwargs)

        return wrapper

    return timer_decorator


@contextmanager
def timer(**kwargs) -> Generator[TimerData]:
    """Context manager to time the execution of a block of code."""
    data: TimerData = kwargs.get("data") or TimerData(**kwargs)
    data.start()
    try:
        yield data
    finally:
        data.stop()


@asynccontextmanager
async def async_timer(**kwargs) -> AsyncGenerator[TimerData]:
    """Async context manager to time the execution of an async block of code."""
    data: TimerData = kwargs.get("data") or TimerData(**kwargs)
    data.start()
    try:
        yield data
    finally:
        data.stop()


TimeType = Literal["seconds", "milliseconds"]


class TimerData:
    """Container for timing information."""

    def __init__(
        self,
        name: str,
        console: bool = False,
        callback: Callable | None = None,
        start: bool = False,
        time_type: TimeType = "seconds",
        **kwargs,
    ) -> None:
        """Initialize the timer data.

        Args:
            name (str): The name of the timer.
            console (bool): Indicates whether to log to the console.
            callback (Callable | None): A callable to invoke when the timer stops.
            **kwargs: Optional keyword arguments.
                ``print_func`` is the function used to print logs.
        """
        self.name: str = name
        self.console: bool = console
        self.callback: Callable | None = callback
        self.print_func: Callable = kwargs.get("print_func", print)
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.time_type: TimeType = time_type
        self._raw_elapsed_time: float = 0.0
        if start:
            self.start()

    @property
    def value(self) -> float:
        """Return the correct property based on the time type and if the timer has stopped."""
        return self.milliseconds if self.time_type == "milliseconds" else self.seconds

    @property
    def value_to_string(self) -> str:
        """Return the elapsed time as a formatted string."""
        string: str = f"{self.value:.6f} {self.time_type}"
        if not self.started:
            string = f"<{self.name}> Timer not started"
        return string

    @property
    def milliseconds(self) -> float:
        """Return the current elapsed time in milliseconds."""
        return self.duration() * 1000

    @property
    def seconds(self) -> float:
        """Return the current elapsed time in seconds."""
        return self.duration()

    @property
    def started(self) -> bool:
        """Check if the timer has been started."""
        return self.start_time > 0.0

    @property
    def stopped(self) -> bool:
        """Check if the timer has been stopped."""
        return self.end_time > 0.0

    def duration(self) -> float:
        """Calculate the elapsed time since the timer was started."""
        if not self.started:
            return 0.0
        if self.stopped:
            return self._raw_elapsed_time
        return perf_counter() - self.start_time

    def print_current_time(self) -> Self:
        """Print the current elapsed time without stopping the timer."""
        self.print_func(f"<{self.name}> Elapsed time: {self.value_to_string}")
        return self

    def start(self) -> Self:
        """Record the starting time using ``perf_counter``."""
        self.start_time = perf_counter()
        return self

    def send_callback(self) -> Self:
        """Invoke the callback if one was provided."""
        if self.callback is not None:
            self.callback(self)
        return self

    def stop(self) -> Self:
        """Stop the timer and optionally log the result."""
        self.end_time = perf_counter()
        self._raw_elapsed_time = self.end_time - self.start_time
        if self.callback:
            self.send_callback()
        if self.console:
            self.print_current_time()
        return self

    def reset(self) -> Self:
        """Reset the timer to its initial state."""
        self.start_time = 0.0
        self.end_time = 0.0
        self._raw_elapsed_time = 0.0
        return self


__all__ = ["TimerData", "timer"]
