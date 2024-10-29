import shutil

from .layout import Layout
from .models.module import Module
from .module import in_deployment_area, in_deprecated_area, is_module_dev_mode


class RemovalError(Exception):
    pass


def check_remove(modules: list[Module], layout: Layout) -> None:
    """Verify that remove() can be run on the current deployment area."""
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


def remove(modules: list[Module], layout: Layout) -> None:
    """Remove the given modules from the deployment area."""
    for module in modules:
        name = module.metadata.name
        version = module.metadata.version
        if is_module_dev_mode(module):
            remove_deployed_module(name, version, layout)
        else:
            remove_deprecated_module(name, version, layout)


def remove_deployed_module(name: str, version: str, layout: Layout) -> None:
    module_file = layout.modulefiles_root / name / version
    module_file.unlink()

    remove_module(name, version, layout)


def remove_deprecated_module(name: str, version: str, layout: Layout) -> None:
    module_file = layout.deprecated_modulefiles_root / name / version
    module_file.unlink()

    remove_module(name, version, layout)


def remove_module(name: str, version: str, layout: Layout) -> None:
    module_folder = layout.get_module_folder(name, version)
    if module_folder.exists():
        shutil.rmtree(module_folder)
