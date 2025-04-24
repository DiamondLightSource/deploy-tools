import subprocess
import sys
import tempfile
from pathlib import Path
from shutil import rmtree

from conftest import run_cli
from deploy_tools import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "deploy_tools", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


def test_schema(schemas: Path):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Generate up to date schema files
        run_cli("schema", tmp_path)

        # Compare with the expected schema files
        for schema in tmp_path.glob("*.json"):
            expected = schemas / schema.name
            if schema.read_text() != expected.read_text():
                raise AssertionError(f"Schema file {expected} is out of date.")


def test_demo_configuration(samples: Path, demo_config: Path):
    # use a fixed path for the demo configuration so that the outputs are consistent
    out_folder = "deploy-tools-output"
    temp_out = Path("/tmp") / out_folder
    expected_out = samples / out_folder

    # make sure the output directory is empty and exists
    rmtree(temp_out, ignore_errors=True)
    temp_out.mkdir(exist_ok=True)

    # generate the demo configuration output
    run_cli("sync", "--from-scratch", str(temp_out), str(demo_config))

    # compare the output with the expected output
    for expected in expected_out.glob("**/*"):
        if expected.is_dir():
            continue
        # check that the file exists in the output directory
        out_file = temp_out / expected.relative_to(expected_out)
        assert out_file.exists(), f"File {out_file} does not exist."

        # check that the file contents are the same
        assert expected.read_text() == out_file.read_text(), (
            f"File {out_file} is different."
        )

    rmtree(temp_out, ignore_errors=True)
