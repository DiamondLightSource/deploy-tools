from .layout import Layout
from .models.module import Release
from .module import is_modulefile_deployed
from .module_creator import ModuleCreator
from .templater import Templater


class DeployError(Exception):
    pass


def check_deploy(releases: list[Release], layout: Layout) -> None:
    """Verify that deploy() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if is_modulefile_deployed(name, version, layout):
            raise DeployError(
                f"Cannot deploy {name}/{version}. Already found in deployment area."
            )


def deploy(releases: list[Release], layout: Layout) -> None:
    """Deploy modules from the provided list."""
    if not releases:
        return

    templater = Templater()
    module_creator = ModuleCreator(templater, layout)

    for release in releases:
        module_creator.create_module(release.module)
