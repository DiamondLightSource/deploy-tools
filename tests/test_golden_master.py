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
    # files and modulefile link should appear, while the modules from stage 1 are left
    # untouched (verified by the stage-2 golden master, which still contains them).
    run_cli("sync", TEMP_OUT, configs / "02-added")
    _assert_expected_files_match(samples / "02-added" / DEPLOYMENT_DIRNAME, TEMP_OUT)

    # Stage 3: deprecate example-module-deps/0.2. Its modulefile link should move out of
    # the live modulefiles area and into the deprecated area, while the built module is
    # left in place.
    run_cli("sync", TEMP_OUT, configs / "03-deprecated")
    _assert_expected_files_match(
        samples / "03-deprecated" / DEPLOYMENT_DIRNAME, TEMP_OUT
    )
    _assert_absent(TEMP_OUT, "modulefiles/example-module-deps")

    # Stage 4: remove the now-deprecated example-module-deps/0.2 entirely. Both its
    # modulefile link and built module should be gone.
    run_cli("sync", TEMP_OUT, configs / "04-removed")
    _assert_expected_files_match(samples / "04-removed" / DEPLOYMENT_DIRNAME, TEMP_OUT)
    _assert_absent(
        TEMP_OUT,
        "modules/example-module-deps",
        "deprecated/modulefiles/example-module-deps",
    )

    rmtree(TEMP_OUT, ignore_errors=True)
