import subprocess
from itertools import chain
from pathlib import Path

from jinja2 import Environment, PackageLoader

from .models.apptainer import ApptainerModel

APPTAINER_LAUNCH_FILE = "apptainer-launch"


class Apptainer:
    def __init__(self):
        self._env = Environment(loader=PackageLoader("deploytools"))

    def generate_sif_file(
        self,
        config: ApptainerModel,
        output_folder: Path,
    ):
        output_path = output_folder / ":".join((config.name, (config.version + ".sif")))

        if not output_path.is_absolute:
            raise Exception("Sif file output path must be absolute")

        if output_path.exists:
            raise Exception("Sif file with this version already exists")

        commands = [
            "apptainer",
            "pull",
            output_path,
            "/".join((config.container.path, config.container.version)),
        ]

        subprocess.run(commands, check=True)

    def create_entrypoint_files(
        self,
        config: ApptainerModel,
        output_folder: Path,
    ):
        template = self._env.get_template("apptainer_entrypoint")

        for entrypoint in config.entrypoints:
            output_file = output_folder / entrypoint.executable_name

            mounts = ",".join(
                chain(config.global_options.mounts, entrypoint.options.mounts)
            )

            apptainer_args = " ".join(
                (
                    config.global_options.apptainer_args,
                    entrypoint.options.apptainer_args,
                )
            )

            command_args = " ".join(
                (
                    config.global_options.command_args,
                    entrypoint.options.command_args,
                )
            )

            parameters = {
                "mounts": mounts,
                "apptainer_args": apptainer_args,
                "sif_name": config.name,
                "sif_version": config.version,
                "command_args": command_args,
            }

            with open(output_file, "w") as f:
                f.write(template.render(**parameters))

    def create_apptainer_launch_file(self, output_folder: Path, sif_folder: Path):
        output_file = output_folder / APPTAINER_LAUNCH_FILE

        template = self._env.get_template(APPTAINER_LAUNCH_FILE)
        with open(output_file, "w") as f:
            f.write(template.render(sif_folder=str(sif_folder)))
