"""`baynext projects create` command."""

import typer
from baynext import Baynext
from httpx import HTTPStatusError
from rich import print_json
from rich.console import Console
from rich.table import Table

from baynext_cli.utils import OutputFormat, OutputOption

app = typer.Typer()


@app.command()
def me(
    ctx: typer.Context,
    output: OutputOption = OutputFormat.TABLE,
) -> None:
    """🆕 Create a new project."""
    try:
        client: Baynext = ctx.obj["client"]
        user = client.user.get()

        if output == OutputFormat.JSON:
            print_json(data=user.model_dump())

        else:
            console = Console()

            table = Table()
            table.add_column("Id")
            table.add_column("Name")
            table.add_column("Email")

            table.add_row(
                str(user.id),
                user.name,
                user.email,
            )

            console.print(table)

    except HTTPStatusError as exc:
        Console().print(
            f"❌ Failed to create project.\nError: {exc.response.status_code} {exc.response.text}",
            style="bold red",
        )
        raise typer.Exit(1) from exc
