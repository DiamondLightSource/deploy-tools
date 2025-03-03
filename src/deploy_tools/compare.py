import difflib
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from pydantic import TypeAdapter

from .layout import Layout
from .models.deployment import (
    DefaultVersionsByName,
    Deployment,
    DeploymentSettings,
    ReleasesByNameAndVersion,
)
from .models.load import load_from_yaml
from .models.module import Module, Release
from .modulefile import get_default_modulefile_version, is_modulefile_deployed
from .snapshot import load_previous_snapshot, load_snapshot
from .validate import validate_default_versions

logger = logging.getLogger(__name__)


class ComparisonError(Exception):
    pass


def compare_to_snapshot(deployment_root: Path, use_previous: bool = False) -> None:
    """Compare deployment area to deployment configuration snapshot.

    This helps us to identify broken environment modules. Note that this does not
    exclude the possibility of all types of issues.

    The `use_previous` argument can be used to provide a comparison with the previous
    Deployment configuration. This is taken as a backup at the very start of the Deploy
    step.

    Args:
        deployment_root: The root folder of the Deployment Area.
        use_previous: If True, compare to the previous snapshot taken as backup at start
            of the Deploy step.
    """
    layout = Layout(deployment_root)

    if use_previous:
        logger.info("Loading previous deployment snapshot")
        deployment_snapshot = load_previous_snapshot(layout)
    else:
        logger.info("Loading deployment snapshot")
        deployment_snapshot = load_snapshot(layout)

    logger.info("Reconstructing deployment configuration from deployment area")
    actual_deployment = _reconstruct_deployment_config_from_modules(layout)

    logger.info("Comparing reconstructed configuration with snapshot")
    _compare_snapshot_to_actual(snapshot=deployment_snapshot, actual=actual_deployment)


def _reconstruct_deployment_config_from_modules(layout: Layout) -> Deployment:
    """Use the deployment area to reconstruct a Deployment configuration object.

    Note that the default versions will be different to those in initial configuration.
    """
    releases = _collect_releases(layout)
    default_versions = _collect_default_modulefile_versions(layout, list(releases))
    settings = DeploymentSettings(default_versions=default_versions)

    return Deployment(settings=settings, releases=releases)


def _collect_releases(layout: Layout) -> ReleasesByNameAndVersion:
    modules = _collect_modules(layout)

    releases: ReleasesByNameAndVersion = defaultdict(dict)

    for module in modules:
        deprecated = _get_deprecated_status(module.name, module.version, layout)
        release = Release(deprecated=deprecated, module=module)
        releases[module.name][module.version] = release

    return releases


def _collect_modules(layout: Layout) -> list[Module]:
    """Accumulate deployed modules and their configuration snapshot.

    This searches for module application files since creation of the modulefiles happens
    after the module.
    """

    modules: list[Module] = []

    for name_path in layout.modules_root.glob("*"):
        for version_path in name_path.glob("*"):
            name = name_path.name
            version = version_path.name
            modules.append(
                load_from_yaml(Module, layout.get_module_snapshot_path(name, version))
            )

    return modules


def _get_deprecated_status(name: str, version: str, layout: Layout) -> bool:
    if is_modulefile_deployed(name, version, layout):
        return False
    elif is_modulefile_deployed(name, version, layout, in_deprecated=True):
        return True

    raise ComparisonError(
        f"Modulefile for {name}/{version} not found in deployment area."
    )


def _collect_default_modulefile_versions(
    layout: Layout, names: list[str]
) -> DefaultVersionsByName:
    default_versions: dict[str, str] = {}

    for name in names:
        default_version = get_default_modulefile_version(name, layout)
        if default_version is not None:
            default_versions[name] = default_version

    return default_versions


def _compare_snapshot_to_actual(snapshot: Deployment, actual: Deployment) -> None:
    _compare_releases(snapshot, actual)
    _compare_default_versions(snapshot, actual)


def _compare_releases(snapshot: Deployment, actual: Deployment) -> None:
    if snapshot.releases != actual.releases:
        raise ComparisonError(
            "Snapshot and actual release configuration do not match, see:\n"
            + _get_dict_diff(snapshot.releases, actual.releases)
        )


def _compare_default_versions(snapshot: Deployment, actual: Deployment) -> None:
    snapshot_defaults = validate_default_versions(snapshot)
    actual_defaults = actual.settings.default_versions

    if snapshot_defaults != actual_defaults:
        raise ComparisonError(
            "Snapshot and actual module default versions do not match, see:\n"
            + _get_dict_diff(snapshot_defaults, actual_defaults)
        )


def _get_dict_diff(d1: dict[str, Any], d2: dict[str, Any]):
    return "\n" + "\n".join(
        difflib.ndiff(
            _yaml_dumps(d1).splitlines(),
            _yaml_dumps(d2).splitlines(),
        )
    )


def _yaml_dumps(obj: dict[str, Any], indent: int | None = None) -> str:
    ta = TypeAdapter(dict[str, Any])
    return yaml.safe_dump(ta.dump_python(obj), indent=indent)
