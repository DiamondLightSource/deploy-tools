from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .models.schema import generate_schema
from .sync import synchronise
from .validate import validate_configuration

__all__ = ["main"]


app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def sync(
    deployment_root: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
    config_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
) -> None:
    """Sync deployment folder with current configuration"""
    synchronise(deployment_root, config_folder)


@app.command(no_args_is_help=True)
def validate(
    deployment_root: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
    config_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
) -> None:
    """Validate deployment configuration and print a list of modules for deployment.

    This is the same validation that the deploy-tools sync command uses."""
    validate_configuration(deployment_root, config_folder)


@app.command(no_args_is_help=True)
def schema(
    output_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
) -> None:
    """Generate JSON schemas for yaml configuration files."""
    generate_schema(output_path)


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


if __name__ == "__main__":
    main()
