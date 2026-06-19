from pathlib import Path

from conftest import run_cli

# Generated modulefiles embed the absolute deployment path. generate_samples.sh builds
# the committed golden master against this fixed root; the test deploys under a per-test
# tmp_path (parallel-safe, self-cleaning) and normalises this prefix away when diffing.
DEPLOYMENT_DIRNAME = "deploy-tools-output"
SAMPLE_DEPLOY_ROOT = Path("/tmp") / DEPLOYMENT_DIRNAME


def _assert_expected_files_match(expected_root: Path, actual_root: Path) -> None:
    """Assert every file under ``expected_root`` matches the one in ``actual_root``.

    This is a one-directional check: files present in the deployment area but absent
    from the golden master (e.g. ``.sif`` images, the ``.git`` directory) are ignored.
    Use ``_assert_absent`` to verify that files have actually been removed.

    The committed master embeds ``SAMPLE_DEPLOY_ROOT`` as the deployment path, in both
    file contents and absolute modulefile-link targets; that prefix is normalised to
    ``actual_root`` before comparing, so the deployment can happen anywhere.

    Args:
        expected_root: Root of the committed golden master tree.
        actual_root: Root of the deployment area to check against it.
    """
    for expected in expected_root.glob("**/*"):
        actual = actual_root / expected.relative_to(expected_root)

        # Modulefiles are symlinks whose absolute target embeds the deployment root;
        # compare the normalised target, don't follow the (dangling) committed link.
        if expected.is_symlink():
            assert actual.is_symlink(), f"{actual} is not a symlink."
            expected_target = str(expected.readlink()).replace(
                str(SAMPLE_DEPLOY_ROOT), str(actual_root)
            )
            assert expected_target == str(actual.readlink()), (
                f"Symlink {actual} points to the wrong target."
            )
            continue

        if expected.is_dir():
            continue

        # check that the file exists in the output directory
        assert actual.exists(), f"File {actual} does not exist."

        # compare contents, normalising the embedded deployment-root prefix
        expected_text = expected.read_text().replace(
            str(SAMPLE_DEPLOY_ROOT), str(actual_root)
        )
        assert expected_text == actual.read_text(), f"File {actual} is different."


def _assert_absent(root: Path, *relative_paths: str) -> None:
    """Assert that none of the given paths exist under ``root``.

    Args:
        root: The base directory to resolve paths against.
        relative_paths: Paths, relative to ``root``, that must not exist.
    """
    for relative_path in relative_paths:
        path = root / relative_path
        assert not path.exists(), f"Path {path} should not exist."


def _assert_validate_matches(expected_dir: Path, *cli_args: str | Path) -> None:
    """Assert ``validate``'s printed summary matches the committed golden master.

    ``validate`` is read-only and previews the next sync, so it is run against the
    deployment area in its pre-sync state.

    Args:
        expected_dir: Stage directory containing the expected ``validate.txt``.
        cli_args: Arguments passed to the ``validate`` CLI command.
    """
    expected = (expected_dir / "validate.txt").read_text()
    assert run_cli("validate", *cli_args) == expected


def _run_stage(
    samples: Path,
    configs: Path,
    area: Path,
    stage: str,
    *,
    from_scratch: bool = False,
    absent: tuple[str, ...] = (),
) -> None:
    """Preview, sync, and verify one lifecycle stage against its golden master.

    Args:
        samples: The committed golden-master samples directory.
        configs: The ``configs`` fixture (root of the test configurations).
        area: The shared deployment area, built up across stages.
        stage: The lifecycle stage name, e.g. ``04-deprecated``.
        from_scratch: Whether this stage deploys into an empty area.
        absent: Paths, relative to ``area``, that must not exist after the sync.
    """
    flags = ["--from-scratch"] if from_scratch else []
    stage_config = configs / "golden-master" / stage
    _assert_validate_matches(samples / stage, *flags, area, stage_config)
    run_cli("sync", *flags, area, stage_config)
    _assert_expected_files_match(samples / stage / DEPLOYMENT_DIRNAME, area)
    _assert_absent(area, *absent)


def test_module_lifecycle(
    samples: Path, configs: Path, stub_apptainer_pull: None, tmp_path: Path
) -> None:
    # tmp_path is a fresh, empty, per-test directory; the stages below share it as one
    # deployment area, each building on the previous state, with no cross-run leakage.

    # Stage 1: deploy the initial configuration into an empty area.
    _run_stage(samples, configs, tmp_path, "01-initial", from_scratch=True)

    # Stage 2: deploy a brand-new module on an incremental (non from-scratch) sync; the
    # modules already deployed are left untouched.
    _run_stage(samples, configs, tmp_path, "02-added")

    # Stage 3: update example-module-extra/1.0 in place (allowed via allow_updates), so
    # the module is rebuilt and its modulefile contents change.
    _run_stage(samples, configs, tmp_path, "03-updated")

    # Stage 4: deprecate example-module-deps/0.2 (en route to removal) and
    # example-module-extra/1.0 (to set up the restore that follows). Both modulefile
    # links move out of the live area into the deprecated area; built modules stay put.
    _run_stage(
        samples,
        configs,
        tmp_path,
        "04-deprecated",
        absent=(
            "modulefiles/example-module-deps",
            "modulefiles/example-module-extra",
        ),
    )

    # Stage 5: restore example-module-extra/1.0 by un-deprecating it. Its modulefile
    # link moves back into the live area; example-module-deps/0.2 stays deprecated.
    _run_stage(
        samples,
        configs,
        tmp_path,
        "05-restored",
        absent=("deprecated/modulefiles/example-module-extra",),
    )

    # Stage 6: remove the now-deprecated example-module-deps/0.2 entirely. Both its
    # modulefile link and built module should be gone; example-module-extra remains.
    _run_stage(
        samples,
        configs,
        tmp_path,
        "06-removed",
        absent=(
            "modules/example-module-deps",
            "deprecated/modulefiles/example-module-deps",
        ),
    )
