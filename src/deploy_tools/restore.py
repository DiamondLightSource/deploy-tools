from .layout import Layout
from .models.module import Module
from .module import is_modulefile_deployed, restore_modulefile


class RestoreError(Exception):
    pass


def check_restore(modules: list[Module], layout: Layout) -> None:
    """Verify that restore() can be run on the current deployment area."""
    for module in modules:
        name = module.name
        version = module.version

        if not is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if is_modulefile_deployed(name, version, layout):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def restore(modules: list[Module], layout: Layout) -> None:
    """Restore a previously deprecated module."""
    for module in modules:
        restore_modulefile(module.name, module.version, layout)
