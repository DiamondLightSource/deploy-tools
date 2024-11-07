from .layout import Layout
from .models.module import Module
from .module import deprecate_modulefile, is_modulefile_deployed


class DeprecateError(Exception):
    pass


def check_deprecate(modules: list[Module], layout: Layout) -> None:
    """Verify that deprecate() can be run on the current deployment area."""
    for module in modules:
        name = module.name
        version = module.version

        if not is_modulefile_deployed(name, version, layout):
            raise DeprecateError(
                f"Cannot deprecate {name}/{version}. Not found in deployment area."
            )

        if is_modulefile_deployed(name, version, layout, in_deprecated=True):
            raise DeprecateError(
                f"Cannot deprecate {name}/{version}. Already found in deprecated area."
            )


def deprecate(modules: list[Module], layout: Layout) -> None:
    """Deprecate a list of modules.

    This will move the modulefile to a 'deprecated' directory. If the modulefile path is
    set up to include the 'deprecated' directory, all modulefiles should continue to
    work.
    """
    for module in modules:
        deprecate_modulefile(module.name, module.version, layout)
