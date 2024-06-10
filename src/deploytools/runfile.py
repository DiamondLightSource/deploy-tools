from pathlib import Path

from jinja2 import Environment, PackageLoader

from .models.runfile import RunFileModel
from .module import ModuleModel


class RunFileCreator:
    def __init__(self, root_folder: Path):
        self._env = Environment(loader=PackageLoader("deploytools"))
        self._root_folder = root_folder
        self._entrypoints_root = self._root_folder / "entrypoints"

    def create_entrypoint_file(
        self,
        config: RunFileModel,
        module: ModuleModel,
    ):
        template = self._env.get_template("runfile_entrypoint")

        output_folder = (
            self._entrypoints_root / module.metadata.name / module.metadata.version
        )
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / config.name

        parameters = {
            "command_path": config.command_path,
            "command_args": config.command_args,
        }

        with open(output_file, "w") as f:
            f.write(template.render(**parameters))

        output_file.chmod(0o755)
