from dataclasses import dataclass, field
from pathlib import Path

from .deployment import (
    load_deployment_snapshot,
)
from .models.deployment import DeploymentConfig, ModulesByNameAndVersion
from .models.module import ModuleConfig


class ValidationError(Exception):
    pass


@dataclass
class UpdateGroup:
    added: list[ModuleConfig] = field(default_factory=list)
    deprecated: list[ModuleConfig] = field(default_factory=list)
    restored: list[ModuleConfig] = field(default_factory=list)
    removed: list[ModuleConfig] = field(default_factory=list)


def validate_deployment(
    deployment: DeploymentConfig, deploy_folder: Path
) -> UpdateGroup:
    last_deployment = load_deployment_snapshot(deploy_folder)
    new_modules = deployment.modules
    old_modules = last_deployment.modules

    update_group = get_update_group(old_modules, new_modules)

    return update_group


def get_update_group(
    old_modules: ModulesByNameAndVersion, new_modules: ModulesByNameAndVersion
) -> UpdateGroup:
    """Get set of modules that have been updated since last deployment."""
    group: UpdateGroup = UpdateGroup()
    for name in new_modules:
        if name not in old_modules:
            group.added.extend(new_modules[name].values())
            continue

        for version, new_module in new_modules[name].items():
            if version not in old_modules[name]:
                group.added.append(new_module)
                continue

            old_module = old_modules[name][version]

            if is_modified(old_module, new_module):
                raise ValidationError(
                    f"Module {name}/{version} modified without updating version."
                )

            if old_module.metadata.deprecated == new_module.metadata.deprecated:
                continue

            if not old_module.metadata.deprecated and new_module.metadata.deprecated:
                group.deprecated.append(new_module)
            else:
                group.restored.append(new_module)

    for name in old_modules:
        if name not in new_modules:
            group.removed.extend(old_modules[name].values())
            continue

        for version, old_module in old_modules[name].items():
            if version not in new_modules[name]:
                group.removed.append(old_module)

    for module in group.removed:
        if not module.metadata.deprecated:
            raise ValidationError(
                f"Module {name}/{version} removed without prior deprecation."
            )

    return group


def is_modified(old_module: ModuleConfig, new_module: ModuleConfig):
    old_copy = old_module.model_copy(deep=True)
    new_copy = new_module.model_copy(deep=True)

    new_copy.metadata.deprecated = False
    old_copy.metadata.deprecated = False

    return not new_copy == old_copy
