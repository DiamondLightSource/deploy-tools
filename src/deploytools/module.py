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


class ModuleCreator:
    """Class for creating modulefiles, including optional dependencies and env vars."""

    def __init__(self, layout: Layout):
        self._templater = Templater()
        self._layout = layout
        self._modulefiles_root = layout.modulefiles_root
        self._entrypoints_root = layout.entrypoints_root

    def create_module_file(self, module: Module):
        template = self._templater.get_template(TemplateType.MODULEFILE)

        config = module.metadata
        entrypoints_folder = self._entrypoints_root / config.name / config.version

        description = config.description
        if description is None:
            description = f"Scripts for {config.name}"

        params = {
            "module_name": config.name,
            "module_description": description,
            "env_vars": config.env_vars,
            "dependencies": config.dependencies,
            "entrypoint_folder": entrypoints_folder,
        }

        module_file = self._modulefiles_root / config.name / config.version
        module_file.parent.mkdir(exist_ok=True, parents=True)

        self._templater.create(module_file, template, params)

    def update_default_versions(
        self, default_versions: DefaultVersionsByName, layout: Layout
    ):
        template = self._templater.get_template(TemplateType.MODULEFILE_VERSION)
        deployed_modules = get_deployed_module_versions(layout)

        for name in deployed_modules:
            version_file = self._modulefiles_root / name / VERSION_FILENAME

            if name in default_versions:
                version = default_versions[name]
                params = {
                    "version": version,
                }

                self._templater.create(version_file, template, params)
            else:
                version_file.unlink(missing_ok=True)


def move_modulefile(name: str, version: str, src_folder: Path, dest_folder: Path):
    src_path = src_folder / name / version

    dest_path = dest_folder / name / version
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src_path, dest_path)


def get_deployed_module_versions(
    layout: Layout, deprecated=False
) -> ModuleVersionsByName:
    modulefiles_root = (
        layout.deprecated_modulefiles_root if deprecated else layout.modulefiles_root
    )
    found_modules: ModuleVersionsByName = defaultdict(list)

    for module_folder in modulefiles_root.glob("*"):
        for version_path in module_folder.glob("*"):
            if version_path.name == VERSION_FILENAME:
                continue

            found_modules[module_folder.name].append(version_path.name)

    return found_modules
