from .module import Release
from .parent import ParentModel

type ReleasesByVersion = dict[str, Release]
type ReleasesByNameAndVersion = dict[str, ReleasesByVersion]
type DefaultVersionsByName = dict[str, str]


class DeploymentSettings(ParentModel):
    """All global configuration settings for the Deployment."""

    default_versions: DefaultVersionsByName = {}


class Deployment(ParentModel):
    """Configuration for all Modules and Applications that should be deployed.

    This will include any deprecated Modules.
    """

    settings: DeploymentSettings
    releases: ReleasesByNameAndVersion
