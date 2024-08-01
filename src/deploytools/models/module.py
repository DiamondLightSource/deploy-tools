from typing import Optional, Sequence

from pydantic import BaseModel

from .application import ApplicationConfig


class ModuleDependencyConfig(BaseModel, extra="forbid"):
    name: str
    version: Optional[str]


class EnvVarConfig(BaseModel, extra="forbid"):
    name: str
    value: str


class ModuleMetadataConfig(BaseModel, extra="forbid"):
    name: str
    version: str
    description: Optional[str] = None
    dependencies: Sequence[ModuleDependencyConfig] = []
    env_vars: Sequence[EnvVarConfig] = []
    deprecated: bool = False


class ModuleConfig(BaseModel, extra="forbid"):
    metadata: ModuleMetadataConfig
    applications: list[ApplicationConfig]
