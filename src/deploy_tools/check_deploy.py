from .layout import Layout
from .models.changes import DeploymentChanges
from .models.module import Release
from .modulefile import is_modulefile_deployed


class CheckDeployError(Exception):
    pass


def check_deploy_can_run(
    changes: DeploymentChanges, layout: Layout, allow_all: bool
) -> None:
    """Check that the Deployment Root is in the expected state for the given changes.

    Note that some of these checks are effectively stubs, and may require more
    fleshed-out checks in future.

    Also, the primary purpose of this section is to give clear feedback as to why
    certain changes can't be performed on the filesystem as-is. There is a level of
    redundancy in this code w.r.t. compare_to_snapshot(), which is not ideal.
    """
    release_changes = changes.release_changes

    _check_deploy_new_releases(release_changes.to_add, layout, allow_all)
    _check_update_releases(release_changes.to_update, layout)
    _check_deprecate_releases(release_changes.to_deprecate, layout)
    _check_restore_releases(release_changes.to_restore, layout)
    _check_remove_releases(release_changes.to_remove, layout, allow_all)


def _check_deploy_new_releases(
    releases: list[Release], layout: Layout, allow_all: bool
) -> None:
    """Check that deploy_new_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        check_deprecated = allow_all and release.deprecated
        if is_modulefile_deployed(
            name, version, layout, in_deprecated=check_deprecated
        ):
            raise CheckDeployError(
                f"Cannot deploy {name}/{version}. Modulefile already exists."
            )


def _check_deprecate_releases(releases: list[Release], layout: Layout) -> None:
    """Check that deprecate_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout):
            raise CheckDeployError(
                f"Cannot deprecate {name}/{version}. Modulefile not found."
            )

        if is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise CheckDeployError(
                f"Cannot deprecate {name}/{version}. Modulefile already exists in "
                f"deprecated area."
            )


def _check_remove_releases(
    releases: list[Release], layout: Layout, allow_all: bool
) -> None:
    """Check that remove_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if release.module.is_dev_mode() or allow_all and not release.deprecated:
            if not is_modulefile_deployed(name, version, layout):
                raise CheckDeployError(
                    f"Cannot remove {name}/{version}. Modulefile not found."
                )
            continue

        if not is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise CheckDeployError(
                f"Cannot remove {name}/{version}. Modulefile not found in deprecated "
                f"area."
            )


def _check_restore_releases(releases: list[Release], layout: Layout) -> None:
    """Check that restore_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise CheckDeployError(
                f"Cannot restore {name}/{version}. Modulefile not found in deprecated "
                f"area."
            )

        if is_modulefile_deployed(name, version, layout):
            raise CheckDeployError(
                f"Cannot restore {name}/{version}. Modulefile already exists."
            )


def _check_update_releases(releases: list[Release], layout: Layout) -> None:
    """Check that update_releases() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout):
            raise CheckDeployError(
                f"Cannot update {name}/{version}. Modulefile not found in deployment "
                f"area."
            )
