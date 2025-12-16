from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from .parent import ParentModel

MOUNT_PATH_REGEX = r"/[^:]*"  # Colon is excluded in short-form apptainer mounts
MOUNT_REGEX = rf"^{MOUNT_PATH_REGEX}(:{MOUNT_PATH_REGEX}(:(ro|rw))?)?$"
IMAGE_VERSION_REGEX = r"^[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}$"  # OCI specification


class EntrypointOptions(ParentModel):
    apptainer_args: Annotated[
        str,
        Field(description="Apptainer arguments to pass when launching the container"),
    ] = ""

    command_args: Annotated[
        str, Field(description="Arguments to pass to command entrypoint")
    ] = ""

    mounts: Annotated[
        list[Annotated[str, StringConstraints(pattern=MOUNT_REGEX)]],
        Field(
            description="A list of mount points to add to the container in the form of "
            "'host_path[:container_path[:opts]]' where opts (mount options) can be "
            "'ro' or 'rw' and defaults to 'rw'"
        ),
    ] = []

    host_binaries: Annotated[
        list[str],
        Field(
            description="A list of host binaries to mount into the container. "
            "These are discovered on the host using the current PATH and are "
            "mounted into the container at /usr/bin/[binary_name]"
        ),
    ] = []


class Entrypoint(ParentModel):
    """Represents an entrypoint to a command on the Apptainer image.

    If no command is provided, the entrypoint (`name`) is used by default. This
    corresponds to the name of the executable provided by the Module.
    """

    name: Annotated[
        str, Field(description="Name of executable to use after loading the Module")
    ]
    command: Annotated[
        str | None,
        Field(description="Command to run in container. Defaults to `name`"),
    ] = None

    options: Annotated[
        EntrypointOptions, Field("Options to apply for this entrypoint")
    ] = EntrypointOptions()


class ContainerImage(ParentModel):
    path: Annotated[
        str,
        Field(
            description="Image URL excluding the version/tag. Must be a valid URL as "
            "described here: "
            "https://apptainer.org/docs/user/main/cli/apptainer_pull.html#synopsis"
        ),
    ]
    version: Annotated[
        str,
        StringConstraints(pattern=IMAGE_VERSION_REGEX),
        Field(description="Version or tag of the docker image"),
    ]

    @property
    def url(self) -> str:
        return f"{self.path}:{self.version}"


class ApptainerApp(ParentModel):
    """Represents an Apptainer application or set of applications using a single image.

    This uses Apptainer to deploy a portable image of the desired container. Multiple
    entrypoints can be specified to allow different commands to be run on the same
    container image.
    """

    app_type: Annotated[
        Literal["apptainer"],
        Field(
            description="An Apptainer (executable container image) with multiple "
            "potential entrypoints"
        ),
    ]
    container: Annotated[ContainerImage, Field(description="Container URL information")]
    entrypoints: Annotated[
        list[Entrypoint],
        Field(description="List of executables to run using the Apptainer"),
    ]
    global_options: Annotated[
        EntrypointOptions,
        Field(description="Global options that apply to all Entrypoints"),
    ] = EntrypointOptions()
