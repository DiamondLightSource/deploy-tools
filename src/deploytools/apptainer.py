import subprocess
from itertools import chain
from pathlib import Path

from jinja2 import Environment, PackageLoader

from .models.apptainer import ApptainerConfig
from .models.module import ModuleConfig

APPTAINER_LAUNCH_FILE = "apptainer-launch"


class ApptainerCreator:
    def __init__(self, root_folder: Path):
        self._env = Environment(loader=PackageLoader("deploytools"))
        self._root_folder = root_folder
        self._entrypoints_root = self._root_folder / "entrypoints"
        self._sif_root = self._root_folder / "sif_files"

    def generate_sif_file(self, config: ApptainerConfig, module: ModuleConfig):
        sif_folder = self._sif_root / module.metadata.name / module.metadata.version
        sif_folder.mkdir(parents=True, exist_ok=True)

        output_path = sif_folder / ":".join((config.name, (config.version + ".sif")))

        if not output_path.is_absolute():
            raise Exception("Sif file output path must be absolute")

        if output_path.exists():
            raise Exception("Sif file with this name and version already exists")

        commands = [
            "apptainer",
            "pull",
            output_path,
            ":".join((config.container.path, config.container.version)),
        ]

        subprocess.run(commands, check=True)

    def create_entrypoint_files(self, config: ApptainerConfig, module: ModuleConfig):
        output_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        output_folder.mkdir(parents=True, exist_ok=True)
        template = self._env.get_template("apptainer_entrypoint")

        for entrypoint in config.entrypoints:
            output_file = output_folder / entrypoint.executable_name

            mounts = ",".join(
                chain(config.global_options.mounts, entrypoint.options.mounts)
            ).strip()

            apptainer_args = " ".join(
                (
                    config.global_options.apptainer_args,
                    entrypoint.options.apptainer_args,
                )
            ).strip()

            command_args = " ".join(
                (
                    config.global_options.command_args,
                    entrypoint.options.command_args,
                )
            ).strip()

            parameters = {
                "mounts": mounts,
                "apptainer_args": apptainer_args,
                "sif_name": config.name,
                "sif_version": config.version,
                "command": entrypoint.command,
                "command_args": command_args,
            }

            with open(output_file, "w") as f:
                f.write(template.render(**parameters))

            output_file.chmod(0o755)

    def create_apptainer_launch_file(self, module: ModuleConfig):
        output_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / APPTAINER_LAUNCH_FILE
        sif_folder = self._sif_root / module.metadata.name / module.metadata.version

        template = self._env.get_template(APPTAINER_LAUNCH_FILE)
        with open(output_file, "w") as f:
            f.write(template.render(sif_folder=str(sif_folder)))

        output_file.chmod(0o755)
