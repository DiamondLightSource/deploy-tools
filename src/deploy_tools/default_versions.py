from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .module_creator import ModuleCreator
from .templater import Templater


def apply_default_versions(
    default_versions: DefaultVersionsByName, layout: Layout
) -> None:
    """Update .version files for current default version settings."""
    templater = Templater()
    module_creator = ModuleCreator(templater, layout)
    module_creator.update_default_versions(default_versions, layout)
