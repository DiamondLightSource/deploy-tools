import shutil
from pathlib import Path

import typer
from typing_extensions import Annotated

from .deployment import (
    DEPLOYMENT_ENTRYPOINTS_DIR,
    DEPLOYMENT_MODULEFILES_DIR,
    DEPLOYMENT_SIF_FILES_DIR,
    get_deployed_versions,
    get_modules_by_name,
    load_deployment_snapshot,
)

app = typer.Typer()

app.command()

PATHS_TO_ARCHIVE = [
    DEPLOYMENT_ENTRYPOINTS_DIR,
    DEPLOYMENT_MODULEFILES_DIR,
    DEPLOYMENT_SIF_FILES_DIR,
]


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
    archive_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
):
    check_module_and_version_not_in_deployment_config(name, version, deploy_folder)
    check_module_and_version_in_previous_deployment(name, version, deploy_folder)
    check_archive_free_for_module_and_version(name, version, archive_folder)

    move_module_paths(name, version, deploy_folder, archive_folder)


def check_module_and_version_not_in_deployment_config(
    name: str, version: str, deploy_folder: Path
):
    deployment = load_deployment_snapshot(deploy_folder, allow_empty=False)
    modules = get_modules_by_name(deployment, validate=False)

    for v, _ in modules[name]:
        if v == version:
            raise ArchiveError(
                f"Version {version} still exists in latest deployment configuration for"
                f" {name}."
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
    for subdir in PATHS_TO_ARCHIVE:
        full_path = archive_folder / subdir / name / version
        if full_path.exists():
            raise ArchiveError(
                f"Path {full_path} already exists. Cannot archive {name}/{version}."
            )


def move_module_paths(
    name: str, version: str, deploy_folder: Path, archive_folder: Path
):
    for subdir in PATHS_TO_ARCHIVE:
        deploy_path = deploy_folder / subdir / name / version

        # Not all modules require the use of all 3 sub dirs
        if deploy_path.exists():
            archive_path = archive_folder / subdir / name / version
            archive_path.parent.mkdir(parents=True, exist_ok=False)
            shutil.move(deploy_path, archive_path)


def main():
    typer.run(archive)
