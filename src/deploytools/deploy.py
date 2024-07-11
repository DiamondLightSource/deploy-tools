from pathlib import Path

import typer
import yaml
from typing_extensions import Annotated

from .apptainer import ApptainerCreator
from .models.apptainer import ApptainerConfig
from .models.deployment import DeploymentConfig
from .models.load import load_deployment
from .models.module import ModuleConfig
from .models.runfile import RunFileConfig
from .module import ModuleCreator
from .runfile import RunFileCreator
from .validation import DEPLOYMENT_SNAPSHOT_FILENAME, validate_deployment

app = typer.Typer()

app.command()


def create_deployment_snapshot(deployment: DeploymentConfig, root_folder: Path):
    file_path = root_folder / DEPLOYMENT_SNAPSHOT_FILENAME

    with open(file_path, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def create_module_files(modules: list[ModuleConfig], root_folder: Path):
    creator = ModuleCreator(root_folder)

    for module in modules:
        creator.create_module_file(module)


def create_entrypoints(modules: list[ModuleConfig], root_folder: Path):
    apptainer_creator = ApptainerCreator(root_folder)
    runfile_creator = RunFileCreator(root_folder)

    for module in modules:
        includes_apptainer = False

        for application in module.applications:
            config = application.app_config

            match config:
                case ApptainerConfig():
                    apptainer_creator.generate_sif_file(config, module)
                    apptainer_creator.create_entrypoint_files(config, module)
                    includes_apptainer = True
                case RunFileConfig():
                    runfile_creator.create_entrypoint_file(config, module)

        if includes_apptainer:
            apptainer_creator.create_apptainer_launch_file(module)


def deploy(
    root_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
    config_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
):
    assert root_folder.exists(), f"Deployment folder {root_folder} does not exist."

    deployment = load_deployment(config_folder)
    modules_list = validate_deployment(deployment, root_folder)
    create_deployment_snapshot(deployment, root_folder)

    if modules_list:
        create_entrypoints(modules_list, root_folder)
        create_module_files(modules_list, root_folder)


def main():
    typer.run(deploy)
