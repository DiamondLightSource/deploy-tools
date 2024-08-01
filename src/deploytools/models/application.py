from typing import Union

from pydantic import BaseModel, Field

from .apptainer import Apptainer
from .command import Command
from .shell import Shell


class Application(BaseModel, extra="forbid"):
    app_config: Union[Apptainer, Command, Shell] = Field(..., discriminator="app_type")
