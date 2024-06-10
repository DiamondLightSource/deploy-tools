import json
from pathlib import Path

import typer
from pydantic import BaseModel
from typing_extensions import Annotated

from .application import ApplicationModel
from .module import ModuleMetadataModel, ModuleModel

app = typer.Typer()

app.command()

schemas: dict[str, type[BaseModel]] = {
    "module.json": ModuleModel,
    "module-metadata.json": ModuleMetadataModel,
    "application.json": ApplicationModel,
}


def generate(
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
    for filename, model in schemas.items():
        out_path = folder_path / filename
        schema = model.model_json_schema()
        with open(out_path, "w+") as f:
            json.dump(schema, f, indent=2)


def main():
    typer.run(generate)
