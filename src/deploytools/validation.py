from collections import defaultdict
from pathlib import Path

from .archive import ARCHIVE_DIR
from .deployment import (
    ModulesByName,
    ModuleVersionsByName,
    get_deployed_versions,
    get_modules_by_name,
    load_deployment_snapshot,
)
from .models.deployment import DeploymentConfig
from .models.module import ModuleConfig


class ValidationError(Exception):
    pass


def validate_deployment(
    deployment: DeploymentConfig, deploy_folder: Path
) -> list[ModuleConfig]:
    last_deployment = load_deployment_snapshot(deploy_folder)
    new_modules = get_modules_by_name(deployment, validate=True)
    last_modules = get_modules_by_name(last_deployment, validate=False)
    deployed_versions = get_deployed_versions(deploy_folder)

    modified_modules = get_modified_modules(last_modules, new_modules)
    is_member, name, version = are_modules_in_deployment(
        deployed_versions, modified_modules
    )
    if is_member:
        raise ValidationError(f"Module {name}/{version} already deployed.")

    archive_folder = deploy_folder / ARCHIVE_DIR
    archived_versions = get_deployed_versions(archive_folder)
    is_member, name, version = are_modules_in_deployment(
        archived_versions, modified_modules
    )
    if is_member:
        raise ValidationError(f"Module {name}/{version} already exists in archive.")

    modified_list: list[ModuleConfig] = []
    for versioned_list in modified_modules.values():
        for _, module in versioned_list:
            modified_list.append(module)
    return modified_list


def get_modified_modules(
    old_modules: ModulesByName, new_modules: ModulesByName
) -> ModulesByName:
    """Get list of modules that have been modified since last deployment.

    We do not care about deleted modules / versions as they require no deployment."""
    modified_modules: ModulesByName = defaultdict(list)
    for name in new_modules:
        if name not in old_modules:
            modified_modules[name] = new_modules[name]
            continue

        old_modules_map = dict(old_modules[name])
        for version, new_config in new_modules[name]:
            if version not in old_modules_map:
                modified_modules[name].append((version, new_config))
                continue

            if not new_config == old_modules_map[version]:
                raise ValidationError(
                    f"Module {name}/{version} modified without updating version."
                )

    return modified_modules


def are_modules_in_deployment(
    deployed_versions: ModuleVersionsByName, modules: ModulesByName
) -> tuple[bool, str, str]:
    for name, modules_list in modules.items():
        for version, _ in modules_list:
            if version in deployed_versions[name]:
                return True, name, version

    return False, "", ""
