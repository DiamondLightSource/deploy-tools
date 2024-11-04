from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .models.module import Module
from .module import VERSION_FILENAME, get_deployed_module_versions
from .templater import Templater, TemplateType


class ModulefileCreator:
    """Class for creating modulefiles, including optional dependencies and env vars."""

    def __init__(self, templater: Templater, layout: Layout) -> None:
        self._templater = templater
        self._layout = layout

    def create_modulefile(self, module: Module) -> None:
        entrypoints_folder = self._layout.get_entrypoints_folder(
            module.name, module.version
        )

        description = module.description
        if description is None:
            description = f"Scripts for {module.name}"

        params = {
            "module_name": module.name,
            "module_description": description,
            "env_vars": module.env_vars,
            "dependencies": module.dependencies,
            "entrypoint_folder": entrypoints_folder,
        }

        modulefile = self._layout.modulefiles_root / module.name / module.version
        modulefile.parent.mkdir(exist_ok=True, parents=True)

        self._templater.create(modulefile, TemplateType.MODULEFILE, params)

    def update_default_versions(
        self, default_versions: DefaultVersionsByName, layout: Layout
    ) -> None:
        deployed_module_versions = get_deployed_module_versions(layout)

        for name in deployed_module_versions:
            version_file = self._layout.modulefiles_root / name / VERSION_FILENAME

            if name in default_versions:
                params = {"version": default_versions[name]}

                self._templater.create(
                    version_file,
                    TemplateType.MODULEFILE_VERSION,
                    params,
                    overwrite=True,
                )
            else:
                version_file.unlink(missing_ok=True)
