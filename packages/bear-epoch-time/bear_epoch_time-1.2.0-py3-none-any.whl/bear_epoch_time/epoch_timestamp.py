"""EpochTimestamp Class for handling epoch time in seconds or milliseconds.

This class provides methods to convert between epoch time and human-readable formats, including datetime objects and formatted strings.
"""

from datetime import datetime
from typing import ClassVar, Literal, Self

from pytz import UTC

from bear_epoch_time._tz import to_timezone
from bear_epoch_time.constants.date_related import (
    DATE_FORMAT,
    DT_FORMAT_WITH_TZ,
    PT_TIME_ZONE,
    TIME_FORMAT,
    TimeZoneType,
)
from bear_epoch_time.time_converter import TimeConverter

REPR_CHOICES = Literal["int", "object", "datetime"]
MULT = Literal[1000, 1]


class EpochTimestamp(int):
    """Custom class to represent epoch timestamps.

    Inherits from int to allow direct arithmetic operations.
    This class is used to represent time in seconds or milliseconds since the epoch (1970-01-01 00:00:00 UTC)
    with it defaulting to ms since that is the most common use case.

    Default value is the current epoch time in milliseconds. It is suggested to set the value to 0 if using it as
    a placeholder value or call `now()` to get the current epoch time.
    """

    _repr_style: ClassVar[REPR_CHOICES] = "int"
    """Three choices: int, object, or datetime.
    Int is the default and is the most common use case.
    Object will return the object representation of the class.
    Datetime will return a human readable timestamp like "10-01-2025." """
    _datefmt: ClassVar[str] = DATE_FORMAT
    """The format of the default date string. Default is "%m-%d-%Y"."""
    _timefmt: ClassVar[str] = TIME_FORMAT
    """The format of the default time string. Default is "%I:%M %p"."""
    _fullfmt: ClassVar[str] = DT_FORMAT_WITH_TZ
    """The format of the default datetime string. Default is "%m-%d-%Y %I:%M %p %Z"."""
    _tz: ClassVar[TimeZoneType] = PT_TIME_ZONE
    """The default timezone for the class. Default is "America/Los_Angeles"."""

    # region Class Methods

    @classmethod
    def set_repr_style(cls, repr_style: REPR_CHOICES) -> None:
        """Set the plain representation of the class.

        Args:
            repr_style (str): The representation style ("int", "object", or "datetime")
        """
        cls._repr_style = repr_style

    @classmethod
    def set_date_format(cls, datefmt: str) -> None:
        """Set the default date format for the class.

        Args:
            datefmt (str): The format of the date string. Default is "%m-%d-%Y".
        """
        cls._datefmt = datefmt

    @classmethod
    def set_time_format(cls, timefmt: str) -> None:
        """Set the default time format for the class.

        Args:
            timefmt (str): The format of the time string. Default is "%I:%M %p".
        """
        cls._timefmt = timefmt

    @classmethod
    def set_full_format(cls, fullfmt: str) -> None:
        """Set the default datetime format for the class.

        Args:
            fullfmt (str): The format of the datetime string. Default is "%m-%d-%Y %I:%M %p %Z".
        """
        cls._fullfmt = fullfmt

    @classmethod
    def set_timezone(cls, tz: TimeZoneType) -> None:
        """Set the default timezone for the class.

        Args:
            tz (TimeZoneType): The timezone to set. Default is PT_TIME_ZONE.
        """
        cls._tz = tz

    @classmethod
    def now(cls, milliseconds: bool = True) -> Self:
        """Get the current epoch time in milliseconds or seconds in UTC.

        Args:
            milliseconds (bool): If True, return milliseconds. If False, return seconds. Default is True for milliseconds.

        Returns:
            EpochTimestamp: The current epoch time.
        """
        multiplier: MULT = 1000 if milliseconds else 1
        t: int = int(datetime.now(UTC).timestamp() * multiplier)
        return cls(t, milliseconds=milliseconds)

    @classmethod
    def from_seconds(cls, seconds: int, milliseconds: bool = True) -> Self:
        """Create an EpochTimestamp from seconds

        Args:
            seconds (int): The number of seconds since the epoch.

        Returns:
            EpochTimestamp: The epoch timestamp in seconds.
        """
        multiplier: MULT = 1000 if milliseconds else 1
        return cls(int(seconds * multiplier), milliseconds=milliseconds)

    @classmethod
    def from_datetime(cls, dt: datetime, milliseconds: bool = True) -> Self:
        """Convert a datetime object to an epoch timestamp.

        Args:
            dt (datetime): The datetime object to convert.
            milliseconds (bool): If True, return milliseconds. If False, return seconds.

        Returns:
            EpochTimestamp: The epoch timestamp in milliseconds or seconds based on the milliseconds argument.
        """
        multiplier: MULT = 1000 if milliseconds else 1
        # If naive datetime, assume it's in UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return cls(int(dt.astimezone(UTC).timestamp() * multiplier), milliseconds=milliseconds)

    @classmethod
    def from_dt_string(
        cls,
        dt_string: str,
        milliseconds: bool = True,
        fmt: str | None = None,
        tz: TimeZoneType | str | None = None,
    ) -> Self:
        """Convert a datetime string to an epoch timestamp

        Args:
            dt_string (str): The datetime string to convert.
            milliseconds (bool): If True, return milliseconds. If False, return seconds.
            fmt (str): The format of the datetime string. Default is "%m-%d-%Y %I:%M %p".

        Returns:
            EpochTimestamp: The epoch timestamp in milliseconds or seconds based on the milliseconds argument.
        """
        multiplier: MULT = 1000 if milliseconds else 1
        dt: datetime = datetime.strptime(dt_string, fmt if fmt else cls._fullfmt)  # noqa: DTZ007
        tz = to_timezone(tz) if tz else cls._tz
        dt = tz.localize(dt) if not dt.tzinfo else dt
        return cls(int(dt.astimezone(UTC).timestamp() * multiplier), milliseconds=milliseconds)

    def __new__(cls, value: int | None = None, milliseconds: bool = True) -> Self:
        """Create a new EpochTimestamp instance."""
        value = value if value is not None else cls.now(milliseconds)
        return super().__new__(cls, value)

    # endregion

    # region Instance Methods

    def __init__(self, value: int | None = None, milliseconds: bool = True) -> None:  # noqa: ARG002
        """Initialize the EpochTimestamp instance."""
        self.milliseconds: bool = milliseconds
        self.multiplier: MULT = 1000 if self.milliseconds else 1

    def __str__(self):
        return int.__str__(self)

    def __repr__(self) -> str:
        if self.is_default:
            return "EpochTimestamp(0) (Default Value)"
        match self._repr_style:
            case "int":
                return f"{int(self)}"
            case "object":
                return f"EpochTimestamp({int(self)})"
            case "datetime":
                return f"{self.to_datetime.strftime(self._datefmt)}"
            case _:
                raise ValueError(f"Invalid repr style: {self._repr_style}")

    def to_string(self, fmt: str | None = None, tz: TimeZoneType | None = None) -> str:
        """Convert the epoch timestamp to a formatted string, taking into account the timezone and format.

        Args:
            fmt (str): The format of the datetime string. Default is "%m-%d-%Y %I:%M %p".
            tz (TimeZoneType | None): The timezone to convert to. Default is PT_TIME_ZONE.

        Returns:
            str: The formatted date string.
        """
        if self.is_default:
            raise ValueError("Cannot convert default value to string.")
        fmt = fmt if fmt else self._fullfmt
        tz = tz if tz else self._tz
        return self.to_datetime.astimezone(tz).strftime(fmt)

    def date_str(self, tz: TimeZoneType | None = None) -> str:
        """Convert the epoch timestamp to a date string in the format "%m-%d-%Y".

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Default is PT_TIME_ZONE.

        Returns:
            str: The formatted date string.
        """
        return self.to_string(fmt=self._datefmt, tz=tz if tz else self._tz)

    def time_str(self, tz: TimeZoneType | None = None) -> str:
        """Convert the epoch timestamp to a time string in the format "%I:%M %p".

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Default is PT_TIME_ZONE.

        Returns:
            str: The formatted time string.
        """
        return self.to_string(fmt=self._timefmt, tz=tz if tz else self._tz)

    def add_timedelta(self, seconds: int = 0, milliseconds: int = 0) -> Self:
        """Add a timedelta to the epoch timestamp.

        Args:
            seconds (int): The number of seconds to add. Default is 0.
            milliseconds (int): The number of milliseconds to add. Default is 0.

        Returns:
            EpochTimestamp: The new epoch timestamp after adding the timedelta.
        """
        total_seconds: float = seconds + (milliseconds / 1000)
        new_timestamp = int((self.to_seconds + total_seconds) * self.multiplier)
        return type(self)(new_timestamp)

    def start_of_day(self, tz: TimeZoneType | None = None) -> Self:
        """Get the start of the day for the epoch timestamp, defaults to midnight of the day in UTC.

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Will default to UTC if not provided.

        Returns:
            EpochTimestamp: The epoch timestamp at the start of the day.
        """
        dt: datetime = self.to_datetime.astimezone(tz) if tz else self.to_datetime
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return type(self).from_datetime(dt, milliseconds=self.milliseconds)

    def end_of_day(self, tz: TimeZoneType | None = None) -> Self:
        """Get the end of the day for the epoch timestamp, defaults to 23:59:59.999999 of the day in UTC.

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Will default to UTC if not provided.

        Returns:
            EpochTimestamp: The epoch timestamp at the end of the day.
        """
        dt: datetime = self.to_datetime.astimezone(tz) if tz else self.to_datetime
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        return type(self).from_datetime(dt, milliseconds=self.milliseconds)

    def time_since(self, other: Self, unit: Literal["M", "d", "h", "m", "s", "ms"] = "d") -> float:
        """Calculate the time difference between this timestamp and another in the specified unit.

        Args:
            other (EpochTimestamp): The other epoch timestamp to compare with.
            unit (str): The unit to return ("M", "d", "h", "m", "s", "ms"). Default is "d" for days.

        Returns:
            float: The time difference in the specified unit.
        """
        return TimeConverter.time_since(int(self.to_seconds), int(other.to_seconds), unit)

    # endregion

    # region Properties

    @property
    def to_datetime(self) -> datetime:
        """Convert the epoch timestamp to a datetime object in UTC.

        Returns:
            datetime: The datetime representation of the epoch timestamp.
        """
        return datetime.fromtimestamp(self / 1000.0 if self.milliseconds else self, tz=UTC)

    @property
    def to_seconds(self) -> int:
        """Get the total seconds from the epoch timestamp (truncated to whole seconds).

        If the timestamp is in milliseconds, it converts it to seconds by truncating
        the millisecond portion, else just returns the integer value.

        Returns:
            int: The total whole seconds since the epoch.
        """
        return int(self / 1000) if self.milliseconds else int(self)

    @property
    def to_milliseconds(self) -> int:
        """Get the total milliseconds from the epoch timestamp.

        If the timestamp is in seconds, it converts it to milliseconds else
        just returns the integer value.

        Returns:
            int: The total milliseconds since the epoch.
        """
        return int(self * 1000) if not self.milliseconds else int(self)

    @property
    def to_int(self) -> int:
        """Converts the epoch timestamp to an integer value. Mostly used for type hinting since this *IS* an int.

        Returns:
            int: The total milliseconds since the epoch.
        """
        return int(self)

    @property
    def to_duration(self) -> str:
        """The duration string representation of the epoch timestamp.

        In other words, this is the duration since the epoch (1970-01-01 00:00:00 UTC) in a human-readable format
        like "675M 28d 2h 12m 28s".

        Returns:
            str: The formatted duration string.
        """
        return TimeConverter.format_seconds(self.to_seconds, show_subseconds=True)

    @property
    def year(self) -> int:
        """Get the year from the epoch timestamp.

        Returns:
            int: The year of the epoch timestamp.
        """
        return self.to_datetime.year

    @property
    def month(self) -> int:
        """Get the month from the epoch timestamp.

        Returns:
            int: The month of the epoch timestamp.
        """
        return self.to_datetime.month

    @property
    def month_name(self) -> str:
        """Get the month name from the epoch timestamp.

        Returns:
            str: The full name of the month of the epoch timestamp.
        """
        return self.to_datetime.strftime("%B")

    @property
    def day(self) -> int:
        """Get the day from the epoch timestamp.

        Returns:
            int: The day of the epoch timestamp.
        """
        return self.to_datetime.day

    @property
    def day_of_week(self) -> int:
        """Get the day of the week from the epoch timestamp.

        Returns:
            int: The day of the week (0=Monday, 6=Sunday).
        """
        return self.to_datetime.weekday()

    @property
    def day_of_year(self) -> int:
        """Get the day of the year from the epoch timestamp.

        Returns:
            int: The day of the year (1-366).
        """
        return self.to_datetime.timetuple().tm_yday

    @property
    def day_name(self) -> str:
        """Get the day name from the epoch timestamp.

        Returns:
            str: The full name of the day of the epoch timestamp like "Monday".
        """
        return self.to_datetime.strftime("%A")

    @property
    def is_default(self) -> bool:
        """Check if the timestamp is zero, this is useful since zero is the default value.

        Returns:
            bool: True if the timestamp is zero, False otherwise.
        """
        return self == 0

    # endregion


if __name__ == "__main__":
    #     # Example usage
    #     default_value = EpochTimestamp(0)
    #     ts = EpochTimestamp.now()
    #     t2 = EpochTimestamp.now(milliseconds=False)

    #     print(f"Default Zero Value = {default_value}")
    #     print(f"Current timestamp in milliseconds: {ts} {ts.milliseconds=}")
    #     print(f"Current timestamp in seconds: {t2} {t2.milliseconds=}")
    time: EpochTimestamp = EpochTimestamp.now()
    print(time.to_seconds)
    print(time.to_milliseconds)
    print(time.to_duration)
