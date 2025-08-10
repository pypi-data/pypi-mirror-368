import nox

VERSIONS: list[str] = ["3.11", "3.12", "3.13"]


@nox.session(venv_backend="uv", tags=["lint"])
def ruff_check(session: nox.Session) -> None:
    """Run ruff linting and formatting checks (CI-friendly, no changes)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--fix",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "check",
        ".",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--check",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["lint", "fix"])
def ruff_fix(session: nox.Session) -> None:
    """Run ruff linting and formatting with auto-fix (development)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--fix",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["typecheck"])
def pyright(session: nox.Session) -> None:
    """Run static type checks."""
    session.install("pyright")
    session.run("pyright")


@nox.session(python=VERSIONS, venv_backend="uv")
def test_all_tests(session: nox.Session):
    session.install("-e", ".")
    session.install("pytest")
    session.run("pytest")
