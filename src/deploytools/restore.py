from .layout import Layout
from .models.module import ModuleConfig
from .module import get_deployed_module_versions, move_modulefile


class RestoreError(Exception):
    pass


def check_restore(modules: list[ModuleConfig], layout: Layout):
    deprecated_modulefiles_root = layout.get_modulefiles_root(deprecated=True)
    deployed_versions = get_deployed_module_versions(layout)

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        module_file = deprecated_modulefiles_root / name / version
        if not module_file.exists():
            raise RestoreError(
                f"Cannot restore {name}/{version}. Not found in deprecated area."
            )

        if version in deployed_versions[name]:
            raise RestoreError(
                f"Cannot restore {name}/{version}. Already found in deployment area."
            )


def restore(modules: list[ModuleConfig], layout: Layout):
    """Restore a previously deprecated module."""
    deployment_modulefiles_root = layout.get_modulefiles_root()
    deprecated_modulefiles_root = layout.get_modulefiles_root(deprecated=True)

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        move_modulefile(
            name, version, deprecated_modulefiles_root, deployment_modulefiles_root
        )
