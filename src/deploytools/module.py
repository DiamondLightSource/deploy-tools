from pathlib import Path

from jinja2 import Environment, PackageLoader

from .models.module import ModuleModel

APPTAINER_LAUNCH_FILE = "apptainer-launch"


class ModuleCreator:
    def __init__(self, root_folder: Path):
        self._env = Environment(loader=PackageLoader("deploytools"))
        self._root_folder = root_folder
        self._modules_root = self._root_folder / "modulefiles"
        self._entrypoints_root = self._root_folder / "entrypoints"

    def create_module_file(self, module: ModuleModel):
        template = self._env.get_template("module")

        config = module.metadata
        entrypoint_folder = self._entrypoints_root / config.name / config.version

        description = config.description
        if description is None:
            description = f"Entrypoint scripts for {config.name}"

        parameters = {
            "module_name": config.name,
            "module_version": config.version,
            "module_description": description,
            "entrypoint_folder": entrypoint_folder,
        }

        module_file = self._modules_root / config.name / config.version
        module_file.parent.mkdir(exist_ok=True, parents=True)

        with open(module_file, "w") as f:
            f.write(template.render(**parameters))
