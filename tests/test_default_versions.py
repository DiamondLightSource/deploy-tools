"""Unit tests for default-version selection.

These call the function directly rather than through the CLI. Here that is to isolate
pure, non-trivial logic (e.g. natsort ordering of non-SemVer versions).
"""

from collections import defaultdict

import pytest

from deploy_tools.models.deployment import (
    Deployment,
    DeploymentSettings,
    ReleasesByNameAndVersion,
)
from deploy_tools.models.module import Module, Release
from deploy_tools.validate import ValidationError, validate_default_versions


def _release(
    name: str, version: str, *, deprecated: bool = False, excluded: bool = False
) -> Release:
    """Build a minimal Release with no applications, for selection tests."""
    return Release(
        module=Module(
            name=name,
            version=version,
            applications=[],
            exclude_from_defaults=excluded,
        ),
        deprecated=deprecated,
    )


def _deployment(
    *releases: Release, default_versions: dict[str, str] | None = None
) -> Deployment:
    """Assemble a Deployment from loose Releases and optional explicit defaults."""
    by_name: ReleasesByNameAndVersion = defaultdict(dict)
    for release in releases:
        by_name[release.module.name][release.module.version] = release

    return Deployment(
        settings=DeploymentSettings(default_versions=default_versions or {}),
        releases=by_name,
    )


def test_auto_selects_latest_version_by_natsort() -> None:
    # natsort, not string ordering: "10.0" must beat "2.0" (which sorts last lexically).
    deployment = _deployment(
        _release("mod", "1.0"),
        _release("mod", "2.0"),
        _release("mod", "10.0"),
    )
    assert validate_default_versions(deployment) == {"mod": "10.0"}


def test_prerelease_sorts_before_final_release() -> None:
    # The documented non-SemVer case: "1.2rc1" must come before "1.2", so the final
    # release is chosen as default over its own release candidate.
    deployment = _deployment(
        _release("mod", "1.2rc1"),
        _release("mod", "1.2"),
    )
    assert validate_default_versions(deployment) == {"mod": "1.2"}


def test_excluded_versions_are_not_auto_selected() -> None:
    # The highest version opts out of defaults, so the next-highest is chosen instead.
    deployment = _deployment(
        _release("mod", "1.0"),
        _release("mod", "2.0", excluded=True),
    )
    assert validate_default_versions(deployment) == {"mod": "1.0"}


def test_deprecated_versions_are_not_auto_selected() -> None:
    # Deprecated releases are excluded from the deployed set, so a higher deprecated
    # version must not become the default over a lower active one.
    deployment = _deployment(
        _release("mod", "1.0"),
        _release("mod", "2.0", deprecated=True),
    )
    assert validate_default_versions(deployment) == {"mod": "1.0"}


def test_explicit_default_is_preserved_over_auto_selection() -> None:
    # An explicit default wins even when a higher version exists.
    deployment = _deployment(
        _release("mod", "1.0"),
        _release("mod", "2.0"),
        default_versions={"mod": "1.0"},
    )
    assert validate_default_versions(deployment) == {"mod": "1.0"}


def test_explicit_default_for_nonexistent_version_raises() -> None:
    # Pointing the default at a version that will not be deployed is rejected.
    deployment = _deployment(
        _release("mod", "1.0"),
        default_versions={"mod": "9.9"},
    )
    with pytest.raises(ValidationError, match="Unable to configure mod/9.9 as default"):
        validate_default_versions(deployment)


def test_explicit_default_for_deprecated_version_raises() -> None:
    # A deprecated version is not in the deployed set, so it cannot be an explicit
    # default either.
    deployment = _deployment(
        _release("mod", "1.0", deprecated=True),
        default_versions={"mod": "1.0"},
    )
    with pytest.raises(ValidationError, match="Unable to configure mod/1.0 as default"):
        validate_default_versions(deployment)


def test_all_versions_excluded_raises() -> None:
    # With every version opting out and no explicit default, there is no eligible
    # version to make default.
    deployment = _deployment(_release("mod", "1.0", excluded=True))
    with pytest.raises(
        ValidationError,
        match="every version for name: mod has set exclude_from_defaults",
    ):
        validate_default_versions(deployment)
