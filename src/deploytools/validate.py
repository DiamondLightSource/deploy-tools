from dataclasses import dataclass, field
from pathlib import Path

import typer
from typing_extensions import Annotated

from .deploy import check_deploy
from .deprecate import check_deprecate
from .layout import Layout
from .models.deployment import Deployment, ModulesByNameAndVersion
from .models.load import load_deployment
from .models.module import Module
from .remove import check_remove
from .restore import check_restore
from .snapshot import (
    load_snapshot,
)


class ValidationError(Exception):
    pass


@dataclass
class UpdateGroup:
    added: list[Module] = field(default_factory=list)
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

    check_actions(update_group, layout)

    display_updates(update_group)


def check_actions(update_group: UpdateGroup, layout: Layout):
    check_deploy(layout)
    check_deprecate(update_group.deprecated, layout)
    check_restore(update_group.restored, layout)
    check_remove(update_group.removed, layout)


def display_updates(update_group: UpdateGroup):
    display_config = {
        "deployed": update_group.added,
        "deprecated": update_group.deprecated,
        "restored": update_group.restored,
        "removed": update_group.removed,
    }

    for description, modules in display_config.items():
        if not modules:
            print(f"No modules to be {description}.")
        else:
            print(f"Modules to be {description}:")

        for module in modules:
            print(f"{module.metadata.name}/{module.metadata.version}")

        print()


def validate_deployment(deployment: Deployment, layout: Layout) -> UpdateGroup:
    last_deployment = load_snapshot(layout)
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
                f"Module {module.metadata.name}/{module.metadata.version} removed"
                "without prior deprecation."
            )

    return group


def is_modified(old_module: Module, new_module: Module):
    old_copy = old_module.model_copy(deep=True)
    new_copy = new_module.model_copy(deep=True)

    new_copy.metadata.deprecated = False
    old_copy.metadata.deprecated = False

    return not new_copy == old_copy
