from .module import Release
from .parent import ParentModel

type ReleasesByVersion = dict[str, Release]
type ReleasesByNameAndVersion = dict[str, ReleasesByVersion]
type DefaultVersionsByName = dict[str, str]


class DeploymentSettings(ParentModel):
    default_versions: DefaultVersionsByName = {}


class Deployment(ParentModel):
    """Configuration for all modules and applications that should be deployed."""

    settings: DeploymentSettings
    releases: ReleasesByNameAndVersion
