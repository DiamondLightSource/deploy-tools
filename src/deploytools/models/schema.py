import json
from pathlib import Path
from typing import Dict, Type

import typer
import yaml
from pydantic import BaseModel
from typing_extensions import Annotated

from .application import ApplicationModel
from .module import ModuleModel

app = typer.Typer()

app.command()


schemas: Dict[str, type[BaseModel]] = {
    "module.json": ModuleModel,
    "application.json": ApplicationModel,
}


def get_from_yaml(model: Type[BaseModel], file_path: Path) -> BaseModel:
    with open(file_path) as f:
        return model(**yaml.safe_load(f))


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
