from typing import TypeAlias

from .module import Module
from .parent import ParentModel

ModulesByVersion: TypeAlias = dict[str, Module]
ModulesByNameAndVersion: TypeAlias = dict[str, ModulesByVersion]
DefaultVersionsByName: TypeAlias = dict[str, str]


class DeploymentSettings(ParentModel):
    default_versions: DefaultVersionsByName = {}


class Deployment(ParentModel):
    """Configuration for all modules and applications that should be deployed."""

    settings: DeploymentSettings
    modules: ModulesByNameAndVersion
