from collections.abc import Sequence
from typing import Literal

from pydantic import Field

from .parent import ParentModel


class EntrypointOptions(ParentModel):
    apptainer_args: str = ""
    command_args: str = ""
    mounts: Sequence[str] = []


class Entrypoint(ParentModel):
    executable_name: str
    command: str | None = None
    options: EntrypointOptions = Field(default_factory=EntrypointOptions)


class ContainerImage(ParentModel):
    path: str
    version: str


class Apptainer(ParentModel):
    """Represents an Apptainer application or set of applications.

    This uses apptainer to deploy a portable image of the desired container. Several
    entrypoints can then be specified to allow for multiple commands to be easily used
    in the same container image.
    """

    app_type: Literal["apptainer"]
    name: str
    version: str
    container: ContainerImage
    entrypoints: Sequence[Entrypoint]
    global_options: EntrypointOptions = Field(default_factory=EntrypointOptions)
