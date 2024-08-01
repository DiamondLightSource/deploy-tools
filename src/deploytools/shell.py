from .layout import Layout
from .models.shell import ShellConfig
from .module import ModuleConfig
from .templater import Templater, TemplateType


class ShellCreator:
    """Class for creating 'shell' entrypoints, which run bash scripts."""

    def __init__(self, layout: Layout):
        self._templater = Templater()
        self._entrypoints_root = layout.get_entrypoints_root()

    def create_entrypoint_file(
        self,
        config: ShellConfig,
        module: ModuleConfig,
    ):
        template = self._templater.get_template(TemplateType.SHELL_ENTRYPOINT)

        entrypoints_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        entrypoint_file = entrypoints_folder / config.name

        parameters = {
            "script": config.script,
        }

        self._templater.create(entrypoint_file, template, parameters, executable=True)
