import os
import shutil

from .layout import Layout
from .models.module import Module
from .module import is_module_deprecated


class RemovalError(Exception):
    pass


def check_remove(modules: list[Module], layout: Layout):
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        if not is_module_deprecated(name, version, layout):
            raise RemovalError(
                f"Cannot remove {name}/{version}. Not found in deprecated area."
            )


def remove(modules: list[Module], layout: Layout):
    """Remove a deprecated module."""
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        remove_deprecated_module(name, version, layout)


def remove_deprecated_module(name: str, version: str, layout: Layout):
    module_file = layout.deprecated_modulefiles_root / name / version
    os.remove(module_file)

    to_remove = [layout.entrypoints_root, layout.sif_files_root]
    for path in to_remove:
        src_path = path / name / version
        shutil.rmtree(src_path)
