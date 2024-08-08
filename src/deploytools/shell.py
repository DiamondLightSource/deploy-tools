from .layout import Layout
from .models.shell import Shell
from .module import Module
from .templater import Template, Templater


class ShellCreator:
    """Class for creating 'shell' entrypoints, which run bash scripts."""

    def __init__(self, templater: Templater, layout: Layout):
        self._templater = templater
        self._entrypoints_root = layout.entrypoints_root

    def create_entrypoint_file(
        self,
        config: Shell,
        module: Module,
    ):
        entrypoints_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        entrypoint_file = entrypoints_folder / config.name

        parameters = {"script": config.script}

        self._templater.create(
            entrypoint_file, Template.SHELL_ENTRYPOINT, parameters, executable=True
        )
