import shutil
from collections import defaultdict
from pathlib import Path
from typing import TypeAlias

from .layout import Layout
from .models.module import ModuleConfig
from .templater import Templater, TemplateType

ModuleVersionsByName: TypeAlias = dict[str, list[str]]


class ModuleCreator:
    """Class for creating modulefiles, including optional dependencies and env vars."""

    def __init__(self, layout: Layout):
        self._templater = Templater()
        self._modulefiles_root = layout.get_modulefiles_root()
        self._entrypoints_root = layout.get_entrypoints_root()

    def create_module_file(self, module: ModuleConfig):
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


def move_modulefile(name: str, version: str, src_folder: Path, dest_folder: Path):
    src_path = src_folder / name / version

    dest_path = dest_folder / name / version
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src_path, dest_path)

    try:
        # Delete the module name directory if it is empty
        src_path.parent.rmdir()
    except OSError:
        pass


def get_deployed_module_versions(
    layout: Layout, deprecated=False
) -> ModuleVersionsByName:
    modulefiles_root = layout.get_modulefiles_root(deprecated=deprecated)
    found_modules: ModuleVersionsByName = defaultdict(list)

    for module_folder in modulefiles_root.glob("*"):
        for version_path in module_folder.glob("*"):
            found_modules[module_folder.name].append(version_path.name)

    return found_modules
