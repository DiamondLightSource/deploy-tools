from pathlib import Path

import typer
from typing_extensions import Annotated

from .deploy import deploy
from .deployment import create_snapshot
from .deprecate import deprecate
from .models.load import load_deployment
from .remove import remove
from .restore import restore
from .validate import check_actions
from .validation import UpdateGroup, validate_deployment


def sync(
    deployment_root: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
    config_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
):
    """Sync deployment folder with current configuration"""
    deployment = load_deployment(config_folder)
    update_group = validate_deployment(deployment, deployment_root)

    check_actions(update_group, deployment_root)

    create_snapshot(deployment, deployment_root)
    perform_actions(update_group, deployment_root)


def perform_actions(update_group: UpdateGroup, deployment_root: Path):
    deploy(update_group.added, deployment_root)
    deprecate(update_group.deprecated, deployment_root)
    restore(update_group.restored, deployment_root)
    remove(update_group.removed, deployment_root)
