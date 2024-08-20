from collections.abc import Sequence

from .application import Application
from .parent import ParentModel


class ModuleDependency(ParentModel):
    name: str
    version: str | None = None


class EnvVar(ParentModel):
    name: str
    value: str


class ModuleMetadata(ParentModel):
    name: str
    version: str
    description: str | None = None
    dependencies: Sequence[ModuleDependency] = []
    env_vars: Sequence[EnvVar] = []
    deprecated: bool = False


class Module(ParentModel):
    """Represents a Module to be deployed.

    Modules can optionally include a set of applications, environment variables to load,
    and a list of module dependencies.
    """

    metadata: ModuleMetadata
    applications: list[Application]
