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
        apptainer_creator.create_apptainer_launch_file(module)

        for application in module.applications:
            config = application.app_config

            match config:
                case ApptainerModel():
                    apptainer_creator.generate_sif_file(config)
                    apptainer_creator.create_entrypoint_files(config, module)
                case RunFileModel():
                    runfile_creator.create_entrypoint_file(config, module)


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
    modules = load_deployments(config_folder)

    create_entrypoints(modules, root_folder)
    create_module_files(modules, root_folder)


def main():
    typer.run(deploy)
