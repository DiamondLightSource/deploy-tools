from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .compare import compare_to_snapshot
from .models.schema import generate_schema
from .sync import synchronise
from .validate import validate_and_check_configuration

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
    from_scratch: Annotated[bool, typer.Option()] = False,
) -> None:
    """Synchronise deployment root with current configuration.

    This will also run the validate command beforehand, but without printing the
    expected changes.
    """
    synchronise(deployment_root, config_folder, from_scratch)


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
    from_scratch: Annotated[bool, typer.Option()] = False,
    test_build: Annotated[bool, typer.Option()] = True,
) -> None:
    """Validate deployment configuration and print a list of expected module changes.

    If specified, this includes a test build of the provided configuration. The
    configuration validation is the same as used by the deploy-tools sync command.
    """
    validate_and_check_configuration(
        deployment_root, config_folder, from_scratch, test_build
    )


@app.command(no_args_is_help=True)
def compare(
    deployment_root: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
    use_previous: Annotated[bool, typer.Option()] = False,
) -> None:
    """Compare the deployment snapshot to deployed modules in the deployment root.

    This allows us to identify any discrepancies. If there was an error during the
    deploy step, we can use this function to determine any required steps for fixing
    files in the deployment root.
    """
    compare_to_snapshot(deployment_root, use_previous)


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


def version_callback(value: bool) -> None:
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
) -> None:
    pass


def main() -> None:
    app()


if __name__ == "__main__":
    main()
