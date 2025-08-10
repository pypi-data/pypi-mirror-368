import pytest

from bear_epoch_time.constants.time_related import (
    MILLISECONDS_IN_SECOND,
    SECONDS_IN_DAY,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE,
    SECONDS_IN_MONTH,
)
from bear_epoch_time.time_converter import TimeConverter


def test_time_since_all_units() -> None:
    assert TimeConverter.time_since(0, SECONDS_IN_MONTH, "M") == 1
    assert TimeConverter.time_since(0, SECONDS_IN_MONTH, "mo") == 1
    assert TimeConverter.time_since(0, SECONDS_IN_DAY, "d") == 1
    assert TimeConverter.time_since(0, SECONDS_IN_HOUR, "h") == 1
    assert TimeConverter.time_since(0, SECONDS_IN_MINUTE, "m") == 1
    assert TimeConverter.time_since(0, 1, "s") == 1
    assert TimeConverter.time_since(0, 1, "ms") == MILLISECONDS_IN_SECOND


def test_parse_to_seconds_invalid() -> None:
    with pytest.raises(ValueError):
        TimeConverter.parse_to_seconds("5x")


def test_parse_to_milliseconds_mixed_units() -> None:
    result = TimeConverter.parse_to_milliseconds("1h 30m 500ms")
    expected = (SECONDS_IN_HOUR + 30 * SECONDS_IN_MINUTE) * MILLISECONDS_IN_SECOND + 500
    assert result == expected


def test_format_negative_values() -> None:
    with pytest.raises(ValueError):
        TimeConverter.format_seconds(-1)
    with pytest.raises(ValueError):
        TimeConverter.format_milliseconds(-1)


def test_timedelta_conversions() -> None:
    assert TimeConverter.from_timedelta(TimeConverter.to_timedelta(60)) == 60
    with pytest.raises(ValueError):
        TimeConverter.to_timedelta(-1)
    with pytest.raises(TypeError):
        TimeConverter.from_timedelta(123)
