from .layout import Layout
from .models.module import Module
from .module import in_deployment_area, in_deprecated_area, move_modulefile


class RestoreError(Exception):
    pass


def check_restore(modules: list[Module], layout: Layout) -> None:
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        if not in_deprecated_area(name, version, layout):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if in_deployment_area(name, version, layout):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def restore(modules: list[Module], layout: Layout) -> None:
    """Restore a previously deprecated module."""
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        move_modulefile(
            name, version, layout.deprecated_modulefiles_root, layout.modulefiles_root
        )
