import subprocess
from pathlib import Path

from .models.application import ApplicationMetadata
from .models.apptainer import Apptainer


def generate_sif_file(
    metadata: ApplicationMetadata,
    config: Apptainer,
    output_folder: Path,
):
    output_path = output_folder / ":".join((metadata.name, (metadata.version + ".sif")))

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


def generate_entrypoint_file(config: Apptainer, output_folder: Path, filename: Path):
    pass
