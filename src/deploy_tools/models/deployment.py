from typing import TypeAlias

from .module import Release
from .parent import ParentModel

ReleasesByVersion: TypeAlias = dict[str, Release]
ReleasesByNameAndVersion: TypeAlias = dict[str, ReleasesByVersion]
DefaultVersionsByName: TypeAlias = dict[str, str]


class DeploymentSettings(ParentModel):
    default_versions: DefaultVersionsByName = {}


class Deployment(ParentModel):
    """Configuration for all modules and applications that should be deployed."""

    settings: DeploymentSettings
    releases: ReleasesByNameAndVersion
