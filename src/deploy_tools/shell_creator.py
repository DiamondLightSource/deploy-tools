from .layout import Layout
from .models.shell import Shell
from .module import Module
from .templater import Templater, TemplateType


class ShellCreator:
    """Class for creating 'shell' entrypoints.

    These shell scripts use 'bash' for improved functionality.
    """

    def __init__(self, templater: Templater, layout: Layout) -> None:
        self._templater = templater
        self._layout = layout

    def create_application_files(
        self,
        app: Shell,
        module: Module,
    ) -> None:
        entrypoints_folder = self._layout.get_entrypoints_folder(
            module.name, module.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        entrypoint_file = entrypoints_folder / app.name

        parameters = {"script": app.script}

        self._templater.create(
            entrypoint_file, TemplateType.SHELL_ENTRYPOINT, parameters, executable=True
        )
