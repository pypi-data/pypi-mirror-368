"""# Constants for the Bear Epoch Time package."""

from typing import LiteralString

from pytz import UTC, timezone

from bear_epoch_time._tz import TimeZoneType

DATE_FORMAT = "%m-%d-%Y"
"""Date format"""

TIME_FORMAT = "%I:%M %p"
"""Time format with 12 hour format"""

TIME_FORMAT_WITH_SECONDS = "%I:%M:%S %p"
"""Time format with 12 hour format and seconds"""

DATE_TIME_FORMAT: LiteralString = f"{DATE_FORMAT} {TIME_FORMAT}"
"""Datetime format with 12 hour format"""

DT_FORMAT_WITH_SECONDS: LiteralString = f"{DATE_FORMAT} {TIME_FORMAT_WITH_SECONDS}"
"""Datetime format with 12 hour format and seconds"""

DT_FORMAT_WITH_TZ: LiteralString = f"{DATE_TIME_FORMAT} %Z"
"""Datetime format with 12 hour format and timezone"""

DT_FORMAT_WITH_TZ_AND_SECONDS: LiteralString = f"{DT_FORMAT_WITH_SECONDS} %Z"
"""Datetime format with 12 hour format, seconds, and timezone"""

PT_TIME_ZONE: TimeZoneType = timezone("America/Los_Angeles")
"""Default timezone, a Pacific Time Zone using a pytz timezone object"""

ET_TIME_ZONE: TimeZoneType = timezone("America/New_York")

UTC_TIME_ZONE: TimeZoneType = UTC
"""UTC timezone, a UTC timezone using a pytz timezone object"""
