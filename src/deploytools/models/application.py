from pydantic import BaseModel, Field

from .apptainer import Apptainer
from .command import Command
from .shell import Shell


class Application(BaseModel, extra="forbid"):
    """Represents one of several application types in module configuration."""

    app_config: Apptainer | Command | Shell = Field(..., discriminator="app_type")
