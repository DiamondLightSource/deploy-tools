import logging
from pathlib import Path

from .build import build, clean_build_area
from .deploy import deploy_changes
from .layout import Layout
from .models.save_and_load import load_deployment
from .snapshot import create_snapshot, load_snapshot
from .validate import (
    validate_deployment_changes,
)

logger = logging.getLogger(__name__)


def synchronise(
    deployment_root: Path,
    config_folder: Path,
    allow_all: bool = False,
    from_scratch: bool = False,
) -> None:
    """Synchronise the deployment folder with the current configuration."""
    logger.info("Loading deployment configuration from: %s", config_folder)
    deployment = load_deployment(config_folder)

    logger.info("Loading deployment snapshot")
    layout = Layout(deployment_root)
    snapshot = load_snapshot(layout, from_scratch)

    logger.info("Validating deployment changes")
    deployment_changes = validate_deployment_changes(deployment, snapshot, allow_all)

    logger.info("Cleaning build area")
    clean_build_area(layout)
    logger.info("Building modules")
    build(deployment_changes, layout)

    logger.info("Creating snapshot")
    create_snapshot(deployment, layout)

    logger.info("Deploying changes")
    deploy_changes(deployment_changes, layout)
