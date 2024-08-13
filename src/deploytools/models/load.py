from pathlib import Path
from typing import TypeVar

import yaml

from .application import Application
from .deployment import (
    Deployment,
    DeploymentSettings,
    ModulesByNameAndVersion,
    ModulesByVersion,
)
from .module import Module, ModuleMetadata

T = TypeVar("T", Deployment, Module, ModuleMetadata, Application, DeploymentSettings)

YAML_FILE_SUFFIX = ".yaml"
MODULE_CONFIG = "config" + YAML_FILE_SUFFIX
DEPLOYMENT_SETTINGS = "settings" + YAML_FILE_SUFFIX


class LoadError(Exception):
    pass


def load_from_yaml(model: type[T], file_path: Path) -> T:
    """Load a single Pydantic model from a yaml file."""
    with open(file_path) as f:
        return model(**yaml.safe_load(f))


def load_module(path: Path) -> Module:
    """Load Module configuration from a yaml file."""
    if path.is_dir() or not path.suffix == YAML_FILE_SUFFIX:
        raise LoadError(f"Unexpected file in configuration directory:\n{path}")

    return load_from_yaml(Module, path)


def load_deployment(config_folder: Path) -> Deployment:
    """Load Deployment configuration from a yaml file."""
    settings = DeploymentSettings()
    modules: ModulesByNameAndVersion = {}
    for path in config_folder.glob("*"):
        if not path.is_dir():
            if path.name == DEPLOYMENT_SETTINGS:
                settings = load_from_yaml(DeploymentSettings, path)
                continue
            raise LoadError(f"Module path is not directory: {path}")

        module_name = path.name
        versioned_modules: ModulesByVersion = {}

        for version_path in path.glob("*"):
            module = load_module(version_path)
            check_filepath_matches_module_metadata(version_path, module.metadata)
            version = module.metadata.version

            if version in versioned_modules:
                raise LoadError(
                    f"Version {version} already exists for {module_name}:\n"
                    f"{version_path}"
                )

            versioned_modules[version] = module

        modules[module_name] = versioned_modules

    return Deployment(settings=settings, modules=modules)


def check_filepath_matches_module_metadata(
    version_path: Path, metadata: ModuleMetadata
) -> None:
    """Ensure the modules file path (in config folder) matches the metadata."""
    if version_path.is_dir() and version_path.suffix == YAML_FILE_SUFFIX:
        raise LoadError(f"Module directory has incorrect suffix:\n{version_path}")

    if not metadata.name == version_path.parent.name:
        raise LoadError(
            f"Module name {metadata.name} does not match path:\n{version_path}"
        )

    version_match = (
        metadata.version == version_path.name
        or version_path.suffix == YAML_FILE_SUFFIX
        and metadata.version == version_path.stem
    )

    if not version_match:
        raise LoadError(
            f"Module version {metadata.version} does not match path:\n{version_path}"
        )
