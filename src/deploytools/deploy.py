from pathlib import Path

from .apptainer import ApptainerCreator
from .command import CommandCreator
from .models.apptainer import ApptainerConfig
from .models.command import CommandConfig
from .models.module import ModuleConfig
from .models.shell import ShellConfig
from .module import ModuleCreator
from .shell import ShellCreator


class DeployError(Exception):
    pass


def check_deploy(deployment_root: Path):
    if not deployment_root.exists():
        raise DeployError(f"Deployment root does not exist:\n{deployment_root}")


def deploy(modules_list: list[ModuleConfig], deplyment_root: Path):
    """Deploy modules from the provided list."""
    if modules_list:
        create_entrypoints(modules_list, deplyment_root)
        create_module_files(modules_list, deplyment_root)


def create_module_files(modules: list[ModuleConfig], deployment_root: Path):
    creator = ModuleCreator(deployment_root)

    for module in modules:
        creator.create_module_file(module)


def create_entrypoints(modules: list[ModuleConfig], deployment_root: Path):
    apptainer_creator = ApptainerCreator(deployment_root)
    command_creator = CommandCreator(deployment_root)
    shell_creator = ShellCreator(deployment_root)

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
