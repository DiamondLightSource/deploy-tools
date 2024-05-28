from pathlib import Path
from typing import Dict

import typer
from typing_extensions import Annotated

from .application import Application
from .module import Module
from .yaml_schema import YamlSchema

app = typer.Typer()

app.command()


schemas: Dict[str, type[YamlSchema]] = {
    "application.json": Application,
    "module.json": Module,
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
        with open(out_path, "w+") as f:
            f.write(model.generate_schema())


def main():
    typer.run(generate)
