from typing import Optional, Union

from pydantic import BaseModel, Field

from .apptainer import ApptainerModel
from .runfile import RunfileModel
from .yaml_schema import YamlSchemaModel


class AppMetadataModel(BaseModel):
    name: str
    module: str
    version: str
    description: Optional[str] = None


class ApplicationModel(YamlSchemaModel):
    metadata: AppMetadataModel
    config: Union[ApptainerModel, RunfileModel] = Field(..., discriminator="app_type")
