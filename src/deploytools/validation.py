from collections import defaultdict
from pathlib import Path

from .deployment import (
    ModuleVersionsByName,
    get_deployed_versions,
    load_deployment_snapshot,
)
from .deprecate import DEPRECATED_DIR
from .models.deployment import DeploymentConfig, ModulesByNameAndVersion
from .models.module import ModuleConfig


class ValidationError(Exception):
    pass


def validate_deployment(
    deployment: DeploymentConfig, deploy_folder: Path
) -> list[ModuleConfig]:
    last_deployment = load_deployment_snapshot(deploy_folder)
    new_modules = deployment.modules
    last_modules = last_deployment.modules
    deployed_versions = get_deployed_versions(deploy_folder)

    modified_modules = get_modified_modules(last_modules, new_modules)
    is_member, name, version = are_modules_in_deployment(
        deployed_versions, modified_modules
    )
    if is_member:
        raise ValidationError(f"Module {name}/{version} already deployed.")

    deprecated_folder = deploy_folder / DEPRECATED_DIR
    deprecated_versions = get_deployed_versions(deprecated_folder)
    is_member, name, version = are_modules_in_deployment(
        deprecated_versions, modified_modules
    )
    if is_member:
        raise ValidationError(f"Module {name}/{version} exists as deprecated module.")

    modified_list: list[ModuleConfig] = []
    for versioned_modules in modified_modules.values():
        modified_list.extend(versioned_modules.values())

    return modified_list


def get_modified_modules(
    old_modules: ModulesByNameAndVersion, new_modules: ModulesByNameAndVersion
) -> ModulesByNameAndVersion:
    """Get list of modules that have been modified since last deployment.

    We do not care about deleted modules / versions as they require no deployment."""
    modified_modules: ModulesByNameAndVersion = defaultdict(dict)
    for name in new_modules:
        if name not in old_modules:
            modified_modules[name] = new_modules[name]
            continue

        for version, new_config in new_modules[name].items():
            if version not in old_modules[name]:
                modified_modules[name][version] = new_config
                continue

            if not new_config == old_modules[name][version]:
                raise ValidationError(
                    f"Module {name}/{version} modified without updating version."
                )

    return modified_modules


def are_modules_in_deployment(
    deployed_versions: ModuleVersionsByName, modules: ModulesByNameAndVersion
) -> tuple[bool, str, str]:
    for name, versioned_modules in modules.items():
        for version in versioned_modules:
            if version in deployed_versions[name]:
                return True, name, version

    return False, "", ""
