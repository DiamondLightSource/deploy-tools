import shutil
from collections import defaultdict
from pathlib import Path
from typing import TypeAlias

from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .models.module import Module
from .templater import Templater, TemplateType

ModuleVersionsByName: TypeAlias = dict[str, list[str]]

VERSION_FILENAME = ".version"
VERSION_GLOB = "*/[!.version]*"
DEVELOPMENT_VERSION = "dev"


class ModuleCreator:
    """Class for creating modulefiles, including optional dependencies and env vars."""

    def __init__(self, templater: Templater, layout: Layout) -> None:
        self._templater = templater
        self._layout = layout
        self._modulefiles_root = layout.modulefiles_root

    def create_module_file(self, module: Module) -> None:
        metadata = module.metadata
        entrypoints_folder = self._layout.get_entrypoints_folder(
            metadata.name, metadata.version
        )

        description = metadata.description
        if description is None:
            description = f"Scripts for {metadata.name}"

        params = {
            "module_name": metadata.name,
            "module_description": description,
            "env_vars": metadata.env_vars,
            "dependencies": metadata.dependencies,
            "entrypoint_folder": entrypoints_folder,
        }

        module_file = self._modulefiles_root / metadata.name / metadata.version
        module_file.parent.mkdir(exist_ok=True, parents=True)

        self._templater.create(module_file, TemplateType.MODULEFILE, params)

    def update_default_versions(
        self, default_versions: DefaultVersionsByName, layout: Layout
    ) -> None:
        deployed_modules = get_deployed_module_versions(layout)

        for name in deployed_modules:
            version_file = self._modulefiles_root / name / VERSION_FILENAME

            if name in default_versions:
                params = {"version": default_versions[name]}

                self._templater.create(
                    version_file,
                    TemplateType.MODULEFILE_VERSION,
                    params,
                    overwrite=True,
                )
            else:
                version_file.unlink(missing_ok=True)


def move_modulefile(
    name: str, version: str, src_folder: Path, dest_folder: Path
) -> None:
    src_path = src_folder / name / version

    dest_path = dest_folder / name / version
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src_path, dest_path)


def get_deployed_module_versions(
    layout: Layout, deprecated: bool = False
) -> ModuleVersionsByName:
    """Return list of modules that have already been deployed."""
    modulefiles_root = (
        layout.deprecated_modulefiles_root if deprecated else layout.modulefiles_root
    )
    found_modules: ModuleVersionsByName = defaultdict(list)

    for version_path in modulefiles_root.glob(VERSION_GLOB):
        found_modules[version_path.parent.name].append(version_path.name)

    return found_modules


def in_deployment_area(name: str, version: str, layout: Layout) -> bool:
    module_file = layout.modulefiles_root / name / version
    return module_file.exists()


def in_deprecated_area(name: str, version: str, layout: Layout) -> bool:
    module_file = layout.deprecated_modulefiles_root / name / version
    return module_file.exists()


def is_module_dev_mode(module: Module) -> bool:
    return module.metadata.version == DEVELOPMENT_VERSION


def is_modified(module_a: Module, module_b: Module) -> bool:
    """Return whether the two module configuration objects have modified settings.

    The 'deprecated' parameter is excluded as it is used for the deprecate/restore
    actions, rather than modifying the deployed files.
    """
    new_copy = module_b.model_copy(deep=True)
    new_copy.metadata.deprecated = module_a.metadata.deprecated

    return not new_copy == module_a
