from pathlib import Path

from .check_deploy import check_deploy_actions
from .deploy import deploy
from .layout import Layout
from .models.load import load_deployment
from .snapshot import create_snapshot, load_snapshot
from .validate import (
    validate_deployment_changes,
)


def synchronise(deployment_root: Path, config_folder: Path) -> None:
    """Synchronise the deployment folder with the current configuration"""
    deployment = load_deployment(config_folder)
    layout = Layout(deployment_root)
    snapshot = load_snapshot(layout)

    deployment_changes = validate_deployment_changes(deployment, snapshot)

    check_deploy_actions(deployment_changes, layout)

    create_snapshot(deployment, layout)
    deploy(deployment_changes, layout)
