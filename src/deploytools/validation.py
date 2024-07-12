from collections import defaultdict
from pathlib import Path
from typing import TypeAlias

from .models.deployment import DeploymentConfig
from .models.load import load_from_yaml
from .models.module import ModuleConfig

DEPLOYMENT_SNAPSHOT_FILENAME = "deployment.yaml"

ModuleVersionsByName: TypeAlias = dict[str, list[str]]
ModulesByName: TypeAlias = dict[str, list[tuple[str, ModuleConfig]]]


class ValidationError(Exception):
    pass


def validate_deployment(
    deployment: DeploymentConfig, deploy_folder: Path
) -> list[ModuleConfig]:
    last_deployment = get_old_deployment_config(deploy_folder)
    new_modules = get_modules_struct(deployment, validate=True)
    last_modules = get_modules_struct(last_deployment, validate=False)

    modified_modules = get_modified_modules(last_modules, new_modules)

    deployed_modules = get_deployed_modules(deploy_folder)
    check_modified_modules_not_previously_deployed(deployed_modules, modified_modules)

    modified_list: list[ModuleConfig] = []
    for versioned_list in modified_modules.values():
        for _, module in versioned_list:
            modified_list.append(module)
    return modified_list


def get_old_deployment_config(deploy_folder: Path) -> DeploymentConfig:
    snapshot_path = deploy_folder / DEPLOYMENT_SNAPSHOT_FILENAME
    if not snapshot_path.exists():
        return DeploymentConfig(modules=[])

    return load_from_yaml(DeploymentConfig, snapshot_path)


def get_modules_struct(deployment: DeploymentConfig, validate: bool) -> ModulesByName:
    modules_struct: ModulesByName = defaultdict(list)
    for module in deployment.modules:
        name = module.metadata.name
        version = module.metadata.version

        if validate and version in modules_struct[name]:
            raise ValidationError(
                f"Module {name} has multiple configurations for version {version}"
            )

        modules_struct[name].append((version, module))

    return modules_struct


def get_modified_modules(
    old_modules: ModulesByName, new_modules: ModulesByName
) -> ModulesByName:
    """Get list of modules that have been modified since last deployment.

    We do not care about deleted modules / versions as they require no deployment."""
    modified_modules: ModulesByName = defaultdict(list)
    for name in new_modules:
        if name not in old_modules:
            modified_modules[name] = new_modules[name]
            continue

        old_modules_map = dict(old_modules[name])
        for version, new_config in new_modules[name]:
            if version not in old_modules_map:
                modified_modules[name].append((version, new_config))
                continue

            if not new_config == old_modules_map[version]:
                raise ValidationError(
                    f"Module {name} with version {version} modified without updating"
                    " configuration"
                )

    return modified_modules


def get_deployed_modules(deploy_folder: Path) -> ModuleVersionsByName:
    modules_folder = deploy_folder / "modulefiles"
    previous_modules: ModuleVersionsByName = defaultdict(list)

    for module_folder in modules_folder.glob("*"):
        for version_folder in module_folder.glob("*"):
            previous_modules[module_folder.name].append(version_folder.name)

    return previous_modules


def check_modified_modules_not_previously_deployed(
    deployed_modules: ModuleVersionsByName, modified_modules: ModulesByName
):
    for name, modules_list in modified_modules.items():
        for version, _ in modules_list:
            if version in deployed_modules[name]:
                raise ValidationError(
                    f"Module previously deployed for name: {name} and version {version}"
                )
