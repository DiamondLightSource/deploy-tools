from enum import StrEnum
from pathlib import Path

from jinja2 import Environment, PackageLoader, Template

__all__ = ["TemplateType", "Templater"]

TEMPLATES_PACKAGE = "deploytools"


class TemplateType(StrEnum):
    MODULEFILE = "modulefile"
    APPTAINER_ENTRYPOINT = "apptainer_entrypoint"
    COMMAND_ENTRYPOINT = "command_entrypoint"
    SHELL_ENTRYPOINT = "shell_entrypoint"


DEFAULT_PERMISSIONS = 0o644
EXECUTABLE_PERMISSIONS = 0o755


class TemplateError(Exception):
    pass


class Templater:
    def __init__(self):
        self._env = Environment(loader=PackageLoader("deploytools"))

    def create(
        self,
        output_file: Path,
        template: Template,
        parameters: dict,
        executable: bool = False,
    ) -> None:
        with open(output_file, "w") as f:
            f.write(template.render(**parameters))

        permissions = EXECUTABLE_PERMISSIONS if executable else DEFAULT_PERMISSIONS
        output_file.chmod(permissions)

    def get_template(self, type: TemplateType) -> Template:
        return self._env.get_template(str(type))
