from .layout import Layout
from .models.module import ModuleConfig
from .module import get_deployed_module_versions, move_modulefile


class DeprecateError(Exception):
    pass


def check_deprecate(modules: list[ModuleConfig], layout: Layout):
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        check_module_and_version_exist_in_deployment(name, version, layout)
        check_deprecated_free_for_module_and_version(name, version, layout)


def deprecate(modules: list[ModuleConfig], layout: Layout):
    """Deprecate a list of modules.

    This will move the modulefile to a 'deprecated' directory."""
    deployment_modulefiles_root = layout.get_modulefiles_root()
    deprecated_modulefiles_root = layout.get_modulefiles_root(deprecated=True)

    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        move_modulefile(
            name, version, deployment_modulefiles_root, deprecated_modulefiles_root
        )


def check_module_and_version_exist_in_deployment(
    name: str, version: str, layout: Layout
):
    versions = get_deployed_module_versions(layout)
    if version not in versions[name]:
        raise DeprecateError(
            f"Cannot deprecate {name}/{version}. Not found in deployment area."
        )


def check_deprecated_free_for_module_and_version(
    name: str, version: str, layout: Layout
):
    module_file = layout.get_modulefiles_root(deprecated=True) / name / version
    if module_file.exists():
        raise DeprecateError(
            f"Cannot deprecate {name}/{version}. Path already exists:\n{module_file}"
        )
