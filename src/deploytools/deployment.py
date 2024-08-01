from collections import defaultdict
from pathlib import Path
from typing import TypeAlias

import yaml

from .models.deployment import DeploymentConfig
from .models.load import load_from_yaml

ModuleVersionsByName: TypeAlias = dict[str, list[str]]

DEPLOYMENT_SNAPSHOT_FILENAME = "deployment.yaml"
DEPLOYMENT_ENTRYPOINTS_DIR = "entrypoints"
DEPLOYMENT_MODULEFILES_DIR = "modulefiles"
DEPLOYMENT_SIF_FILES_DIR = "sif_files"

DEPLOYMENT_SUBDIRS = [
    DEPLOYMENT_ENTRYPOINTS_DIR,
    DEPLOYMENT_MODULEFILES_DIR,
    DEPLOYMENT_SIF_FILES_DIR,
]


class DeploymentError(Exception):
    pass


def create_snapshot(deployment: DeploymentConfig, deployment_root: Path):
    snapshot_file = deployment_root / DEPLOYMENT_SNAPSHOT_FILENAME

    with open(snapshot_file, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def load_snapshot(deployment_root: Path, allow_empty=True) -> DeploymentConfig:
    snapshot_file = deployment_root / DEPLOYMENT_SNAPSHOT_FILENAME

    if not snapshot_file.exists():
        if allow_empty:
            return DeploymentConfig(modules={})

        raise DeploymentError(f"Deployment snapshot does not exist:\n{snapshot_file}")

    return load_from_yaml(DeploymentConfig, snapshot_file)


def get_deployed_versions(deployment_root: Path) -> ModuleVersionsByName:
    modulefiles_root = deployment_root / DEPLOYMENT_MODULEFILES_DIR
    previous_modules: ModuleVersionsByName = defaultdict(list)

    for module_folder in modulefiles_root.glob("*"):
        for version_path in module_folder.glob("*"):
            previous_modules[module_folder.name].append(version_path.name)

    return previous_modules
