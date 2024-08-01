from pathlib import Path

from .deployment import (
    DEPLOYMENT_MODULEFILES_DIR,
    get_deployed_versions,
)
from .deprecate import DEPRECATED_DIR
from .models.module import ModuleConfig
from .module import move_modulefile


class RestoreError(Exception):
    pass


def check_restore(modules: list[ModuleConfig], deployment_root: Path):
    deprecated_root = deployment_root / DEPRECATED_DIR
    deployed_versions = get_deployed_versions(deployment_root)

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        module_file = deprecated_root / DEPLOYMENT_MODULEFILES_DIR / name / version
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
    deprecated_root = deployment_root / DEPRECATED_DIR

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        move_modulefile(name, version, deprecated_root, deployment_root)
