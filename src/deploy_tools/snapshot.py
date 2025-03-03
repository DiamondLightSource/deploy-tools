import logging

import yaml

from .layout import Layout
from .models.deployment import Deployment, DeploymentSettings
from .models.load import load_from_yaml

logger = logging.getLogger(__name__)


class SnapshotError(Exception):
    pass


def create_snapshot(deployment: Deployment, layout: Layout) -> None:
    """Create a snapshot file for the deployment configuration.

    This snapshot can then be used to compare the previous and current deployment
    configuration when a compare, validate or sync process is run.
    """
    _backup_snapshot(layout)
    logger.debug("Creating snapshot: %s", layout.deployment_snapshot_path)
    with open(layout.deployment_snapshot_path, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def _backup_snapshot(layout: Layout) -> None:
    """Move the existing Deployment snapshot to save as a backup

    This could be useful when attempting to fix any issues caused by a failed Deploy
    step.
    """
    if layout.deployment_snapshot_path.exists():
        logger.debug(
            "Backup previous snapshot to: %s", layout.previous_deployment_snapshot_path
        )
        layout.deployment_snapshot_path.rename(layout.previous_deployment_snapshot_path)


def load_snapshot(layout: Layout, from_scratch: bool = False) -> Deployment:
    """Load snapshot of the Deployment configuration taken at start of Deploy step.

    Args:
        layout: The ``Layout`` representing the Deployment Area.
        from_scratch: If True, this will return the default ``Deployment`` configuration
            in order to work with an empty Deployment Area.
    """
    if from_scratch:
        if not layout.deployment_root.exists():
            raise SnapshotError(
                f"Deployment root does not exist:\n{layout.deployment_root}"
            )

        if layout.deployment_snapshot_path.exists():
            raise SnapshotError(
                f"Deployment snapshot must not exist when deploying from scratch:\n"
                f"{layout.deployment_snapshot_path}"
            )

        logger.debug("Loading empty deployment configuration as snapshot")
        return Deployment(settings=DeploymentSettings(), releases={})

    logger.debug("Loading snapshot: %s", layout.deployment_snapshot_path)
    return load_from_yaml(Deployment, layout.deployment_snapshot_path)


def load_previous_snapshot(layout: Layout) -> Deployment:
    logger.debug(
        "Loading previous snapshot: %s", layout.previous_deployment_snapshot_path
    )
    return load_from_yaml(Deployment, layout.previous_deployment_snapshot_path)
