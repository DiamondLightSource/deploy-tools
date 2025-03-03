import logging
from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .compare import compare_to_snapshot
from .models.schema import generate_schema
from .sync import synchronise
from .validate import validate_and_check_configuration

__all__ = ["main"]


def verbose_callback(value: int) -> None:
    match value:
        case 2:
            level = logging.DEBUG
        case 1:
            level = logging.INFO
        case 0 | _:
            level = logging.WARNING

    logging.basicConfig(
        format="%(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S", level=level
    )


DEPLOYMENT_ROOT_ARGUMENT = Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        show_default=False,
        help="Root of the deployment area to use.",
    ),
]
CONFIG_FOLDER_ARGUMENT = Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=False,
        dir_okay=True,
        show_default=False,
        help="Folder containing configuration for deployment.",
    ),
]
SCHEMA_OUTPUT_PATH_ARGUMENT = Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        show_default=False,
        help="Output path to write all .json schema files to.",
    ),
]
FROM_SCRATCH_OPTION = Annotated[
    bool,
    typer.Option(
        "--from-scratch/--not-from-scratch",
        help="Deploy into an empty deployment area.",
    ),
]
TEST_BUILD_OPTION = Annotated[
    bool,
    typer.Option(
        "--test-build/--no-test-build", help="Test the build in a temporary directory."
    ),
]
USE_PREVIOUS_OPTION = Annotated[
    bool,
    typer.Option(
        "--use-previous/--use-current", help="Use previous snapshot for comparison."
    ),
]
VERBOSE_OPTION = Annotated[
    int,
    typer.Option(
        "--verbose",
        "-v",
        help="Set verbosity level by passing option multiple times.",
        count=True,
        max=2,
        clamp=True,
        show_default="WARNING",
        callback=verbose_callback,
    ),
]


app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def sync(
    deployment_root: DEPLOYMENT_ROOT_ARGUMENT,
    config_folder: CONFIG_FOLDER_ARGUMENT,
    from_scratch: FROM_SCRATCH_OPTION = False,
    verbose: VERBOSE_OPTION = 0,
) -> None:
    """Synchronise deployment root with current configuration.

    This will also run the validate command beforehand, but without printing the
    expected changes.
    """
    synchronise(deployment_root, config_folder, from_scratch)


@app.command(no_args_is_help=True)
def validate(
    deployment_root: DEPLOYMENT_ROOT_ARGUMENT,
    config_folder: CONFIG_FOLDER_ARGUMENT,
    from_scratch: FROM_SCRATCH_OPTION = False,
    test_build: TEST_BUILD_OPTION = True,
    verbose: VERBOSE_OPTION = 0,
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
    deployment_root: DEPLOYMENT_ROOT_ARGUMENT,
    use_previous: USE_PREVIOUS_OPTION = False,
    verbose: VERBOSE_OPTION = 0,
) -> None:
    """Compare the deployment snapshot to deployed modules in the deployment root.

    This allows us to identify any discrepancies. If there was an error during the
    deploy step, we can use this function to determine any required steps for fixing
    files in the deployment root.
    """
    compare_to_snapshot(deployment_root, use_previous)


@app.command(no_args_is_help=True)
def schema(
    output_path: SCHEMA_OUTPUT_PATH_ARGUMENT,
    verbose: VERBOSE_OPTION = 0,
) -> None:
    """Generate JSON schemas for yaml configuration files."""
    generate_schema(output_path)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def common(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show program's version number and exit.",
            callback=version_callback,
        ),
    ] = None,
) -> None:
    pass


def main() -> None:
    app()


if __name__ == "__main__":
    main()
