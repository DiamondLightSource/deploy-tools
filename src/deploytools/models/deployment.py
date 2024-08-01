from typing import TypeAlias

from pydantic import BaseModel

from .module import Module

ModulesByVersion: TypeAlias = dict[str, Module]
ModulesByNameAndVersion: TypeAlias = dict[str, ModulesByVersion]


class Deployment(BaseModel, extra="forbid"):
    modules: ModulesByNameAndVersion
