import os
import shutil
from pathlib import Path

import typer
from typing_extensions import Annotated

from .deployment import (
    DEPLOYMENT_ENTRYPOINTS_DIR,
    DEPLOYMENT_MODULEFILES_DIR,
    DEPLOYMENT_SIF_FILES_DIR,
    get_deployed_versions,
)
from .deprecate import DEPRECATED_DIR

REMOVE_SUBDIRS = [
    DEPLOYMENT_ENTRYPOINTS_DIR,
    DEPLOYMENT_SIF_FILES_DIR,
]


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
    """Remove a deprecated module."""
    deprecated_folder = deploy_folder / DEPRECATED_DIR
    check_module_and_version_in_deprecated_deployment(name, version, deprecated_folder)
    remove_deprecated_module(name, version, deprecated_folder, deploy_folder)


def check_module_and_version_in_deprecated_deployment(
    name: str, version: str, deprecated_folder: Path
):
    versions = get_deployed_versions(deprecated_folder)
    if version not in versions[name]:
        raise RemovalError(
            f"Version {version} has not previously been deprecated for {name}."
        )


def remove_deprecated_module(
    name: str, version: str, deprecated_folder: Path, deploy_folder: Path
):
    modulefile_path = deprecated_folder / DEPLOYMENT_MODULEFILES_DIR / name / version
    os.remove(modulefile_path)

    for subdir in REMOVE_SUBDIRS:
        src_path = deploy_folder / subdir / name / version
        shutil.rmtree(src_path)

        try:
            # Delete the module name directory if it is empty
            src_path.parent.rmdir()
        except OSError:
            pass
