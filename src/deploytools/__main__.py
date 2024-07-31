import typer

from . import __version__
from .models.schema import schema
from .sync import sync
from .validate import validate

__all__ = ["main"]


app = typer.Typer(no_args_is_help=True)

command = app.command(no_args_is_help=True)

command(sync)
command(validate)
command(schema)


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        help="Show program's version number and exit",
        callback=version_callback,
    ),
):
    pass


def main():
    app()
