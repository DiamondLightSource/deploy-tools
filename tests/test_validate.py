from pathlib import Path

import pytest

from conftest import run_cli
from deploy_tools.validate import ValidationError

# Configurations that 'validate' should reject when deployed from scratch into an empty
# area. Each maps a config folder under configs/invalid to a substring expected in the
# resulting ValidationError.
INVALID_INITIAL_CONFIGS = [
    ("unknown-dependency", "unknown module dependency"),
    ("missing-default", "Unable to configure"),
    ("all-excluded-defaults", "exclude_from_defaults"),
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
    run_cli("sync", "--from-scratch", tmp_path, configs / "minimal")
    with pytest.raises(ValidationError, match="modified without updating version"):
        run_cli("validate", tmp_path, configs / "invalid" / "modified-no-allow-updates")


def test_validate_rejects_removal_without_deprecation(
    tmp_path: Path, configs: Path
) -> None:
    # Deploy a baseline module, then validate a config that drops it without first
    # deprecating it (and without --allow-all): this must be rejected.
    run_cli("sync", "--from-scratch", tmp_path, configs / "minimal")
    with pytest.raises(ValidationError, match="removed without prior deprecation"):
        run_cli("validate", tmp_path, configs / "invalid" / "removed-no-deprecation")


def test_validate_rejects_added_deprecated_module(
    tmp_path: Path, configs: Path
) -> None:
    # Deploy a baseline module, then validate a config that introduces a brand-new
    # release already in a deprecated state. Deprecating a module on initial creation
    # is only allowed with --allow-all, so a normal validate must reject it.
    run_cli("sync", "--from-scratch", tmp_path, configs / "minimal")
    with pytest.raises(ValidationError, match="cannot have deprecated status"):
        run_cli("validate", tmp_path, configs / "invalid" / "added-deprecated")


def test_validate_allows_added_deprecated_module_with_allow_all(
    tmp_path: Path, configs: Path
) -> None:
    # The --allow-all flag deliberately permits introducing an already-deprecated
    # release on initial creation.
    run_cli("sync", "--from-scratch", tmp_path, configs / "minimal")
    run_cli(
        "validate", "--allow-all", tmp_path, configs / "invalid" / "added-deprecated"
    )


def test_validate_test_build(tmp_path: Path, configs: Path) -> None:
    # --test-build actually builds the modules into a temporary area and syntax-checks
    # the generated shell entrypoints, so exercise it on a valid shell-only config.
    run_cli("validate", "--test-build", "--from-scratch", tmp_path, configs / "minimal")
