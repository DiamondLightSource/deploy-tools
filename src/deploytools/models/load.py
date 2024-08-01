from pathlib import Path
from typing import TypeVar

import yaml

from .application import Application
from .deployment import Deployment, ModulesByNameAndVersion, ModulesByVersion
from .module import Module, ModuleMetadata

T = TypeVar("T", Deployment, Module, ModuleMetadata, Application)

YAML_FILE_SUFFIX = ".yaml"
CONFIG_FILENAME = "config" + YAML_FILE_SUFFIX


class LoadError(Exception):
    pass


def load_from_yaml(model: type[T], file_path: Path) -> T:
    with open(file_path) as f:
        return model(**yaml.safe_load(f))


def load_module_folder(folder: Path) -> Module:
    metadata: ModuleMetadata = load_from_yaml(ModuleMetadata, folder / CONFIG_FILENAME)

    applications = []

    for file in folder.glob("*"):
        if file.name == CONFIG_FILENAME:
            continue

        applications.append(load_from_yaml(Application, file))

    module = Module(metadata=metadata, applications=applications)
    return module


def load_module(path: Path) -> Module:
    if path.is_dir():
        return load_module_folder(path)
    elif path.suffix == YAML_FILE_SUFFIX:
        return load_from_yaml(Module, path)

    raise LoadError(f"Unexpected file in configuration directory:\n{path}")


def load_deployment(config_folder: Path) -> Deployment:
    modules: ModulesByNameAndVersion = {}
    for module_folder in config_folder.glob("*"):
        if not module_folder.is_dir():
            raise LoadError(f"Module path is not directory: {module_folder}")

        module_name = module_folder.name
        versioned_modules: ModulesByVersion = {}

        for version_path in module_folder.glob("*"):
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

    return Deployment(modules=modules)


def check_filepath_matches_module_metadata(
    version_path: Path, metadata: ModuleMetadata
):
    name_path = version_path.parent

    if not metadata.name == name_path.name:
        raise LoadError(
            f"Module name {metadata.name} does not match path in configuration "
            f"directory:\n{version_path}"
        )

    if version_path.is_dir() and version_path.suffix == YAML_FILE_SUFFIX:
        raise LoadError(
            f"Module directory has incorrect suffix {YAML_FILE_SUFFIX}:\n{version_path}"
        )

    version_match = (
        metadata.version == version_path.name
        or version_path.suffix == YAML_FILE_SUFFIX
        and metadata.version == version_path.stem
    )

    if not version_match:
        raise LoadError(
            f"Module version {metadata.version} does not match path in configuration "
            f"directory:\n{version_path}"
        )
