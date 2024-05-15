import subprocess
import sys

from deploytools import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "deploytools", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
