from __future__ import annotations

from argparse import ArgumentParser, Namespace
from contextlib import redirect_stdout, suppress
from dataclasses import dataclass
from enum import IntEnum
from importlib.metadata import PackageNotFoundError, version
from io import StringIO
import sys
from typing import Any, Literal, Self, overload

STDERR = sys.stderr


@dataclass(frozen=True)
class Value:
    """A frozen dataclass for holding constant integer values."""

    value: int
    text: str
    default: int = 0


class RichIntEnum(IntEnum):
    """Base class for IntEnums with rich metadata."""

    text: str
    default: int

    def __new__(cls, value: Value) -> Self:
        obj: Self = int.__new__(cls, value.value)
        obj._value_ = value.value
        obj.text = value.text
        obj.default = value.default
        return obj

    def __int__(self) -> int:
        """Return the integer value of the enum."""
        return self.value

    def __str__(self) -> str:
        """Return a string representation of the enum."""
        return f"{self.name} ({self.value}): {self.text}"

    @classmethod
    def keys(cls) -> list[str]:
        """Return a list of all enum member names."""
        return [item.name for item in cls]

    @overload
    @classmethod
    def get(cls, value: str | int | Self, default: Self) -> Self: ...

    @overload
    @classmethod
    def get(cls, value: str | int | Self, default: None = None) -> None: ...

    @classmethod
    def get(cls, value: str | int | Self | Any, default: Self | None = None) -> Self | None:
        """Try to get an enum member by its value, name, or text."""
        if isinstance(value, cls):
            return value
        with suppress(ValueError):
            if isinstance(value, int):
                return cls.from_int(value)
            if isinstance(value, str):
                return cls.from_name(value)
        return default

    @classmethod
    def from_name(cls, name: str) -> Self:
        """Convert a string name to its corresponding enum member."""
        try:
            return cls[name.upper()]
        except KeyError as e:
            raise ValueError(f"Name {name} not found in {cls.__name__}") from e

    @classmethod
    def from_int(cls, code: int) -> Self:
        """Convert an integer to its corresponding enum member."""
        for item in cls:
            if item.value == code:
                return item
        raise ValueError(f"Value {code} not found in {cls.__name__}")

    @classmethod
    def int_to_text(cls, code: int) -> str:
        """Convert an integer to its text representation."""
        try:
            return cls.from_int(code).text
        except ValueError:
            return "Unknown value"


class ExitCode(RichIntEnum):
    """An enumeration of common exit codes used in shell commands."""

    SUCCESS = Value(0, "Success")
    FAILURE = Value(1, "General error")
    MISUSE_OF_SHELL_COMMAND = Value(2, "Misuse of shell command")
    COMMAND_CANNOT_EXECUTE = Value(126, "Command invoked cannot execute")
    COMMAND_NOT_FOUND = Value(127, "Command not found")
    INVALID_ARGUMENT_TO_EXIT = Value(128, "Invalid argument to exit")
    SCRIPT_TERMINATED_BY_CONTROL_C = Value(130, "Script terminated by Control-C")
    PROCESS_KILLED_BY_SIGKILL = Value(137, "Process killed by SIGKILL (9)")
    SEGMENTATION_FAULT = Value(139, "Segmentation fault (core dumped)")
    PROCESS_TERMINATED_BY_SIGTERM = Value(143, "Process terminated by SIGTERM (15)")
    EXIT_STATUS_OUT_OF_RANGE = Value(255, "Exit status out of range")


class VerParts(RichIntEnum):
    """Enumeration for version parts."""

    MAJOR = Value(0, "major")
    MINOR = Value(1, "minor")
    PATCH = Value(2, "patch")

    @classmethod
    def choices(cls) -> list[str]:
        """Return a list of valid version parts."""
        return [version_part.text for version_part in cls]

    @classmethod
    def parts(cls) -> int:
        """Return the total number of version parts."""
        return len(cls.choices())


VALID_BUMP_TYPES: list[str] = VerParts.choices()
ALL_PARTS: int = VerParts.parts()


@dataclass
class Version:
    """Model to represent a version string."""

    major: int = 0
    """Major version number."""
    minor: int = 0
    """Minor version number."""
    patch: int = 0
    """Patch version number."""

    @classmethod
    def from_string(cls, version_str: str) -> Self:
        """Create a Version instance from a version string.

        Args:
            version_str: A version string in the format "major.minor.patch".

        Returns:
            A Version instance.

        Raises:
            ValueError: If the version string is not in the correct format.
        """
        try:
            version_str = version_str.replace("-", ".").replace("+", ".")
            parts: list[str] = version_str.split(".")[:ALL_PARTS]  # Ignore any extra parts
            major, minor, patch = parts
            return cls(major=int(major), minor=int(minor), patch=int(patch))
        except ValueError as e:
            raise ValueError(
                f"Invalid version string format: {version_str}. Expected integers for major, minor, and patch."
            ) from e

    def increment(self, attr_name: str) -> None:
        """Increment the specified part of the version."""
        setattr(self, attr_name, getattr(self, attr_name) + 1)

    @property
    def version_string(self) -> str:
        """Return the version as a string in the format "major.minor.patch".

        Returns:
            A string representation of the version.
        """
        return f"{self.major}.{self.minor}.{self.patch}"

    def default(self, part: str) -> None:
        """Clear the specified part of the version.

        Args:
            part: The part of the version to clear.
        """
        if hasattr(self, part):
            setattr(self, part, 0)

    def new_version(self, bump_type: str) -> Version:
        """Return a new version string based on the bump type."""
        bump_part: VerParts = VerParts.get(bump_type, default=VerParts.PATCH)
        self.increment(bump_part.text)
        for part in VerParts:
            if part.value > bump_part.value:
                self.default(part.text)
        return self

    @classmethod
    def from_func(cls, package_name: str) -> Self:
        """Create a Version instance from the current package version.

        Returns:
            A Version instance with the current package version.

        Raises:
            PackageNotFoundError: If the package is not found.
        """
        try:
            current_version = version(package_name)
            return cls.from_string(current_version)
        except PackageNotFoundError as e:
            raise PackageNotFoundError(f"Package '{package_name}' not found: {e}") from e


def _bump_version(version: str, bump_type: Literal["major", "minor", "patch"]) -> Version:
    """Bump the version based on the specified type.

    Args:
        version: The current version string (e.g., "1.2.3").
        bump_type: The type of bump ("major", "minor", or "patch").

    Returns:
        The new version string.

    Raises:
        ValueError: If the version format is invalid or bump_type is unsupported.
    """
    ver: Version = Version.from_string(version)
    return ver.new_version(bump_type)


def _get_version(package_name: str) -> str:
    """Get the version of the specified package.

    Args:
        package_name: The name of the package to get the version for.

    Returns:
        A Version instance representing the current version of the package.

    Raises:
        PackageNotFoundError: If the package is not found.
    """
    record = StringIO()
    with redirect_stdout(record):
        cli_get_version([package_name])
    return record.getvalue().strip()


def cli_get_version(args: list[str] | None = None) -> ExitCode:
    """Get the version of the current package.

    Returns:
        The version of the package.
    """
    if args is None:
        args = sys.argv[1:]
    parser = ArgumentParser(description="Get the version of the package.")
    parser.add_argument("package_name", nargs="?", type=str, help="Name of the package to get the version for.")
    arguments: Namespace = parser.parse_args(args)
    if not arguments.package_name:
        print("No package name provided. Please specify a package name.")
        return ExitCode.FAILURE
    package_name: str = arguments.package_name
    try:
        current_version = version(package_name)
        print(current_version)
    except PackageNotFoundError:
        print(f"Package '{package_name}' not found.")
        return ExitCode.FAILURE
    return ExitCode.SUCCESS


def cli_bump(args: list[str] | None = None) -> ExitCode:
    if args is None:
        args = sys.argv[1:]
    parser = ArgumentParser(description="Bump the version of the package.")
    parser.add_argument("bump_type", type=str, choices=VALID_BUMP_TYPES, default="patch")
    parser.add_argument("package_name", nargs="?", type=str, help="Name of the package to bump the version for.")
    parser.add_argument("current_version", type=str, help="Current version of the package.")
    arguments: Namespace = parser.parse_args(args)
    bump_type: Literal["major", "minor", "patch"] = arguments.bump_type
    if not arguments.package_name:
        print("No package name provided.")
        return ExitCode.FAILURE
    package_name: str = arguments.package_name
    if bump_type not in VALID_BUMP_TYPES:
        print(f"Invalid argument '{bump_type}'. Use one of: {', '.join(VALID_BUMP_TYPES)}.")
        return ExitCode.FAILURE
    current_version: str = arguments.current_version or _get_version(package_name)
    try:
        new_version: Version = _bump_version(version=current_version, bump_type=bump_type)
        print(new_version.version_string)
        return ExitCode.SUCCESS
    except ValueError as e:
        print(f"Error: {e}")
        return ExitCode.FAILURE
    except Exception as e:
        print(f"Unexpected error: {e}")
        return ExitCode.FAILURE
