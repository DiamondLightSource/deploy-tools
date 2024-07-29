from pathlib import Path

import typer
from typing_extensions import Annotated

from .deployment import (
    DEPLOYMENT_MODULEFILES_DIR,
    get_deployed_versions,
    get_modules_by_name,
    load_deployment_snapshot,
    move_modulefile,
)

DEPRECATED_DIR = "deprecated"


class DeprecateError(Exception):
    pass


def deprecate(
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
    """Deprecate a module by moving it to a separate directory.

    There is no expectation that the module will work correctly after archiving."""
    deprecated_folder = deploy_folder / DEPRECATED_DIR

    check_module_and_version_not_in_deployment_config(name, version, deploy_folder)
    check_module_and_version_in_previous_deployment(name, version, deploy_folder)
    check_deprecated_free_for_module_and_version(name, version, deprecated_folder)

    move_modulefile(name, version, deploy_folder, deprecated_folder)


def check_module_and_version_not_in_deployment_config(
    name: str, version: str, deploy_folder: Path
):
    deployment = load_deployment_snapshot(deploy_folder, allow_empty=False)
    modules = get_modules_by_name(deployment, validate=False)

    for v, _ in modules[name]:
        if v == version:
            raise DeprecateError(
                f"Module {name}/{version} still exists in deployment configuration."
            )


def check_module_and_version_in_previous_deployment(
    name: str, version: str, deploy_folder: Path
):
    versions = get_deployed_versions(deploy_folder)
    if version not in versions[name]:
        raise DeprecateError(
            f"Version {version} has not previously been deployed for {name}."
        )


def check_deprecated_free_for_module_and_version(
    name: str, version: str, deprecated_folder: Path
):
    full_path = deprecated_folder / DEPLOYMENT_MODULEFILES_DIR / name / version
    if full_path.exists():
        raise DeprecateError(
            f"Cannot deprecate {name}/{version}. Path already exists:\n{full_path}"
        )
