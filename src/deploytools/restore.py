from .layout import Layout
from .models.module import Module
from .module import is_module_deployed, is_module_deprecated, move_modulefile


class RestoreError(Exception):
    pass


def check_restore(modules: list[Module], layout: Layout):
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        if not is_module_deprecated(name, version, layout):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if is_module_deployed(name, version, layout):
            raise RestoreError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def restore(modules: list[Module], layout: Layout):
    """Restore a previously deprecated module."""
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        move_modulefile(
            name, version, layout.deprecated_modulefiles_root, layout.modulefiles_root
        )
