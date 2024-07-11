from pathlib import Path

from jinja2 import Environment, PackageLoader

from .models.module import ModuleConfig

APPTAINER_LAUNCH_FILE = "apptainer-launch"


class ModuleCreator:
    def __init__(self, deploy_folder: Path):
        self._env = Environment(loader=PackageLoader("deploytools"))
        self._deploy_folder = deploy_folder
        self._modules_folder = self._deploy_folder / "modulefiles"
        self._entrypoints_folder = self._deploy_folder / "entrypoints"

    def create_module_file(self, module: ModuleConfig):
        template = self._env.get_template("modulefile")

        config = module.metadata
        entrypoint_folder = self._entrypoints_folder / config.name / config.version

        description = config.description
        if description is None:
            description = f"Entrypoint scripts for {config.name}"

        parameters = {
            "module_name": config.name,
            "module_description": description,
            "env_vars": config.env_vars,
            "dependencies": config.dependencies,
            "entrypoint_folder": entrypoint_folder,
        }

        module_file = self._modules_folder / config.name / config.version
        module_file.parent.mkdir(exist_ok=True, parents=True)

        with open(module_file, "w") as f:
            f.write(template.render(**parameters))
