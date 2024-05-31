from typing import Union

from pydantic import BaseModel, Field

from .apptainer import ApptainerModel
from .runfile import RunFileModel


class ApplicationModel(BaseModel):
    app_config: Union[ApptainerModel, RunFileModel] = Field(
        ..., discriminator="app_type"
    )
