import yaml

from .layout import Layout
from .models.deployment import Deployment, DeploymentSettings
from .models.load import load_from_yaml


class SnapshotError(Exception):
    pass


def create_snapshot(deployment: Deployment, layout: Layout) -> None:
    """Create a snapshot file for the deployment configuration.

    This snapshot can then be used to compare the previous and current deployment
    configuration when a validate or sync process is run.
    """
    with open(layout.deployment_snapshot_path, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def load_snapshot(layout: Layout, allow_empty: bool = True) -> Deployment:
    if not layout.deployment_snapshot_path.exists():
        if allow_empty:
            return Deployment(settings=DeploymentSettings(), releases={})

        raise SnapshotError(
            f"Cannot load deployment snapshot:\n{layout.deployment_snapshot_path}"
        )

    return load_from_yaml(Deployment, layout.deployment_snapshot_path)
