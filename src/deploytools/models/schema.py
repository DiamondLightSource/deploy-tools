import json
from pathlib import Path

import typer
from pydantic import BaseModel
from typing_extensions import Annotated

from .application import ApplicationConfig
from .deployment import DeploymentConfig
from .module import ModuleConfig, ModuleMetadataConfig

app = typer.Typer()

app.command()

schemas: dict[str, type[BaseModel]] = {
    "module.json": ModuleConfig,
    "module-metadata.json": ModuleMetadataConfig,
    "application.json": ApplicationConfig,
    "deployment.json": DeploymentConfig,
}


def schema(
    folder_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
):
    """Generate JSON schema for yaml configuration files."""
    for filename, model in schemas.items():
        out_path = folder_path / filename
        schema = model.model_json_schema()
        with open(out_path, "w+") as f:
            json.dump(schema, f, indent=2)
