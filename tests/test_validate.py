from pathlib import Path

import pytest

from conftest import run_cli
from deploy_tools.validate import ValidationError

# Configurations that 'validate' should reject when deployed from scratch into an empty
# area. Each maps a config folder under configs/invalid to a substring expected in the
# resulting ValidationError.
INVALID_INITIAL_CONFIGS = [
    (
        "unknown-dependency",
        "Module example-module-dependent/1.0 has unknown module dependency "
        "example-module-base/9.9",
    ),
    (
        "default-version-not-deployed",
        "Unable to configure example-module-shell/2.0 as default",
    ),
    (
        "no-eligible-default",
        "every version for name: example-module-shell has set exclude_from_defaults",
    ),
]


@pytest.mark.parametrize("config_name, message", INVALID_INITIAL_CONFIGS)
def test_validate_rejects_invalid_initial_config(
    tmp_path: Path, configs: Path, config_name: str, message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        run_cli(
            "validate", "--from-scratch", tmp_path, configs / "invalid" / config_name
        )


def test_validate_rejects_update_without_allow_updates(
    tmp_path: Path, configs: Path
) -> None:
    # Deploy a baseline whose module did not opt in to allow_updates, then validate a
    # config that changes that module in place: this must be rejected.
    run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "minimal")
    with pytest.raises(
        ValidationError,
        match="Module example-module-shell/1.0 modified without updating version",
    ):
        run_cli(
            "validate", tmp_path, configs / "invalid" / "modified-without-allow-updates"
        )


def test_validate_rejects_removal_without_deprecation(
    tmp_path: Path, configs: Path
) -> None:
    # Deploy a baseline module, then validate a config that drops it without first
    # deprecating it (and without --allow-all): this must be rejected.
    run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "minimal")
    with pytest.raises(
        ValidationError,
        match="Module example-module-shell/1.0 removed without prior deprecation",
    ):
        run_cli(
            "validate", tmp_path, configs / "invalid" / "removed-without-deprecation"
        )


def test_validate_rejects_added_deprecated_module(
    tmp_path: Path, configs: Path
) -> None:
    # Deploy a baseline module, then validate a config that introduces a brand-new
    # release already in a deprecated state. Deprecating a module on initial creation
    # is only allowed with --allow-all, so a normal validate must reject it.
    run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "minimal")
    with pytest.raises(
        ValidationError,
        match="Module example-module-shell/2.0 cannot have deprecated status",
    ):
        run_cli("validate", tmp_path, configs / "invalid" / "deprecated-on-creation")


def test_validate_allows_added_deprecated_module_with_allow_all(
    tmp_path: Path, configs: Path
) -> None:
    # The --allow-all flag deliberately permits introducing an already-deprecated
    # release on initial creation.
    run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "minimal")
    run_cli(
        "validate",
        "--allow-all",
        tmp_path,
        configs / "invalid" / "deprecated-on-creation",
    )


def test_validate_test_build(tmp_path: Path, configs: Path) -> None:
    # --test-build actually builds the modules into a temporary area and syntax-checks
    # the generated shell entrypoints, so exercise it on a valid shell-only config.
    run_cli(
        "validate",
        "--test-build",
        "--from-scratch",
        tmp_path,
        configs / "valid" / "minimal",
    )


def test_validate_test_build_rejects_invalid_script(
    tmp_path: Path, configs: Path
) -> None:
    # --test-build runs `bash -n` over each generated shell entrypoint, so a script that
    # is not valid bash must be rejected.
    with pytest.raises(
        ValidationError, match="Output script .*/test-shell-echo is invalid with errors"
    ):
        run_cli(
            "validate",
            "--test-build",
            "--from-scratch",
            tmp_path,
            configs / "invalid" / "invalid-shell-script",
        )


def test_validate_reports_no_actions_when_unchanged(
    tmp_path: Path, configs: Path
) -> None:
    # Validating a config that is already fully deployed previews no changes.
    run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "minimal")
    output = run_cli("validate", tmp_path, configs / "valid" / "minimal")
    assert "No release actions required" in output
