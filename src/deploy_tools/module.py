import shutil
from collections import defaultdict
from pathlib import Path
from typing import TypeAlias

from .layout import Layout
from .models.module import Module

ModuleVersionsByName: TypeAlias = dict[str, list[str]]

VERSION_FILENAME = ".version"
VERSION_GLOB = "*/[!.version]*"
DEVELOPMENT_VERSION = "dev"


def deprecate_modulefile(name: str, version: str, layout: Layout):
    _move_modulefile(
        name,
        version,
        layout.modulefiles_root,
        layout.deprecated_modulefiles_root,
    )


def restore_modulefile(name: str, version: str, layout: Layout):
    _move_modulefile(
        name,
        version,
        layout.deprecated_modulefiles_root,
        layout.modulefiles_root,
    )


def _move_modulefile(
    name: str, version: str, src_folder: Path, dest_folder: Path
) -> None:
    src_path = src_folder / name / version

    dest_path = dest_folder / name / version
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src_path, dest_path)


def get_deployed_module_versions(layout: Layout) -> ModuleVersionsByName:
    """Return list of modules that have already been deployed."""
    modulefiles_root = layout.get_modulefiles_root(from_deprecated=False)
    found_modules: ModuleVersionsByName = defaultdict(list)

    for version_path in modulefiles_root.glob(VERSION_GLOB):
        found_modules[version_path.parent.name].append(version_path.name)

    return found_modules


def in_deployment_area(name: str, version: str, layout: Layout) -> bool:
    modulefile = layout.get_modulefile(name, version)
    return modulefile.exists()


def in_deprecated_area(name: str, version: str, layout: Layout) -> bool:
    modulefile = layout.get_modulefile(name, version, True)
    return modulefile.exists()


def is_module_dev_mode(module: Module) -> bool:
    return module.version == DEVELOPMENT_VERSION


def is_modified(module_a: Module, module_b: Module) -> bool:
    """Return whether the two module configuration objects have modified settings."""
    return not module_b == module_a
