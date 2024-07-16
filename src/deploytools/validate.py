from pathlib import Path

import typer
from typing_extensions import Annotated

from .models.load import load_deployment
from .validation import validate_deployment

app = typer.Typer()

app.command()


def validate(
    deploy_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
        ),
    ],
    config_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
):
    """Validate deployment configuration and print a list of modules for deployment.

    This is the same validation that the deploy-modules command uses."""
    assert deploy_folder.exists(), f"Deployment folder does not exist:\n{deploy_folder}"

    deployment = load_deployment(config_folder)
    modules_list = validate_deployment(deployment, deploy_folder)

    if not modules_list:
        print("No modules to be released.")
    else:
        print("Modules to be released:")

    for module in modules_list:
        print(f"{module.metadata.name}/{module.metadata.version}")
