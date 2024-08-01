from pathlib import Path

from .layout import (
    DEPRECATED_ROOT_NAME,
    MODULEFILES_ROOT_NAME,
)
from .models.module import ModuleConfig
from .module import get_deployed_module_versions, move_modulefile


class DeprecateError(Exception):
    pass


def check_deprecate(modules: list[ModuleConfig], deployment_root: Path):
    deprecated_root = deployment_root / DEPRECATED_ROOT_NAME

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        check_module_and_version_exist_in_deployment(name, version, deployment_root)
        check_deprecated_free_for_module_and_version(name, version, deprecated_root)


def deprecate(modules: list[ModuleConfig], deployment_root: Path):
    """Deprecate a list of modules.

    This will move the modulefile to a 'deprecated' directory."""
    deprecated_root = deployment_root / DEPRECATED_ROOT_NAME

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        move_modulefile(name, version, deployment_root, deprecated_root)


def check_module_and_version_exist_in_deployment(
    name: str, version: str, deployment_root: Path
):
    versions = get_deployed_module_versions(deployment_root)
    if version not in versions[name]:
        raise DeprecateError(
            f"Cannot deprecate {name}/{version}. Not found in deployment area."
        )


def check_deprecated_free_for_module_and_version(
    name: str, version: str, deprecated_root: Path
):
    module_file = deprecated_root / MODULEFILES_ROOT_NAME / name / version
    if module_file.exists():
        raise DeprecateError(
            f"Cannot deprecate {name}/{version}. Path already exists:\n{module_file}"
        )
