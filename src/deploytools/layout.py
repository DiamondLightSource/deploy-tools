"""Constants and classes for describing the layout of the deployment area."""

from pathlib import Path


class Layout:
    ENTRYPOINTS_ROOT_NAME = "entrypoints"
    MODULEFILES_ROOT_NAME = "modulefiles"
    SIF_FILES_ROOT_NAME = "sif_files"
    DEPRECATED_ROOT_NAME = "deprecated"

    DEPLOYMENT_SNAPSHOT_FILENAME = "deployment.yaml"

    def __init__(self, deployment_root: Path):
        self._root = deployment_root

    def get_deployment_root(self) -> Path:
        return self._root

    def get_deprecated_root(self) -> Path:
        return self._root / self.DEPRECATED_ROOT_NAME

    def get_entrypoints_root(self) -> Path:
        return self._root / self.ENTRYPOINTS_ROOT_NAME

    def get_sif_files_root(self) -> Path:
        return self._root / self.SIF_FILES_ROOT_NAME

    def get_modulefiles_root(self, deprecated: bool = False) -> Path:
        if deprecated:
            return self.get_deprecated_root() / self.MODULEFILES_ROOT_NAME
        else:
            return self._root / self.MODULEFILES_ROOT_NAME

    def get_deployment_snapshot_file(self) -> Path:
        return self._root / self.DEPLOYMENT_SNAPSHOT_FILENAME
