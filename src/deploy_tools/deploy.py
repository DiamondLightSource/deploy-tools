from .apptainer import ApptainerCreator
from .command import CommandCreator
from .layout import Layout
from .models.apptainer import Apptainer
from .models.command import Command
from .models.module import Module
from .models.shell import Shell
from .module import ModulefileCreator, in_deployment_area
from .shell import ShellCreator
from .templater import Templater


class DeployError(Exception):
    pass


def check_deploy(modules: list[Module], layout: Layout) -> None:
    """Verify that deploy() can be run on the current deployment area."""
    if not layout.deployment_root.exists():
        raise DeployError(f"Deployment root does not exist:\n{layout.deployment_root}")

    for module in modules:
        name = module.name
        version = module.version

        if in_deployment_area(name, version, layout):
            raise DeployError(
                f"Cannot deploy {name}/{version}. Already found in deployment area."
            )


def deploy(modules: list[Module], layout: Layout) -> None:
    """Deploy modules from the provided list."""
    if not modules:
        return

    templater = Templater()
    modulefile_creator = ModulefileCreator(templater, layout)
    apptainer_creator = ApptainerCreator(templater, layout)
    command_creator = CommandCreator(templater, layout)
    shell_creator = ShellCreator(templater, layout)

    for module in modules:
        modulefile_creator.create_modulefile(module)

        for app in module.applications:
            match app:
                case Apptainer():
                    apptainer_creator.create_application_files(app, module)
                case Command():
                    command_creator.create_application_files(app, module)
                case Shell():
                    shell_creator.create_application_files(app, module)
