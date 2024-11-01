from pathlib import Path


class Layout:
    """Represents the layout of the deployment area."""

    MODULES_ROOT_NAME = "modules"
    MODULEFILES_ROOT_NAME = "modulefiles"
    DEPRECATED_ROOT_NAME = "deprecated"
    ENTRYPOINTS_FOLDER = "entrypoints"
    SIF_FILES_FOLDER = "sif_files"

    DEPLOYMENT_SNAPSHOT_FILENAME = "deployment.yaml"

    def __init__(self, deployment_root: Path) -> None:
        self._root = deployment_root

    def get_module_folder(self, name: str, version: str) -> Path:
        return self.modules_root / name / version

    def get_entrypoints_folder(self, name: str, version: str):
        return self.get_module_folder(name, version) / self.ENTRYPOINTS_FOLDER

    def get_sif_files_folder(self, name: str, version: str):
        return self.get_module_folder(name, version) / self.SIF_FILES_FOLDER

    def get_modulefiles_root(self, from_deprecated: bool = False):
        return (
            self.deprecated_modulefiles_root
            if from_deprecated
            else self.modulefiles_root
        )

    def get_modulefile(self, name: str, version: str, from_deprecated: bool = False):
        return self.get_modulefiles_root(from_deprecated) / name / version

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
    def snapshot_file(self) -> Path:
        return self._root / self.DEPLOYMENT_SNAPSHOT_FILENAME
