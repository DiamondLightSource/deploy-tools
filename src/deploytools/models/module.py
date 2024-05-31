from typing import Optional, Sequence

from pydantic import BaseModel

from .yaml_schema import YamlSchemaModel


class ModuleMetadataModel(BaseModel):
    name: str
    version: str


class ExternalModuleModel(BaseModel):
    name: str
    version: Optional[str]


class EnvVarModel(BaseModel):
    name: str
    value: str


class ModuleModel(YamlSchemaModel):
    metadata: ModuleMetadataModel
    dependencies: Optional[Sequence[ExternalModuleModel]]
    environment_vars: Optional[Sequence[EnvVarModel]]
