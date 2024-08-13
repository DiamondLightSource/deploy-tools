from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

import typer
from typing_extensions import Annotated

from .default_versions import check_default_versions
from .deploy import check_deploy
from .deprecate import check_deprecate
from .layout import Layout
from .models.deployment import (
    DefaultVersionsByName,
    Deployment,
    ModulesByNameAndVersion,
)
from .models.load import load_deployment
from .models.module import Module
from .module import (
    DEVELOPMENT_VERSION,
    ModuleVersionsByName,
    is_module_dev_mode,
)
from .remove import check_remove
from .restore import check_restore
from .snapshot import load_snapshot
from .update import check_update


class ValidationError(Exception):
    pass


@dataclass
class UpdateGroup:
    added: list[Module] = field(default_factory=list)
    updated: list[Module] = field(default_factory=list)
    deprecated: list[Module] = field(default_factory=list)
    restored: list[Module] = field(default_factory=list)
    removed: list[Module] = field(default_factory=list)


def validate(
    deployment_root: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
    config_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
) -> None:
    """Validate deployment configuration and print a list of modules for deployment.

    This is the same validation that the deploytools sync command uses."""
    deployment = load_deployment(config_folder)
    layout = Layout(deployment_root)
    snapshot = load_snapshot(layout)

    update_group = validate_deployment(deployment, snapshot)
    default_versions = validate_default_versions(deployment)

    check_actions(update_group, default_versions, layout)
    display_updates(update_group)


def check_actions(
    update_group: UpdateGroup, default_versions: DefaultVersionsByName, layout: Layout
) -> None:
    check_deploy(update_group.added, layout)
    check_update(update_group.updated, layout)
    check_deprecate(update_group.deprecated, layout)
    check_restore(update_group.restored, layout)
    check_remove(update_group.removed, layout)

    check_default_versions(default_versions, layout)


def display_updates(update_group: UpdateGroup) -> None:
    display_config = {
        "deployed": update_group.added,
        "updated": update_group.updated,
        "deprecated": update_group.deprecated,
        "restored": update_group.restored,
        "removed": update_group.removed,
    }

    for action, modules in display_config.items():
        print(f"Modules to be {action}:")

        for module in modules:
            print(f"{module.metadata.name}/{module.metadata.version}")

        print()


def validate_deployment(deployment: Deployment, snapshot: Deployment) -> UpdateGroup:
    old_modules = snapshot.modules
    new_modules = deployment.modules

    validate_module_dependencies(deployment)
    return get_update_group(old_modules, new_modules)


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
                if is_module_dev_mode(new_module):
                    group.updated.append(new_module)
                    continue

                raise ValidationError(
                    f"Module {name}/{version} modified without updating version."
                )

            if not old_module.metadata.deprecated and new_module.metadata.deprecated:
                group.deprecated.append(new_module)
            elif old_module.metadata.deprecated and not new_module.metadata.deprecated:
                group.restored.append(new_module)

    for name in old_modules:
        if name not in new_modules:
            group.removed.extend(old_modules[name].values())
            continue

        for version, old_module in old_modules[name].items():
            if version not in new_modules[name]:
                group.removed.append(old_module)

    validate_added_modules(group.added)
    validate_updated_modules(group.updated)
    validate_deprecated_modules(group.deprecated)
    validate_removed_modules(group.removed)

    return group


def is_modified(old_module: Module, new_module: Module) -> bool:
    new_copy = new_module.model_copy(deep=True)
    new_copy.metadata.deprecated = old_module.metadata.deprecated

    return not new_copy == old_module


def validate_added_modules(modules: list[Module]) -> None:
    for module in modules:
        metadata = module.metadata
        if metadata.deprecated:
            if is_module_dev_mode(module):
                raise ValidationError(
                    f"Module {metadata.name}/{metadata.version} cannot be specified as"
                    f"deprecated as it is in development mode."
                )

            raise ValidationError(
                f"Module {metadata.name}/{metadata.version} cannot have deprecated "
                f"status on initial creation."
            )


def validate_updated_modules(modules: list[Module]) -> None:
    for module in modules:
        metadata = module.metadata
        if metadata.deprecated:
            raise ValidationError(
                f"Module {metadata.name}/{metadata.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def validate_deprecated_modules(modules: list[Module]) -> None:
    for module in modules:
        if is_module_dev_mode(module):
            metadata = module.metadata
            raise ValidationError(
                f"Module {metadata.name}/{metadata.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def validate_removed_modules(modules: list[Module]) -> None:
    for module in modules:
        if not is_module_dev_mode(module) and not module.metadata.deprecated:
            raise ValidationError(
                f"Module {module.metadata.name}/{module.metadata.version} removed "
                "without prior deprecation."
            )


def validate_default_versions(deployment: Deployment) -> DefaultVersionsByName:
    final_deployed_modules = get_final_deployed_module_versions(deployment)

    for name, version in deployment.settings.default_versions.items():
        if version not in final_deployed_modules[name]:
            raise ValidationError(
                f"Unable to configure {name}/{version} as default; module will not "
                f"exist."
            )

    default_versions = get_all_default_versions(
        deployment.settings.default_versions, final_deployed_modules
    )

    return default_versions


def get_final_deployed_module_versions(
    deployment: Deployment,
) -> ModuleVersionsByName:
    final_versions: dict[str, list[str]] = defaultdict(list)
    for name, module_versions in deployment.modules.items():
        final_versions[name] = [
            version
            for version, module in module_versions.items()
            if not module.metadata.deprecated
        ]

    return final_versions


def get_all_default_versions(
    initial_defaults: DefaultVersionsByName,
    final_deployed_modules: ModuleVersionsByName,
) -> DefaultVersionsByName:
    final_defaults: DefaultVersionsByName = {}
    final_defaults.update(initial_defaults)

    for name in final_deployed_modules:
        if name not in final_defaults:
            version_list = deepcopy(final_deployed_modules[name])
            version_list.sort()
            if len(version_list) == 1 or not version_list[-1] == DEVELOPMENT_VERSION:
                final_defaults[name] = version_list[-1]
            else:
                final_defaults[name] = version_list[-2]

    return final_defaults


def validate_module_dependencies(deployment: Deployment) -> None:
    final_deployed_modules = get_final_deployed_module_versions(deployment)

    for name, module_versions in deployment.modules.items():
        for version, module in module_versions.items():
            for dependency in module.metadata.dependencies:
                dep_name = dependency.name
                dep_version = dependency.version
                if dep_name in final_deployed_modules:
                    if dep_version is None:
                        raise ValidationError(
                            f"Module {name}/{version} must use specific version for "
                            f"module dependency {dep_name} as it is in configuration."
                        )

                    if dep_version not in final_deployed_modules[dep_name]:
                        raise ValidationError(
                            f"Module {name}/{version} has unknown module dependency "
                            f"{dep_name}/{dep_version}."
                        )
