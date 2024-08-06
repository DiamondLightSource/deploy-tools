from .deploy import deploy
from .layout import Layout
from .models.module import Module
from .module import in_deployment_area
from .remove import remove_deployed_module


class UpdateError(Exception):
    pass


def check_update(modules: list[Module], layout: Layout):
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        if not in_deployment_area(name, version, layout):
            raise UpdateError(
                f"Cannot update {name}/{version}. Not found in deployment area."
            )


def update(modules: list[Module], layout: Layout) -> None:
    """Update development modules from the provided list."""
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        remove_deployed_module(name, version, layout)

    deploy(modules, layout)
