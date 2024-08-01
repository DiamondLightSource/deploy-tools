from typing import TypeAlias

from pydantic import BaseModel

from .module import ModuleConfig

ModulesByVersion: TypeAlias = dict[str, ModuleConfig]
ModulesByNameAndVersion: TypeAlias = dict[str, ModulesByVersion]


class DeploymentConfig(BaseModel, extra="forbid"):
    modules: ModulesByNameAndVersion
