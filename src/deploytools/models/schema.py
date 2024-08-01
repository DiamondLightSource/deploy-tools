import json
from pathlib import Path

import typer
from pydantic import BaseModel
from typing_extensions import Annotated

from .application import Application
from .deployment import Deployment
from .module import Module, ModuleMetadata

SCHEMA_NAMES: dict[str, type[BaseModel]] = {
    "module.json": Module,
    "module-metadata.json": ModuleMetadata,
    "application.json": Application,
    "deployment.json": Deployment,
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
):
    """Generate JSON schema for yaml configuration files."""
    for filename, model in SCHEMA_NAMES.items():
        out_path = output_path / filename
        schema = model.model_json_schema()
        with open(out_path, "w+") as f:
            json.dump(schema, f, indent=2)
