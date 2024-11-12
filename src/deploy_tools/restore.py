from .layout import Layout
from .models.module import Release
from .module import is_modulefile_deployed, restore_modulefile


class RestoreError(Exception):
    pass


def check_restore(releases: list[Release], layout: Layout) -> None:
    """Verify that restore() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if is_modulefile_deployed(name, version, layout):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def restore(releases: list[Release], layout: Layout) -> None:
    """Restore a previously deprecated module."""
    for release in releases:
        restore_modulefile(release.module.name, release.module.version, layout)
