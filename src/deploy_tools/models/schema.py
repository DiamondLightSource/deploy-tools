import json
import logging
from pathlib import Path

from pydantic import BaseModel

from .deployment import Deployment, DeploymentSettings
from .module import Release

logger = logging.getLogger(__name__)

SCHEMA_NAMES: dict[str, type[BaseModel]] = {
    "module.json": Release,
    "release.json": Release,
    "deployment.json": Deployment,
    "deployment-settings.json": DeploymentSettings,
}


def generate_schema(output_path: Path) -> None:
    """Generate JSON schemas for yaml configuration files.

    While the ``Deployment`` object is not intended to be created by hand, it may need
    to be fixed manually in certain circumstances so a schema is considered useful.
    """
    for filename, model in SCHEMA_NAMES.items():
        out_path = output_path / filename
        logger.info("Creating schema file for %s", model.__name__)
        logger.debug("Output path: %s", out_path)

        schema = model.model_json_schema()
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
            f.write("\n")  # json.dump does not add final newline
