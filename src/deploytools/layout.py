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

    @property
    def deployment_root(self) -> Path:
        return self._root

    @property
    def deprecated_root(self) -> Path:
        return self._root / self.DEPRECATED_ROOT_NAME

    @property
    def entrypoints_root(self) -> Path:
        return self._root / self.ENTRYPOINTS_ROOT_NAME

    @property
    def sif_files_root(self) -> Path:
        return self._root / self.SIF_FILES_ROOT_NAME

    @property
    def modulefiles_root(self) -> Path:
        return self._root / self.MODULEFILES_ROOT_NAME

    @property
    def deprecated_modulefiles_root(self) -> Path:
        return self.deprecated_root / self.MODULEFILES_ROOT_NAME

    @property
    def snapshot_file(self) -> Path:
        return self._root / self.DEPLOYMENT_SNAPSHOT_FILENAME

    def get_application_paths(self) -> list[Path]:
        return [self.entrypoints_root, self.sif_files_root]
