from typing import Optional, Sequence

from pydantic import BaseModel


class ModuleMetadataModel(BaseModel):
    name: str
    version: str


class ExternalModuleModel(BaseModel):
    name: str
    version: Optional[str]


class EnvVarModel(BaseModel):
    name: str
    value: str


class ModuleModel(BaseModel):
    metadata: ModuleMetadataModel
    dependencies: Sequence[ExternalModuleModel] = []
    environment_vars: Sequence[EnvVarModel] = []
