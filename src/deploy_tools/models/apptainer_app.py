from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import Field

from .parent import ParentModel


class EntrypointOptions(ParentModel):
    apptainer_args: Annotated[
        str,
        Field(description="Apptainer arguments to pass when launching the container"),
    ] = ""

    command_args: Annotated[
        str, Field(description="Arguments to pass to command entrypoint")
    ] = ""

    mounts: Annotated[
        Sequence[str],
        Field(
            description="A list of mount points to add to the container in the form of "
            "'host_path:container_path'"
        ),
    ] = []

    host_binaries: Annotated[
        Sequence[str],
        Field(
            description="A list of host binaries to mount into the container. "
            "These are discovered on the host using the current PATH and are "
            "mounted into the container at /usr/bin/<binary_name>."
        ),
    ] = []


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


class ApptainerApp(ParentModel):
    """Represents an Apptainer application or set of applications for a single image.

    This uses Apptainer to deploy a portable image of the desired container. Several
    entrypoints can then be specified to allow for multiple commands run on the same
    container image.
    """

    app_type: Literal["apptainer"]
    container: ContainerImage
    entrypoints: Sequence[Entrypoint]
    global_options: EntrypointOptions = EntrypointOptions()
