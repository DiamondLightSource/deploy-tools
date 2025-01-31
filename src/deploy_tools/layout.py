from pathlib import Path
from typing import Self


class Layout:
    """Represents the layout of the deployment area."""

    MODULES_ROOT_NAME = "modules"
    MODULEFILES_ROOT_NAME = "modulefiles"
    DEPRECATED_ROOT_NAME = "deprecated"
    BUILD_ROOT_NAME = "build"
    ENTRYPOINTS_FOLDER = "entrypoints"
    SIF_FILES_FOLDER = "sif_files"

    DEPLOYMENT_SNAPSHOT_FILENAME = "deployment.yaml"
    MODULE_SNAPSHOT_FILENAME = "module.yaml"
    BUILT_MODULEFILE_FILENAME = "modulefile"

    def __init__(self, deployment_root: Path, build_root: Path | None = None) -> None:
        self._root = deployment_root

        if build_root is not None:
            self._build_root = build_root
        else:
            self._build_root = self._root / self.BUILD_ROOT_NAME

    def get_module_folder(self, name: str, version: str) -> Path:
        return self.modules_root / name / version

    def get_entrypoints_folder(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.ENTRYPOINTS_FOLDER

    def get_sif_files_folder(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.SIF_FILES_FOLDER

    def get_modulefiles_root(self, from_deprecated: bool = False) -> Path:
        return (
            self.deprecated_modulefiles_root
            if from_deprecated
            else self.modulefiles_root
        )

    def get_built_modulefile(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.BUILT_MODULEFILE_FILENAME

    def get_modulefile(
        self, name: str, version: str, from_deprecated: bool = False
    ) -> Path:
        return self.get_modulefiles_root(from_deprecated) / name / version

    def get_module_snapshot_path(self, name: str, version: str) -> Path:
        return self.get_module_folder(name, version) / self.MODULE_SNAPSHOT_FILENAME

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
    def build_layout(self) -> Self:
        return self.__class__(self._build_root)
