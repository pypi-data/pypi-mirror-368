"""Tests for the async timer functionality in bear_epoch_time."""

import asyncio

from bear_epoch_time.timer import async_timer, create_async_timer

from .conftest import DummyConsole


def test_async_timer_context_manager() -> None:
    dummy = DummyConsole()

    async def inner() -> None:
        """Inner function to test the async timer context manager."""
        async with async_timer(name="custom_async", console=True, print_func=dummy) as data:
            assert data.name == "custom_async"
            assert data.console is True
            assert data.print_func is dummy
            await asyncio.sleep(0)

    asyncio.run(inner())
    assert len(dummy.messages) == 1
    assert "custom_async" in dummy.messages[0]


def test_create_async_timer_decorator() -> None:
    """Test the create_async_timer decorator."""
    dummy = DummyConsole()

    @create_async_timer(console=True, print_func=dummy)
    async def decorated() -> str:
        """Decorated async function to test the timer."""
        await asyncio.sleep(0)
        return "done"

    result: str = asyncio.run(decorated())
    assert result == "done"
    assert len(dummy.messages) == 1
    assert "decorated" in dummy.messages[0]
