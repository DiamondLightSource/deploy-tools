from .models.changes import DeploymentChanges, ReleaseChanges
from .models.deployment import (
    DefaultVersionsByName,
)


def print_updates(
    old_default_versions: DefaultVersionsByName, deployment_changes: DeploymentChanges
) -> None:
    """Print a summary of all changes."""
    _print_module_updates(deployment_changes.release_changes)
    _print_version_updates(old_default_versions, deployment_changes.default_versions)


def _print_module_updates(release_changes: ReleaseChanges) -> None:
    display_config = {
        "deployed": release_changes.to_add,
        "updated": release_changes.to_update,
        "deprecated": release_changes.to_deprecate,
        "restored": release_changes.to_restore,
        "removed": release_changes.to_remove,
    }

    for action, releases in display_config.items():
        print(f"Modules to be {action}:")

        for release in releases:
            print(f"{release.module.name}/{release.module.version}")

        print()


def _print_version_updates(
    old_defaults: DefaultVersionsByName, new_defaults: DefaultVersionsByName
) -> None:
    print("Updated module defaults:")
    module_names = old_defaults.keys() | new_defaults.keys()

    for name in module_names:
        old = old_defaults.get(name, "None")
        new = new_defaults.get(name, "None")
        if not old == new:
            print(f"{name} {old} -> {new}")

    print()
