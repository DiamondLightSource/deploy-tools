import json
from pathlib import Path

import typer
from pydantic import BaseModel
from typing_extensions import Annotated

from .deployment import Deployment, DeploymentSettings
from .module import Module

SCHEMA_NAMES: dict[str, type[BaseModel]] = {
    "module.json": Module,
    "deployment.json": Deployment,
    "deployment-settings.json": DeploymentSettings,
}


def schema(
    output_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
) -> None:
    """Generate JSON schema for yaml configuration files."""
    for filename, model in SCHEMA_NAMES.items():
        out_path = output_path / filename
        schema = model.model_json_schema()
        with open(out_path, "w+") as f:
            json.dump(schema, f, indent=2)
