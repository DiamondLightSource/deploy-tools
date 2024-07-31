from pathlib import Path

import typer
from typing_extensions import Annotated

from .deploy import deploy
from .deployment import create_deployment_snapshot
from .deprecate import deprecate
from .models.load import load_deployment
from .remove import remove
from .restore import restore
from .validate import check_actions
from .validation import UpdateGroup, validate_deployment


def sync(
    deploy_folder: Annotated[
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
    update_group = validate_deployment(deployment, deploy_folder)

    check_actions(update_group, deploy_folder)

    create_deployment_snapshot(deployment, deploy_folder)
    perform_actions(update_group, deploy_folder)


def perform_actions(update_group: UpdateGroup, deploy_folder: Path):
    deploy(update_group.added, deploy_folder)
    deprecate(update_group.deprecated, deploy_folder)
    restore(update_group.restored, deploy_folder)
    remove(update_group.removed, deploy_folder)
