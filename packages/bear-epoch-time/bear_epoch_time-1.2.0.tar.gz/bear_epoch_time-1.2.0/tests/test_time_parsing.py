"""Epoch time parsing tests for bear_epoch_time."""

from bear_epoch_time._helpers import TimeConverter
from bear_epoch_time.constants.date_related import DT_FORMAT_WITH_TZ_AND_SECONDS
from bear_epoch_time.constants.time_related import SECONDS_IN_MINUTE, SECONDS_IN_MONTH
from bear_epoch_time.epoch_timestamp import EpochTimestamp

time_convert = TimeConverter()


def test_month_and_minute_parsing() -> None:
    total: float = TimeConverter.parse_to_seconds("1M 5m")
    assert total == SECONDS_IN_MONTH + 5 * SECONDS_IN_MINUTE


def test_seconds_to_time_month_format() -> None:
    assert TimeConverter.format_seconds(SECONDS_IN_MONTH) == "1M"


def test_epoch_timestamp() -> None:
    EpochTimestamp.set_full_format(DT_FORMAT_WITH_TZ_AND_SECONDS)
    timestamp = EpochTimestamp(value=1749777032000)  # 06-12-2025 06:10:32 PM PDT
    formatted: str = timestamp.to_string()
    assert formatted == "06-12-2025 06:10:32 PM PDT", f"Expected '06-12-2025 06:10:32 PM PDT', got '{formatted}'"
