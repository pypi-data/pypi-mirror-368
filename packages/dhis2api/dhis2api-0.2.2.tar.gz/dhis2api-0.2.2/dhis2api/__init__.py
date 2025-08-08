"""Convenience imports and package metadata for :mod:`dhis2api`."""

from importlib.metadata import PackageNotFoundError, version
from .country import Country

__all__ = ["Country", "__version__"]


def _read_version_fallback() -> str:
    """Return version from pyproject.toml if distribution metadata is missing."""
    try:
        # Python 3.11+: stdlib tomllib
        import tomllib  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover
        try:
            import tomli as tomllib  # fallback for 3.10/3.9 if installed
        except Exception:
            return "unknown"

    import os
    from pathlib import Path

    # Find pyproject.toml relative to this file
    root = Path(__file__).resolve().parents[1]
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return "unknown"

    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        # Poetry layout
        return data.get("tool", {}).get("poetry", {}).get("version", "unknown")
    except Exception:  # pragma: no cover
        return "unknown"


try:
    # must match the package name in pyproject.toml
    __version__ = version("dhis2api")
# not installed (e.g., `poetry install --no-root`)
except PackageNotFoundError:
    __version__ = _read_version_fallback()
