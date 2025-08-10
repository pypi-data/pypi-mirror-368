from __future__ import annotations

from dataclasses import dataclass, field
import importlib.metadata
from importlib.metadata import PackageNotFoundError, metadata, version
import os
import platform
import sys

from bear_epoch_time._internal._get_version import Version
from bear_epoch_time._internal._version import __version__

__PACKAGE_NAME__ = "bear_epoch_time"


@dataclass
class _Package:
    """Dataclass to store package information."""

    name: str = __PACKAGE_NAME__
    """Package name."""
    version: str = __version__
    """Package version."""
    _version: Version = field(default_factory=lambda: Version.from_string(__version__))
    description: str = "No description available."
    """Package description."""

    def __post_init__(self) -> None:
        """Post-initialization to ensure version is a string."""
        if not isinstance(self.version, str) or "0.0.0" in self.version:
            self.version = version(self.name) if self.name else "0.0.0"
        if not self.description:
            try:
                self.description = metadata(self.name)["Summary"]
            except PackageNotFoundError:
                self.description = "No description available."

    def __str__(self) -> str:
        """String representation of the package information."""
        return f"{self.name} v{self.version}: {self.description}"


@dataclass(frozen=True)
class _Variable:
    """Dataclass describing an environment variable."""

    name: str
    """Variable name."""
    value: str
    """Variable value."""


@dataclass(frozen=True)
class _Environment:
    """Dataclass to store environment information."""

    interpreter_name: str
    """Python interpreter name."""
    interpreter_version: str
    """Python interpreter version."""
    interpreter_path: str
    """Path to Python executable."""
    platform: str
    """Operating System."""
    packages: list[_Package]
    """Installed packages."""
    variables: list[_Variable]
    """Environment variables."""


def _interpreter_name_version() -> tuple[str, str]:
    if hasattr(sys, "implementation"):
        impl = sys.implementation.version
        version = f"{impl.major}.{impl.minor}.{impl.micro}"
        kind = impl.releaselevel
        if kind != "final":
            version += kind[0] + str(impl.serial)
        return sys.implementation.name, version
    return "", "0.0.0"


def _get_package_info(dist: str = __PACKAGE_NAME__) -> _Package:
    try:
        return _Package(
            name=dist,
            version=__version__,
            description=metadata(dist)["Summary"],
        )
    except PackageNotFoundError:
        return _Package(name=dist)


def _get_name(dist: str = __PACKAGE_NAME__) -> str:
    """Get name of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A package name.
    """
    return _get_package_info(dist).name


def _get_version(dist: str = __PACKAGE_NAME__) -> str:
    """Get version of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    return _get_package_info(dist).version


def _get_description(dist: str = __PACKAGE_NAME__) -> str:
    """Get description of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A description string.
    """
    return _get_package_info(dist).description


def _get_debug_info() -> _Environment:
    """Get debug/environment information.

    Returns:
        Environment information.
    """
    py_name, py_version = _interpreter_name_version()
    packages: list[str] = [__PACKAGE_NAME__]
    variables: list[str] = [
        "PYTHONPATH",
        *[var for var in os.environ if var.startswith(__PACKAGE_NAME__.replace("-", "_"))],
    ]
    return _Environment(
        interpreter_name=py_name,
        interpreter_version=py_version,
        interpreter_path=sys.executable,
        platform=platform.platform(),
        variables=[_Variable(var, val) for var in variables if (val := os.getenv(var))],
        packages=[_Package(pkg, _get_version(pkg)) for pkg in packages],
    )


def get_installed_packages() -> list[_Package]:
    """Get all installed packages in current environment"""
    packages = []
    for dist in importlib.metadata.distributions():
        packages.append({"name": dist.metadata["Name"], "version": dist.version})
    return packages


def _print_debug_info() -> None:
    """Print debug/environment information."""
    info: _Environment = _get_debug_info()
    print(f"- __System__: {info.platform}")
    print(f"- __Python__: {info.interpreter_name} {info.interpreter_version} ({info.interpreter_path})")
    print("- __Environment variables__:")
    for var in info.variables:
        print(f"  - `{var.name}`: `{var.value}`")
    print("- __Installed packages__:")
    for pkg in info.packages:
        print(f"  - `{pkg.name}` v{pkg.version}")


if __name__ == "__main__":
    # _print_debug_info()
    print(_get_package_info())
