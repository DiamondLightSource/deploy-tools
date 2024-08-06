from .layout import Layout
from .models.module import Module
from .module import is_module_deployed, is_module_deprecated, move_modulefile


class DeprecateError(Exception):
    pass


def check_deprecate(modules: list[Module], layout: Layout):
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        if not is_module_deployed(name, version, layout):
            raise DeprecateError(
                f"Cannot deprecate {name}/{version}. Not found in deployment area."
            )

        if is_module_deprecated(name, version, layout):
            raise DeprecateError(
                f"Cannot deprecate {name}/{version}. Already found in deprecated area."
            )


def deprecate(modules: list[Module], layout: Layout):
    """Deprecate a list of modules.

    This will move the modulefile to a 'deprecated' directory."""
    for module in modules:
        move_modulefile(
            module.metadata.name,
            module.metadata.version,
            layout.modulefiles_root,
            layout.deprecated_modulefiles_root,
        )
