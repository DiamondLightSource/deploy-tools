from pathlib import Path

from .layout import (
    DEPRECATED_ROOT_NAME,
    MODULEFILES_ROOT_NAME,
)
from .models.module import ModuleConfig
from .module import get_deployed_module_versions, move_modulefile


class RestoreError(Exception):
    pass


def check_restore(modules: list[ModuleConfig], deployment_root: Path):
    deprecated_root = deployment_root / DEPRECATED_ROOT_NAME
    deployed_versions = get_deployed_module_versions(deployment_root)

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        module_file = deprecated_root / MODULEFILES_ROOT_NAME / name / version
        if not module_file.exists():
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if version in deployed_versions[name]:
            raise RestoreError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def restore(modules: list[ModuleConfig], deployment_root: Path):
    """Restore a previously deprecated module."""
    deprecated_root = deployment_root / DEPRECATED_ROOT_NAME

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        move_modulefile(name, version, deprecated_root, deployment_root)
