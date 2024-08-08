from pathlib import Path

import typer
from typing_extensions import Annotated

from .default_versions import apply_default_versions
from .deploy import deploy
from .deprecate import deprecate
from .layout import Layout
from .models.deployment import DefaultVersionsByName
from .models.load import load_deployment
from .remove import remove
from .remove_name_folders import remove_name_folders
from .restore import restore
from .snapshot import create_snapshot, load_snapshot
from .update import update
from .validate import (
    UpdateGroup,
    check_actions,
    validate_default_versions,
    validate_deployment,
)


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
) -> None:
    """Sync deployment folder with current configuration"""
    deployment = load_deployment(config_folder)
    layout = Layout(deployment_root)
    snapshot = load_snapshot(layout)

    update_group = validate_deployment(deployment, snapshot)
    default_versions = validate_default_versions(deployment)

    check_actions(update_group, default_versions, layout)

    create_snapshot(deployment, layout)
    perform_actions(update_group, layout, default_versions)


def perform_actions(
    update_group: UpdateGroup, layout: Layout, default_versions: DefaultVersionsByName
) -> None:
    deploy(update_group.added, layout)
    update(update_group.updated, layout)
    deprecate(update_group.deprecated, layout)
    restore(update_group.restored, layout)
    remove(update_group.removed, layout)

    apply_default_versions(default_versions, layout)
    remove_name_folders(
        update_group.deprecated, update_group.restored, update_group.removed, layout
    )
