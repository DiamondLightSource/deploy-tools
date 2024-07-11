from typing import Union

from pydantic import BaseModel, Field

from .apptainer import ApptainerConfig
from .runfile import RunFileConfig


class ApplicationConfig(BaseModel):
    app_config: Union[ApptainerConfig, RunFileConfig] = Field(
        ..., discriminator="app_type"
    )
