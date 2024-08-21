from pydantic import Field

from .apptainer import Apptainer
from .command import Command
from .parent import ParentModel
from .shell import Shell


class Application(ParentModel):
    """Represents one of several application types in module configuration."""

    app_config: Apptainer | Command | Shell = Field(..., discriminator="app_type")
