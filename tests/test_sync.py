from pathlib import Path

from conftest import run_cli
from deploy_tools.layout import Layout

MODULE_NAME = "example-module-multi"


def test_deprecate_then_remove_multiple_versions_of_same_module(
    tmp_path: Path, configs: Path
):
    # Regression test for issues with removing name folders for the same module name
    # twice.
    run_cli("sync", "--from-scratch", tmp_path, configs / "multi-version-active")

    layout = Layout(tmp_path)
    live_name_folder = layout.modulefiles_root / MODULE_NAME
    deprecated_name_folder = layout.deprecated_modulefiles_root / MODULE_NAME

    run_cli("sync", tmp_path, configs / "multi-version-deprecated")
    assert not live_name_folder.exists()
    assert {p.name for p in deprecated_name_folder.iterdir()} == {"1.0", "2.0"}

    run_cli("sync", tmp_path, configs / "empty")
    assert not deprecated_name_folder.exists()
    assert not (layout.modules_root / MODULE_NAME).exists()
    assert run_cli("compare", tmp_path) == ""
