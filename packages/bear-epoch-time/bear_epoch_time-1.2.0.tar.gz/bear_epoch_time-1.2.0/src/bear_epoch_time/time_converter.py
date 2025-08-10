"""A comprehensive time conversion utility class."""

from datetime import timedelta
from enum import StrEnum
import re
from typing import Any

from bear_epoch_time.constants.time_related import (
    MILLISECONDS_IN_SECOND,
    SECONDS_IN_DAY,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE,
    SECONDS_IN_MONTH,
)


class Unit(StrEnum):
    """Enumeration for time units."""

    MONTH = "M"
    MONTH_ALT = "mo"
    DAY = "d"
    HOUR = "h"
    MINUTE = "m"
    SECOND = "s"
    MILLISECOND = "ms"


class TimeConverter:
    """A comprehensive time conversion utility class."""

    @staticmethod
    def time_since(first: int, second: int, unit: str = "d") -> float:
        """Calculate time since another timestamp in the specified unit.

        Args:
            first (int): The first timestamp.
            second (int): The second timestamp.
            unit (str): The unit to return ("M", "d", "h", "m", "s", "ms")

        Returns:
            float: The time difference in the specified unit.
        """
        seconds_diff = int(abs(first - second))

        match unit:
            case "M" | "mo":
                return seconds_diff / SECONDS_IN_MONTH
            case "d":
                return seconds_diff / SECONDS_IN_DAY
            case "h":
                return seconds_diff / SECONDS_IN_HOUR
            case "m":
                return seconds_diff / SECONDS_IN_MINUTE
            case "s":
                return seconds_diff
            case "ms":
                return seconds_diff * MILLISECONDS_IN_SECOND
            case _:
                raise ValueError(f"Invalid unit: {unit}")

    @staticmethod
    def parse_to_seconds(time_str: str) -> float:
        """Parse a time string to seconds."""
        time_parts: list[tuple[str, str]] = re.findall(r"(\d+(?:\.\d+)?)\s*(M|mo|ms|[dhms])", time_str)
        if not time_parts:
            raise ValueError(f"Invalid time format: {time_str}")

        condensed: str = "".join(f"{v}{u}" for v, u in time_parts)
        if condensed != re.sub(r"\s+", "", time_str):
            raise ValueError(f"Invalid time format: {time_str}")

        total_seconds = 0.0
        for value, unit in time_parts:
            try:
                v = float(value)
            except ValueError as e:
                raise ValueError(f"Invalid time value: {value}") from e
            match unit:
                case Unit.MONTH | Unit.MONTH_ALT:
                    total_seconds += v * SECONDS_IN_MONTH
                case Unit.DAY:
                    total_seconds += v * SECONDS_IN_DAY
                case Unit.HOUR:
                    total_seconds += v * SECONDS_IN_HOUR
                case Unit.MINUTE:
                    total_seconds += v * SECONDS_IN_MINUTE
                case Unit.SECOND:
                    total_seconds += v
                case Unit.MILLISECOND:
                    total_seconds += v / MILLISECONDS_IN_SECOND
                case _:
                    raise ValueError(f"Invalid time unit: {unit}")
        return total_seconds

    @staticmethod
    def parse_to_milliseconds(time_str: str) -> float:
        """Parse a time string to milliseconds."""
        return TimeConverter.parse_to_seconds(time_str) * MILLISECONDS_IN_SECOND

    @staticmethod
    def format_seconds(seconds: float, show_subseconds: bool = True) -> str:
        """Format seconds as a human-readable time string."""
        if seconds < 0:
            raise ValueError("Seconds cannot be negative")

        months, remainder = divmod(seconds, SECONDS_IN_MONTH)
        days, remainder = divmod(remainder, SECONDS_IN_DAY)
        hours, remainder = divmod(remainder, SECONDS_IN_HOUR)
        minutes, remainder = divmod(remainder, SECONDS_IN_MINUTE)

        whole_seconds = int(remainder)
        fractional_part: float = remainder - whole_seconds

        time_parts: list[str] = []
        if months > 0:
            time_parts.append(f"{int(months)}M")
        if days > 0:
            time_parts.append(f"{int(days)}d")
        if hours > 0:
            time_parts.append(f"{int(hours)}h")
        if minutes > 0:
            time_parts.append(f"{int(minutes)}m")
        if whole_seconds > 0:
            time_parts.append(f"{whole_seconds}s")

        if show_subseconds and fractional_part > 0:
            milliseconds = int(fractional_part * MILLISECONDS_IN_SECOND)
            if milliseconds > 0:
                time_parts.append(f"{milliseconds}ms")
        return " ".join(time_parts)

    @staticmethod
    def format_milliseconds(milliseconds: float) -> str:
        """Format milliseconds as a human-readable time string."""
        if milliseconds < 0:
            raise ValueError("Milliseconds cannot be negative")
        return TimeConverter.format_seconds(milliseconds / MILLISECONDS_IN_SECOND)

    @staticmethod
    def to_timedelta(seconds: float) -> timedelta:
        """Convert seconds to a timedelta object."""
        if seconds < 0:
            raise ValueError("Seconds cannot be negative")
        return timedelta(seconds=seconds)

    @staticmethod
    def from_timedelta(td: timedelta | Any) -> float:
        """Convert a timedelta object to seconds."""
        if not isinstance(td, timedelta):
            raise TypeError("Expected a timedelta object")
        return td.total_seconds()


if __name__ == "__main__":
    print(TimeConverter.parse_to_seconds("2h 30m 15s"))
    print(TimeConverter.parse_to_milliseconds("1d 2h 3m 4s 500ms"))
    print(TimeConverter.format_seconds(3661.5))
    print(TimeConverter.format_milliseconds(1234567))
    print(TimeConverter.to_timedelta(3600))
    print(TimeConverter.from_timedelta(timedelta(days=1, hours=2, minutes=3)))
