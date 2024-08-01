from pathlib import Path

from jinja2 import Environment, PackageLoader

from .deployment import DEPLOYMENT_ENTRYPOINTS_DIR
from .models.command import CommandConfig
from .module import ModuleConfig

COMMAND_ENTRYPOINT_TEMPLATE = "command_entrypoint"


class CommandCreator:
    """Class for creating 'command' entrypoints, which run an executable on a path."""

    def __init__(self, deployment_root: Path):
        self._env = Environment(loader=PackageLoader("deploytools"))
        self._entrypoints_root = deployment_root / DEPLOYMENT_ENTRYPOINTS_DIR

    def create_entrypoint_file(
        self,
        config: CommandConfig,
        module: ModuleConfig,
    ):
        template = self._env.get_template(COMMAND_ENTRYPOINT_TEMPLATE)

        entrypoints_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        entrypoints_folder.mkdir(parents=True, exist_ok=True)
        entrypoint_file = entrypoints_folder / config.name

        parameters = {
            "command_path": config.command_path,
            "command_args": config.command_args,
        }

        with open(entrypoint_file, "w") as f:
            f.write(template.render(**parameters))

        entrypoint_file.chmod(0o755)
