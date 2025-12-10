from collections import defaultdict
from typing import Annotated

from pydantic import Field

from .module import Module, Release
from .parent import ParentModel

type ReleasesByVersion = dict[str, Release]
type ReleasesByNameAndVersion = dict[str, ReleasesByVersion]
type DefaultVersionsByName = dict[str, str]

type ModulesByName = dict[str, list[Module]]
type ModuleVersionsByName = dict[str, list[str]]


class DeploymentSettings(ParentModel):
    """All global configuration settings for the Deployment."""

    default_versions: Annotated[
        DefaultVersionsByName,
        Field(
            description="Mapping of [module-name]:[version] to use as default when "
            "no version is specified in a `module load` command. If no default is "
            "specified, deploy-tools will use natsort to place e.g. 1.2 after all "
            "alpha, beta and rc candidates as described here: "
            "https://natsort.readthedocs.io/en/7.1.1/examples.html#sorting-more-expressive-versioning-schemes"
        ),
    ] = {}


class Deployment(ParentModel):
    """Configuration for all Modules and Applications that should be deployed.

    This will include any deprecated Modules.
    """

    settings: DeploymentSettings
    releases: ReleasesByNameAndVersion

    def get_final_deployed_modules(self) -> ModulesByName:
        """Return modules that are expected to be deployed after a sync command.

        This explicitly excludes any deprecated modules.
        """
        final_modules: ModulesByName = defaultdict(list)
        for name, release_versions in self.releases.items():
            modules = [
                release.module
                for release in release_versions.values()
                if not release.deprecated
            ]

            if modules:
                final_modules[name] = modules

        return final_modules

    def get_final_deployed_versions(self) -> ModuleVersionsByName:
        """Return module versions that are expected to be deployed after a sync command.

        This explicitly excludes any deprecated modules.
        """
        final_versions: ModuleVersionsByName = defaultdict(list)

        for name, modules in self.get_final_deployed_modules().items():
            final_versions[name] = [module.version for module in modules]

        return final_versions
