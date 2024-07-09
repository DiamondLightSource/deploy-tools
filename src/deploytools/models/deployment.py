from pydantic import BaseModel

from .module import ModuleModel


class DeploymentModel(BaseModel):
    modules: list[ModuleModel]
