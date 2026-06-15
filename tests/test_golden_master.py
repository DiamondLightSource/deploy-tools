from pathlib import Path
from shutil import rmtree

from conftest import run_cli

# Fixed deployment path so that generated modulefiles (which embed absolute paths) match
# the committed golden master output. The lifecycle stages below all share this single
# deployment area, as each stage builds on the previous deployment state.
DEPLOYMENT_DIRNAME = "deploy-tools-output"
TEMP_OUT = Path("/tmp") / DEPLOYMENT_DIRNAME


def _assert_expected_files_match(expected_root: Path, actual_root: Path) -> None:
    """Assert every file under ``expected_root`` matches the one in ``actual_root``.

    This is a one-directional check: files present in the deployment area but absent
    from the golden master (e.g. ``.sif`` images, the ``.git`` directory) are ignored.
    Use ``_assert_absent`` to verify that files have actually been removed.
    """
    for expected in expected_root.glob("**/*"):
        if expected.is_dir():
            continue

        # check that the file exists in the output directory
        actual = actual_root / expected.relative_to(expected_root)
        assert actual.exists(), f"File {actual} does not exist."

        # check that the file contents are the same
        assert expected.read_text() == actual.read_text(), (
            f"File {actual} is different."
        )


def _assert_absent(root: Path, *relative_paths: str) -> None:
    """Assert that none of the given paths exist under ``root``."""
    for relative_path in relative_paths:
        path = root / relative_path
        assert not path.exists(), f"Path {path} should not exist."


def test_module_lifecycle(samples: Path, configs: Path):
    # make sure the output directory is empty and exists
    rmtree(TEMP_OUT, ignore_errors=True)
    TEMP_OUT.mkdir(exist_ok=True)

    # Stage 1: deploy the initial configuration into an empty area.
    run_cli("sync", "--from-scratch", TEMP_OUT, configs / "01-initial")
    _assert_expected_files_match(samples / "01-initial" / DEPLOYMENT_DIRNAME, TEMP_OUT)

    # Stage 2: deploy a brand-new module on an incremental (non from-scratch) sync. Its
    # files and modulefile link should appear, while the modules already deployed are
    # left untouched (this stage's golden master still contains them unchanged).
    run_cli("sync", TEMP_OUT, configs / "02-added")
    _assert_expected_files_match(samples / "02-added" / DEPLOYMENT_DIRNAME, TEMP_OUT)

    # Stage 3: update example-module-extra/1.0 in place. Its config changed and it was
    # deployed with allow_updates, so the module is rebuilt and replaced; the golden
    # master captures the new modulefile contents.
    run_cli("sync", TEMP_OUT, configs / "03-updated")
    _assert_expected_files_match(samples / "03-updated" / DEPLOYMENT_DIRNAME, TEMP_OUT)

    # Stage 4: deprecate example-module-deps/0.2 (en route to removal) and
    # example-module-extra/1.0 (to set up the restore that follows). Both modulefile
    # links move out of the live area into the deprecated area; built modules stay put.
    run_cli("sync", TEMP_OUT, configs / "04-deprecated")
    _assert_expected_files_match(
        samples / "04-deprecated" / DEPLOYMENT_DIRNAME, TEMP_OUT
    )
    _assert_absent(
        TEMP_OUT,
        "modulefiles/example-module-deps",
        "modulefiles/example-module-extra",
    )

    # Stage 5: restore example-module-extra/1.0 by un-deprecating it. Its modulefile
    # link moves back into the live area; example-module-deps/0.2 stays deprecated.
    run_cli("sync", TEMP_OUT, configs / "05-restored")
    _assert_expected_files_match(samples / "05-restored" / DEPLOYMENT_DIRNAME, TEMP_OUT)
    _assert_absent(TEMP_OUT, "deprecated/modulefiles/example-module-extra")

    # Stage 6: remove the now-deprecated example-module-deps/0.2 entirely. Both its
    # modulefile link and built module should be gone; example-module-extra remains.
    run_cli("sync", TEMP_OUT, configs / "06-removed")
    _assert_expected_files_match(samples / "06-removed" / DEPLOYMENT_DIRNAME, TEMP_OUT)
    _assert_absent(
        TEMP_OUT,
        "modules/example-module-deps",
        "deprecated/modulefiles/example-module-deps",
    )

    rmtree(TEMP_OUT, ignore_errors=True)
