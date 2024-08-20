from collections.abc import Sequence

from pydantic import BaseModel

from .application import Application


class ModuleDependency(BaseModel, extra="forbid"):
    name: str
    version: str | None = None


class EnvVar(BaseModel, extra="forbid"):
    name: str
    value: str


class ModuleMetadata(BaseModel, extra="forbid"):
    name: str
    version: str
    description: str | None = None
    dependencies: Sequence[ModuleDependency] = []
    env_vars: Sequence[EnvVar] = []
    deprecated: bool = False


class Module(BaseModel, extra="forbid"):
    """Represents a Module to be deployed.

    Modules can optionally include a set of applications, environment variables to load,
    and a list of module dependencies.
    """

    metadata: ModuleMetadata
    applications: list[Application]
