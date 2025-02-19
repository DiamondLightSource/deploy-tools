from .deployment import DefaultVersionsByName
from .module import Release
from .parent import ParentModel


class ReleaseChanges(ParentModel):
    """List of Release changes required to update the Deployment."""

    to_add: list[Release] = []
    to_update: list[Release] = []
    to_deprecate: list[Release] = []
    to_restore: list[Release] = []
    to_remove: list[Release] = []


class DeploymentChanges(ParentModel):
    """Corresponds to changes between two ``Deployment`` instances."""

    release_changes: ReleaseChanges = ReleaseChanges()
    default_versions: DefaultVersionsByName = {}
