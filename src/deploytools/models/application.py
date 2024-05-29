from typing import Union

from pydantic import BaseModel, Field

from .apptainer import Apptainer
from .runfile import Runfile
from .yaml_schema import YamlSchema


class ApplicationMetadata(BaseModel):
    name: str
    module: str
    version: str


class Application(YamlSchema):
    metadata: ApplicationMetadata
    config: Union[Apptainer, Runfile] = Field(..., discriminator="app_type")
