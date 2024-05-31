from typing import Optional, Sequence

from pydantic import BaseModel

from .application import ApplicationModel


class ModuleDependencyModel(BaseModel):
    name: str
    version: Optional[str]


class EnvVarModel(BaseModel):
    name: str
    value: str


class ModuleMetadataModel(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    dependencies: Sequence[ModuleDependencyModel] = []
    env_vars: Sequence[EnvVarModel] = []


class ModuleModel(BaseModel):
    metadata: ModuleMetadataModel
    applications: Sequence[ApplicationModel]
