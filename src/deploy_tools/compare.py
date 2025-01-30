from collections import defaultdict
from pathlib import Path

from .layout import Layout
from .models.deployment import (
    DefaultVersionsByName,
    Deployment,
    DeploymentSettings,
    ReleasesByNameAndVersion,
)
from .models.load import load_from_yaml
from .models.module import Module, Release
from .module import get_default_modulefile_version, is_modulefile_deployed
from .snapshot import load_snapshot
from .validate import validate_default_versions


class ComparisonError(Exception):
    pass


def compare_to_snapshot(deployment_root: Path) -> None:
    """Compare deployment area to deployment configuration snapshot.

    This enables us to identify broken environment modules. Note that this does not
    exclude the possibility of all types of issues.
    """
    layout = Layout(deployment_root)

    deployment_snapshot = load_snapshot(layout)
    actual_deployment = _create_deployment_config_from_modules(layout)

    _compare_snapshot_to_actual(snapshot=deployment_snapshot, actual=actual_deployment)


def _create_deployment_config_from_modules(layout: Layout) -> Deployment:
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
        f"Modulefile for {name}/{version} not found. Verification failed."
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
            f"Snapshot and actual release configuration do not match, see:\n"
            f"Snapshot: {snapshot.releases}\nActual: {actual.releases}"
        )


def _compare_default_versions(snapshot: Deployment, actual: Deployment) -> None:
    snapshot_defaults = validate_default_versions(snapshot)
    actual_defaults = actual.settings.default_versions

    if snapshot_defaults != actual_defaults:
        raise ComparisonError(
            f"Snapshot and actual module default versions do not match, see:\n"
            f"Snapshot: {snapshot_defaults}\nActual: {actual_defaults}"
        )
