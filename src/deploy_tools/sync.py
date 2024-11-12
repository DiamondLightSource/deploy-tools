from pathlib import Path

from .default_versions import apply_default_versions
from .deploy import deploy
from .deprecate import deprecate
from .layout import Layout
from .models.changes import DeploymentChanges
from .models.load import load_deployment
from .remove import remove
from .remove_name_folders import remove_name_folders
from .restore import restore
from .snapshot import create_snapshot, load_snapshot
from .update import update
from .validate import (
    check_actions,
    validate_deployment_changes,
)


def synchronise(deployment_root: Path, config_folder: Path) -> None:
    """Synchronise the deployment folder with the current configuration"""
    deployment = load_deployment(config_folder)
    layout = Layout(deployment_root)
    snapshot = load_snapshot(layout)

    deployment_changes = validate_deployment_changes(deployment, snapshot)

    check_actions(deployment_changes.release_changes, layout)

    create_snapshot(deployment, layout)
    perform_actions(deployment_changes, layout)


def perform_actions(changes: DeploymentChanges, layout: Layout) -> None:
    release_changes = changes.release_changes

    deploy(release_changes.to_add, layout)
    update(release_changes.to_update, layout)
    deprecate(release_changes.to_deprecate, layout)
    restore(release_changes.to_restore, layout)
    remove(release_changes.to_remove, layout)

    apply_default_versions(changes.default_versions, layout)
    remove_name_folders(
        release_changes.to_deprecate,
        release_changes.to_restore,
        release_changes.to_remove,
        layout,
    )
