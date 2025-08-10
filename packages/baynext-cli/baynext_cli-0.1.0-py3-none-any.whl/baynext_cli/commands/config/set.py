"""`baynext config set` command."""

import typer
from rich import print as rprint

from baynext_cli.config import set_config
from baynext_cli.utils import PropertyArg

app = typer.Typer()


@app.command()
def set(property_: PropertyArg, value: str) -> None:  # noqa: A001
    """Set the value of a specific Baynext CLI property."""
    set_config(property_, value)
    rprint(f"✅ Property [bold]{property_}[/bold] set to [bold]{value}[/bold]")
