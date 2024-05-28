from typing import Union

from pydantic import Field

from .apptainer import Apptainer
from .runfile import Runfile
from .yaml_schema import YamlSchema


class Application(YamlSchema):
    name: str
    module: str
    version: str
    config: Union[Apptainer, Runfile] = Field(..., discriminator="app_type")
