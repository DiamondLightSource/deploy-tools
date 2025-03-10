import logging
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from .build import build
from .layout import Layout
from .models.changes import DeploymentChanges, ReleaseChanges
from .models.deployment import (
    DefaultVersionsByName,
    Deployment,
    ReleasesByNameAndVersion,
)
from .models.module import DEVELOPMENT_VERSION, Release
from .models.save_and_load import load_deployment
from .modulefile import (
    ModuleVersionsByName,
)
from .print_updates import print_updates
from .snapshot import load_snapshot

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def validate_and_test_configuration(
    deployment_root: Path,
    config_folder: Path,
    allow_all: bool = False,
    from_scratch: bool = False,
    test_build: bool = True,
) -> None:
    """Validate deployment configuration and perform a test build."""
    with TemporaryDirectory() as build_dir:
        logger.info("Loading deployment configuration from: %s", config_folder)
        deployment = load_deployment(config_folder)

        logger.info("Loading deployment snapshot")
        layout = Layout(deployment_root, build_root=Path(build_dir))
        snapshot = load_snapshot(layout, from_scratch)

        logger.info("Validating deployment changes")
        deployment_changes = validate_deployment_changes(
            deployment, snapshot, allow_all
        )

        logger.info("Retrieving previous default versions")
        snapshot_default_versions = validate_default_versions(snapshot)

        if test_build:
            logger.info("Performing test build")
            build(deployment_changes, layout)

        logger.info("Printing updates")
        print_updates(snapshot_default_versions, deployment_changes)


def validate_deployment_changes(
    deployment: Deployment, snapshot: Deployment, allow_all: bool
) -> DeploymentChanges:
    """Validate configuration to get set of actions that need to be carried out."""
    release_changes = validate_release_changes(deployment, snapshot, allow_all)
    default_versions = validate_default_versions(deployment)
    return DeploymentChanges(
        release_changes=release_changes, default_versions=default_versions
    )


def validate_release_changes(
    deployment: Deployment, snapshot: Deployment, allow_all: bool
) -> ReleaseChanges:
    """Validate configuration to get set of Release changes."""
    old_releases = snapshot.releases
    new_releases = deployment.releases

    _validate_module_dependencies(deployment)
    return _get_release_changes(old_releases, new_releases, allow_all)


def _validate_module_dependencies(deployment: Deployment) -> None:
    """Ensure that all module dependencies are set appropriately.

    This checks any module dependency names that come from current configuration to
    ensure they exist and are not deprecated. Not specifying a particular version is
    only valid for dependencies that are managed outside of the current deployment
    configuration.
    """
    final_deployed_modules = _get_final_deployed_module_versions(deployment)

    for name, release_versions in deployment.releases.items():
        for version, release in release_versions.items():
            for dependency in release.module.dependencies:
                dep_name = dependency.name
                dep_version = dependency.version
                if dep_version is not None and dep_name in final_deployed_modules:
                    if dep_version not in final_deployed_modules[dep_name]:
                        raise ValidationError(
                            f"Module {name}/{version} has unknown module dependency "
                            f"{dep_name}/{dep_version}."
                        )


def _get_final_deployed_module_versions(
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


def _get_release_changes(
    old_releases: ReleasesByNameAndVersion,
    new_releases: ReleasesByNameAndVersion,
    allow_all: bool,
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

            if old_release.module != new_release.module:
                if new_release.module.is_dev_mode():
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

    _validate_added_modules(release_changes.to_add, allow_all)
    _validate_updated_modules(release_changes.to_update)
    _validate_deprecated_modules(release_changes.to_deprecate)
    _validate_removed_modules(release_changes.to_remove, allow_all)

    return release_changes


def _validate_added_modules(releases: list[Release], from_scratch: bool) -> None:
    for release in releases:
        module = release.module
        if release.deprecated:
            if module.is_dev_mode():
                raise ValidationError(
                    f"Module {module.name}/{module.version} cannot be specified as"
                    f"deprecated as it is in development mode."
                )

            if not from_scratch:
                raise ValidationError(
                    f"Module {module.name}/{module.version} cannot have deprecated "
                    f"status on initial creation."
                )


def _validate_updated_modules(releases: list[Release]) -> None:
    for release in releases:
        module = release.module
        if release.deprecated:
            raise ValidationError(
                f"Module {module.name}/{module.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def _validate_deprecated_modules(releases: list[Release]) -> None:
    for release in releases:
        module = release.module
        if module.is_dev_mode():
            raise ValidationError(
                f"Module {module.name}/{module.version} cannot be specified as "
                f"deprecated as it is in development mode."
            )


def _validate_removed_modules(releases: list[Release], allow_all: bool) -> None:
    for release in releases:
        module = release.module
        if not allow_all and not module.is_dev_mode() and not release.deprecated:
            raise ValidationError(
                f"Module {module.name}/{module.version} removed without prior "
                f"deprecation."
            )


def validate_default_versions(deployment: Deployment) -> DefaultVersionsByName:
    """Validate configuration to get set of default version changes."""
    final_deployed_modules = _get_final_deployed_module_versions(deployment)

    for name, version in deployment.settings.default_versions.items():
        if version not in final_deployed_modules[name]:
            raise ValidationError(
                f"Unable to configure {name}/{version} as default; module will not "
                f"exist."
            )

    default_versions = _get_all_default_versions(
        deployment.settings.default_versions, final_deployed_modules
    )

    return default_versions


def _get_all_default_versions(
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
