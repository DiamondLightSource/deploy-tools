import os
import shutil
from pathlib import Path

import typer
from typing_extensions import Annotated

from .archive import ARCHIVE_DIR
from .deployment import (
    DEPLOYMENT_SUBDIRS,
    get_deployed_versions,
)

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
    archive_folder = deploy_folder / ARCHIVE_DIR
    check_module_and_version_in_archived_deployment(name, version, archive_folder)
    remove_module_paths(name, version, archive_folder)


def check_module_and_version_in_archived_deployment(
    name: str, version: str, archive_folder: Path
):
    versions = get_deployed_versions(archive_folder)
    if version not in versions[name]:
        raise RemovalError(
            f"Version {version} has not previously been archived for {name}."
        )


def remove_module_paths(name: str, version: str, archive_folder: Path):
    for subdir in DEPLOYMENT_SUBDIRS:
        archive_path = archive_folder / subdir / name / version
        if archive_path.is_dir():
            shutil.rmtree(archive_path)
        else:
            os.remove(archive_path)

        try:
            # Delete the module name directory if it is empty
            archive_path.parent.rmdir()
        except OSError:
            pass


def main():
    typer.run(remove)
