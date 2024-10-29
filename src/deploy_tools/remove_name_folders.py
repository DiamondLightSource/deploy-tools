import shutil
from pathlib import Path

from .layout import Layout
from .models.module import Module
from .module import VERSION_GLOB


class RemoveNameFoldersError(Exception):
    pass


def remove_name_folders(
    deprecated: list[Module],
    restored: list[Module],
    removed: list[Module],
    layout: Layout,
) -> None:
    """Remove module name folders where all versions have been removed."""
    for module in deprecated:
        delete_modulefile_name_folder(module.metadata.name, layout.modulefiles_root)

    for module in restored:
        delete_modulefile_name_folder(
            module.metadata.name, layout.deprecated_modulefiles_root
        )

    for module in removed:
        delete_modulefile_name_folder(
            module.metadata.name, layout.deprecated_modulefiles_root
        )
        delete_name_folder(module.metadata.name, layout.modules_root)


def delete_modulefile_name_folder(name: str, modulefiles_root: Path) -> None:
    modulefiles_name_path = modulefiles_root / name
    if modulefiles_name_path.glob(VERSION_GLOB):
        shutil.rmtree(modulefiles_name_path)


def delete_name_folder(name: str, area_root: Path) -> None:
    name_folder = area_root / name
    try:
        name_folder.rmdir()
    except OSError:
        pass
