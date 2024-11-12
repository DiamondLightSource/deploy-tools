from .deploy import deploy
from .layout import Layout
from .models.module import Release
from .module import is_modulefile_deployed
from .remove import remove_deployed_module


class UpdateError(Exception):
    pass


def check_update(releases: list[Release], layout: Layout) -> None:
    """Verify that update() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if not is_modulefile_deployed(name, version, layout):
            raise UpdateError(
                f"Cannot update {name}/{version}. Not found in deployment area."
            )


def update(releases: list[Release], layout: Layout) -> None:
    """Update development modules from the provided list."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        remove_deployed_module(name, version, layout)

    deploy(releases, layout)
