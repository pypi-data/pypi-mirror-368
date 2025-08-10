"""`baynext config get` command."""

import typer

from baynext_cli.config import get_config
from baynext_cli.utils import PropertyArg

app = typer.Typer()


@app.command()
def get(property_: PropertyArg) -> None:
    """Get the value of a specific Baynext CLI property."""
    config_data = get_config()
    value = config_data.get(property_)
    if value is None:
        typer.echo(f"Property '{property_}' is not set.", err=True)
        raise typer.Exit(1)
    typer.echo(f"{property_}: {value}")
