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
from .models.module import Module, Release
from .models.save_and_load import load_from_yaml
from .modulefile import get_default_modulefile_version, get_deployed_modulefile_versions
from .snapshot import load_previous_snapshot, load_snapshot
from .validate import validate_default_versions

logger = logging.getLogger(__name__)


class ComparisonError(Exception):
    pass


def compare_to_snapshot(
    deployment_root: Path, use_previous: bool = False, from_scratch: bool = False
) -> None:
    """Compare deployment area to deployment configuration snapshot.

    This helps us to identify broken environment modules. Note that this does not
    exclude the possibility of all types of issues.

    The `use_previous` argument can be used to provide a comparison with the previous
    Deployment configuration. This is taken as a backup at the very start of the Deploy
    step.

    The `from_scratch` argument checks that the deployment area is in a suitable state
    for a clean deployment into an empty directory.

    Args:
        deployment_root: The root folder of the Deployment Area.
        use_previous: If True, compare to the previous snapshot taken as backup at start
            of the Deploy step.
        from_scratch: If True, check that the deployment area is empty and ignore other
            requirements.
    """
    layout = Layout(deployment_root)

    if from_scratch:
        logger.info("Checking deployment area is empty for a from-scratch deployment")

        if not layout.deployment_root.exists() or not layout.deployment_root.is_dir():
            raise ComparisonError(
                f"Deployment root folder does not exist:\n{layout.deployment_root}"
            )

        if next(layout.deployment_root.iterdir(), None):
            raise ComparisonError(
                f"Deployment root folder is not empty:\n{layout.deployment_root}"
            )
        return

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
    modulefiles = get_deployed_modulefile_versions(layout)
    deprecated_modulefiles = get_deployed_modulefile_versions(layout, True)

    releases: ReleasesByNameAndVersion = defaultdict(dict)
    for module in modules:
        name = module.name
        version = module.version
        has_modulefile = version in modulefiles.get(name, [])
        has_deprecated_modulefile = version in deprecated_modulefiles.get(name, [])

        if has_modulefile and has_deprecated_modulefile:
            raise ComparisonError(
                f"Duplicate modulefiles for {name}/{version} found in default and "
                f"deprecated areas."
            )
        elif not has_modulefile and not has_deprecated_modulefile:
            raise ComparisonError(f"No modulefile found for {name}/{version}.")

        release = Release(deprecated=has_deprecated_modulefile, module=module)
        releases[name][version] = release

    for name, versions in modulefiles.items():
        for version in versions:
            if version not in releases[name]:
                raise ComparisonError(
                    f"Modulefile exists without corresponding built module for "
                    f"{name}/{version}"
                )

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
