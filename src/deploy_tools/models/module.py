from collections.abc import Sequence
from typing import Annotated

from pydantic import Field

from deploy_tools.models.binary_app import BinaryApp

from .apptainer_app import ApptainerApp
from .parent import ParentModel
from .shell_app import ShellApp

Application = Annotated[
    ApptainerApp | ShellApp | BinaryApp, Field(..., discriminator="app_type")
]


class ModuleDependency(ParentModel):
    """Specify an Environment Module to include as a dependency.

    If the dependent Environment Module is managed by this same Deployment (i.e. is a
    Module), you must specify a specific version in order to pass validation.
    """

    name: str
    version: str | None = None


class EnvVar(ParentModel):
    """Represents an environment variable to set when loading the Module."""

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
    allow_updates: bool = False
    exclude_from_defaults: bool = False
    load_script: list[str] = []
    unload_script: list[str] = []


class Release(ParentModel):
    """Represents a Module along with its lifecycle (deprecation) status."""

    module: Module
    deprecated: bool = False
