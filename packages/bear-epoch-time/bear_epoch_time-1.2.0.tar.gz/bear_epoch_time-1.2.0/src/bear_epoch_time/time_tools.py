"""A module for managing time-related operations, including epoch timestamps, date formatting, and timezone handling."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from pytz import UTC, BaseTzInfo

from bear_epoch_time.epoch_timestamp import EpochTimestamp

from .constants.date_related import (
    DATE_FORMAT,
    DT_FORMAT_WITH_TZ,
    PT_TIME_ZONE,
    TIME_FORMAT,
    TimeZoneType,
)

if TYPE_CHECKING:
    from pytz.tzinfo import DstTzInfo, StaticTzInfo


class TimeTools:
    """A utility class for managing time-related operations, including epoch timestamps, date formatting, and timezone handling.

    Attributes:
        timezone (TimeZoneType): The timezone to use for date and time operations. Defaults to PT_TIME_ZONE.
        datefmt (str): The format string for date and time formatting. Defaults to DT_FORMAT_WITH_TZ.
    """

    def __init__(self, timezone: TimeZoneType = PT_TIME_ZONE, datefmt: str = DT_FORMAT_WITH_TZ):
        """Initialize the TimeTools instance with a specified timezone and date format."""
        # TODO: Update to use user's local timezone if available, otherwise use PT_TIME_ZONE
        self.timezone: TimeZoneType = timezone
        # TODO: Update to use user's preferred date format if available, otherwise use DT_FORMAT_WITH_TZ
        self.datefmt: str = datefmt

    def now(self, milliseconds: bool = True) -> EpochTimestamp:
        """Get a UTC epoch timestamp in milliseconds or seconds.

        Args:
            milliseconds (bool): If True, return the timestamp in milliseconds. If False, return in seconds. Default is True.

        Returns:
            EpochTimestamp: The current epoch timestamp in milliseconds or formatted string.
        """
        return EpochTimestamp.now(milliseconds=milliseconds)

    def now_as_str(self) -> str:
        """Get the current date and time as a formatted string.

        Returns:
            str: The current date and time as a formatted string.
        """
        return self.format_now

    @property
    def format_now(self) -> str:
        """Get the current date and time as a formatted string.

        Returns:
            str: The current date and time as a formatted string.
        """
        return EpochTimestamp.now().to_string(fmt=self.datefmt, tz=self.timezone)

    def dt_to_ts(self, dt: datetime, milliseconds: bool = True) -> EpochTimestamp:
        """Convert a datetime object to an epoch timestamp.

        Args:
            dt (datetime): The datetime object to convert.
            milliseconds (bool): If True, return milliseconds. If False, return seconds. Default is True.

        Returns:
            EpochTimestamp: The epoch timestamp in milliseconds or seconds based on the milliseconds argument.
        """
        return EpochTimestamp.from_datetime(dt, milliseconds=milliseconds)

    def str_to_ts(self, date_str: str, fmt: str | None = None) -> EpochTimestamp:
        """Convert a date string to an epoch timestamp in milliseconds.

        Args:
            date_str (str): The date string to convert.
            fmt (str | None): Format string. Uses instance default if not provided.

        Returns:
            EpochTimestamp: The epoch timestamp in milliseconds.
        """
        format_str: str = fmt or self.datefmt
        return EpochTimestamp.from_dt_string(date_str, milliseconds=True, fmt=format_str)

    def ts_to_str(self, ts: EpochTimestamp) -> str:
        """Convert an epoch timestamp to a formatted date string.

        Args:
            ts (EpochTimestamp): The epoch timestamp to convert.

        Returns:
            str: The formatted date string.
        """
        return ts.to_string(fmt=self.datefmt, tz=self.timezone)

    def ts_to_dt(self, ts: EpochTimestamp) -> datetime:
        """Convert an epoch timestamp to a datetime object.

        Args:
            ts (EpochTimestamp): The epoch timestamp to convert.

        Returns:
            datetime: The datetime object.
        """
        return ts.to_datetime.astimezone(self.timezone)

    def add_delta(
        self,
        ts: EpochTimestamp,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        dt_obj: timedelta | None = None,
    ) -> EpochTimestamp:
        """Add a timedelta to an epoch timestamp.

        Args:
            ts (EpochTimestamp): The epoch timestamp to modify.
            days (int): Number of days to add.
            hours (int): Number of hours to add.
            minutes (int): Number of minutes to add.
            seconds (int): Number of seconds to add.
            dt_obj (timedelta | None): A timedelta object to add (combined with other params).

        Returns:
            EpochTimestamp: The modified epoch timestamp.
        """
        if dt_obj:
            if not isinstance(dt_obj, timedelta):
                raise TypeError("timedelta_obj must be an instance of datetime.timedelta")
            days += dt_obj.days
            seconds += int(dt_obj.seconds + (dt_obj.microseconds / 1_000_000))
        else:
            seconds = seconds + (minutes * 60) + (hours * 3600) + (days * 86400)
        return ts.add_timedelta(seconds=seconds)

    def get_day_range(self, ts: EpochTimestamp | None = None) -> tuple[EpochTimestamp, EpochTimestamp]:
        """Get the start and end of a day from an epoch timestamp in the instance timezone, defaulting to now.

        Args:
            ts (EpochTimestamp): The epoch timestamp to convert (optional, defaults to now).

        Returns:
            tuple[EpochTimestamp, EpochTimestamp]: A tuple containing the start and end of the day as epoch timestamps.
        """
        if ts is None:
            ts = EpochTimestamp.now()

        timestamp_start: EpochTimestamp = ts.start_of_day(tz=self.timezone)
        timestamp_end: EpochTimestamp = ts.end_of_day(tz=self.timezone)
        return timestamp_start, timestamp_end

    def is_same_day(self, start_date: EpochTimestamp, end_date: EpochTimestamp) -> bool:
        """Check if two epoch timestamps are on the same day.

        Args:
            start_date (EpochTimestamp): The first epoch timestamp.
            end_date (EpochTimestamp): The second epoch timestamp.

        Returns:
            bool: True if both timestamps are on the same day, False otherwise.
        """
        dt1: datetime = datetime.fromtimestamp(start_date.to_seconds, tz=UTC)
        dt2: datetime = datetime.fromtimestamp(end_date.to_seconds, tz=UTC)
        return dt1.date() == dt2.date()

    def is_multi_day(
        self,
        start_date: str | datetime,
        end_date: str | datetime,
        fmt: str | None = None,
        tz: TimeZoneType | None = None,
    ) -> bool:
        """Determines if the span between two dates covers multiple days.

        Args:
            start_date (str | datetime): The start date.
            end_date (str | datetime): The end date.
            fmt (str | None): Format for string parsing. Defaults to self._datefmt.
            tz (TimeZoneType | None): Timezone for naive datetimes. Defaults to self._tz.

        Returns:
            bool: If the span covers multiple days, return True. Else, return False.
        """
        date_fmt: str = fmt or self.datefmt
        timezone: BaseTzInfo | DstTzInfo | StaticTzInfo = tz or self.timezone

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, date_fmt)  # noqa: DTZ007
            if start_date.tzinfo is None:
                start_date = timezone.localize(start_date)

        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, date_fmt)  # noqa: DTZ007
            if end_date.tzinfo is None:
                end_date = timezone.localize(end_date)

        start_date = start_date.astimezone(timezone)
        end_date = end_date.astimezone(timezone)

        return start_date.date() != end_date.date()

    def time_only(self, ts: EpochTimestamp) -> str:
        """Get the time part of an epoch timestamp as a formatted string.

        Args:
            ts (EpochTimestamp): The epoch timestamp to convert.

        Returns:
            str: The time part of the timestamp.
        """
        return ts.to_string(fmt=TIME_FORMAT, tz=self.timezone)

    def date_only(self, ts: EpochTimestamp) -> str:
        """Get the date part of an epoch timestamp as a formatted string.

        Args:
            ts (EpochTimestamp): The epoch timestamp to convert.

        Returns:
            str: The date part of the timestamp.
        """
        return ts.to_string(fmt=DATE_FORMAT, tz=self.timezone)


# if __name__ == "__main__":

#     # def example_callback(timer_data: TimerData):
#     #     print(f"Timer '{timer_data.name}' finished in {timer_data._raw_elapsed_time} ms")

#     # # Example usage
#     # with timer(
#     #     name="Tester Timer",
#     #     console=True,
#     # ) as time:
#     #     sleep(2)  # Simulate some work
#     #     data: TimerData = time

#     # get start and end of day
#     time_tools = TimeTools()
#     start_of_day, end_of_day = time_tools.get_day_range()
#     print(f"Start of day: {start_of_day.to_string()}")
#     print(f"End of day: {end_of_day.to_string()}")
