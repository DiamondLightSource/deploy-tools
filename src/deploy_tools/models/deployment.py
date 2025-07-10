from collections import defaultdict

from .module import Module, Release
from .parent import ParentModel

type ReleasesByVersion = dict[str, Release]
type ReleasesByNameAndVersion = dict[str, ReleasesByVersion]
type DefaultVersionsByName = dict[str, str]

type ModulesByName = dict[str, list[Module]]
type ModuleVersionsByName = dict[str, list[str]]


class DeploymentSettings(ParentModel):
    """All global configuration settings for the Deployment."""

    default_versions: DefaultVersionsByName = {}


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
