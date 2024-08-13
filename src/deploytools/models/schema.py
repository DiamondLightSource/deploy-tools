import json
from pathlib import Path

from pydantic import BaseModel

from .deployment import Deployment, DeploymentSettings
from .module import Module

SCHEMA_NAMES: dict[str, type[BaseModel]] = {
    "module.json": Module,
    "deployment.json": Deployment,
    "deployment-settings.json": DeploymentSettings,
}


def generate_schema(output_path: Path) -> None:
    """Generate JSON schemas for yaml configuration files."""
    for filename, model in SCHEMA_NAMES.items():
        out_path = output_path / filename
        schema = model.model_json_schema()
        with open(out_path, "w+") as f:
            json.dump(schema, f, indent=2)
