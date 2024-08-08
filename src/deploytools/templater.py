from enum import StrEnum
from pathlib import Path
from typing import Any

import jinja2

__all__ = ["TemplateType", "Templater"]

TEMPLATES_PACKAGE = "deploytools"


class TemplateType(StrEnum):
    MODULEFILE = "modulefile"
    MODULEFILE_VERSION = "modulefile_version"
    APPTAINER_ENTRYPOINT = "apptainer_entrypoint"
    COMMAND_ENTRYPOINT = "command_entrypoint"
    SHELL_ENTRYPOINT = "shell_entrypoint"


DEFAULT_PERMISSIONS = 0o644
EXECUTABLE_PERMISSIONS = 0o755


class Templater:
    def __init__(self) -> None:
        self._env = jinja2.Environment(loader=jinja2.PackageLoader("deploytools"))
        self._templates: dict[str, jinja2.Template] = {}
        self._load_templates()

    def create(
        self,
        output_file: Path,
        template: TemplateType,
        parameters: dict[str, Any],
        executable: bool = False,
    ) -> None:
        with open(output_file, "w") as f:
            f.write(self._templates[template].render(**parameters))

        permissions = EXECUTABLE_PERMISSIONS if executable else DEFAULT_PERMISSIONS
        output_file.chmod(permissions)

    def _load_templates(self) -> None:
        for template_type in TemplateType:
            self._templates[template_type] = self._env.get_template(str(template_type))
