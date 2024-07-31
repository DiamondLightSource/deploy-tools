from pathlib import Path

from .deployment import (
    DEPLOYMENT_MODULEFILES_DIR,
    get_deployed_versions,
    move_modulefile,
)
from .deprecate import DEPRECATED_DIR
from .models.module import ModuleConfig


class RestoreError(Exception):
    pass


def check_restore(modules: list[ModuleConfig], deploy_folder: Path):
    deprecated_folder = deploy_folder / DEPRECATED_DIR
    deployed_versions = get_deployed_versions(deploy_folder)

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        modulefile = deprecated_folder / DEPLOYMENT_MODULEFILES_DIR / name / version
        if not modulefile.exists():
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if version in deployed_versions[name]:
            raise RestoreError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def restore(modules: list[ModuleConfig], deploy_folder: Path):
    """Restore a previously deprecated module."""
    deprecated_folder = deploy_folder / DEPRECATED_DIR

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        move_modulefile(name, version, deprecated_folder, deploy_folder)
