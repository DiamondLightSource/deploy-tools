import yaml

from .layout import Layout
from .models.deployment import Deployment, DeploymentSettings
from .models.load import load_from_yaml


class SnapshotError(Exception):
    pass


def create_snapshot(deployment: Deployment, layout: Layout) -> None:
    with open(layout.snapshot_file, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def load_snapshot(layout: Layout, allow_empty: bool = True) -> Deployment:
    if not layout.snapshot_file.exists():
        if allow_empty:
            return Deployment(settings=DeploymentSettings(), modules={})

        raise SnapshotError(f"Cannot load deployment snapshot:\n{layout.snapshot_file}")

    return load_from_yaml(Deployment, layout.snapshot_file)
