import logging
import os
import shutil
from pathlib import Path

from .layout import Layout
from .models.changes import DeploymentChanges
from .models.module import Release
from .modulefile import (
    apply_default_versions,
    deprecate_modulefile_link,
    restore_modulefile_link,
)

logger = logging.getLogger(__name__)

MODULE_VERSIONS_GLOB = f"[!{Layout.DEFAULT_VERSION_FILENAME}]*"


def deploy_changes(changes: DeploymentChanges, layout: Layout) -> None:
    """Perform the Deploy step for the specified changes."""
    logger.debug("Deploying changes to: %s", layout.deployment_root)
    release_changes = changes.release_changes

    logger.debug("Removing deleted modules: %d", len(release_changes.to_remove))
    _remove_releases(release_changes.to_remove, layout)

    logger.debug("Deploying new releases: %d", len(release_changes.to_add))
    _deploy_new_releases(release_changes.to_add, layout)
    logger.debug("Deploying updated releases: %d", len(release_changes.to_update))
    _deploy_releases(release_changes.to_update, layout, exist_ok=True)

    logger.debug("Deprecating releases: %d", len(release_changes.to_deprecate))
    _deprecate_releases(release_changes.to_deprecate, layout)
    logger.debug("Restoring releases %d", len(release_changes.to_restore))
    _restore_releases(release_changes.to_restore, layout)

    logger.debug("Applying default versions")
    apply_default_versions(changes.default_versions, layout)
    logger.debug("Clearing up empty folders")
    _remove_name_folders(
        release_changes.to_deprecate,
        release_changes.to_restore,
        release_changes.to_remove,
        layout,
    )


def _remove_releases(to_remove: list[Release], layout: Layout) -> None:
    """Remove the given modules from the deployment area."""
    for release in to_remove:
        name = release.module.name
        version = release.module.version

        from_deprecated = not release.module.is_dev_mode()
        _remove_deployed_module(name, version, layout, from_deprecated)


def _deploy_new_releases(to_add: list[Release], layout: Layout) -> None:
    """Deploy modules from the provided list."""
    _deploy_releases(to_add, layout)

    for release in to_add:
        name = release.module.name
        version = release.module.version
        deprecated = release.deprecated

        modulefile = layout.get_modulefile(name, version)
        modulefile_link = layout.get_modulefile_link(
            name, version, from_deprecated=deprecated
        )

        modulefile_link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(modulefile, modulefile_link)


def _deploy_releases(
    to_deploy: list[Release], layout: Layout, exist_ok: bool = False
) -> None:
    build_layout = layout.build_layout

    for release in to_deploy:
        module = release.module
        built_module_folder = build_layout.get_module_folder(
            module.name, module.version
        )
        final_module_folder = layout.get_module_folder(module.name, module.version)
        final_module_folder.parent.mkdir(parents=True, exist_ok=True)

        if exist_ok and final_module_folder.exists():
            shutil.rmtree(final_module_folder)

        built_module_folder.rename(final_module_folder)


def _deprecate_releases(to_deprecate: list[Release], layout: Layout) -> None:
    """Deprecate a list of modules.

    For each module, this will move the modulefile link to the 'deprecated' directory
    under the Deployment Area. If the user's MODULEPATH is set to include the
    'deprecated/modulefiles' directory, all modules should be available as before.
    """
    for release in to_deprecate:
        deprecate_modulefile_link(release.module.name, release.module.version, layout)


def _remove_deployed_module(
    name: str, version: str, layout: Layout, from_deprecated: bool = False
) -> None:
    modulefile = layout.get_modulefile_link(name, version, from_deprecated)
    modulefile.unlink()

    _remove_module(name, version, layout)


def _remove_module(name: str, version: str, layout: Layout) -> None:
    module_folder = layout.get_module_folder(name, version)
    if module_folder.exists():
        shutil.rmtree(module_folder)


def _restore_releases(to_restore: list[Release], layout: Layout) -> None:
    """Restore a previously deprecated module."""
    for release in to_restore:
        restore_modulefile_link(release.module.name, release.module.version, layout)


def _remove_name_folders(
    deprecated: list[Release],
    restored: list[Release],
    removed: list[Release],
    layout: Layout,
) -> None:
    """Remove module name folders where all versions have been removed.

    Several types of path are of the form <root>/name/version. When removing version
    files in operations such as deprecation, if all versions are removed the parent
    folder (called name folder here) will still exist. This function is designed to
    remove them.

    Note that the non-deprecated modulefile name folder will not be empty, as the
    default version file will still exist.
    """
    for release in deprecated:
        _delete_modulefiles_name_folder(layout, release.module.name)

    for release in restored:
        _delete_modulefiles_name_folder(layout, release.module.name, True)

    for release in removed:
        _delete_modulefiles_name_folder(layout, release.module.name, True)
        _delete_name_folder(release.module.name, layout.modules_root)


def _delete_modulefiles_name_folder(
    layout: Layout, name: str, from_deprecated: bool = False
) -> None:
    modulefiles_name_path = layout.get_modulefiles_root(from_deprecated) / name

    # Ignore the default version file when checking for existing modulefile links
    if next(modulefiles_name_path.glob(MODULE_VERSIONS_GLOB), None) is None:
        shutil.rmtree(modulefiles_name_path)


def _delete_name_folder(name: str, area_root: Path) -> None:
    name_folder = area_root / name
    try:
        name_folder.rmdir()
    except OSError:
        pass
