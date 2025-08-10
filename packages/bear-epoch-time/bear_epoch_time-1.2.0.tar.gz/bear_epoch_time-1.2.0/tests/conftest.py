"""Conftest file for pytest configuration and fixtures."""


class DummyConsole:
    def __init__(self) -> None:
        """Initialize a dummy console to capture printed messages."""
        self.messages = []

    def print(self, msg, **_) -> None:
        """Simulate printing a message to the console."""
        self.messages.append(msg)

    def __call__(self, msg, **kwargs) -> None:
        """Allow the instance to be called like a function."""
        self.print(msg, **kwargs)
