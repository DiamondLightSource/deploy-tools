from pathlib import Path

import typer
from typing_extensions import Annotated

from .deployment import (
    DEPLOYMENT_SUBDIRS,
    get_deployed_versions,
    get_modules_by_name,
    load_deployment_snapshot,
    move_module,
)

app = typer.Typer()

app.command()


ARCHIVE_DIR = "archived"


class ArchiveError(Exception):
    pass


def archive(
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
    """Archive a module by moving it to a separate directory.

    There is no expectation that the module will work correctly after archiving."""
    archive_folder = deploy_folder / ARCHIVE_DIR

    check_module_and_version_not_in_deployment_config(name, version, deploy_folder)
    check_module_and_version_in_previous_deployment(name, version, deploy_folder)
    check_archive_free_for_module_and_version(name, version, archive_folder)

    move_module(name, version, deploy_folder, archive_folder)


def check_module_and_version_not_in_deployment_config(
    name: str, version: str, deploy_folder: Path
):
    deployment = load_deployment_snapshot(deploy_folder, allow_empty=False)
    modules = get_modules_by_name(deployment, validate=False)

    for v, _ in modules[name]:
        if v == version:
            raise ArchiveError(
                f"Module {name}/{version} still exists in deployment configuration."
            )


def check_module_and_version_in_previous_deployment(
    name: str, version: str, deploy_folder: Path
):
    versions = get_deployed_versions(deploy_folder)
    if version not in versions[name]:
        raise ArchiveError(
            f"Version {version} has not previously been deployed for {name}."
        )


def check_archive_free_for_module_and_version(
    name: str, version: str, archive_folder: Path
):
    for subdir in DEPLOYMENT_SUBDIRS:
        full_path = archive_folder / subdir / name / version
        if full_path.exists():
            raise ArchiveError(
                f"Cannot archive {name}/{version}. Path already exists:\n{full_path}"
            )
