from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .module import VERSION_FILENAME, ModuleCreator, ModuleVersionsByName


class DefaultVersionsError(Exception):
    pass


def check_default_versions(
    default_versions: DefaultVersionsByName,
    final_deployed_modules: ModuleVersionsByName,
    layout: Layout,
) -> None:
    for name, versions in final_deployed_modules.items():
        version_file = layout.modulefiles_root / name / VERSION_FILENAME
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
