from typing import TypeAlias

from pydantic import BaseModel, Field

from .module import Module

ModulesByVersion: TypeAlias = dict[str, Module]
ModulesByNameAndVersion: TypeAlias = dict[str, ModulesByVersion]


class DefaultVersion(BaseModel, extra="forbid"):
    name: str
    version: str


class DeploymentSettings(BaseModel, extra="forbid"):
    default_versions: list[DefaultVersion] = Field(default_factory=list)


class Deployment(BaseModel, extra="forbid"):
    settings: DeploymentSettings
    modules: ModulesByNameAndVersion
