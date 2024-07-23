from pathlib import Path

import typer
from typing_extensions import Annotated

from .apptainer import ApptainerCreator
from .command import CommandCreator
from .deployment import create_deployment_snapshot
from .models.apptainer import ApptainerConfig
from .models.command import CommandConfig
from .models.load import load_deployment
from .models.module import ModuleConfig
from .models.shell import ShellConfig
from .module import ModuleCreator
from .shell import ShellCreator
from .validation import validate_deployment


def deploy(
    deploy_folder: Annotated[
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
    """Validate and deploy modules that have been updated since the last deployment."""
    assert deploy_folder.exists(), f"Deployment folder does not exist:\n{deploy_folder}"

    deployment = load_deployment(config_folder)
    modules_list = validate_deployment(deployment, deploy_folder)
    create_deployment_snapshot(deployment, deploy_folder)

    if modules_list:
        create_entrypoints(modules_list, deploy_folder)
        create_module_files(modules_list, deploy_folder)


def create_module_files(modules: list[ModuleConfig], deploy_folder: Path):
    creator = ModuleCreator(deploy_folder)

    for module in modules:
        creator.create_module_file(module)


def create_entrypoints(modules: list[ModuleConfig], deploy_folder: Path):
    apptainer_creator = ApptainerCreator(deploy_folder)
    command_creator = CommandCreator(deploy_folder)
    shell_creator = ShellCreator(deploy_folder)

    for module in modules:
        includes_apptainer = False

        for application in module.applications:
            config = application.app_config

            match config:
                case ApptainerConfig():
                    apptainer_creator.generate_sif_file(config, module)
                    apptainer_creator.create_entrypoint_files(config, module)
                    includes_apptainer = True
                case CommandConfig():
                    command_creator.create_entrypoint_file(config, module)
                case ShellConfig():
                    shell_creator.create_entrypoint_file(config, module)

        if includes_apptainer:
            apptainer_creator.create_apptainer_launch_file(module)
