"""Main entry point."""

from typing import Annotated

import typer
from baynext import Baynext

from baynext_cli import __version__
from baynext_cli.commands import config, user
from baynext_cli.config import get_config_value

app = typer.Typer(
    name=f"Baynext CLI {__version__}",
    help="⚡️ Baynext CLI - Manage your projects and teams from the command line",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add command groups
app.add_typer(user.app, rich_help_panel="User Commands")
app.add_typer(config.app)


@app.command()
def version() -> None:
    """📋 Show version information."""
    typer.echo(f"Baynext CLI v{__version__}")


@app.callback()
def main_callback(
    ctx: typer.Context,
    token: Annotated[
        str,
        typer.Option(
            "--token",
            "-t",
            help="API token for authentication",
            show_default=True,
            envvar="BAYNEXT_TOKEN",
        ),
    ] = get_config_value("token"),
) -> None:
    """Manage datasets within a project.

    Use this command to list, get details of, or manage datasets in your projects.
    """
    if not token:
        ctx.obj = {
            "client": Baynext(),
        }

    else:
        ctx.obj = {
            "token": token,
            "client": Baynext(http_bearer=token),
        }


if __name__ == "__main__":
    app()
