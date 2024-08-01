from pathlib import Path

import typer
from typing_extensions import Annotated

from .deploy import check_deploy
from .deprecate import check_deprecate
from .models.load import load_deployment
from .remove import check_remove
from .restore import check_restore
from .validation import UpdateGroup, validate_deployment


def validate(
    deployment_root: Annotated[
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

    This is the same validation that the deploytools sync command uses."""
    assert (
        deployment_root.exists()
    ), f"Deployment folder does not exist:\n{deployment_root}"

    deployment = load_deployment(config_folder)
    update_group = validate_deployment(deployment, deployment_root)

    check_actions(update_group, deployment_root)

    display_updates(update_group)


def check_actions(update_group: UpdateGroup, deployment_root: Path):
    check_deploy(deployment_root)
    check_deprecate(update_group.deprecated, deployment_root)
    check_restore(update_group.restored, deployment_root)
    check_remove(update_group.removed, deployment_root)


def display_updates(update_group: UpdateGroup):
    display_config = {
        "deployed": update_group.added,
        "deprecated": update_group.deprecated,
        "restored": update_group.restored,
        "removed": update_group.removed,
    }

    for description, modules in display_config.items():
        if not modules:
            print(f"No modules to be {description}.")
        else:
            print(f"Modules to be {description}:")

        for module in modules:
            print(f"{module.metadata.name}/{module.metadata.version}")

        print()
