from pathlib import Path
from typing import TypeVar

import yaml

from .application import ApplicationModel
from .module import ModuleModel

T = TypeVar("T", ApplicationModel, ModuleModel)

CONFIG_FILENAME = "config.yaml"


def load_from_yaml(model: type[T], file_path: Path) -> T:
    with open(file_path) as f:
        return model(**yaml.safe_load(f))


def load_module_folder(folder: Path) -> ModuleModel:
    module: ModuleModel = load_from_yaml(ModuleModel, folder / CONFIG_FILENAME)

    for file in folder.glob("*"):
        if file.name == CONFIG_FILENAME:
            continue

        application = load_from_yaml(ApplicationModel, file)
        module.applications.append(application)

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
