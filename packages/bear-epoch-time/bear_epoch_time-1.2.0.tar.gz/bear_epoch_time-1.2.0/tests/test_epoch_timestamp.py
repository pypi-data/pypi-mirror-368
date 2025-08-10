"""Tests for the EpochTimestamp class in bear_epoch_time."""

from datetime import datetime

import pytest
from pytz import UTC, timezone

from bear_epoch_time.constants.date_related import (
    DT_FORMAT_WITH_SECONDS,
    DT_FORMAT_WITH_TZ_AND_SECONDS,
    ET_TIME_ZONE,
    PT_TIME_ZONE,
)
from bear_epoch_time.epoch_timestamp import EpochTimestamp


class TestEpochTimestampCreation:
    """Test various ways to create EpochTimestamp objects."""

    def test_default_creation_is_not_zero(self):
        """Default creation should give current time, not zero."""
        ts = EpochTimestamp()
        assert ts != 0
        assert not ts.is_default

    def test_explicit_zero_creation(self):
        """Explicitly creating with 0 should give default value."""
        ts = EpochTimestamp(0)
        assert ts == 0
        assert ts.is_default

    def test_milliseconds_vs_seconds_creation(self):
        """Test creation with milliseconds vs seconds flag."""
        ts_ms = EpochTimestamp(1000, milliseconds=True)
        ts_s = EpochTimestamp(1, milliseconds=False)

        assert ts_ms.to_seconds == 1
        assert ts_s.to_seconds == 1
        assert ts_ms.milliseconds is True
        assert ts_s.milliseconds is False


class TestEpochTimestampFromDatetime:
    """Test creating EpochTimestamp from datetime objects."""

    def test_from_naive_datetime(self):
        """Test creating from naive datetime (should assume UTC)."""
        dt = datetime(2025, 6, 12, 18, 10, 32)  # noqa: DTZ001
        ts: EpochTimestamp = EpochTimestamp.from_datetime(dt)

        expected_utc: datetime = dt.replace(tzinfo=UTC)
        assert ts.to_datetime == expected_utc

    def test_from_timezone_aware_datetime(self):
        """Test creating from timezone-aware datetime."""
        pst = timezone("America/Los_Angeles")
        dt_pst = pst.localize(datetime(2025, 6, 12, 18, 10, 32))  # noqa: DTZ001
        ts = EpochTimestamp.from_datetime(dt_pst)

        expected_utc = dt_pst.astimezone(UTC)
        assert ts.to_datetime == expected_utc

    def test_milliseconds_vs_seconds_from_datetime(self):
        """Test milliseconds flag when creating from datetime."""
        dt = datetime(2025, 6, 12, 18, 10, 32, tzinfo=UTC)

        ts_ms = EpochTimestamp.from_datetime(dt, milliseconds=True)
        ts_s = EpochTimestamp.from_datetime(dt, milliseconds=False)

        assert ts_ms.milliseconds is True
        assert ts_s.milliseconds is False
        assert ts_ms.to_seconds == ts_s.to_seconds


class TestEpochTimestampFromStringBUG:
    """Test the buggy from_dt_string method - these tests should FAIL initially."""

    def test_timezone_aware_string_parsing_bug(self):
        """Test that demonstrates critical timezone parsing bug in from_dt_string method.

        The bug: When parsing datetime strings with timezone information using strptime(),
        the timezone information is parsed but then ignored. The resulting naive datetime
        is incorrectly treated as being in the system's local timezone when converted to UTC.

        Expected behavior: A string "06-12-2025 06:10:32 PM PDT" should be interpreted
        as 6:10 PM Pacific Daylight Time and converted to the equivalent UTC timestamp.

        Actual buggy behavior: The timezone suffix "PDT" is ignored, and the time is
        treated as if it were in the system's local timezone instead.

        This test should FAIL initially, proving the bug exists.
        """
        dt_string = "06-12-2025 06:10:32 PM PDT"
        ts = EpochTimestamp.from_dt_string(dt_string, fmt=DT_FORMAT_WITH_TZ_AND_SECONDS)

        pst = timezone("America/Los_Angeles")
        expected_dt = pst.localize(datetime(2025, 6, 12, 18, 10, 32))  # noqa: DTZ001
        expected_ts = EpochTimestamp.from_datetime(expected_dt)

        assert ts.to_seconds == expected_ts.to_seconds, (
            f"Expected {expected_ts.to_seconds} but got {ts.to_seconds}. "
            f"Bug: timezone info in string is ignored, treated as system timezone instead."
        )

    def test_utc_string_parsing(self):
        """Test parsing datetime strings with UTC timezone designation.

        Note: Python's strptime with %Z cannot properly parse timezone abbreviations
        into timezone-aware datetime objects. The timezone must be passed explicitly.
        This test demonstrates the correct way to parse such strings.
        """
        dt_string = "06-12-2025 06:10:32 PM UTC"
        # Pass UTC explicitly since %Z doesn't set tzinfo in strptime
        ts = EpochTimestamp.from_dt_string(dt_string, fmt=DT_FORMAT_WITH_TZ_AND_SECONDS, tz=UTC)

        expected_dt = UTC.localize(datetime(2025, 6, 12, 18, 10, 32))  # noqa: DTZ001
        expected_ts = EpochTimestamp.from_datetime(expected_dt)

        assert ts.to_seconds == expected_ts.to_seconds

    def test_naive_string_parsing(self):
        """Test parsing datetime strings without any timezone information.

        When no timezone is specified in the format or string, the current implementation
        treats the datetime as naive and then applies astimezone(UTC), which assumes
        the naive datetime is in the system's local timezone.

        This test documents the current behavior for naive datetime strings.
        The behavior may or may not be correct depending on the intended use case,
        but it should be consistent and predictable.
        """
        dt_string = "06-12-2025 06:10:32 PM"
        fmt = "%m-%d-%Y %I:%M:%S %p"

        ts = EpochTimestamp.from_dt_string(dt_string, fmt=fmt)

        assert ts != 0
        assert not ts.is_default

    def test_same_time_different_timezones_produce_different_utc(self):
        """Test that the same local time interpreted in different timezones produces different UTC timestamps.

        This is a fundamental test of timezone handling correctness using the proper API.
        When we parse the same naive datetime string but specify different timezones,
        the resulting UTC timestamps should be different because they represent
        different moments in absolute time.

        For example, 6:10 PM in Los Angeles (PDT, UTC-7) occurs 3 hours earlier than
        6:10 PM in New York (EDT, UTC-4). This test verifies that our timezone
        parameter correctly handles this conversion.

        This tests the core functionality: parsing naive strings with explicit timezone context.
        """
        naive_time_string = "06-12-2025 06:10:32 PM"

        ts_la: EpochTimestamp = EpochTimestamp.from_dt_string(
            dt_string=naive_time_string,
            fmt=DT_FORMAT_WITH_SECONDS,
            tz=PT_TIME_ZONE,
        )
        ts_ny: EpochTimestamp = EpochTimestamp.from_dt_string(
            dt_string=naive_time_string,
            fmt=DT_FORMAT_WITH_SECONDS,
            tz=ET_TIME_ZONE,
        )

        assert ts_la.to_seconds != ts_ny.to_seconds, (
            f"Same local time in different timezones should produce different UTC timestamps. "
            f"LA: {ts_la.to_seconds}, NY: {ts_ny.to_seconds}"
        )

        time_diff_hours = abs(ts_la.to_seconds - ts_ny.to_seconds) / 3600
        assert time_diff_hours == 3, f"Expected 3 hour difference, got {time_diff_hours} hours"


class TestEpochTimestampConversion:
    """Test timestamp conversion methods."""

    def test_to_string_formatting(self):
        """Test string formatting with different formats and timezones.

        Verifies that EpochTimestamp can format itself into human-readable strings
        using different format patterns and timezone conversions. Tests both the
        default formatting behavior and timezone-specific formatting.
        """
        dt_utc: datetime = UTC.localize(datetime(2025, 6, 12, 18, 10, 32))  # noqa: DTZ001
        ts: EpochTimestamp = EpochTimestamp.from_datetime(dt_utc)
        formatted = ts.to_string()
        assert isinstance(formatted, str)
        assert "2025" in formatted

        pst_formatted = ts.to_string(tz=PT_TIME_ZONE)
        assert isinstance(pst_formatted, str)
        assert "11:10" in pst_formatted or "11:10:32" in pst_formatted
        assert "PDT" in pst_formatted

    def test_date_and_time_strings(self):
        """Test date_str and time_str methods."""
        dt_utc: datetime = UTC.localize(datetime(2025, 6, 12, 18, 10, 32))  # noqa: DTZ001
        ts: EpochTimestamp = EpochTimestamp.from_datetime(dt_utc)

        date_str: str = ts.date_str()
        time_str: str = ts.time_str()

        assert isinstance(date_str, str)
        assert isinstance(time_str, str)
        assert "06-12-2025" in date_str or "6-12-2025" in date_str
        assert "PM" in time_str or "AM" in time_str

    def test_default_value_string_conversion_raises(self):
        """Test that default value (0) raises error on string conversion."""
        ts = EpochTimestamp(0)
        assert ts.is_default

        with pytest.raises(ValueError, match="Cannot convert default value to string"):
            ts.to_string()

    def test_date_properties(self):
        """Test date properties."""
        dt_utc = UTC.localize(datetime(2025, 6, 12, 18, 10, 32))  # noqa: DTZ001
        ts: EpochTimestamp = EpochTimestamp.from_datetime(dt_utc)

        assert ts.year == 2025
        assert ts.month == 6
        assert ts.day == 12
        assert ts.day_of_week == 3  # Thursday
        assert ts.day_of_year == 163


class TestEpochTimestampArithmetic:
    """Test timestamp arithmetic operations."""

    def test_add_timedelta_seconds(self):
        """Test adding seconds to timestamp and verify immutability.

        Verifies that adding time to an EpochTimestamp creates a new instance
        rather than modifying the original, ensuring immutable behavior.
        """
        ts = EpochTimestamp(1000)
        new_ts = ts.add_timedelta(seconds=1)

        assert new_ts.to_seconds == ts.to_seconds + 1
        assert new_ts != ts

    def test_add_timedelta_milliseconds(self):
        """Test adding milliseconds to timestamp for precision arithmetic."""
        ts = EpochTimestamp(1000)
        new_ts = ts.add_timedelta(milliseconds=500)

        assert new_ts == ts + 500

    def test_start_and_end_of_day(self):
        """Test calculating day boundaries for timestamp arithmetic.

        Verifies that start_of_day and end_of_day methods correctly calculate
        midnight boundaries for a given timestamp, ensuring proper day-based
        time range calculations.
        """
        dt_utc = UTC.localize(datetime(2025, 6, 12, 15, 30, 45))  # noqa: DTZ001
        ts: EpochTimestamp = EpochTimestamp.from_datetime(dt_utc)

        start_of_day = ts.start_of_day()
        end_of_day = ts.end_of_day()

        start_dt = start_of_day.to_datetime
        assert start_dt.hour == 0
        assert start_dt.minute == 0
        assert start_dt.second == 0

        end_dt = end_of_day.to_datetime
        assert end_dt.hour == 23
        assert end_dt.minute == 59
        assert end_dt.second == 59

        assert start_dt.date() == end_dt.date()


class TestEpochTimestampProperties:
    """Test timestamp properties."""

    def test_milliseconds_seconds_conversion(self):
        """Test bidirectional conversion between milliseconds and seconds precision.

        Verifies that EpochTimestamp correctly handles both millisecond and second
        precision, and can convert between them accurately regardless of the
        initial precision setting.
        """
        ts_ms = EpochTimestamp(5000, milliseconds=True)

        assert ts_ms.to_seconds == 5
        assert ts_ms.to_milliseconds == 5000
        assert ts_ms.to_int == 5000

        ts_s = EpochTimestamp(5, milliseconds=False)

        assert ts_s.to_seconds == 5
        assert ts_s.to_milliseconds == 5000
        assert ts_s.to_int == 5

    def test_is_default_property(self):
        """Test is_default property."""
        default_ts = EpochTimestamp(0)
        normal_ts = EpochTimestamp(1000)

        assert default_ts.is_default
        assert not normal_ts.is_default


class TestEpochTimestampClassMethods:
    """Test class-level configuration methods."""

    def test_now_method(self):
        """Test the now() class method for current timestamp generation.

        Verifies that the now() method correctly generates current timestamps
        in both millisecond and second precision, and that the timestamps
        are reasonable and approximately equivalent when converted to the same units.
        """
        ts_ms = EpochTimestamp.now(milliseconds=True)
        ts_s = EpochTimestamp.now(milliseconds=False)

        assert ts_ms.milliseconds is True
        assert ts_s.milliseconds is False
        assert ts_ms != 0
        assert ts_s != 0

        assert abs(ts_ms.to_seconds - ts_s.to_seconds) <= 1

    def test_class_configuration_methods(self):
        """Test class-level configuration methods for global behavior customization.

        Verifies that the class configuration methods (set_repr_style, set_date_format, etc.)
        work correctly and actually modify the class-level attributes that control
        default behavior for all EpochTimestamp instances.

        These methods allow users to customize the global defaults for string formatting,
        timezone handling, and representation styles.
        """
        original_repr_style = EpochTimestamp._repr_style
        original_datefmt = EpochTimestamp._datefmt
        original_timefmt = EpochTimestamp._timefmt
        original_fullfmt = EpochTimestamp._fullfmt
        original_tz = EpochTimestamp._tz

        try:
            EpochTimestamp.set_repr_style("int")
            EpochTimestamp.set_date_format("%Y-%m-%d")
            EpochTimestamp.set_time_format("%H:%M:%S")
            EpochTimestamp.set_full_format("%Y-%m-%d %H:%M:%S %Z")
            EpochTimestamp.set_timezone(UTC)

            assert EpochTimestamp._repr_style == "int"
            assert EpochTimestamp._datefmt == "%Y-%m-%d"
            assert EpochTimestamp._timefmt == "%H:%M:%S"
            assert EpochTimestamp._fullfmt == "%Y-%m-%d %H:%M:%S %Z"
            assert EpochTimestamp._tz == UTC
        finally:
            EpochTimestamp.set_repr_style(original_repr_style)
            EpochTimestamp.set_date_format(original_datefmt)
            EpochTimestamp.set_time_format(original_timefmt)
            EpochTimestamp.set_full_format(original_fullfmt)
            EpochTimestamp.set_timezone(original_tz)
