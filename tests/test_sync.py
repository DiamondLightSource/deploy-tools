import shutil
from pathlib import Path

import pytest

from conftest import run_cli
from deploy_tools.layout import Layout
from deploy_tools.snapshot import SnapshotError
from deploy_tools.sync import SyncError

MODULE_NAME = "example-module-multi"


def test_deprecate_then_remove_multiple_versions_of_same_module(
    tmp_path: Path, configs: Path
) -> None:
    # Regression test for issues with removing name folders for the same module name
    # twice.
    run_cli(
        "sync", "--from-scratch", tmp_path, configs / "valid" / "multi-version-active"
    )

    layout = Layout(tmp_path)
    live_name_folder = layout.modulefiles_root / MODULE_NAME
    deprecated_name_folder = layout.deprecated_modulefiles_root / MODULE_NAME

    run_cli("sync", tmp_path, configs / "valid" / "multi-version-deprecated")
    assert not live_name_folder.exists()
    assert {p.name for p in deprecated_name_folder.iterdir()} == {"1.0", "2.0"}

    run_cli("sync", tmp_path, configs / "valid" / "empty")
    assert not deprecated_name_folder.exists()
    assert not (layout.modules_root / MODULE_NAME).exists()
    assert run_cli("compare", tmp_path) == ""


def test_sync_applies_explicit_default_version_over_auto_selection(
    tmp_path: Path, configs: Path
) -> None:
    # settings.yaml pins the default to 1.0 even though 2.0 is deployed and would be
    # auto-selected. Confirm the explicit pin is set in the on-disk .version file.
    run_cli(
        "sync",
        "--from-scratch",
        tmp_path,
        configs / "valid" / "multi-version-explicit-default",
    )

    default_version_file = Layout(tmp_path).get_default_version_file(MODULE_NAME)
    assert "set ModulesVersion 1.0" in default_version_file.read_text()


def test_sync_rejects_deployment_area_without_git_repo(
    tmp_path: Path, configs: Path
) -> None:
    # An area whose .git has been lost still has a snapshot but no history to commit
    # against: a corrupt state surfaced as a clean error, not a GitPython traceback.
    run_cli(
        "sync", "--from-scratch", tmp_path, configs / "valid" / "multi-version-active"
    )
    shutil.rmtree(tmp_path / ".git")

    with pytest.raises(SyncError, match="not a git repository"):
        run_cli("sync", tmp_path, configs / "valid" / "multi-version-active")


def test_sync_from_scratch_rejects_existing_snapshot(
    tmp_path: Path, configs: Path
) -> None:
    # --from-scratch must refuse to run when the area already holds a snapshot.
    run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "minimal")
    with pytest.raises(
        SnapshotError, match="must not exist when deploying from scratch"
    ):
        run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "minimal")
