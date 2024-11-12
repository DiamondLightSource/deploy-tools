import shutil
from pathlib import Path

from .layout import Layout
from .models.module import Release
from .module import VERSION_GLOB


class RemoveNameFoldersError(Exception):
    pass


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
