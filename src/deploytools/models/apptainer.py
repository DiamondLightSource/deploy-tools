from typing import Literal, Optional, Sequence

from pydantic import BaseModel, Field


class EntrypointOptions(BaseModel, extra="forbid"):
    apptainer_args: str = ""
    command_args: str = ""
    mounts: Sequence[str] = []


class Entrypoint(BaseModel, extra="forbid"):
    executable_name: str
    command: Optional[str] = None
    options: EntrypointOptions = Field(default_factory=EntrypointOptions)


class ContainerImage(BaseModel, extra="forbid"):
    path: str
    version: str


class Apptainer(BaseModel, extra="forbid"):
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
