"""Tests for the timer context manager in bear_epoch_time."""

import re
import time

from bear_epoch_time.timer import timer

from .conftest import DummyConsole


class TestTimerContextManager:
    """Tests for the timer context manager."""

    def test_custom_name_and_console(self) -> None:
        """Test that the timer can be used with a custom name and console."""
        dummy = DummyConsole()
        with timer(name="custom", console=True, print_func=dummy) as data:
            assert data.name == "custom"
            assert data.console is True
            assert data.print_func is dummy
        assert len(dummy.messages) == 1
        assert "custom" in dummy.messages[0]
        assert "Elapsed time" in dummy.messages[0]

    def test_subsecond_accuracy(self) -> None:
        """Test that the timer can measure subsecond durations accurately."""
        dummy = DummyConsole()
        with timer(name="quick", console=True, print_func=dummy) as t:
            time.sleep(0.05)

        assert 0 < t.seconds < 0.2
        assert 50 <= t.milliseconds < 200

    def test_logging_precision(self) -> None:
        """Test that the timer logs elapsed time with high precision."""
        dummy = DummyConsole()
        with timer(name="precision", console=True, print_func=dummy):
            pass

        assert re.search(r"Elapsed time: [0-9]*\.[0-9]{6} seconds", dummy.messages[0])
