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
    DeploymentSettings,
    ModulesByNameAndVersion,
)
from .models.load import load_deployment
from .models.module import Module
from .module import (
    DEVELOPMENT_VERSION,
    ModuleVersionsByName,
    get_deployed_module_versions,
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
):
    """Validate deployment configuration and print a list of modules for deployment.

    This is the same validation that the deploytools sync command uses."""
    deployment = load_deployment(config_folder)
    layout = Layout(deployment_root)
    update_group = validate_deployment(deployment, layout)
    default_versions = validate_default_versions(
        update_group, deployment.settings, layout
    )

    check_actions(update_group, default_versions, layout)
    display_updates(update_group)


def check_actions(
    update_group: UpdateGroup, default_versions: DefaultVersionsByName, layout: Layout
):
    check_deploy(update_group.added, layout)
    check_update(update_group.updated, layout)
    check_deprecate(update_group.deprecated, layout)
    check_restore(update_group.restored, layout)
    check_remove(update_group.removed, layout)

    check_default_versions(default_versions, layout)


def display_updates(update_group: UpdateGroup):
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


def validate_deployment(deployment: Deployment, layout: Layout) -> UpdateGroup:
    last_deployment = load_snapshot(layout)
    old_modules = last_deployment.modules
    new_modules = deployment.modules

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


def is_modified(old_module: Module, new_module: Module):
    new_copy = new_module.model_copy(deep=True)
    new_copy.metadata.deprecated = old_module.metadata.deprecated

    return not new_copy == old_module


def validate_added_modules(modules: list[Module]):
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


def validate_updated_modules(modules: list[Module]):
    for module in modules:
        metadata = module.metadata
        if metadata.deprecated:
            raise ValidationError(
                f"Module {metadata.name}/{metadata.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def validate_deprecated_modules(modules: list[Module]):
    for module in modules:
        if is_module_dev_mode(module):
            metadata = module.metadata
            raise ValidationError(
                f"Module {metadata.name}/{metadata.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def validate_removed_modules(modules: list[Module]):
    for module in modules:
        if not is_module_dev_mode(module) and not module.metadata.deprecated:
            raise ValidationError(
                f"Module {module.metadata.name}/{module.metadata.version} removed "
                "without prior deprecation."
            )


def validate_default_versions(
    update_group: UpdateGroup, settings: DeploymentSettings, layout: Layout
) -> DefaultVersionsByName:
    final_deployed_modules = get_final_deployed_module_versions(update_group, layout)

    for name, version in settings.default_versions.items():
        if version not in final_deployed_modules[name]:
            raise ValidationError(
                f"Unable to configure {name}/{version} as default; module will not "
                f"exist."
            )

    default_versions = get_all_default_versions(
        settings.default_versions, final_deployed_modules
    )

    return default_versions


def get_final_deployed_module_versions(
    update_group: UpdateGroup, layout: Layout
) -> ModuleVersionsByName:
    deployed_modules = get_deployed_module_versions(layout)
    added_modules = update_group.added + update_group.restored
    removed_modules = update_group.deprecated

    for module in added_modules:
        deployed_modules[module.metadata.name].append(module.metadata.version)

    for module in removed_modules:
        deployed_modules[module.metadata.name].remove(module.metadata.version)

    return deployed_modules


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
