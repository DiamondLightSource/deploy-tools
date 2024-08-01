from pathlib import Path

from jinja2 import Environment, PackageLoader

from .deployment import DEPLOYMENT_ENTRYPOINTS_DIR
from .models.shell import ShellConfig
from .module import ModuleConfig

SHELL_ENTRYPOINT_TEMPLATE = "shell_entrypoint"


class ShellCreator:
    """Class for creating 'shell' entrypoints, which run bash scripts."""

    def __init__(self, deployment_root: Path):
        self._env = Environment(loader=PackageLoader("deploytools"))
        self._entrypoints_root = deployment_root / DEPLOYMENT_ENTRYPOINTS_DIR

    def create_entrypoint_file(
        self,
        config: ShellConfig,
        module: ModuleConfig,
    ):
        template = self._env.get_template(SHELL_ENTRYPOINT_TEMPLATE)

        entrypoints_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        entrypoint_file = entrypoints_folder / config.name

        parameters = {
            "script": config.script,
        }

        with open(entrypoint_file, "w") as f:
            f.write(template.render(**parameters))

        entrypoint_file.chmod(0o755)
