from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from .build import build
from .check_deploy import check_deploy_actions
from .layout import Layout
from .models.changes import DeploymentChanges, ReleaseChanges
from .models.deployment import (
    DefaultVersionsByName,
    Deployment,
    ReleasesByNameAndVersion,
)
from .models.load import load_deployment
from .models.module import Release
from .module import (
    DEVELOPMENT_VERSION,
    ModuleVersionsByName,
    is_modified,
    is_module_dev_mode,
)
from .snapshot import load_snapshot


class ValidationError(Exception):
    pass


def validate_configuration(deployment_root: Path, config_folder: Path) -> None:
    """Validate deployment configuration and print a list of modules for deployment.

    The validate_* functions consider only the current and previous deployment
    to identify what changes need to be made, while check_actions will look at the
    current deployment area to ensure that the specified actions can be completed."""
    with TemporaryDirectory() as build_dir:
        deployment = load_deployment(config_folder)
        layout = Layout(deployment_root, Path(build_dir))
        snapshot = load_snapshot(layout)

        deployment_changes = validate_deployment_changes(deployment, snapshot)

        check_deploy_actions(deployment_changes, layout)

        build(deployment_changes, layout)

        print_updates(snapshot.settings.default_versions, deployment_changes)


def print_updates(
    old_default_versions: DefaultVersionsByName, deployment_changes: DeploymentChanges
) -> None:
    print_module_updates(deployment_changes.release_changes)
    print_version_updates(old_default_versions, deployment_changes.default_versions)


def print_module_updates(release_changes: ReleaseChanges) -> None:
    display_config = {
        "deployed": release_changes.to_add,
        "updated": release_changes.to_update,
        "deprecated": release_changes.to_deprecate,
        "restored": release_changes.to_restore,
        "removed": release_changes.to_remove,
    }

    for action, releases in display_config.items():
        print(f"Modules to be {action}:")

        for release in releases:
            print(f"{release.module.name}/{release.module.version}")

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


def validate_deployment_changes(
    deployment: Deployment, snapshot: Deployment
) -> DeploymentChanges:
    release_changes = validate_release_changes(deployment, snapshot)
    default_versions = validate_default_versions(deployment)
    return DeploymentChanges(
        release_changes=release_changes, default_versions=default_versions
    )


def validate_release_changes(
    deployment: Deployment, snapshot: Deployment
) -> ReleaseChanges:
    """Validate configuration to get set of actions that need to be carried out."""
    old_releases = snapshot.releases
    new_releases = deployment.releases

    validate_module_dependencies(deployment)
    return get_release_changes(old_releases, new_releases)


def get_release_changes(
    old_releases: ReleasesByNameAndVersion, new_releases: ReleasesByNameAndVersion
) -> ReleaseChanges:
    release_changes = ReleaseChanges()
    for name in new_releases:
        if name not in old_releases:
            release_changes.to_add.extend(new_releases[name].values())
            continue

        for version, new_release in new_releases[name].items():
            if version not in old_releases[name]:
                release_changes.to_add.append(new_release)
                continue

            old_release = old_releases[name][version]

            if is_modified(old_release.module, new_release.module):
                if is_module_dev_mode(new_release.module):
                    release_changes.to_update.append(new_release)
                    continue

                raise ValidationError(
                    f"Module {name}/{version} modified without updating version."
                )

            if not old_release.deprecated and new_release.deprecated:
                release_changes.to_deprecate.append(new_release)
            elif old_release.deprecated and not new_release.deprecated:
                release_changes.to_restore.append(new_release)

    for name in old_releases:
        if name not in new_releases:
            release_changes.to_remove.extend(old_releases[name].values())
            continue

        for version, old_release in old_releases[name].items():
            if version not in new_releases[name]:
                release_changes.to_remove.append(old_release)

    validate_added_modules(release_changes.to_add)
    validate_updated_modules(release_changes.to_update)
    validate_deprecated_modules(release_changes.to_deprecate)
    validate_removed_modules(release_changes.to_remove)

    return release_changes


def validate_added_modules(releases: list[Release]) -> None:
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


def validate_updated_modules(releases: list[Release]) -> None:
    for release in releases:
        module = release.module
        if release.deprecated:
            raise ValidationError(
                f"Module {module.name}/{module.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def validate_deprecated_modules(releases: list[Release]) -> None:
    for release in releases:
        module = release.module
        if is_module_dev_mode(module):
            raise ValidationError(
                f"Module {module.name}/{module.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def validate_removed_modules(releases: list[Release]) -> None:
    for release in releases:
        module = release.module
        if not is_module_dev_mode(module) and not release.deprecated:
            raise ValidationError(
                f"Module {module.name}/{module.version} removed without prior"
                f"deprecation."
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
