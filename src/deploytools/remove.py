from pathlib import Path

import typer
from typing_extensions import Annotated

from .archive import ARCHIVE_DIR
from .deployment import get_deployed_versions, remove_module

app = typer.Typer()

app.command()


class RemovalError(Exception):
    pass


def remove(
    name: str,
    version: str,
    deploy_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
):
    """Remove an archived module."""
    archive_folder = deploy_folder / ARCHIVE_DIR
    check_module_and_version_in_archived_deployment(name, version, archive_folder)
    remove_module(name, version, archive_folder)


def check_module_and_version_in_archived_deployment(
    name: str, version: str, archive_folder: Path
):
    versions = get_deployed_versions(archive_folder)
    if version not in versions[name]:
        raise RemovalError(
            f"Version {version} has not previously been archived for {name}."
        )


def main():
    typer.run(remove)
