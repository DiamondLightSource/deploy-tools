import json
from pathlib import Path

import typer
import yaml
from typing_extensions import Annotated

from .application import ApplicationModel
from .module import ModuleModel

app = typer.Typer()

app.command()

ConfigClass = ModuleModel | ApplicationModel

schemas: dict[str, type[ConfigClass]] = {
    "module.json": ModuleModel,
    "application.json": ApplicationModel,
}


def get_from_yaml(model: type[ConfigClass], file_path: Path) -> ConfigClass:
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
