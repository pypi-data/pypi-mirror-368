"""`baynext config` command."""

import typer

from .get import app as get_app
from .set import app as set_app
from .show import app as show_app

app = typer.Typer(
    name="config",
    help="⚙️ View and edit Baynext CLI properties",
    no_args_is_help=True,
)

app.add_typer(get_app)
app.add_typer(set_app)
app.add_typer(show_app)
