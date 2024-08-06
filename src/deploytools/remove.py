import os
import shutil

from .layout import Layout
from .models.module import Module
from .module import in_deployment_area, in_deprecated_area, is_module_dev_mode


class RemovalError(Exception):
    pass


def check_remove(modules: list[Module], layout: Layout):
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version

        if is_module_dev_mode(module):
            if not in_deployment_area(name, version, layout):
                raise RemovalError(
                    f"Cannot remove {name}/{version}. Not found in deployment area."
                )
            continue

        if not in_deprecated_area(name, version, layout):
            raise RemovalError(
                f"Cannot remove {name}/{version}. Not found in deprecated area."
            )


def remove(modules: list[Module], layout: Layout):
    """Remove a deprecated module."""
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        if is_module_dev_mode(module):
            remove_deployed_module(name, version, layout)
        else:
            remove_deprecated_module(name, version, layout)


def remove_deployed_module(name: str, version: str, layout: Layout):
    module_file = layout.modulefiles_root / name / version
    os.remove(module_file)

    remove_application_paths(name, version, layout)


def remove_deprecated_module(name: str, version: str, layout: Layout):
    module_file = layout.deprecated_modulefiles_root / name / version
    os.remove(module_file)

    remove_application_paths(name, version, layout)


def remove_application_paths(name: str, version: str, layout: Layout):
    to_remove = layout.get_application_paths()
    for path in to_remove:
        version_path = path / name / version
        if version_path.exists():
            shutil.rmtree(version_path)
