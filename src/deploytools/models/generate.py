from pathlib import Path
from typing import Dict

import typer
from typing_extensions import Annotated

from .application import ApplicationModel
from .module import ModuleModel
from .yaml_schema import YamlSchemaModel

app = typer.Typer()

app.command()


schemas: Dict[str, type[YamlSchemaModel]] = {
    "application.json": ApplicationModel,
    "module.json": ModuleModel,
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
