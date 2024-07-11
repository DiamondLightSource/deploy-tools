from pathlib import Path
from typing import TypeVar

import yaml

from .application import ApplicationConfig
from .deployment import DeploymentConfig
from .module import ModuleConfig, ModuleMetadataConfig

T = TypeVar(
    "T", DeploymentConfig, ModuleConfig, ModuleMetadataConfig, ApplicationConfig
)

CONFIG_FILENAME = "config.yaml"


def load_from_yaml(model: type[T], file_path: Path) -> T:
    with open(file_path) as f:
        return model(**yaml.safe_load(f))


def load_module_folder(folder: Path) -> ModuleConfig:
    metadata: ModuleMetadataConfig = load_from_yaml(
        ModuleMetadataConfig, folder / CONFIG_FILENAME
    )

    applications = []

    for file in folder.glob("*"):
        if file.name == CONFIG_FILENAME:
            continue

        applications.append(load_from_yaml(ApplicationConfig, file))

    module = ModuleConfig(metadata=metadata, applications=applications)
    return module


def load_module_file(file: Path) -> ModuleConfig:
    return load_from_yaml(ModuleConfig, file)


def load_deployment(config_folder: Path) -> DeploymentConfig:
    modules: list[ModuleConfig] = []
    for file in config_folder.glob("*"):
        if file.is_dir():
            modules.append(load_module_folder(file))
        elif file.suffix == ".yaml":
            modules.append(load_from_yaml(ModuleConfig, file))

    return DeploymentConfig(modules=modules)
