from typing import Union

from pydantic import BaseModel, Field

from .apptainer import ApptainerConfig
from .command import CommandConfig


class ApplicationConfig(BaseModel):
    app_config: Union[ApptainerConfig, CommandConfig] = Field(
        ..., discriminator="app_type"
    )
