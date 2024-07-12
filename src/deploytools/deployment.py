from collections import defaultdict
from pathlib import Path
from typing import TypeAlias

import yaml

from .models.deployment import DeploymentConfig
from .models.load import load_from_yaml
from .models.module import ModuleConfig

ModuleVersionsByName: TypeAlias = dict[str, list[str]]
ModulesByName: TypeAlias = dict[str, list[tuple[str, ModuleConfig]]]

DEPLOYMENT_SNAPSHOT_FILENAME = "deployment.yaml"


class DeploymentError(Exception):
    pass


def create_deployment_snapshot(deployment: DeploymentConfig, deploy_folder: Path):
    file_path = deploy_folder / DEPLOYMENT_SNAPSHOT_FILENAME

    with open(file_path, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def load_deployment_snapshot(deploy_folder: Path, allow_empty=True) -> DeploymentConfig:
    snapshot_path = deploy_folder / DEPLOYMENT_SNAPSHOT_FILENAME

    if not snapshot_path.exists():
        if allow_empty:
            return DeploymentConfig(modules=[])

        raise DeploymentError(f"Snapshot path does not exist:\n{snapshot_path}")

    return load_from_yaml(DeploymentConfig, snapshot_path)


def get_modules_by_name(deployment: DeploymentConfig, validate: bool) -> ModulesByName:
    modules_struct: ModulesByName = defaultdict(list)
    for module in deployment.modules:
        name = module.metadata.name
        version = module.metadata.version

        if validate and version in modules_struct[name]:
            raise DeploymentError(
                f"Module {name} has multiple configurations for version {version}"
            )

        modules_struct[name].append((version, module))

    return modules_struct


def get_deployed_versions(deploy_folder: Path) -> ModuleVersionsByName:
    modules_folder = deploy_folder / "modulefiles"
    previous_modules: ModuleVersionsByName = defaultdict(list)

    for module_folder in modules_folder.glob("*"):
        for version_folder in module_folder.glob("*"):
            previous_modules[module_folder.name].append(version_folder.name)

    return previous_modules
