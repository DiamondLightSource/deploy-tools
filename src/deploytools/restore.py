from .layout import Layout
from .models.module import Module
from .module import get_deployed_module_versions, move_modulefile


class RestoreError(Exception):
    pass


def check_restore(modules: list[Module], layout: Layout):
    deployed_versions = get_deployed_module_versions(layout)

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        module_file = layout.deprecated_modulefiles_root / name / version
        if not module_file.exists():
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if version in deployed_versions[name]:
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
