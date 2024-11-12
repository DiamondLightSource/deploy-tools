from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

from .deploy import check_deploy
from .deprecate import check_deprecate
from .layout import Layout
from .models.deployment import (
    DefaultVersionsByName,
    Deployment,
    ReleasesByNameAndVersion,
)
from .models.load import load_deployment
from .models.module import Module, Release
from .module import (
    DEVELOPMENT_VERSION,
    ModuleVersionsByName,
    is_modified,
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


def validate_configuration(deployment_root: Path, config_folder: Path) -> None:
    """Validate deployment configuration and print a list of modules for deployment.

    The validate_* functions consider only the current and previous deployment
    to identify what changes need to be made, while check_actions will look at the
    current deployment area to ensure that the specified actions can be completed."""
    deployment = load_deployment(config_folder)
    layout = Layout(deployment_root)
    snapshot = load_snapshot(layout)

    update_group = validate_update_group(deployment, snapshot)
    default_versions = validate_default_versions(deployment)

    check_actions(update_group, default_versions, layout)

    print_module_updates(update_group)
    print_version_updates(
        snapshot.settings.default_versions, deployment.settings.default_versions
    )


def check_actions(
    update_group: UpdateGroup, default_versions: DefaultVersionsByName, layout: Layout
) -> None:
    """Check the deployment area to ensure that all actions can be carried out."""
    check_deploy(update_group.added, layout)
    check_update(update_group.updated, layout)
    check_deprecate(update_group.deprecated, layout)
    check_restore(update_group.restored, layout)
    check_remove(update_group.removed, layout)


def print_module_updates(update_group: UpdateGroup) -> None:
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
            print(f"{module.name}/{module.version}")

        print()


def print_version_updates(
    old_defaults: DefaultVersionsByName, new_defaults: DefaultVersionsByName
) -> None:
    print("Updated module defaults:")
    module_names = old_defaults.keys() | new_defaults.keys()

    for name in module_names:
        old = old_defaults.get(name, "None")
        new = new_defaults.get(name, "None")
        if not old == new:
            print(f"{name} {old} -> {new}")

    print()


def validate_update_group(deployment: Deployment, snapshot: Deployment) -> UpdateGroup:
    """Validate configuration to get set of actions that need to be carried out."""
    old_modules = snapshot.releases
    new_modules = deployment.releases

    validate_module_dependencies(deployment)
    return get_update_group(old_modules, new_modules)


def get_update_group(
    old_releases: ReleasesByNameAndVersion, new_releases: ReleasesByNameAndVersion
) -> UpdateGroup:
    added: list[Release] = []
    updated: list[Release] = []
    deprecated: list[Release] = []
    restored: list[Release] = []
    removed: list[Release] = []
    for name in new_releases:
        if name not in old_releases:
            added.extend(new_releases[name].values())
            continue

        for version, new_release in new_releases[name].items():
            if version not in old_releases[name]:
                added.append(new_release)
                continue

            old_release = old_releases[name][version]

            if is_modified(old_release.module, new_release.module):
                if is_module_dev_mode(new_release.module):
                    updated.append(new_release)
                    continue

                raise ValidationError(
                    f"Module {name}/{version} modified without updating version."
                )

            if not old_release.deprecated and new_release.deprecated:
                deprecated.append(new_release)
            elif old_release.deprecated and not new_release.deprecated:
                restored.append(new_release)

    for name in old_releases:
        if name not in new_releases:
            removed.extend(old_releases[name].values())
            continue

        for version, old_release in old_releases[name].items():
            if version not in new_releases[name]:
                removed.append(old_release)

    update_group = UpdateGroup()
    update_group.added = validate_added_modules(added)
    update_group.updated = validate_updated_modules(updated)
    update_group.deprecated = validate_deprecated_modules(deprecated)
    update_group.restored = validate_restored_modules(restored)
    update_group.removed = validate_removed_modules(removed)

    return update_group


def validate_added_modules(releases: list[Release]) -> list[Module]:
    for release in releases:
        module = release.module
        if release.deprecated:
            if is_module_dev_mode(module):
                raise ValidationError(
                    f"Module {module.name}/{module.version} cannot be specified as"
                    f"deprecated as it is in development mode."
                )

            raise ValidationError(
                f"Module {module.name}/{module.version} cannot have deprecated "
                f"status on initial creation."
            )

    return get_modules_list_from_releases(releases)


def validate_updated_modules(releases: list[Release]) -> list[Module]:
    for release in releases:
        module = release.module
        if release.deprecated:
            raise ValidationError(
                f"Module {module.name}/{module.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )

    return get_modules_list_from_releases(releases)


def validate_deprecated_modules(releases: list[Release]) -> list[Module]:
    for release in releases:
        module = release.module
        if is_module_dev_mode(module):
            raise ValidationError(
                f"Module {module.name}/{module.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )

    return get_modules_list_from_releases(releases)


def validate_restored_modules(releases: list[Release]) -> list[Module]:
    return get_modules_list_from_releases(releases)


def validate_removed_modules(releases: list[Release]) -> list[Module]:
    for release in releases:
        module = release.module
        if not is_module_dev_mode(module) and not release.deprecated:
            raise ValidationError(
                f"Module {module.name}/{module.version} removed without prior"
                f"deprecation."
            )

    return get_modules_list_from_releases(releases)


def get_modules_list_from_releases(releases: list[Release]):
    return [release.module for release in releases]


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
    """Return module versions that will be deployed after sync action has completed.

    This explicitly excludes any deprecated modules.
    """
    final_versions: ModuleVersionsByName = defaultdict(list)
    for name, release_versions in deployment.releases.items():
        versions = [
            version
            for version, release in release_versions.items()
            if not release.deprecated
        ]

        if versions:
            final_versions[name] = versions

    return final_versions


def get_all_default_versions(
    initial_defaults: DefaultVersionsByName,
    final_deployed_module_versions: ModuleVersionsByName,
) -> DefaultVersionsByName:
    """Return the default versions that will be used for all modules in configuration.

    All modules will have a .version file to specify their default, even if they do not
    specify one in configuration. This is to ensure that 'development' versions are not
    accidentally used as the default.
    """
    final_defaults: DefaultVersionsByName = {}
    final_defaults.update(initial_defaults)

    for name in final_deployed_module_versions:
        if name in final_defaults:
            continue

        version_list = deepcopy(final_deployed_module_versions[name])
        if DEVELOPMENT_VERSION in version_list:
            version_list.remove(DEVELOPMENT_VERSION)

        version_list.sort()
        final_defaults[name] = version_list[-1]

    return final_defaults


def validate_module_dependencies(deployment: Deployment) -> None:
    """Ensure that all module dependencies are set appropriately.

    This checks any module dependency names that come from current configuration to
    ensure they exist and are not deprecated. Not specifying a particular version is
    only valid for dependencies that are managed outside of the current deployment
    configuration.
    """
    final_deployed_modules = get_final_deployed_module_versions(deployment)

    for name, release_versions in deployment.releases.items():
        for version, release in release_versions.items():
            for dependency in release.module.dependencies:
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
