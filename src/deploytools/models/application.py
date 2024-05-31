from typing import Optional, Union

from pydantic import BaseModel, Field

from .apptainer import ApptainerModel
from .runfile import RunFileModel


class AppMetadataModel(BaseModel):
    name: str
    module: str
    version: str
    description: Optional[str] = None


class ApplicationModel(BaseModel):
    metadata: AppMetadataModel
    config: Union[ApptainerModel, RunFileModel] = Field(..., discriminator="app_type")
