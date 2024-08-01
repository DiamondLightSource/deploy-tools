from .apptainer import ApptainerCreator
from .command import CommandCreator
from .layout import Layout
from .models.apptainer import Apptainer
from .models.command import Command
from .models.module import Module
from .models.shell import Shell
from .module import ModuleCreator
from .shell import ShellCreator


class DeployError(Exception):
    pass


def check_deploy(layout: Layout):
    deployment_root = layout.get_deployment_root()
    if not layout.get_deployment_root().exists():
        raise DeployError(f"Deployment root does not exist:\n{deployment_root}")


def deploy(modules_list: list[Module], layout: Layout):
    """Deploy modules from the provided list."""
    if modules_list:
        create_entrypoints(modules_list, layout)
        create_module_files(modules_list, layout)


def create_module_files(modules: list[Module], layout: Layout):
    creator = ModuleCreator(layout)

    for module in modules:
        creator.create_module_file(module)


def create_entrypoints(modules: list[Module], layout: Layout):
    apptainer_creator = ApptainerCreator(layout)
    command_creator = CommandCreator(layout)
    shell_creator = ShellCreator(layout)

    for module in modules:
        for application in module.applications:
            config = application.app_config

            match config:
                case Apptainer():
                    apptainer_creator.generate_sif_file(config, module)
                    apptainer_creator.create_entrypoint_files(config, module)
                case Command():
                    command_creator.create_entrypoint_file(config, module)
                case Shell():
                    shell_creator.create_entrypoint_file(config, module)
