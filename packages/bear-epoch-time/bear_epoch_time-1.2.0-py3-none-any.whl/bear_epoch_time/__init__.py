"""This module provides tools for working with epoch time, including"""

from importlib.metadata import version

from ._tools import add_ord_suffix
from .constants import DEFAULT_DATE_FORMAT, DEFAULT_TIME_FORMAT, DEFAULT_TIMEZONE
from .constants.date_related import DATE_FORMAT, DATE_TIME_FORMAT
from .epoch_timestamp import EpochTimestamp
from .time_tools import TimeTools
from .timer import TimerData, async_timer, create_async_timer, create_timer, timer

__version__: str = version("bear-epoch-time")

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "DEFAULT_DATE_FORMAT",
    "DEFAULT_TIMEZONE",
    "DEFAULT_TIME_FORMAT",
    "EpochTimestamp",
    "TimeTools",
    "TimerData",
    "__version__",
    "add_ord_suffix",
    "async_timer",
    "create_async_timer",
    "create_timer",
    "timer",
]
