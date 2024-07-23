from pathlib import Path

import typer
from typing_extensions import Annotated

from .archive import ARCHIVE_DIR
from .deployment import (
    DEPLOYMENT_MODULEFILES_DIR,
    get_deployed_versions,
    move_module,
)


class RestoreError(Exception):
    pass


def restore(
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
    """Restore a previously archived module."""
    archive_folder = deploy_folder / ARCHIVE_DIR

    check_archive_includes_module_and_version(name, version, archive_folder)
    check_module_and_version_not_in_deployment(name, version, deploy_folder)

    move_module(name, version, archive_folder, deploy_folder)


def check_module_and_version_not_in_deployment(
    name: str, version: str, deploy_folder: Path
):
    versions = get_deployed_versions(deploy_folder)
    if version in versions[name]:
        raise RestoreError(
            f"Module {name}/{version} already exists in deployment. Cannot restore"
        )


def check_archive_includes_module_and_version(
    name: str, version: str, archive_folder: Path
):
    full_path = archive_folder / DEPLOYMENT_MODULEFILES_DIR / name / version
    if not full_path.exists():
        raise RestoreError(
            f"Module {name}/{version} does not exist in archive. Cannot restore."
        )
