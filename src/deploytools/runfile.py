from pathlib import Path

from jinja2 import Environment, PackageLoader

from .models.runfile import RunFileModel


class RunFile:
    def __init__(self):
        self._env = Environment(loader=PackageLoader("deploytools"))

    def create_entrypoint_file(
        self,
        config: RunFileModel,
        output_folder: Path,
    ):
        template = self._env.get_template("runfile_entrypoint")

        output_file = output_folder / config.name

        parameters = {
            "command_path": config.command_path,
            "command_args": config.command_args,
        }

        with open(output_file, "w") as f:
            f.write(template.render(**parameters))
