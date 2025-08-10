"""Baynext CLI."""

import tomllib
from pathlib import Path

with Path.open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

__version__ = pyproject["project"]["version"]

__all__ = [
    "__version__",
]
