from typing import TypeAlias

from pydantic import BaseModel

from .module import Module

ModulesByVersion: TypeAlias = dict[str, Module]
ModulesByNameAndVersion: TypeAlias = dict[str, ModulesByVersion]
DefaultVersionsByName: TypeAlias = dict[str, str]


class DeploymentSettings(BaseModel, extra="forbid"):
    default_versions: DefaultVersionsByName = {}


class Deployment(BaseModel, extra="forbid"):
    """Configuration for all modules and applications that should be deployed."""

    settings: DeploymentSettings
    modules: ModulesByNameAndVersion
