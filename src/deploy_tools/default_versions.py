from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .module import VERSION_FILENAME
from .module_creator import ModulefileCreator
from .templater import Templater


class DefaultVersionsError(Exception):
    pass


def check_default_versions(
    default_versions: DefaultVersionsByName,
    layout: Layout,
) -> None:
    """Verify that appy_default_versions() can be run on the current deployment area."""
    for name in default_versions:
        version_file = layout.modulefiles_root / name / VERSION_FILENAME
        if version_file.is_dir():
            raise DefaultVersionsError(
                f"Version file {version_file} is directory; cannot update or remove."
            )


def apply_default_versions(
    default_versions: DefaultVersionsByName, layout: Layout
) -> None:
    """Update .version files for current default version settings."""
    templater = Templater()
    module_creator = ModulefileCreator(templater, layout)
    module_creator.update_default_versions(default_versions, layout)
