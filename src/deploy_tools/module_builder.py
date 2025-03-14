from .app_builder import AppBuilder
from .layout import Layout
from .models.module import Module
from .models.save_and_load import save_as_yaml
from .templater import Templater, TemplateType


class ModuleBuilder:
    """Class for creating modules, including modulefiles and all application files."""

    def __init__(self, templater: Templater, layout: Layout) -> None:
        self._templater = templater
        self._layout = layout
        self._build_layout = layout.build_layout

        self.app_creator = AppBuilder(templater, self._build_layout)

    def create_module(self, module: Module) -> None:
        self._create_modulefile(module)

        for app in module.applications:
            self.app_creator.create_application_files(app, module)

        self._create_module_snapshot(module)

    def _create_modulefile(self, module: Module) -> None:
        entrypoints_folder = self._layout.get_entrypoints_folder(
            module.name, module.version
        )

        description = module.description
        if description is None:
            description = f"Scripts for {module.name}"

        params = {
            "module_name": module.name,
            "module_description": description,
            "env_vars": module.env_vars,
            "dependencies": module.dependencies,
            "entrypoint_folder": entrypoints_folder,
        }

        built_modulefile = self._build_layout.get_modulefile(
            module.name, module.version
        )

        self._templater.create(
            built_modulefile, TemplateType.MODULEFILE, params, create_parents=True
        )

    def _create_module_snapshot(self, module: Module) -> None:
        snapshot_path = self._build_layout.get_module_snapshot_path(
            module.name, module.version
        )
        save_as_yaml(module, snapshot_path, create_parents=True)
