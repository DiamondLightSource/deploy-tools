from pathlib import Path
from typing import TypeVar

import yaml

from .application import ApplicationModel
from .module import ModuleMetadataModel, ModuleModel

T = TypeVar("T", ApplicationModel, ModuleModel, ModuleMetadataModel)

CONFIG_FILENAME = "config.yaml"


def load_from_yaml(model: type[T], file_path: Path) -> T:
    with open(file_path) as f:
        return model(**yaml.safe_load(f))


def load_module_folder(folder: Path) -> ModuleModel:
    metadata: ModuleMetadataModel = load_from_yaml(
        ModuleMetadataModel, folder / CONFIG_FILENAME
    )

    applications = []

    for file in folder.glob("*"):
        if file.name == CONFIG_FILENAME:
            continue

        applications.append(load_from_yaml(ApplicationModel, file))

    module = ModuleModel(metadata=metadata, applications=applications)
    return module


def load_module_file(file: Path) -> ModuleModel:
    return load_from_yaml(ModuleModel, file)


def load_deployments(config_folder: Path) -> list[ModuleModel]:
    modules: list[ModuleModel] = []
    for file in config_folder.glob("*"):
        if file.is_dir():
            modules.append(load_module_folder(file))
        elif file.suffix == ".yaml":
            modules.append(load_module_file(file))

    return modules
