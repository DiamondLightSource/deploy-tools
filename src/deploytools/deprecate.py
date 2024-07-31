from pathlib import Path

from .deployment import (
    DEPLOYMENT_MODULEFILES_DIR,
    get_deployed_versions,
    move_modulefile,
)
from .models.module import ModuleConfig

DEPRECATED_DIR = "deprecated"


class DeprecateError(Exception):
    pass


def check_deprecate(modules: list[ModuleConfig], deploy_folder: Path):
    deprecated_folder = deploy_folder / DEPRECATED_DIR

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        check_module_and_version_exist_in_deployment(name, version, deploy_folder)
        check_deprecated_free_for_module_and_version(name, version, deprecated_folder)


def deprecate(modules: list[ModuleConfig], deploy_folder: Path):
    """Deprecate a list of modules.

    This will move the modulefile to a 'deprecated' directory."""
    deprecated_folder = deploy_folder / DEPRECATED_DIR

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        move_modulefile(name, version, deploy_folder, deprecated_folder)


def check_module_and_version_exist_in_deployment(
    name: str, version: str, deploy_folder: Path
):
    versions = get_deployed_versions(deploy_folder)
    if version not in versions[name]:
        raise DeprecateError(
            f"Cannot deprecate {name}/{version}. Not found in deployment area."
        )


def check_deprecated_free_for_module_and_version(
    name: str, version: str, deprecated_folder: Path
):
    full_path = deprecated_folder / DEPLOYMENT_MODULEFILES_DIR / name / version
    if full_path.exists():
        raise DeprecateError(
            f"Cannot deprecate {name}/{version}. Path already exists:\n{full_path}"
        )
