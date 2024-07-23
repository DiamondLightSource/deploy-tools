from typing import Union

from pydantic import BaseModel, Field

from .apptainer import ApptainerConfig
from .command import CommandConfig
from .shell import ShellConfig


class ApplicationConfig(BaseModel):
    app_config: Union[ApptainerConfig, CommandConfig, ShellConfig] = Field(
        ..., discriminator="app_type"
    )
