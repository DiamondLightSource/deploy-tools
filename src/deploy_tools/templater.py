from enum import StrEnum
from pathlib import Path
from typing import Any

import jinja2

__all__ = ["TemplateType", "Templater"]

TEMPLATES_PACKAGE = "deploy_tools"


class TemplateType(StrEnum):
    MODULEFILE = "modulefile"
    MODULEFILE_VERSION = "modulefile_version"
    APPTAINER_ENTRYPOINT = "apptainer_entrypoint"
    SHELL_ENTRYPOINT = "shell_entrypoint"


DEFAULT_PERMISSIONS = 0o644
EXECUTABLE_PERMISSIONS = 0o755


class Templater:
    """Abstracts the specifics of jinja2 templating and our particular template files.

    File permissions are also managed here to ensure consistency of output between
    different Application types.
    """

    def __init__(self) -> None:
        self._env = jinja2.Environment(loader=jinja2.PackageLoader(TEMPLATES_PACKAGE))
        self._templates: dict[str, jinja2.Template] = {}
        self._load_templates()

    def create(
        self,
        output_file: Path,
        template: TemplateType,
        parameters: dict[str, Any],
        executable: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Create an output file, using the given template and template parameters."""
        open_mode = "w" if overwrite else "x"
        with open(output_file, open_mode) as f:
            f.write(self._templates[template].render(**parameters))

        permissions = EXECUTABLE_PERMISSIONS if executable else DEFAULT_PERMISSIONS
        output_file.chmod(permissions)

    def _load_templates(self) -> None:
        for template_type in TemplateType:
            self._templates[template_type] = self._env.get_template(str(template_type))
