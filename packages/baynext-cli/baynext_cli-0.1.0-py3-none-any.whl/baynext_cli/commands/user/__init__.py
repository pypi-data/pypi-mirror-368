"""`baynext user` commands."""

import typer

from .me import app as me_app

app = typer.Typer(
    name="user",
    help="👥 Manage your Baynext user profile",
)

app.add_typer(me_app)
