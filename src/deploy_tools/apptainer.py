import subprocess
import uuid
from itertools import chain
from pathlib import Path

from .layout import Layout
from .models.apptainer import Apptainer
from .models.module import Module, ModuleMetadata
from .templater import Templater, TemplateType


class ApptainerError(Exception):
    pass


class ApptainerCreator:
    """Class for creating apptainer entrypoints using a specified image and commands."""

    def __init__(self, templater: Templater, layout: Layout) -> None:
        self._templater = templater
        self._layout = layout

    def create_application_files(self, config: Apptainer, module: Module) -> None:
        self._generate_sif_file(config, module)
        metadata = module.metadata

        entrypoints_folder = self._layout.get_entrypoints_folder(
            metadata.name, metadata.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        sif_file = self._get_sif_file_path(config, module.metadata)

        global_options = config.global_options
        for entrypoint in config.entrypoints:
            options = entrypoint.options
            entrypoint_file = entrypoints_folder / entrypoint.executable_name

            mounts = ",".join(chain(global_options.mounts, options.mounts)).strip()

            apptainer_args = f"{global_options.apptainer_args} {options.apptainer_args}"
            apptainer_args = apptainer_args.strip()

            command_args = f"{global_options.command_args} {options.command_args}"
            command_args = command_args.strip()

            params = {
                "mounts": mounts,
                "apptainer_args": apptainer_args,
                "sif_file": sif_file,
                "command": entrypoint.command,
                "command_args": command_args,
            }

            self._templater.create(
                entrypoint_file,
                TemplateType.APPTAINER_ENTRYPOINT,
                params,
                executable=True,
            )

    def _generate_sif_file(self, config: Apptainer, module: Module) -> None:
        sif_file = self._get_sif_file_path(config, module.metadata)
        sif_file.parent.mkdir(parents=True, exist_ok=True)

        if not sif_file.is_absolute():
            raise ApptainerError(f"Sif file output path must be absolute:\n{sif_file}")

        if sif_file.exists():
            raise ApptainerError(f"Sif file output already exists:\n{sif_file}")

        commands = ["apptainer", "pull", sif_file, config.container.url]
        subprocess.run(commands, check=True)

    def _get_sif_file_path(self, config: Apptainer, metadata: ModuleMetadata) -> Path:
        sif_folder = self._layout.get_sif_files_folder(metadata.name, metadata.version)
        file_name = uuid.uuid3(uuid.NAMESPACE_URL, config.container.url).hex
        return sif_folder / f"{file_name}.sif"
