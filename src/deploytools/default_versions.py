from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .models.module import Module
from .module import (
    VERSION_FILENAME,
    ModuleCreator,
    ModuleVersionsByName,
    get_deployed_module_versions,
)


class DefaultVersionsError(Exception):
    pass


def check_default_versions(
    default_versions: DefaultVersionsByName,
    added_modules: list[Module],
    removed_modules: list[Module],
    layout: Layout,
) -> None:
    final_deployed_modules = get_final_deployed_module_versions(
        layout, added_modules, removed_modules
    )

    for name, versions in final_deployed_modules.items():
        version_file = layout.get_modulefiles_root() / name / VERSION_FILENAME
        if version_file.is_dir():
            raise DefaultVersionsError(
                f"Version file {version_file} is directory; cannot update or remove."
            )

        if name in default_versions:
            default = default_versions[name]
            if default not in versions:
                raise DefaultVersionsError(
                    f"Unable to configure {name}/{default} as default; module does not "
                    f"exist."
                )


def apply_default_versions(default_versions: DefaultVersionsByName, layout: Layout):
    """Update version files for current default settings."""
    module_creator = ModuleCreator(layout)
    module_creator.update_default_versions(default_versions, layout)


def get_final_deployed_module_versions(
    layout: Layout, added_modules: list[Module], removed_modules: list[Module]
) -> ModuleVersionsByName:
    deployed_modules = get_deployed_module_versions(layout)

    for module in added_modules:
        deployed_modules[module.metadata.name].append(module.metadata.version)

    for module in removed_modules:
        deployed_modules[module.metadata.name].remove(module.metadata.version)

    return deployed_modules
