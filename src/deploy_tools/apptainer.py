import subprocess
from pathlib import Path


class ApptainerError(Exception):
    pass


def create_sif_file(
    output_path: Path,
    container_url: str,
    create_parents: bool = False,
) -> None:
    if create_parents:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    if not output_path.is_absolute():
        raise ApptainerError(
            f"Building Apptainer file: "
            f"Sif file output path must be absolute:\n{output_path}"
        )

    if output_path.exists():
        raise ApptainerError(
            f"Building Apptainer file: Sif file output already exists:\n{output_path}"
        )

    commands = ["apptainer", "pull", output_path, container_url]
    subprocess.run(commands, check=True)
