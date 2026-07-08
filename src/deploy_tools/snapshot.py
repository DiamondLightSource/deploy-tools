import io
import logging
from typing import cast

import yaml
from git import BadName, Repo
from pydantic import ValidationError as PydanticValidationError

from .errors import DeployToolsError
from .layout import Layout
from .models.deployment import Deployment, DeploymentSettings
from .models.save_and_load import load_from_yaml, save_as_yaml

logger = logging.getLogger(__name__)


class SnapshotError(DeployToolsError):
    """Raised when a deployment snapshot is missing or in an unexpected state."""


def create_snapshot(deployment: Deployment, layout: Layout) -> None:
    """Create a snapshot file for the deployment configuration.

    This snapshot can then be used to compare the previous and current deployment
    configuration when a compare, validate or sync process is run.
    """
    logger.debug("Creating snapshot: %s", layout.deployment_snapshot_path)
    save_as_yaml(deployment, layout.deployment_snapshot_path)


def load_snapshot(layout: Layout, from_scratch: bool = False) -> Deployment:
    """Load snapshot of the Deployment configuration taken at start of Deploy step.

    Args:
        layout: The ``Layout`` representing the Deployment Area.
        from_scratch: If True, this will return the default ``Deployment``
            configuration in order to work with an empty Deployment Area.
    """
    if not layout.deployment_root.exists() or not layout.deployment_root.is_dir():
        raise SnapshotError(
            f"Deployment root folder does not exist:\n{layout.deployment_root}"
        )

    if from_scratch:
        if layout.deployment_snapshot_path.exists():
            raise SnapshotError(
                f"Deployment snapshot must not exist when deploying from scratch:\n"
                f"{layout.deployment_snapshot_path}"
            )

        logger.debug("Loading empty deployment configuration as snapshot")
        return Deployment(settings=DeploymentSettings(), releases={})

    if not layout.deployment_snapshot_path.exists():
        raise SnapshotError(
            f"Deployment snapshot not found:\n{layout.deployment_snapshot_path}"
        )

    logger.debug("Loading snapshot: %s", layout.deployment_snapshot_path)
    try:
        with open(layout.deployment_snapshot_path) as f:
            return load_from_yaml(Deployment, f)
    except (OSError, yaml.YAMLError, PydanticValidationError, TypeError) as exc:
        raise SnapshotError(
            f"Deployment snapshot could not be read:\n{layout.deployment_snapshot_path}"
        ) from exc


def load_snapshot_from_ref(layout: Layout, ref: str) -> Deployment:
    """Load the deployment snapshot from the given git ref of the deployment area."""
    logger.debug("Loading snapshot from ref: %s", ref)
    with Repo(layout.deployment_root) as repo:
        try:
            ref_snapshot = repo.commit(ref).tree[layout.DEPLOYMENT_SNAPSHOT_FILENAME]
        except (BadName, KeyError) as exc:
            raise SnapshotError(
                f"Deployment snapshot not found at git ref:\n{ref}"
            ) from exc

        snapshot_bytes = cast(bytes, ref_snapshot.data_stream.read())
        with io.BytesIO(snapshot_bytes) as snapshot_f:
            return load_from_yaml(Deployment, snapshot_f)
