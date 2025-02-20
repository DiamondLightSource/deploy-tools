import subprocess
import uuid
from itertools import chain
from pathlib import Path

from .layout import ModuleBuildLayout
from .models.apptainer import Apptainer
from .models.module import Application, Module
from .models.shell import Shell
from .templater import Templater, TemplateType


class AppBuilderError(Exception):
    pass


class AppBuilder:
    """Class for creating application entrypoints and associated files."""

    def __init__(self, templater: Templater, build_layout: ModuleBuildLayout) -> None:
        self._templater = templater
        self._build_layout = build_layout

    def create_application_files(self, app: Application, module: Module):
        match app:
            case Apptainer():
                self.create_apptainer_files(app, module)
            case Shell():
                self.create_shell_file(app, module)

    def create_apptainer_files(self, app: Apptainer, module: Module) -> None:
        """Create apptainer entrypoints using a specified image and commands."""
        self._generate_sif_file(app, module)
        entrypoints_folder = self._build_layout.get_entrypoints_folder(
            module.name, module.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        relative_sif_file = self._get_sif_file_path(app, module).relative_to(
            entrypoints_folder, walk_up=True
        )

        global_options = app.global_options
        for entrypoint in app.entrypoints:
            options = entrypoint.options
            entrypoint_file = entrypoints_folder / entrypoint.name

            mounts = ",".join(chain(global_options.mounts, options.mounts)).strip()

            apptainer_args = f"{global_options.apptainer_args} {options.apptainer_args}"
            apptainer_args = apptainer_args.strip()

            command = entrypoint.command if entrypoint.command else entrypoint.name

            command_args = f"{global_options.command_args} {options.command_args}"
            command_args = command_args.strip()

            params = {
                "mounts": mounts,
                "apptainer_args": apptainer_args,
                "relative_sif_file": relative_sif_file,
                "command": command,
                "command_args": command_args,
            }

            self._templater.create(
                entrypoint_file,
                TemplateType.APPTAINER_ENTRYPOINT,
                params,
                executable=True,
            )

    def _generate_sif_file(self, app: Apptainer, module: Module) -> None:
        sif_file = self._get_sif_file_path(app, module)
        sif_file.parent.mkdir(parents=True, exist_ok=True)

        if not sif_file.is_absolute():
            raise AppBuilderError(
                f"Building Apptainer files: "
                f"Sif file output path must be absolute:\n{sif_file}"
            )

        if sif_file.exists():
            raise AppBuilderError(
                f"Building Apptainer files: Sif file output already exists:\n{sif_file}"
            )

        commands = ["apptainer", "pull", sif_file, app.container.url]
        subprocess.run(commands, check=True)

    def _get_sif_file_path(self, app: Apptainer, module: Module) -> Path:
        sif_folder = self._build_layout.get_sif_files_folder(
            module.name, module.version
        )
        file_name = uuid.uuid3(uuid.NAMESPACE_URL, app.container.url).hex
        return sif_folder / f"{file_name}.sif"

    def create_shell_file(self, app: Shell, module: Module) -> None:
        """Create shell script using Bash for improved functionality."""
        entrypoints_folder = self._build_layout.get_entrypoints_folder(
            module.name, module.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        entrypoint_file = entrypoints_folder / app.name

        parameters = {"script": app.script}

        self._templater.create(
            entrypoint_file, TemplateType.SHELL_ENTRYPOINT, parameters, executable=True
        )
