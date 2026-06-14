import subprocess
import sys

from deploy_tools import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "deploy_tools", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
