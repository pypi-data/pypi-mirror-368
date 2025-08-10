from datetime import datetime

from dateutil import parser as dateutil_parser
from dateutil.tz import gettz
from pytz import UTC, UnknownTimeZoneError, timezone
from pytz.tzinfo import BaseTzInfo, DstTzInfo, StaticTzInfo
from tzlocal import get_localzone

TimeZoneType = BaseTzInfo | DstTzInfo | StaticTzInfo
TzInputType = str | TimeZoneType


def get_local_timezone() -> TimeZoneType:
    """Get the local timezone using tzlocal and return it as a pytz timezone object."""
    try:
        local_tz_str = str(get_localzone())
        return timezone(local_tz_str)
    except (UnknownTimeZoneError, Exception):
        return UTC


def parse_datetime_string(dt_string: str, default_tz: TimeZoneType = UTC) -> datetime:
    """Parse a datetime string preserving timezone information using dateutil.

    Args:
        dt_string (str): The datetime string to parse.
        default_tz (TimeZoneType): Default timezone to use if none found in string.
            If None, uses UTC as default.

    Returns:
        datetime: A timezone-aware datetime object.

    Examples:
        >>> parse_datetime_string("06-12-2025 06:10:32 PM PDT")
        datetime.datetime(2025, 6, 12, 18, 10, 32, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)

        >>> parse_datetime_string("2025-06-12 18:10:32")
        datetime.datetime(2025, 6, 12, 18, 10, 32, tzinfo=<UTC>)
    """
    try:
        parsed_dt: datetime = dateutil_parser.parse(dt_string)

        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=default_tz)
        return parsed_dt
    except (ValueError, TypeError) as e:
        raise ValueError(f"Unable to parse datetime string '{dt_string}': {e}") from e


def to_timezone(tz_input: TzInputType | None) -> TimeZoneType:
    """Convert various timezone inputs to a pytz timezone object.

    Args:
        tz_input: Can be a timezone string, pytz timezone, or None.

    Returns:
        TimeZoneType: A pytz timezone object.

    Examples:
        >>> to_timezone("America/New_York")
        <DstTzInfo 'America/New_York' LMT-1 day, 19:04:00 STD>

        >>> to_timezone("PST")
        <StaticTzInfo 'PST'>

        >>> to_timezone(None)
        <UTC>
    """
    if tz_input is None:
        return UTC

    if isinstance(tz_input, TimeZoneType):
        return tz_input

    if isinstance(tz_input, str):
        try:
            return timezone(tz_input)
        except UnknownTimeZoneError:
            try:
                dateutil_tz = gettz(tz_input)
                if dateutil_tz is not None:
                    return timezone(str(dateutil_tz))
                return UTC
            except Exception:
                return UTC

    raise ValueError(f"Unable to normalize timezone input: {tz_input}")


def convert_between_timezones(dt: datetime, target_tz: TzInputType) -> datetime:
    """Convert a datetime from one timezone to another.

    Args:
        dt (datetime): The datetime to convert (should be timezone-aware).
        target_tz: The target timezone.

    Returns:
        datetime: The datetime converted to the target timezone.

    Raises:
        ValueError: If the input datetime is naive.
    """
    if dt.tzinfo is None:
        raise ValueError("Input datetime must be timezone-aware")

    target_tz = to_timezone(target_tz)
    return dt.astimezone(target_tz)


def is_timezone_aware(dt: datetime) -> bool:
    """Check if a datetime object is timezone-aware.

    Args:
        dt (datetime): The datetime to check.

    Returns:
        bool: True if timezone-aware, False if naive.
    """
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def make_timezone_aware(dt: datetime, tz: TzInputType | None = None) -> datetime:
    """Make a naive datetime timezone-aware by adding timezone information.

    Args:
        dt (datetime): The naive datetime to make aware.
        tz: The timezone to apply. If None, uses UTC.

    Returns:
        datetime: A timezone-aware datetime.

    Raises:
        ValueError: If the datetime is already timezone-aware.
    """
    if is_timezone_aware(dt):
        raise ValueError("Datetime is already timezone-aware")

    tz = to_timezone(tz)
    return tz.localize(dt)


def strip_timezone(dt: datetime) -> datetime:
    """Remove timezone information from a datetime, making it naive.

    Args:
        dt (datetime): The timezone-aware datetime.

    Returns:
        datetime: A naive datetime with timezone info removed.
    """
    return dt.replace(tzinfo=None)


__all__ = [
    "TimeZoneType",
    "convert_between_timezones",
    "get_local_timezone",
    "is_timezone_aware",
    "make_timezone_aware",
    "parse_datetime_string",
    "strip_timezone",
    "to_timezone",
]
