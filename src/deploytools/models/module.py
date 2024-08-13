from typing import Optional, Sequence

from pydantic import BaseModel

from .application import Application


class ModuleDependency(BaseModel, extra="forbid"):
    name: str
    version: Optional[str] = None


class EnvVar(BaseModel, extra="forbid"):
    name: str
    value: str


class ModuleMetadata(BaseModel, extra="forbid"):
    name: str
    version: str
    description: Optional[str] = None
    dependencies: Sequence[ModuleDependency] = []
    env_vars: Sequence[EnvVar] = []
    deprecated: bool = False


class Module(BaseModel, extra="forbid"):
    metadata: ModuleMetadata
    applications: list[Application]
