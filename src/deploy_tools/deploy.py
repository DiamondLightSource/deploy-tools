from .layout import Layout
from .models.module import Module
from .module import is_modulefile_deployed
from .module_creator import ModuleCreator
from .templater import Templater


class DeployError(Exception):
    pass


def check_deploy(modules: list[Module], layout: Layout) -> None:
    """Verify that deploy() can be run on the current deployment area."""
    for module in modules:
        name = module.name
        version = module.version

        if is_modulefile_deployed(name, version, layout):
            raise DeployError(
                f"Cannot deploy {name}/{version}. Already found in deployment area."
            )


def deploy(modules: list[Module], layout: Layout) -> None:
    """Deploy modules from the provided list."""
    if not modules:
        return

    templater = Templater()
    module_creator = ModuleCreator(templater, layout)

    for module in modules:
        module_creator.create_module(module)
