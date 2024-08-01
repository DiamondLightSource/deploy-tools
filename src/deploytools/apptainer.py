import subprocess
from itertools import chain
from pathlib import Path

from .deployment import DEPLOYMENT_ENTRYPOINTS_DIR, DEPLOYMENT_SIF_FILES_DIR
from .models.apptainer import ApptainerConfig
from .models.module import ModuleConfig, ModuleMetadataConfig
from .templater import Templater, TemplateType


class ApptainerError(Exception):
    pass


class ApptainerCreator:
    """Class for creating apptainer entrypoints using a specified image and command."""

    def __init__(self, deployment_root: Path):
        self._templater = Templater()
        self._entrypoints_root = deployment_root / DEPLOYMENT_ENTRYPOINTS_DIR
        self._sif_root = deployment_root / DEPLOYMENT_SIF_FILES_DIR

    def generate_sif_file(self, config: ApptainerConfig, module: ModuleConfig):
        sif_file = self.get_sif_file_path(config, module.metadata)
        sif_file.parent.mkdir(parents=True, exist_ok=True)

        if not sif_file.is_absolute():
            raise ApptainerError(f"Sif file output path must be absolute:\n{sif_file}")

        if sif_file.exists():
            raise ApptainerError(f"Sif file output already exists:\n{sif_file}")

        container_path = f"{config.container.path}:{config.container.version}"

        commands = ["apptainer", "pull", sif_file, container_path]
        subprocess.run(commands, check=True)

    def create_entrypoint_files(self, config: ApptainerConfig, module: ModuleConfig):
        entrypoints_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        template = self._templater.get_template(TemplateType.APPTAINER_ENTRYPOINT)

        sif_file = self.get_sif_file_path(config, module.metadata)

        global_options = config.global_options
        for entrypoint in config.entrypoints:
            options = entrypoint.options
            entrypoint_file = entrypoints_folder / entrypoint.executable_name

            mounts = ",".join(chain(global_options.mounts, options.mounts)).strip()

            apptainer_args = f"{global_options.apptainer_args} {options.apptainer_args}"
            apptainer_args.strip()

            command_args = f"{global_options.command_args} {options.command_args}"
            command_args.strip()

            params = {
                "mounts": mounts,
                "apptainer_args": apptainer_args,
                "sif_file": sif_file,
                "command": entrypoint.command,
                "command_args": command_args,
            }

            self._templater.create(entrypoint_file, template, params, executable=True)

    def get_sif_file_path(
        self, config: ApptainerConfig, metadata: ModuleMetadataConfig
    ):
        sif_parent = self._sif_root / metadata.name / metadata.version
        sif_file = sif_parent / f"{config.name}:{config.version}.sif"

        return sif_file
