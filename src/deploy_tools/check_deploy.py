from .layout import Layout
from .models.changes import DeploymentChanges
from .models.module import Release
from .module import is_module_dev_mode, is_modulefile_deployed


class CheckDeployError(Exception):
    pass


def check_deploy_actions(changes: DeploymentChanges, layout: Layout):
    release_changes = changes.release_changes

    check_deploy_new_releases(release_changes.to_add, layout)
    check_update_releases(release_changes.to_update, layout)
    check_deprecate_releases(release_changes.to_deprecate, layout)
    check_restore_releases(release_changes.to_restore, layout)
    check_remove_releases(release_changes.to_remove, layout)


def check_deploy_new_releases(releases: list[Release], layout: Layout) -> None:
    """Verify that deploy_new_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if is_modulefile_deployed(name, version, layout):
            raise CheckDeployError(
                f"Cannot deploy {name}/{version}. Already found in deployment area."
            )


def check_deprecate_releases(releases: list[Release], layout: Layout) -> None:
    """Verify that deprecate_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout):
            raise CheckDeployError(
                f"Cannot deprecate {name}/{version}. Not found in deployment area."
            )

        if is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise CheckDeployError(
                f"Cannot deprecate {name}/{version}. Already found in deprecated area."
            )


def check_remove_releases(releases: list[Release], layout: Layout) -> None:
    """Verify that remove_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if is_module_dev_mode(release.module):
            if not is_modulefile_deployed(name, version, layout):
                raise CheckDeployError(
                    f"Cannot remove {name}/{version}. Not found in deployment area."
                )
            continue

        if not is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise CheckDeployError(
                f"Cannot remove {name}/{version}. Not found in deprecated area."
            )


def check_restore_releases(releases: list[Release], layout: Layout) -> None:
    """Verify that restore_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise CheckDeployError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if is_modulefile_deployed(name, version, layout):
            raise CheckDeployError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def check_update_releases(releases: list[Release], layout: Layout) -> None:
    """Verify that update_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout):
            raise CheckDeployError(
                f"Cannot update {name}/{version}. Not found in deployment area."
            )
