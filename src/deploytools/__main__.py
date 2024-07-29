import typer

from . import __version__
from .deploy import deploy
from .deprecate import deprecate
from .models.schema import schema
from .remove import remove
from .restore import restore
from .validate import validate

__all__ = ["main"]


app = typer.Typer(no_args_is_help=True)

command = app.command(no_args_is_help=True)

command(deprecate)
command(deploy)
command(remove)
command(restore)
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
