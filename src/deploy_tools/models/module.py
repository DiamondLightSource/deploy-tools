from collections.abc import Sequence

from .application import Application
from .parent import ParentModel


class ModuleDependency(ParentModel):
    name: str
    version: str | None = None


class EnvVar(ParentModel):
    name: str
    value: str


class Module(ParentModel):
    """Represents a Module to be deployed.

    Modules can optionally include a set of applications, environment variables to load,
    and a list of module dependencies.
    """

    name: str
    version: str
    description: str | None = None
    dependencies: Sequence[ModuleDependency] = []
    env_vars: Sequence[EnvVar] = []
    applications: list[Application]


class Release(ParentModel):
    """Represents a Module to be deployed along with its lifecycle status."""

    module: Module
    deprecated: bool = False
