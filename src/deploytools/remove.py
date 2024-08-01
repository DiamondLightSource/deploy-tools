import os
import shutil
from pathlib import Path

from .deprecate import DEPRECATED_DIR
from .layout import (
    DEPLOYMENT_ENTRYPOINTS_DIR,
    DEPLOYMENT_MODULEFILES_DIR,
    DEPLOYMENT_SIF_FILES_DIR,
)
from .models.module import ModuleConfig
from .module import get_deployed_module_versions

REMOVE_SUBDIRS = [
    DEPLOYMENT_ENTRYPOINTS_DIR,
    DEPLOYMENT_SIF_FILES_DIR,
]


class RemovalError(Exception):
    pass


def check_remove(modules: list[ModuleConfig], deployment_root: Path):
    deprecated_root = deployment_root / DEPRECATED_DIR

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        check_module_and_version_in_deprecated(name, version, deprecated_root)


def remove(modules: list[ModuleConfig], deployment_root: Path):
    """Remove a deprecated module."""
    deprecated_root = deployment_root / DEPRECATED_DIR

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        remove_deprecated_module(name, version, deprecated_root, deployment_root)


def check_module_and_version_in_deprecated(
    name: str, version: str, deprecated_root: Path
):
    versions = get_deployed_module_versions(deprecated_root)
    if version not in versions[name]:
        raise RemovalError(
            f"Cannot remove {name}/{version}. Not found in deprecated area."
        )


def remove_deprecated_module(
    name: str, version: str, deprecated_root: Path, deployment_root: Path
):
    module_file = deprecated_root / DEPLOYMENT_MODULEFILES_DIR / name / version
    os.remove(module_file)
    delete_folder_if_empty(module_file.parent)

    for subdir in REMOVE_SUBDIRS:
        src_path = deployment_root / subdir / name / version
        shutil.rmtree(src_path)

        delete_folder_if_empty(src_path.parent)


def delete_folder_if_empty(path: Path):
    try:
        path.rmdir()
    except OSError:
        pass
