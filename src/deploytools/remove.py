from pathlib import Path

import typer
from typing_extensions import Annotated

from .deployment import get_deployed_versions, remove_module
from .deprecate import DEPRECATED_DIR


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
    remove_module(name, version, deprecated_folder)


def check_module_and_version_in_deprecated_deployment(
    name: str, version: str, deprecated_folder: Path
):
    versions = get_deployed_versions(deprecated_folder)
    if version not in versions[name]:
        raise RemovalError(
            f"Version {version} has not previously been deprecated for {name}."
        )
