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


class LoadError(Exception):
    pass


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


def load_module(path: Path) -> ModuleConfig:
    if path.is_dir():
        return load_module_folder(path)
    elif path.suffix == ".yaml":
        return load_from_yaml(ModuleConfig, path)

    raise LoadError(f"Unexpected file in configuration directory:\n{path}")


def load_deployment(config_folder: Path) -> DeploymentConfig:
    modules: list[ModuleConfig] = []
    for module_folder in config_folder.glob("*"):
        if not module_folder.is_dir():
            raise LoadError(f"Module path is not directory: {module_folder}")

        for version_path in module_folder.glob("*"):
            module = load_module(version_path)
            if not module.metadata.name == module_folder.name:
                raise LoadError(
                    f"Module name {module.metadata.name} does not match path in "
                    f"configuration directory:\n{module_folder}"
                )

            modules.append(module)

    return DeploymentConfig(modules=modules)
