from pathlib import Path

from conftest import run_cli


def test_sync_builds_real_sif_file(configs: Path, tmp_path: Path) -> None:
    # The golden-master test stubs the apptainer pull, so this is the only test that
    # exercises a real one. It needs apptainer installed and network access to ghcr.io;
    # a missing binary fails the test (via run_cli) rather than skipping it, by design.
    run_cli("sync", "--from-scratch", tmp_path, configs / "valid" / "apptainer-pull")

    sif_files = list(tmp_path.glob("**/*.sif"))
    assert sif_files, "sync did not produce a .sif file"
    assert all(f.stat().st_size > 0 for f in sif_files), "produced .sif file is empty"
