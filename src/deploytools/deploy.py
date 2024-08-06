from .apptainer import ApptainerCreator
from .command import CommandCreator
from .layout import Layout
from .models.apptainer import Apptainer
from .models.command import Command
from .models.module import Module
from .models.shell import Shell
from .module import ModuleCreator, in_deployment_area
from .shell import ShellCreator


class DeployError(Exception):
    pass


def check_deploy(modules: list[Module], layout: Layout):
    if not layout.deployment_root.exists():
        raise DeployError(f"Deployment root does not exist:\n{layout.deployment_root}")

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        if in_deployment_area(name, version, layout):
            raise DeployError(
                f"Cannot deploy {name}/{version}. Already found in deployment area."
            )


def deploy(modules: list[Module], layout: Layout) -> None:
    """Deploy modules from the provided list."""
    if not modules:
        return

    module_creator = ModuleCreator(layout)
    apptainer_creator = ApptainerCreator(layout)
    command_creator = CommandCreator(layout)
    shell_creator = ShellCreator(layout)

    for module in modules:
        module_creator.create_module_file(module)

        for application in module.applications:
            config = application.app_config
            match config:
                case Apptainer():
                    apptainer_creator.create_entrypoint_files(config, module)
                case Command():
                    command_creator.create_entrypoint_file(config, module)
                case Shell():
                    shell_creator.create_entrypoint_file(config, module)
