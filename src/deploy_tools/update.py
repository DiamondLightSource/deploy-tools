from .deploy import deploy
from .layout import Layout
from .models.module import Module
from .module import is_modulefile_deployed
from .remove import remove_deployed_module


class UpdateError(Exception):
    pass


def check_update(modules: list[Module], layout: Layout) -> None:
    """Verify that update() can be run on the current deployment area."""
    for module in modules:
        name = module.name
        version = module.version

        if not is_modulefile_deployed(name, version, layout):
            raise UpdateError(
                f"Cannot update {name}/{version}. Not found in deployment area."
            )


def update(modules: list[Module], layout: Layout) -> None:
    """Update development modules from the provided list."""
    for module in modules:
        name = module.name
        version = module.version

        remove_deployed_module(name, version, layout)

    deploy(modules, layout)
