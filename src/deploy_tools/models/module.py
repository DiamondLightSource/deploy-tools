from typing import Annotated

from pydantic import Field, StringConstraints

from deploy_tools.models.binary_app import BinaryApp

from .apptainer_app import ApptainerApp
from .parent import ParentModel
from .shell_app import ShellApp

Application = Annotated[
    ApptainerApp | ShellApp | BinaryApp, Field(..., discriminator="app_type")
]

MODULE_NAME_REGEX = "^[a-zA-Z][0-9a-zA-Z_-]*$"  # Don't allow leading underscore
MODULE_VERSION_REGEX = "^[^.].*$"
ENV_VAR_NAME_REGEX = "^[a-zA-Z_][a-zA-Z0-9_]*$"  # Environment Modules & shell standard


class ModuleDependency(ParentModel):
    """Specify an Environment Module to include as a dependency.

    The version is optional. If a version is given and the dependency is a Module
    managed by this same Deployment, that version must exist among the deployed
    (non-deprecated) versions to pass validation. If no version is given, the
    dependency's default version is resolved at load time and is not validated.
    """

    name: Annotated[str, Field(description="Name of module dependency")]
    version: Annotated[
        str | None,
        Field(
            description="Version of dependency. If omitted, the default version is "
            "resolved at load time. If given for a deploy-tools-managed module, the "
            "version must exist in the deployment."
        ),
    ] = None


class EnvVar(ParentModel):
    """Represents an environment variable to set when loading the Module."""

    name: Annotated[
        str,
        StringConstraints(pattern=ENV_VAR_NAME_REGEX),
        Field(
            description="Name of environment variable. Must start with a letter or "
            "underscore and contain only letters, digits or underscores."
        ),
    ]
    value: Annotated[str, Field(description="Value of environment variable")]


class Module(ParentModel):
    """Represents a Module to be deployed.

    Modules can optionally include a set of applications, environment variables to load,
    and a list of module dependencies.
    """

    name: Annotated[
        str,
        StringConstraints(pattern=MODULE_NAME_REGEX),
        Field(
            description="Name of module to use when loading. Must start with a letter "
            "and contain only letters, digits, hyphens or underscores."
        ),
    ]
    version: Annotated[
        str,
        StringConstraints(pattern=MODULE_VERSION_REGEX),
        Field(
            description="Version of this module. This cannot include spaces, cannot "
            "start with a full stop and the filename must match as `[version].yaml`"
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            description="Description that can be read with the `module whatis "
            "[module-name]` command"
        ),
    ] = None
    dependencies: Annotated[
        list[ModuleDependency], Field(description="List of module dependencies")
    ] = []
    env_vars: Annotated[
        list[EnvVar],
        Field(description="List of environment variables to set when loading module"),
    ] = []
    applications: Annotated[
        list[Application], Field(description="Applications to be included in Module")
    ]
    allow_updates: Annotated[
        bool,
        Field(
            description="Allow updates to this module version after initial deployment"
        ),
    ] = False
    exclude_from_defaults: Annotated[
        bool,
        Field(
            description="Exclude this module version from being automatically set as "
            "default, but you can still manually set it. This is used for e.g. alphas"
        ),
    ] = False
    load_script: Annotated[
        list[str],
        Field(
            description="Provide list of commands that are run on module load. You "
            "need to add `system` before any bash command (e.g. `system ls /dir`), as "
            "Modulefiles otherwise use Tcl. This field should be used carefully; "
            "please speak to a deploy-tools admin before use"
        ),
    ] = []
    unload_script: Annotated[
        list[str],
        Field(
            description="Provide list of commands that are run on module unload. You "
            "need to add `system` before any bash command (e.g. `system ls /dir`), as "
            "Modulefiles otherwise use Tcl. This field should be used carefully; "
            "please speak to a deploy-tools admin before use"
        ),
    ] = []


class Release(ParentModel):
    """Represents a Module along with its lifecycle (deprecation) status."""

    module: Annotated[
        Module, Field(description="Module (name, version & configuration) to release")
    ]
    deprecated: Annotated[
        bool, Field(description="Whether this Module version is deprecated")
    ] = False
