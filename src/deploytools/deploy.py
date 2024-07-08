import os
from pathlib import Path

import typer
from typing_extensions import Annotated

from .apptainer import ApptainerCreator
from .models.apptainer import ApptainerModel
from .models.load import load_deployments
from .models.module import ModuleModel
from .models.runfile import RunFileModel
from .module import ModuleCreator
from .runfile import RunFileCreator

app = typer.Typer()

app.command()


def create_module_files(modules: list[ModuleModel], root_folder: Path):
    creator = ModuleCreator(root_folder)

    for module in modules:
        creator.create_module_file(module)


def create_entrypoints(modules: list[ModuleModel], root_folder: Path):
    apptainer_creator = ApptainerCreator(root_folder)
    runfile_creator = RunFileCreator(root_folder)

    for module in modules:
        includes_apptainer = False

        for application in module.applications:
            config = application.app_config

            match config:
                case ApptainerModel():
                    apptainer_creator.generate_sif_file(config)
                    apptainer_creator.create_entrypoint_files(config, module)
                    includes_apptainer = True
                case RunFileModel():
                    runfile_creator.create_entrypoint_file(config, module)

        if includes_apptainer:
            apptainer_creator.create_apptainer_launch_file(module)


def dir_empty(dir_path: Path):
    return not next(os.scandir(dir_path), None)


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
    # For testing
    assert dir_empty(root_folder), "Root folder for deployment must be empty"

    modules = load_deployments(config_folder)

    create_entrypoints(modules, root_folder)
    create_module_files(modules, root_folder)


def main():
    typer.run(deploy)
