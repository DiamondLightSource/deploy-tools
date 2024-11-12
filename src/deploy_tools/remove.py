import shutil

from .layout import Layout
from .models.module import Release
from .module import is_module_dev_mode, is_modulefile_deployed


class RemovalError(Exception):
    pass


def check_remove(releases: list[Release], layout: Layout) -> None:
    """Verify that remove() can be run on the current deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version

        if is_module_dev_mode(release.module):
            if not is_modulefile_deployed(name, version, layout):
                raise RemovalError(
                    f"Cannot remove {name}/{version}. Not found in deployment area."
                )
            continue

        if not is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise RemovalError(
                f"Cannot remove {name}/{version}. Not found in deprecated area."
            )


def remove(releases: list[Release], layout: Layout) -> None:
    """Remove the given modules from the deployment area."""
    for release in releases:
        name = release.module.name
        version = release.module.version
        if is_module_dev_mode(release.module):
            remove_deployed_module(name, version, layout)
        else:
            remove_deployed_module(name, version, layout, from_deprecated=True)


def remove_deployed_module(
    name: str, version: str, layout: Layout, from_deprecated: bool = False
) -> None:
    modulefile = layout.get_modulefile(name, version, from_deprecated)
    modulefile.unlink()

    remove_module(name, version, layout)


def remove_module(name: str, version: str, layout: Layout) -> None:
    module_folder = layout.get_module_folder(name, version)
    if module_folder.exists():
        shutil.rmtree(module_folder)
