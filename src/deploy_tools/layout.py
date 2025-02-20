from pathlib import Path


class ModuleAreaLayout:
    """Represents the layout of Modules with the given root path.

    This is generic to both built and deployed modules.
    """

    ENTRYPOINTS_FOLDER = "entrypoints"

    MODULE_SNAPSHOT_FILENAME = "module.yaml"
    MODULEFILE_FILENAME = "modulefile"

    def __init__(self, root: Path) -> None:
        self._root = root

    def get_module_folder(self, name: str, version: str) -> Path:
        return self._root / name / version

    def get_entrypoints_folder(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.ENTRYPOINTS_FOLDER

    def get_modulefile(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.MODULEFILE_FILENAME

    def get_module_snapshot_path(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.MODULE_SNAPSHOT_FILENAME


class ModuleBuildLayout(ModuleAreaLayout):
    """Represents the layout used for Modules during the build process.

    When intended to be used before the Deploy step, this should be done on the same
    filesystem as the Deployment Area, in order to ensure that all filesystem moves are
    atomic.
    """

    SIF_FILES_FOLDER = "sif_files"

    def get_sif_files_folder(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.SIF_FILES_FOLDER

    @property
    def build_root(self):
        return self._root


class Layout:
    """Represents the layout of the deployment area."""

    MODULES_ROOT_NAME = "modules"
    MODULEFILES_ROOT_NAME = "modulefiles"
    DEPRECATED_ROOT_NAME = "deprecated"
    DEFAULT_BUILD_ROOT_NAME = "build"
    DEFAULT_VERSION_FILENAME = ".version"

    DEPLOYMENT_SNAPSHOT_FILENAME = "deployment.yaml"
    PREVIOUS_DEPLOYMENT_SNAPSHOT_FILENAME = "previous-deployment.yaml"

    def __init__(self, deployment_root: Path, build_root: Path | None = None) -> None:
        self._root = deployment_root
        self._modules_layout = ModuleAreaLayout(self.modules_root)

        if build_root is not None:
            self._build_root = build_root
        else:
            self._build_root = self._root / self.DEFAULT_BUILD_ROOT_NAME

    def get_module_folder(self, name: str, version: str) -> Path:
        return self._modules_layout.get_module_folder(name, version)

    def get_entrypoints_folder(self, name: str, version: str) -> Path:
        return self._modules_layout.get_entrypoints_folder(name, version)

    def get_modulefiles_root(self, from_deprecated: bool = False) -> Path:
        return (
            self.deprecated_modulefiles_root
            if from_deprecated
            else self.modulefiles_root
        )

    def get_modulefile_link(
        self, name: str, version: str, from_deprecated: bool = False
    ) -> Path:
        return self.get_modulefiles_root(from_deprecated) / name / version

    def get_modulefile(self, name: str, version: str) -> Path:
        return self._modules_layout.get_modulefile(name, version)

    def get_module_snapshot_path(self, name: str, version: str) -> Path:
        return self._modules_layout.get_module_snapshot_path(name, version)

    def get_default_version_file(self, name: str) -> Path:
        return self.modulefiles_root / name / self.DEFAULT_VERSION_FILENAME

    @property
    def deployment_root(self) -> Path:
        return self._root

    @property
    def deprecated_root(self) -> Path:
        return self._root / self.DEPRECATED_ROOT_NAME

    @property
    def modules_root(self) -> Path:
        return self._root / self.MODULES_ROOT_NAME

    @property
    def modulefiles_root(self) -> Path:
        return self._root / self.MODULEFILES_ROOT_NAME

    @property
    def deprecated_modulefiles_root(self) -> Path:
        return self.deprecated_root / self.MODULEFILES_ROOT_NAME

    @property
    def deployment_snapshot_path(self) -> Path:
        return self._root / self.DEPLOYMENT_SNAPSHOT_FILENAME

    @property
    def previous_deployment_snapshot_path(self) -> Path:
        return self._root / self.PREVIOUS_DEPLOYMENT_SNAPSHOT_FILENAME

    @property
    def build_layout(self) -> ModuleBuildLayout:
        return ModuleBuildLayout(self._build_root)
