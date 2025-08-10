"""Utility functions and types for the Baynext CLI."""

from enum import Enum
from typing import Annotated

from typer import Argument, Option


class OutputFormat(str, Enum):
    """Output format options."""

    TABLE = "table"
    JSON = "json"


OutputOption = Annotated[
    OutputFormat,
    Option(
        "-o",
        "--output",
        help="Output format: 'table' or 'json'",
        show_envvar=False,
    ),
]


PropertyArg = Annotated[
    str,
    Argument(
        metavar="PROPERTY",
        help="The name of the property to get",
    ),
]
