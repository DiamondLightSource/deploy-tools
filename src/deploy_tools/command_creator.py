from .layout import Layout
from .models.command import Command
from .models.module import Module
from .templater import Templater, TemplateType


class CommandCreator:
    """Class for creating 'command' entrypoints, which run an executable on a path."""

    def __init__(self, templater: Templater, layout: Layout) -> None:
        self._templater = templater
        self._layout = layout

    def create_application_files(
        self,
        app: Command,
        module: Module,
    ) -> None:
        entrypoints_folder = self._layout.get_entrypoints_folder(
            module.name, module.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        entrypoint_file = entrypoints_folder / app.name

        params = {
            "command_path": app.command_path,
            "command_args": app.command_args,
        }

        self._templater.create(
            entrypoint_file, TemplateType.COMMAND_ENTRYPOINT, params, executable=True
        )
