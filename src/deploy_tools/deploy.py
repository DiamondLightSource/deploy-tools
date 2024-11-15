import shutil
from pathlib import Path

from deploy_tools.layout import Layout
from deploy_tools.models.changes import DeploymentChanges
from deploy_tools.models.deployment import DefaultVersionsByName
from deploy_tools.models.module import Release
from deploy_tools.module import (
    VERSION_GLOB,
    deprecate_modulefile,
    is_module_dev_mode,
    restore_modulefile,
)
from deploy_tools.module_creator import ModuleCreator
from deploy_tools.templater import Templater


def deploy(changes: DeploymentChanges, layout: Layout) -> None:
    release_changes = changes.release_changes

    deploy_new_releases(release_changes.to_add, layout)
    update_releases(release_changes.to_update, layout)
    deprecate_releases(release_changes.to_deprecate, layout)
    restore_releases(release_changes.to_restore, layout)
    remove_releases(release_changes.to_remove, layout)

    apply_default_versions(changes.default_versions, layout)
    remove_name_folders(
        release_changes.to_deprecate,
        release_changes.to_restore,
        release_changes.to_remove,
        layout,
    )


def deploy_new_releases(to_add: list[Release], layout: Layout) -> None:
    """Deploy modules from the provided list."""
    if not to_add:
        return

    templater = Templater()
    module_creator = ModuleCreator(templater, layout)

    for release in to_add:
        module_creator.create_module(release.module)


def deprecate_releases(to_deprecate: list[Release], layout: Layout) -> None:
    """Deprecate a list of modules.

    This will move the modulefile to a 'deprecated' directory. If the modulefile path is
    set up to include the 'deprecated' directory, all modulefiles should continue to
    work.
    """
    for release in to_deprecate:
        deprecate_modulefile(release.module.name, release.module.version, layout)


def remove_releases(to_remove: list[Release], layout: Layout) -> None:
    """Remove the given modules from the deployment area."""
    for release in to_remove:
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


def restore_releases(to_restore: list[Release], layout: Layout) -> None:
    """Restore a previously deprecated module."""
    for release in to_restore:
        restore_modulefile(release.module.name, release.module.version, layout)


def update_releases(to_update: list[Release], layout: Layout) -> None:
    """Update development modules from the provided list."""
    for release in to_update:
        name = release.module.name
        version = release.module.version

        remove_deployed_module(name, version, layout)

    deploy_new_releases(to_update, layout)


def apply_default_versions(
    default_versions: DefaultVersionsByName, layout: Layout
) -> None:
    """Update .version files for current default version settings."""
    templater = Templater()
    module_creator = ModuleCreator(templater, layout)
    module_creator.update_default_versions(default_versions, layout)


def remove_name_folders(
    deprecated: list[Release],
    restored: list[Release],
    removed: list[Release],
    layout: Layout,
) -> None:
    """Remove module name folders where all versions have been removed."""
    for release in deprecated:
        delete_modulefile_name_folder(layout, release.module.name)

    for release in restored:
        delete_modulefile_name_folder(layout, release.module.name, True)

    for release in removed:
        delete_modulefile_name_folder(layout, release.module.name, True)
        delete_name_folder(release.module.name, layout.modules_root)


def delete_modulefile_name_folder(
    layout: Layout, name: str, from_deprecated: bool = False
) -> None:
    modulefiles_name_path = layout.get_modulefiles_root(from_deprecated) / name
    if modulefiles_name_path.glob(VERSION_GLOB):
        shutil.rmtree(modulefiles_name_path)


def delete_name_folder(name: str, area_root: Path) -> None:
    name_folder = area_root / name
    try:
        name_folder.rmdir()
    except OSError:
        pass
