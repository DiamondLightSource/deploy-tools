from .apptainer import ApptainerCreator
from .command import CommandCreator
from .layout import Layout
from .models.apptainer import ApptainerConfig
from .models.command import CommandConfig
from .models.module import ModuleConfig
from .models.shell import ShellConfig
from .module import ModuleCreator
from .shell import ShellCreator


class DeployError(Exception):
    pass


def check_deploy(layout: Layout):
    deployment_root = layout.get_deployment_root()
    if not layout.get_deployment_root().exists():
        raise DeployError(f"Deployment root does not exist:\n{deployment_root}")


def deploy(modules_list: list[ModuleConfig], layout: Layout):
    """Deploy modules from the provided list."""
    if modules_list:
        create_entrypoints(modules_list, layout)
        create_module_files(modules_list, layout)


def create_module_files(modules: list[ModuleConfig], layout: Layout):
    creator = ModuleCreator(layout)

    for module in modules:
        creator.create_module_file(module)


def create_entrypoints(modules: list[ModuleConfig], layout: Layout):
    apptainer_creator = ApptainerCreator(layout)
    command_creator = CommandCreator(layout)
    shell_creator = ShellCreator(layout)

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
