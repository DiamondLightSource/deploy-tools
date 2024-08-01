import yaml

from .layout import Layout
from .models.deployment import Deployment, DeploymentSettings
from .models.load import load_from_yaml


class SnapshotError(Exception):
    pass


def create_snapshot(deployment: Deployment, layout: Layout) -> None:
    snapshot_file = layout.get_deployment_snapshot_file()

    with open(snapshot_file, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def load_snapshot(layout: Layout, allow_empty=True) -> Deployment:
    snapshot_file = layout.get_deployment_snapshot_file()

    if not snapshot_file.exists():
        if allow_empty:
            return Deployment(settings=DeploymentSettings(), modules={})

        raise SnapshotError(f"Deployment snapshot does not exist:\n{snapshot_file}")

    return load_from_yaml(Deployment, snapshot_file)
