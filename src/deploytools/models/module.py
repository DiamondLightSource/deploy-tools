from typing import Optional, Sequence

from pydantic import BaseModel

from .application import ApplicationConfig


class ModuleDependencyConfig(BaseModel):
    name: str
    version: Optional[str]


class EnvVarConfig(BaseModel):
    name: str
    value: str


class ModuleMetadataConfig(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    dependencies: Sequence[ModuleDependencyConfig] = []
    env_vars: Sequence[EnvVarConfig] = []


class ModuleConfig(BaseModel):
    metadata: ModuleMetadataConfig
    applications: list[ApplicationConfig]
