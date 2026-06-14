from pathlib import Path
from shutil import rmtree

from conftest import run_cli


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
