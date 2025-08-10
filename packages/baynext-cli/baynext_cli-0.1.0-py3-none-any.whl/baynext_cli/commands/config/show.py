"""`baynext config show` command."""

import typer
from rich.console import Console
from rich.table import Table

from baynext_cli.config import get_config

app = typer.Typer()

console = Console()


@app.command()
def show() -> None:
    """Show all Baynext CLI properties."""
    config_data = get_config()
    table = Table(title="Baynext CLI Configuration")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    for key, value in config_data.items():
        table.add_row(key, str(value))

    console.print(table)
