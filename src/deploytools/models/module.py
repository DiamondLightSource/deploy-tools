from typing import Optional, Sequence

from pydantic import BaseModel

from .yaml_schema import YamlSchema


class ExternalModule(BaseModel):
    name: str
    version: Optional[str]


class EnvVar(BaseModel):
    name: str
    value: str


class Module(YamlSchema):
    name: str
    version: str
    dependencies: Optional[Sequence[ExternalModule]]
    environment_vars: Optional[Sequence[EnvVar]]
