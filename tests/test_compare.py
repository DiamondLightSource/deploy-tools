from pathlib import Path
from shutil import rmtree

import pytest

from conftest import run_cli
from deploy_tools.compare import ComparisonError, compare_to_snapshot
from deploy_tools.layout import Layout
from deploy_tools.snapshot import SnapshotError

# The minimal config deploys a single shell-only module. Tests that start from a clean
# deployment and then corrupt it in one specific way share these coordinates.
MODULE_NAME = "example-module-shell"
MODULE_VERSION = "1.0"


def _sync_minimal(area: Path, configs: Path) -> Layout:
    """Deploy the minimal shell-only config into ``area`` and return its ``Layout``.

    Several tests below need a single, cleanly-deployed module that they then corrupt in
    one specific way, so this captures the shared from-scratch sync.

    Args:
        area: Empty deployment area to deploy into.
        configs: The ``configs`` fixture: the directory holding sample configurations.

    Returns:
        A ``Layout`` describing the freshly-deployed ``area``.
    """
    run_cli("sync", "--from-scratch", area, configs / "valid" / "minimal")
    return Layout(area)


def test_compare_accepts_clean_deployment(tmp_path: Path, configs: Path):
    # A deployment area is self-consistent immediately after a sync, so compare should
    # succeed and print nothing.
    _sync_minimal(tmp_path, configs)
    assert run_cli("compare", tmp_path) == ""


def test_compare_accepts_deprecated_modules(tmp_path: Path, configs: Path):
    # Ensure compare runs successfully with deprecated modulefile links.
    run_cli(
        "sync", "--from-scratch", tmp_path, configs / "golden-master" / "04-deprecated"
    )
    assert run_cli("compare", tmp_path) == ""


def test_compare_from_scratch_accepts_empty_area(tmp_path: Path):
    # --from-scratch only checks that the area is an existing, empty directory.
    assert run_cli("compare", "--from-scratch", tmp_path) == ""


def test_compare_from_scratch_rejects_non_empty_area(tmp_path: Path):
    # Any pre-existing content means the area is not ready for a from-scratch deploy.
    (tmp_path / "stray-file").touch()
    with pytest.raises(ComparisonError, match="not empty"):
        run_cli("compare", "--from-scratch", tmp_path)


def test_compare_rejects_missing_snapshot(tmp_path: Path):
    # An existing area with no deployment.yaml has no snapshot to compare against.
    with pytest.raises(SnapshotError, match="snapshot not found"):
        run_cli("compare", tmp_path)


def test_compare_rejects_module_without_modulefile(tmp_path: Path, configs: Path):
    # Removing a module's modulefile link leaves a built module that is not exposed.
    layout = _sync_minimal(tmp_path, configs)
    layout.get_modulefile_link(MODULE_NAME, MODULE_VERSION).unlink()
    with pytest.raises(ComparisonError, match="No modulefile found"):
        run_cli("compare", tmp_path)


def test_compare_rejects_modulefile_without_module(tmp_path: Path, configs: Path):
    # Removing the built module leaves a dangling modulefile link
    layout = _sync_minimal(tmp_path, configs)
    rmtree(layout.get_module_folder(MODULE_NAME, MODULE_VERSION))
    with pytest.raises(ComparisonError, match="without corresponding built module"):
        run_cli("compare", tmp_path)


def test_compare_rejects_duplicate_modulefiles(tmp_path: Path, configs: Path):
    # The same modulefile must not appear in both the live and deprecated areas.
    layout = _sync_minimal(tmp_path, configs)
    deprecated_link = layout.get_modulefile_link(
        MODULE_NAME, MODULE_VERSION, from_deprecated=True
    )
    deprecated_link.parent.mkdir(parents=True, exist_ok=True)
    deprecated_link.touch()
    with pytest.raises(ComparisonError, match="Duplicate modulefiles"):
        run_cli("compare", tmp_path)


def test_compare_rejects_release_mismatch(tmp_path: Path, configs: Path):
    # Tamper with the snapshot's record of the module so it no longer matches the module
    # configuration reconstructed from the deployment area.
    layout = _sync_minimal(tmp_path, configs)
    snapshot = layout.deployment_snapshot_path
    contents = snapshot.read_text()
    assert "Minimal shell-only module" in contents
    snapshot.write_text(
        contents.replace("Minimal shell-only module", "Tampered module")
    )
    with pytest.raises(ComparisonError, match="release configuration do not match"):
        run_cli("compare", tmp_path)


def test_compare_rejects_default_version_mismatch(tmp_path: Path, configs: Path):
    # Point the module's .version file at a different version than the snapshot expects.
    layout = _sync_minimal(tmp_path, configs)
    version_file = layout.get_default_version_file(MODULE_NAME)
    version_file.write_text("#%Module1.0\nset ModulesVersion 9.9\n")
    with pytest.raises(ComparisonError, match="default versions do not match"):
        run_cli("compare", tmp_path)


def test_compare_use_ref_detects_drift(tmp_path: Path, configs: Path):
    # sync commits a snapshot to the deployment area's git repo on every run. After two
    # syncs the area matches its own (HEAD) snapshot, but not the previous commit's
    # snapshot, which predates the module added by the second sync.
    run_cli(
        "sync", "--from-scratch", tmp_path, configs / "golden-master" / "01-initial"
    )
    run_cli("sync", tmp_path, configs / "golden-master" / "02-added")

    assert run_cli("compare", tmp_path) == ""
    assert run_cli("compare", "--use-ref", "HEAD", tmp_path) == ""

    with pytest.raises(ComparisonError, match="release configuration do not match"):
        run_cli("compare", "--use-ref", "HEAD~1", tmp_path)


def test_compare_from_scratch_rejects_missing_root(tmp_path: Path):
    # The CLI's argument validation rejects a non-existent path before the command runs,
    # so exercise this guard by calling the function directly.
    with pytest.raises(ComparisonError, match="does not exist"):
        compare_to_snapshot(tmp_path / "does-not-exist", from_scratch=True)


def test_compare_rejects_missing_root(tmp_path: Path):
    # As above, but for the snapshot-loading path used by a non from-scratch compare.
    with pytest.raises(SnapshotError, match="does not exist"):
        compare_to_snapshot(tmp_path / "does-not-exist")
