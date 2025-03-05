from collections import defaultdict
from pathlib import Path

import yaml
from pydantic import BaseModel

from .deployment import (
    Deployment,
    DeploymentSettings,
    ReleasesByNameAndVersion,
)
from .module import Module, Release

YAML_FILE_SUFFIX = ".yaml"
DEPLOYMENT_SETTINGS = "settings" + YAML_FILE_SUFFIX


class LoadError(Exception):
    pass


def save_as_yaml(obj: BaseModel, output_path: Path) -> None:
    with open(output_path, "w") as f:
        yaml.safe_dump(obj.model_dump(), f)


def load_from_yaml[T: BaseModel](model: type[T], file_path: Path) -> T:
    """Load a single Pydantic model from a yaml file."""
    with open(file_path) as f:
        return model(**yaml.safe_load(f))


def load_deployment(config_folder: Path) -> Deployment:
    """Load Deployment configuration from a yaml file."""
    settings = load_from_yaml(DeploymentSettings, config_folder / DEPLOYMENT_SETTINGS)

    releases: ReleasesByNameAndVersion = defaultdict(dict)
    for version_path in config_folder.glob("*/*"):
        release = _load_release(version_path)
        module = release.module

        # This also guarantees unique module names and versions in configuration
        _check_filepath_matches(version_path, module)

        name = module.name
        version = module.version

        releases[name][version] = release

    return Deployment(settings=settings, releases=releases)


def _load_release(path: Path) -> Release:
    """Load Module configuration from a yaml file."""
    if path.is_dir() or not path.suffix == YAML_FILE_SUFFIX:
        raise LoadError(f"Unexpected file in configuration directory:\n{path}")

    return load_from_yaml(Release, path)


def _check_filepath_matches(version_path: Path, module: Module) -> None:
    """Ensure the Module's file path (in config folder) matches the metadata.

    It should be the Module's name and version as /<config_folder>/<name>/<version>.yaml
    """
    if version_path.is_dir() and version_path.suffix == YAML_FILE_SUFFIX:
        raise LoadError(f"Module directory has incorrect suffix:\n{version_path}")

    if not module.name == version_path.parent.name:
        raise LoadError(
            f"Module name {module.name} does not match path:\n{version_path}"
        )

    version_match = (
        module.version == version_path.name
        or version_path.suffix == YAML_FILE_SUFFIX
        and module.version == version_path.stem
    )

    if not version_match:
        raise LoadError(
            f"Module version {module.version} does not match path:\n{version_path}"
        )
