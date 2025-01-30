from collections.abc import Sequence
from typing import Annotated

from pydantic import Field

from .apptainer import Apptainer
from .command import Command
from .parent import ParentModel
from .shell import Shell

Application = Annotated[
    Apptainer | Command | Shell, Field(..., discriminator="app_type")
]

DEVELOPMENT_VERSION = "dev"


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

    def is_dev_mode(self) -> bool:
        return self.version == DEVELOPMENT_VERSION


class Release(ParentModel):
    """Represents a Module to be deployed along with its lifecycle status."""

    module: Module
    deprecated: bool = False
