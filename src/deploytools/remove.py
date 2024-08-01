import os
import shutil
from pathlib import Path

from .layout import Layout
from .models.module import ModuleConfig
from .module import get_deployed_module_versions


class RemovalError(Exception):
    pass


def check_remove(modules: list[ModuleConfig], layout: Layout):
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        check_module_and_version_in_deprecated(name, version, layout)


def remove(modules: list[ModuleConfig], layout: Layout):
    """Remove a deprecated module."""
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        remove_deprecated_module(name, version, layout)


def check_module_and_version_in_deprecated(name: str, version: str, layout: Layout):
    versions = get_deployed_module_versions(layout, deprecated=True)
    if version not in versions[name]:
        raise RemovalError(
            f"Cannot remove {name}/{version}. Not found in deprecated area."
        )


def remove_deprecated_module(name: str, version: str, layout: Layout):
    module_file = layout.get_modulefiles_root(deprecated=True) / name / version
    os.remove(module_file)
    delete_folder_if_empty(module_file.parent)

    to_remove = [layout.get_entrypoints_root(), layout.get_sif_files_root()]
    for path in to_remove:
        src_path = path / name / version
        shutil.rmtree(src_path)

        delete_folder_if_empty(src_path.parent)


def delete_folder_if_empty(path: Path):
    try:
        path.rmdir()
    except OSError:
        pass
