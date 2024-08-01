from pathlib import Path

from jinja2 import Environment, PackageLoader

from .deployment import DEPLOYMENT_ENTRYPOINTS_DIR, DEPLOYMENT_MODULEFILES_DIR
from .models.module import ModuleConfig

MODULEFILE_TEMPLATE = "modulefile"


class ModuleCreator:
    """Class for creating modulefiles, including optional dependencies and env vars."""

    def __init__(self, deployment_root: Path):
        self._env = Environment(loader=PackageLoader("deploytools"))
        self._modulefiles_root = deployment_root / DEPLOYMENT_MODULEFILES_DIR
        self._entrypoints_root = deployment_root / DEPLOYMENT_ENTRYPOINTS_DIR

    def create_module_file(self, module: ModuleConfig):
        template = self._env.get_template(MODULEFILE_TEMPLATE)

        config = module.metadata
        entrypoints_folder = self._entrypoints_root / config.name / config.version

        description = config.description
        if description is None:
            description = f"Scripts for {config.name}"

        parameters = {
            "module_name": config.name,
            "module_description": description,
            "env_vars": config.env_vars,
            "dependencies": config.dependencies,
            "entrypoint_folder": entrypoints_folder,
        }

        module_file = self._modulefiles_root / config.name / config.version
        module_file.parent.mkdir(exist_ok=True, parents=True)

        with open(module_file, "w") as f:
            f.write(template.render(**parameters))
