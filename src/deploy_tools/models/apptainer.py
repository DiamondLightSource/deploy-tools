from collections.abc import Sequence
from typing import Literal

from .parent import ParentModel


class EntrypointOptions(ParentModel):
    apptainer_args: str = ""
    command_args: str = ""
    mounts: Sequence[str] = []


class Entrypoint(ParentModel):
    """Represents an entrypoint to a command on the Apptainer image.

    If no command is provided, the entrypoint (`name`) is used by default. This
    corresponds to the name of the executable provided by the Module."""

    name: str
    command: str | None = None
    options: EntrypointOptions = EntrypointOptions()


class ContainerImage(ParentModel):
    path: str
    version: str

    @property
    def url(self) -> str:
        return f"{self.path}:{self.version}"


class Apptainer(ParentModel):
    """Represents an Apptainer application or set of applications for a single image.

    This uses Apptainer to deploy a portable image of the desired container. Several
    entrypoints can then be specified to allow for multiple commands run on the same
    container image.
    """

    app_type: Literal["apptainer"]
    container: ContainerImage
    entrypoints: Sequence[Entrypoint]
    global_options: EntrypointOptions = EntrypointOptions()
