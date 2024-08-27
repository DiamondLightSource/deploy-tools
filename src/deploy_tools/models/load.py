from collections import defaultdict
from pathlib import Path
from typing import TypeVar

import yaml

from .application import Application
from .deployment import (
    Deployment,
    DeploymentSettings,
    ModulesByNameAndVersion,
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
    settings = load_from_yaml(DeploymentSettings, config_folder / DEPLOYMENT_SETTINGS)

    modules: ModulesByNameAndVersion = defaultdict(dict)
    for version_path in config_folder.glob("*/*"):
        module = load_module(version_path)
        # This also guarantees unique module names and versions in configuration
        check_filepath_matches_module_metadata(version_path, module.metadata)

        name = module.metadata.name
        version = module.metadata.version

        modules[name][version] = module

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
