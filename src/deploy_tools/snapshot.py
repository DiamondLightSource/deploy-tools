import yaml

from .layout import Layout
from .models.deployment import Deployment, DeploymentSettings
from .models.load import load_from_yaml


class SnapshotError(Exception):
    pass


def create_snapshot(deployment: Deployment, layout: Layout) -> None:
    """Create a snapshot file for the deployment configuration.

    This snapshot can then be used to compare the previous and current deployment
    configuration when a compare, validate or sync process is run.
    """
    _backup_snapshot(layout)
    with open(layout.deployment_snapshot_path, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def _backup_snapshot(layout: Layout) -> None:
    """Move the existing Deployment snapshot to save as a backup

    This could be useful when attempting to fix any issues caused by a failed Deploy
    step.
    """
    if layout.deployment_snapshot_path.exists():
        layout.deployment_snapshot_path.rename(layout.previous_deployment_snapshot_path)


def load_snapshot(layout: Layout, from_scratch: bool = False) -> Deployment:
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

        return Deployment(settings=DeploymentSettings(), releases={})

    return load_from_yaml(Deployment, layout.deployment_snapshot_path)
