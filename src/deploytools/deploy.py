from pathlib import Path

from .apptainer import ApptainerCreator
from .command import CommandCreator
from .models.apptainer import ApptainerConfig
from .models.command import CommandConfig
from .models.module import ModuleConfig
from .models.shell import ShellConfig
from .module import ModuleCreator
from .shell import ShellCreator


def check_deploy(deploy_folder: Path):
    assert deploy_folder.exists(), f"Deployment folder does not exist:\n{deploy_folder}"


def deploy(modules_list: list[ModuleConfig], deploy_folder: Path):
    """Deploy modules from the provided list."""
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
        for application in module.applications:
            config = application.app_config

            match config:
                case ApptainerConfig():
                    apptainer_creator.generate_sif_file(config, module)
                    apptainer_creator.create_entrypoint_files(config, module)
                case CommandConfig():
                    command_creator.create_entrypoint_file(config, module)
                case ShellConfig():
                    shell_creator.create_entrypoint_file(config, module)
