import yaml

from .apptainer_creator import ApptainerCreator
from .command_creator import CommandCreator
from .layout import Layout
from .models.apptainer import Apptainer
from .models.command import Command
from .models.deployment import DefaultVersionsByName
from .models.module import Module
from .models.shell import Shell
from .module import DEFAULT_VERSION_FILENAME, get_deployed_modulefile_versions
from .shell_creator import ShellCreator
from .templater import Templater, TemplateType


class ModuleCreator:
    """Class for creating modules, including modulefiles and all application files."""

    def __init__(self, templater: Templater, layout: Layout) -> None:
        self._templater = templater
        self._layout = layout
        self._build_layout = layout.build_layout

        self.apptainer_creator = ApptainerCreator(templater, self._build_layout)
        self.command_creator = CommandCreator(templater, self._build_layout)
        self.shell_creator = ShellCreator(templater, self._build_layout)

    def create_modulefile(self, module: Module) -> None:
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

        built_modulefile = self._build_layout.get_built_modulefile(
            module.name, module.version
        )
        built_modulefile.parent.mkdir(exist_ok=True, parents=True)

        self._templater.create(built_modulefile, TemplateType.MODULEFILE, params)

    def update_default_versions(
        self, default_versions: DefaultVersionsByName, layout: Layout
    ) -> None:
        deployed_module_versions = get_deployed_modulefile_versions(layout)

        for name in deployed_module_versions:
            version_file = (
                self._layout.modulefiles_root / name / DEFAULT_VERSION_FILENAME
            )

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

    def create_module_snapshot(self, module: Module):
        snapshot_path = self._build_layout.get_module_snapshot_path(
            module.name, module.version
        )
        snapshot_path.parent.mkdir(exist_ok=True, parents=True)

        with open(snapshot_path, "w") as f:
            yaml.safe_dump(module.model_dump(), f)

    def create_module(self, module: Module):
        self.create_modulefile(module)

        for app in module.applications:
            match app:
                case Apptainer():
                    self.apptainer_creator.create_application_files(app, module)
                case Command():
                    self.command_creator.create_application_files(app, module)
                case Shell():
                    self.shell_creator.create_application_files(app, module)

        self.create_module_snapshot(module)
