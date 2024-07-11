from pydantic import BaseModel

from .module import ModuleConfig


class DeploymentConfig(BaseModel):
    modules: list[ModuleConfig]
