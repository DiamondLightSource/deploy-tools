from pathlib import Path

from jinja2 import Environment, PackageLoader

from .models.module import ModuleMetadataModel

APPTAINER_LAUNCH_FILE = "apptainer-launch"


class Module:
    def __init__(self):
        self._env = Environment(loader=PackageLoader("deploytools"))

    def create_module_file(
        self, config: ModuleMetadataModel, output_folder: Path, entrypoint_folder: Path
    ):
        template = self._env.get_template("module")

        description = config.description
        if description is None:
            description = f"Entrypoint scripts for {config.name}"

        parameters = {
            "module_name": config.name,
            "module_version": config.version,
            "module_description": description,
            "entrypoint_folder": entrypoint_folder,
        }

        output_file = output_folder / config.name / config.version
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, "w") as f:
            f.write(template.render(**parameters))
