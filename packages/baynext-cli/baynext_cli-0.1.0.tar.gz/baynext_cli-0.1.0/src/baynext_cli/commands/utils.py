"""Utility functions for dataset commands in Baynext CLI."""

import typer


def get_project_id_from_ctx(ctx: typer.Context) -> str:
    """Retrieve project ID from the context object.

    Args:
        ctx (typer.Context): The context object containing command-line arguments.

    Returns:
        str: The project ID if available, otherwise raises an error.

    Raises:
        typer.Exit: If the project ID is not specified in the context.

    """
    project_id = ctx.obj.get("project_id")
    if not project_id:
        typer.echo(
            "Please specify a project ID using --project-id or -p option.",
            err=True,
        )
        raise typer.Exit(1)
    return project_id
