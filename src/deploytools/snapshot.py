from pathlib import Path

import yaml

from deploytools.layout import DEPLOYMENT_SNAPSHOT_FILENAME
from deploytools.models.deployment import DeploymentConfig
from deploytools.models.load import load_from_yaml


class SnapshotError(Exception):
    pass


def create_snapshot(deployment: DeploymentConfig, deployment_root: Path) -> None:
    snapshot_file = deployment_root / DEPLOYMENT_SNAPSHOT_FILENAME

    with open(snapshot_file, "w") as f:
        yaml.safe_dump(deployment.model_dump(), f)


def load_snapshot(deployment_root: Path, allow_empty=True) -> DeploymentConfig:
    snapshot_file = deployment_root / DEPLOYMENT_SNAPSHOT_FILENAME

    if not snapshot_file.exists():
        if allow_empty:
            return DeploymentConfig(modules={})

        raise SnapshotError(f"Deployment snapshot does not exist:\n{snapshot_file}")

    return load_from_yaml(DeploymentConfig, snapshot_file)
